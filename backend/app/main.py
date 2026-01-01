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
from app.analytics.features.players_analytics import extract_and_aggregate_players, filter_players
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
MATCHES_DATA: List[ApiMatch] = []
PLAYERS_DATA: List[PlayerStats] = [] # Cache de jugadores
TEAMS_PER_YEAR: Dict[str, List[str]] = {} # year -> [team_codes]

try:
    all_teams = {}
    all_matches = []

    for year in YEARS:
        # ... (keep existing loop) ...
        # (This block is skipped in replacement content for brevity if not modifying logic inside loop immediately. 
        # But we need to make sure we populate PLAYERS_DATA *after* the loop).
        pass 

    # --- REEMPLAZAR BLOQUE DE CARGA EXISTENTE SI ES NECESARIO O AGREGAR AL FINAL ---
    # Para simplicidad, asumo que insertamos esto DESPUES del bucle for year in YEARS principal
    # Pero replace_file_content necesita contexto contiguo.
    # Mejor edito el bloque de "try... except" completo o la sección POSTERIOR a la carga.
    
    # Voy a buscar donde termina la carga (lineas ~85-90) y agregar la población de PLAYERS.
    
# Mejor estrategia: Modificar donde se define TEAMS_DATA y MATCHES_DATA para incluir PLAYERS_DATA
# Y luego buscar el final de la carga para llamar a extract_and_aggregate_players

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

    # Convertir a listas finales
    TEAMS_DATA = list(all_teams.values())
    MATCHES_DATA = all_matches
    
    # NEW: Populate Players Cache
    PLAYERS_DATA = extract_and_aggregate_players(MATCHES_DATA)
    
    print(f"Datos cargados exitosamente: {len(TEAMS_DATA)} equipos, {len(MATCHES_DATA)} partidos, {len(PLAYERS_DATA)} jugadores (goleadores).")

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
    
    # Mockup inicial para futura evolución de la predicción
    # Aquí es donde integraremos ML o heurísticas avanzadas.
    # Por ahora devolvemos estático o simple logic wrapper.
    
    # Lógica base existente
    base_prediction = predict_match(team_a, team_b, MATCHES_DATA)
    
    # Mockup de datos extendidos que queremos devolver en el futuro
    mockup_advanced = {
        **base_prediction, # Mantiene compatibilidad con lo actual
        "advanced_metrics": {
            "win_probability_a": 0.45,
            "win_probability_b": 0.30, 
            "draw_probability": 0.25,
            "predicted_score": "2-1",
            "confidence_score": 0.75, # 0-1
            "key_factors": [
                "Team A has better recent form",
                "Historical H2H favors Team A slightly"
            ]
        },
        "simulation_details": {
            "iterations": 1000,
            "most_likely_outcome": "Win A"
        }
    }
    
    return mockup_advanced


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


# --- ENDPOINTS DE JUGADORES (NUEVO) ---

@router.get("/players", response_model=List[PlayerStats])
def get_players(
    teamId: Optional[str] = Query(None, description="Filtrar por Team Code"),
    search: Optional[str] = Query(None, description="Buscar por nombre parcial"),
    minGoals: int = Query(0, ge=0)
):
    """
    Listado de jugadores (goleadores).
    Nota: Solo incluye jugadores que han marcado al menos un gol en la historia,
    ya que no tenemos plantillas completas.
    """
    if not PLAYERS_DATA:
        # Intentar recargar si está vacío (edge case init fail)
        if MATCHES_DATA and not PLAYERS_DATA:
            global PLAYERS_DATA
            PLAYERS_DATA.extend(extract_and_aggregate_players(MATCHES_DATA))
            
        if not PLAYERS_DATA:
             raise HTTPException(status_code=503, detail="Datos de jugadores no disponibles")

    return filter_players(PLAYERS_DATA, team_id=teamId, min_goals=minGoals, search=search)

@router.get("/players/{id}", response_model=PlayerStats)
def get_player_by_id(id: str):
    """
    Obtener perfil de jugador. 
    ID actual es 'Nombre_TeamCode' (e.g. 'Maradona_ARG') para unicidad simple,
    o simplemente iteramos buscando match por nombre si el ID es simple.
    Para robustez, usaremos busqueda por Name+TeamCode si viene en el formato,
    o search first match.
    El front debería usar el ID que viene en /players (que, ups, no definimos campo ID explicito en PlayerStats, usamos Name+Team implícito).
    Vamos a asumir que id = Name (si es único) o esperamos un formato compuesto.
    Simplificación: Busqueda exacta por nombre.
    """
    if not PLAYERS_DATA: raise HTTPException(status_code=503, detail="Datos no cargados")
    
    # Decodificar ID si es necesario (URL encoded)
    # Busqueda: Primero match exacto de ID contra (Name + '_' + TeamCode)
    # Si no, match exacto solo Nombre.
    
    player = next((p for p in PLAYERS_DATA if f"{p.name}_{p.team_code}" == id), None)
    
    if not player:
         # Fallback: Try match by name only (careful with homonyms)
         player = next((p for p in PLAYERS_DATA if p.name == id), None)
         
    if not player:
        raise HTTPException(status_code=404, detail=f"Player '{id}' not found")
        
    return player

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
