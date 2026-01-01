from fastapi import FastAPI, APIRouter, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
from pathlib import Path

from app.core.entities import ApiMatch, TeamGroupInfo, TeamStats, TeamTrendStats, RivalStats
from app.data.ingestion.json_reader import load_worldcup_data_from_json, load_worldcup_groups_data_from_json
from app.data.cleaning.match_cleaner import flatten_and_transform_matches, filter_matches_by_team
from app.analytics.stats_calculator import calculate_team_stats, calculate_team_trends, calculate_top_rivals

# Analytics Features Imports
from app.analytics.features.goals_analytics import (
    calculate_goals_summary, 
    calculate_team_rankings, 
    calculate_h2h_goals_summary, 
    calculate_stage_summary,
    calculate_minute_distribution,
    calculate_time_split,
    get_match_goals_timeline,
    calculate_goal_records
)
from app.analytics.features.history import calculate_head_to_head
from app.analytics.features.goal_stats import calculate_goal_stats 
from app.analytics.features.streaks import calculate_streak_stats
from app.analytics.features.home_away import calculate_home_away_stats
from app.analytics.features.momentum import calculate_momentum
from app.analytics.features.graph_analysis import calculate_graph_stats
from app.analytics.features.goal_percentage import calculate_goal_percentage_stats
from app.analytics.features.effectiveness import calculate_effectiveness_stats
from app.analytics.features.possession import calculate_possession_stats
from app.analytics.match_predictor import predict_match

# Variables globales para almacenar los datos en memoria
TEAMS_DATA: List[TeamGroupInfo] = []
MATCHES_DATA: List[ApiMatch] = []
TEAMS_PER_YEAR: Dict[str, List[str]] = {} # year -> [team_codes]

try:
    all_teams = {}
    all_matches = []

    for year in YEARS:
        year_dir = DATASETS_DIR / year
        WORLDCUP_GROUPS_JSON_PATH = year_dir / "worldcup.groups.json"
        WORLDCUP_JSON_PATH = year_dir / "worldcup.json"

        # Cargar grupos y equipos
        if WORLDCUP_GROUPS_JSON_PATH.exists():
            worldcup_groups_data = load_worldcup_groups_data_from_json(WORLDCUP_GROUPS_JSON_PATH)
            teams_in_year = []
            for group in worldcup_groups_data.groups:
                for team in group.teams:
                    all_teams[team.code] = team
                    teams_in_year.append(team.code)
            TEAMS_PER_YEAR[year] = teams_in_year

        # Cargar partidos
        if WORLDCUP_JSON_PATH.exists():
            worldcup_data = load_worldcup_data_from_json(WORLDCUP_JSON_PATH)
            all_matches.extend(flatten_and_transform_matches(worldcup_data, year=year))

    TEAMS_DATA = sorted(list(all_teams.values()), key=lambda x: x.name)
    MATCHES_DATA = all_matches

except Exception as e:
    print(f"Error crítico al cargar datos: {e}")
    # No fallamos hard aquí para permitir que la app arranque y muestre error 503 si se piden datos
    pass


# ==============================================================================
# ROUTER Y ENDPOINTS
# ==============================================================================

router = APIRouter(prefix="/api/v1", tags=["api-unificada"])

# --- ENDPOINTS BÁSICOS DE EQUIPOS Y ANÁLISIS ---

# Devuelve la lista de equipos disponibles, con filtros opcionales
@router.get("/teams", response_model=List[TeamGroupInfo])
def obtener_equipos(
    worldcupId: Optional[str] = Query(None, description="Filtra equipos que participaron en este año"),
    sort: Optional[str] = Query("name", description="Campo de ordenamiento (name, code)")
):
    filtered_teams = TEAMS_DATA
    
    if worldcupId:
        if worldcupId in TEAMS_PER_YEAR:
            participating_codes = set(TEAMS_PER_YEAR[worldcupId])
            filtered_teams = [t for t in filtered_teams if t.code in participating_codes]
        else:
            return [] # Año no encontrado o sin equipos

    # Ordenamiento básico
    if sort == "code":
        filtered_teams = sorted(filtered_teams, key=lambda x: x.code)
    else:
        filtered_teams = sorted(filtered_teams, key=lambda x: x.name)
        
    return filtered_teams

# Calcula y devuelve estadísticas generales de un equipo
@router.get("/stats/{team_code}", response_model=TeamStats)
def obtener_estadisticas_por_equipo(team_code: str):
    return calculate_team_stats(MATCHES_DATA, team_code)

# (Nuevo) Obtiene las tendencias históricas (stats por año) de un equipo
@router.get("/teams/{team_code}/trends", response_model=List[TeamTrendStats])
def obtener_tendencias_equipo(team_code: str):
    if not MATCHES_DATA: raise HTTPException(status_code=503, detail="Datos no cargados")
    return calculate_team_trends(MATCHES_DATA, team_code)

# (Nuevo) Obtiene los rivales históricos ordenados por cantidad de partidos
@router.get("/teams/{team_code}/rivals", response_model=List[RivalStats])
def obtener_rivales_equipo(team_code: str):
    if not MATCHES_DATA: raise HTTPException(status_code=503, detail="Datos no cargados")
    return calculate_top_rivals(MATCHES_DATA, team_code)

# Devuelve todos los partidos cargados en memoria (Legacy)
@router.get("/analisis", response_model=List[ApiMatch])
def obtener_analisis():
    return MATCHES_DATA


# --- ENDPOINTS DE MATCHES (Búsqueda y Filtros) ---

# Busca y filtra partidos con paginación y criterios avanzados
@router.get("/matches", response_model=Dict[str, Any])
def get_matches(
    worldcupId: Optional[str] = Query(None, description="Filtra por año del mundial"),
    stage: Optional[str] = Query(None, description="Filtra por fase/ronda"),
    teamA: Optional[str] = Query(None, description="Filtra por equipo A"),
    teamB: Optional[str] = Query(None, description="Filtra por equipo B"),
    dateFrom: Optional[str] = Query(None, description="Fecha desde (YYYY-MM-DD)"),
    dateTo: Optional[str] = Query(None, description="Fecha hasta (YYYY-MM-DD)"),
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100)
):
    if not MATCHES_DATA:
        raise HTTPException(status_code=503, detail="Datos no cargados")

    filtered_matches = MATCHES_DATA

    # Filtros
    if worldcupId:
        filtered_matches = [m for m in filtered_matches if m.year == worldcupId]
    
    if stage:
        filtered_matches = [m for m in filtered_matches if stage.lower() in m.stage.lower()]

    if teamA:
        tA = teamA.lower()
        filtered_matches = [m for m in filtered_matches if tA in m.team_a.lower() or tA in m.team_a_code.lower()]
    
    if teamB:
        tB = teamB.lower()
        filtered_matches = [m for m in filtered_matches if tB in m.team_b.lower() or tB in m.team_b_code.lower()]

    if dateFrom:
        filtered_matches = [m for m in filtered_matches if m.date >= dateFrom]
    
    if dateTo:
        filtered_matches = [m for m in filtered_matches if m.date <= dateTo]

    # Ordenamiento
    filtered_matches.sort(key=lambda x: (x.date, x.id), reverse=True)

    # Paginación
    total_items = len(filtered_matches)
    total_pages = (total_items + pageSize - 1) // pageSize
    start_idx = (page - 1) * pageSize
    end_idx = start_idx + pageSize
    
    return {
        "data": filtered_matches[start_idx:end_idx],
        "meta": {
            "total": total_items,
            "page": page,
            "pageSize": pageSize,
            "totalPages": total_pages
        }
    }

# Obtiene un partido específico por su ID Global (Ej: 1990-1)
@router.get("/matches/{id}", response_model=ApiMatch)
def get_match_by_global_id(id: str):
    if not MATCHES_DATA:
        raise HTTPException(status_code=503, detail="Datos no cargados")

    match = next((m for m in MATCHES_DATA if m.global_id == id), None)
    if not match:
        raise HTTPException(status_code=404, detail=f"Match {id} not found")
    return match

# Obtiene un partido específico por Año y Número (Legacy/Alternativo)
@router.get("/matches/{year}/{match_id}", response_model=ApiMatch)
def get_match_by_year_and_id(year: str, match_id: int):
    if not MATCHES_DATA:
        raise HTTPException(status_code=503, detail="Datos no cargados")

    match = next((m for m in MATCHES_DATA if m.year == year and m.id == match_id), None)
    if not match:
        raise HTTPException(status_code=404, detail=f"Match {year}-{match_id} not found")
    return match


# --- ENDPOINTS DE PREDICCIONES Y ESTADÍSTICAS AVANZADAS ---

# Obtiene el historial de enfrentamientos (Head to Head) entre dos equipos
@router.get("/predict/history/{team_a}/{team_b}")
def get_history(team_a: str, team_b: str):
    if not MATCHES_DATA: raise HTTPException(status_code=503, detail="Datos no cargados")
    return calculate_head_to_head(team_a, team_b, MATCHES_DATA)

# Obtiene estadísticas de goles a favor y en contra
@router.get("/predict/stats/goals/{team_code}")
def get_goal_stats(team_code: str):
    if not MATCHES_DATA: raise HTTPException(status_code=503, detail="Datos no cargados")
    return calculate_goal_stats(team_code, MATCHES_DATA)

# Obtiene estadísticas de rachas (victorias/derrotas consecutivas)
@router.get("/predict/stats/streaks/{team_code}")
def get_streak_stats(team_code: str):
    if not MATCHES_DATA: raise HTTPException(status_code=503, detail="Datos no cargados")
    return calculate_streak_stats(team_code, MATCHES_DATA)

# Obtiene estadísticas de rendimiento local vs visitante
@router.get("/predict/stats/home-away/{team_code}")
def get_home_away_stats(team_code: str):
    if not MATCHES_DATA: raise HTTPException(status_code=503, detail="Datos no cargados")
    return calculate_home_away_stats(team_code, MATCHES_DATA)

# Obtiene el Momentum (tendencia reciente) del equipo
@router.get("/predict/stats/momentum/{team_code}")
def get_momentum_stats(team_code: str):
    if not MATCHES_DATA: raise HTTPException(status_code=503, detail="Datos no cargados")
    return calculate_momentum(team_code, MATCHES_DATA)

# Obtiene análisis de grafo (victorias indirectas)
@router.get("/predict/stats/graph/{team_code}")
def get_graph_stats(team_code: str):
    if not MATCHES_DATA: raise HTTPException(status_code=503, detail="Datos no cargados")
    return calculate_graph_stats(team_code, MATCHES_DATA)

# Obtiene porcentaje de partidos con goles
@router.get("/predict/stats/goal-percentage/{team_code}")
def get_goal_percentage_stats(team_code: str):
    if not MATCHES_DATA: raise HTTPException(status_code=503, detail="Datos no cargados")
    return calculate_goal_percentage_stats(team_code, MATCHES_DATA)

# Obtiene estadísticas de efectividad (goles vs intentos)
@router.get("/predict/stats/effectiveness/{team_code}")
def get_effectiveness_stats(team_code: str):
    if not MATCHES_DATA: raise HTTPException(status_code=503, detail="Datos no cargados")
    return calculate_effectiveness_stats(team_code, MATCHES_DATA)

# Obtiene estadísticas de posesión (estimada o real)
@router.get("/predict/stats/possession/{team_code}")
def get_possession_stats(team_code: str):
    if not MATCHES_DATA: raise HTTPException(status_code=503, detail="Datos no cargados")
    return calculate_possession_stats(team_code, MATCHES_DATA)

# Genera una predicción de resultado entre dos equipos
@router.get("/predict/match-prediction/{team_a}/{team_b}")
def get_match_prediction(team_a: str, team_b: str):
    if not MATCHES_DATA: raise HTTPException(status_code=503, detail="Datos no cargados")
    return predict_match(team_a, team_b, MATCHES_DATA)


# --- ENDPOINTS DE GOLES (NUEVO) ---

@router.get("/goals/summary", response_model=Dict[str, Any])
def get_goals_summary(
    worldcupId: Optional[str] = Query(None, description="Filtrar por año"),
    dateFrom: Optional[str] = Query(None, description="Desde fecha YYYY-MM-DD"),
    dateTo: Optional[str] = Query(None, description="Hasta fecha YYYY-MM-DD"),
    stage: Optional[str] = Query(None, description="Filtra por fase")
):
    if not MATCHES_DATA: raise HTTPException(status_code=503, detail="Datos no cargados")
    
    matches = MATCHES_DATA
    if worldcupId: matches = [m for m in matches if m.year == worldcupId]
    if stage: matches = [m for m in matches if stage.lower() in m.stage.lower()]
    if dateFrom: matches = [m for m in matches if m.date >= dateFrom]
    if dateTo: matches = [m for m in matches if m.date <= dateTo]
    
    return calculate_goals_summary(matches)

@router.get("/goals/team-rankings", response_model=List[Dict[str, Any]])
def get_team_goal_rankings(
    worldcupId: Optional[str] = Query(None),
    stage: Optional[str] = Query(None),
    dateFrom: Optional[str] = Query(None),
    dateTo: Optional[str] = Query(None),
    sort: str = Query("gf", description="gf|ga|gd|avgGf"),
    limit: int = Query(10, le=50)
):
    if not MATCHES_DATA: raise HTTPException(status_code=503, detail="Datos no cargados")
    
    matches = MATCHES_DATA
    if worldcupId: matches = [m for m in matches if m.year == worldcupId]
    if stage: matches = [m for m in matches if stage.lower() in m.stage.lower()]
    if dateFrom: matches = [m for m in matches if m.date >= dateFrom]
    if dateTo: matches = [m for m in matches if m.date <= dateTo]
    
    return calculate_team_rankings(matches, sort_by=sort, limit=limit)

@router.get("/goals/h2h-summary", response_model=Dict[str, Any])
def get_h2h_goals_summary(
    teamA: str, 
    teamB: str,
    worldcupId: Optional[str] = Query(None),
    stage: Optional[str] = Query(None),
    dateFrom: Optional[str] = Query(None),
    dateTo: Optional[str] = Query(None)
):
    if not MATCHES_DATA: raise HTTPException(status_code=503, detail="Datos no cargados")
    
    matches = MATCHES_DATA
    if worldcupId: matches = [m for m in matches if m.year == worldcupId]
    if stage: matches = [m for m in matches if stage.lower() in m.stage.lower()]
    if dateFrom: matches = [m for m in matches if m.date >= dateFrom]
    if dateTo: matches = [m for m in matches if m.date <= dateTo]

    return calculate_h2h_goals_summary(teamA, teamB, matches)

@router.get("/goals/stage-summary", response_model=List[Dict[str, Any]])
def get_stage_goals_summary(
    worldcupId: Optional[str] = Query(None),
    dateFrom: Optional[str] = Query(None),
    dateTo: Optional[str] = Query(None)
):
    if not MATCHES_DATA: raise HTTPException(status_code=503, detail="Datos no cargados")
    
    matches = MATCHES_DATA
    if worldcupId: matches = [m for m in matches if m.year == worldcupId]
    if dateFrom: matches = [m for m in matches if m.date >= dateFrom]
    if dateTo: matches = [m for m in matches if m.date <= dateTo]
    
    return calculate_stage_summary(matches)

@router.get("/goals/minute-distribution", response_model=List[Dict[str, Any]])
def get_minute_distribution(
    worldcupId: Optional[str] = Query(None),
    teamId: Optional[str] = Query(None, description="Team Code"),
    stage: Optional[str] = Query(None),
    bins: int = Query(15, ge=1, le=45)
):
    if not MATCHES_DATA: raise HTTPException(status_code=503, detail="Datos no cargados")
    
    matches = MATCHES_DATA
    if worldcupId: matches = [m for m in matches if m.year == worldcupId]
    if stage: matches = [m for m in matches if stage.lower() in m.stage.lower()]
    if teamId: matches = filter_matches_by_team(matches, teamId)
    
    return calculate_minute_distribution(matches, bin_size=bins)

@router.get("/goals/time-split", response_model=Dict[str, int])
def get_time_split(
    worldcupId: Optional[str] = Query(None),
    teamId: Optional[str] = Query(None),
    mode: str = Query("halves", regex="^(halves)$") # Future extension: |bins
):
    if not MATCHES_DATA: raise HTTPException(status_code=503, detail="Datos no cargados")
    
    matches = MATCHES_DATA
    if worldcupId: matches = [m for m in matches if m.year == worldcupId]
    if teamId: matches = filter_matches_by_team(matches, teamId)
    
    return calculate_time_split(matches, mode=mode)

@router.get("/goals/matches/{match_id}/timeline", response_model=List[Dict[str, Any]])
def get_match_timeline(match_id: str):
    """Get timeline for a specific match by Global ID (e.g. 1990-1)"""
    if not MATCHES_DATA: raise HTTPException(status_code=503, detail="Datos no cargados")
    
    match = next((m for m in MATCHES_DATA if m.global_id == match_id), None)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
        
    return get_match_goals_timeline(match)

@router.get("/goals/records", response_model=Dict[str, Any])
def get_goal_records(
    worldcupId: Optional[str] = Query(None),
    stage: Optional[str] = Query(None),
    dateFrom: Optional[str] = Query(None),
    dateTo: Optional[str] = Query(None)
):
    if not MATCHES_DATA: raise HTTPException(status_code=503, detail="Datos no cargados")
    
    matches = MATCHES_DATA
    if worldcupId: matches = [m for m in matches if m.year == worldcupId]
    if stage: matches = [m for m in matches if stage.lower() in m.stage.lower()]
    if dateFrom: matches = [m for m in matches if m.date >= dateFrom]
    if dateTo: matches = [m for m in matches if m.date <= dateTo]
    
    return calculate_goal_records(matches)

# ==============================================================================
# CONFIGURACIÓN DE LA APP
# ==============================================================================

app = FastAPI(title="Plantilla Predictor - FastAPI Unified")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Bienvenido al API del Predictor Mundial (Unificada)"}

@app.get("/api/health")
def health():
    return {"ok": True}

# Incluir el router único
app.include_router(router)
