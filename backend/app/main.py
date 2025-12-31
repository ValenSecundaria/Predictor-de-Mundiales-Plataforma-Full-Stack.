from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pathlib import Path

from app.core.entities import ApiMatch, TeamGroupInfo, TeamStats
from app.data.ingestion.json_reader import load_worldcup_data_from_json, load_worldcup_groups_data_from_json
from app.data.cleaning.match_cleaner import flatten_and_transform_matches, filter_matches_by_team
from app.analytics.stats_calculator import calculate_team_stats

from app.api.routers import predict as predict_router
from app.api.routers import matches as matches_router

router = APIRouter(prefix="/api/v1", tags=["analisis"])

BASE_DIR = Path(__file__).resolve().parent
DATASETS_DIR = BASE_DIR / "data" / "datasets"

def get_available_years(datasets_dir: Path) -> List[str]:
    years = []
    if datasets_dir.exists():
        for item in datasets_dir.iterdir():
            if item.is_dir() and item.name.isdigit():
                if (item / "worldcup.json").exists():
                    years.append(item.name)
    return sorted(years)

YEARS = get_available_years(DATASETS_DIR)

try:
    all_teams = {}
    all_matches = []

    for year in YEARS:
        year_dir = DATASETS_DIR / year
        WORLDCUP_GROUPS_JSON_PATH = year_dir / "worldcup.groups.json"
        WORLDCUP_JSON_PATH = year_dir / "worldcup.json"

        worldcup_groups_data = load_worldcup_groups_data_from_json(WORLDCUP_GROUPS_JSON_PATH)
        for group in worldcup_groups_data.groups:
            for team in group.teams:
                all_teams[team.code] = team

        worldcup_data = load_worldcup_data_from_json(WORLDCUP_JSON_PATH)
        all_matches.extend(flatten_and_transform_matches(worldcup_data, year=year))

    TEAMS_DATA = sorted(list(all_teams.values()), key=lambda x: x.name)
    MATCHES_DATA = all_matches

    predict_router.MATCHES_STORE = MATCHES_DATA
    matches_router.MATCHES_STORE = MATCHES_DATA

except FileNotFoundError as e:
    raise RuntimeError(f"No se pudo iniciar la aplicación: Archivo de datos no encontrado. {e}")
except Exception as e:
    raise RuntimeError(f"Error crítico al procesar datos durante el inicio: {e}")

@router.get("/teams", response_model=List[TeamGroupInfo])
def obtener_equipos():
    return TEAMS_DATA

@router.get("/analisis", response_model=List[ApiMatch])
def obtener_analisis():
    return MATCHES_DATA

@router.get("/analisis/{team_code}", response_model=List[ApiMatch])
def obtener_partidos_por_equipo(team_code: str):
    partidos_filtrados = filter_matches_by_team(MATCHES_DATA, team_code)
    return partidos_filtrados
		
@router.get("/stats/{team_code}", response_model=TeamStats)
def obtener_estadisticas_por_equipo(team_code: str):
    stats = calculate_team_stats(MATCHES_DATA, team_code)
    return stats

app = FastAPI(title="Plantilla Predictor - FastAPI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Bienvenido al API del Predictor Mundial"}

@app.get("/api/health")
def health(): return {"ok": True}

app.include_router(router)
app.include_router(predict_router.router)
app.include_router(matches_router.router)
