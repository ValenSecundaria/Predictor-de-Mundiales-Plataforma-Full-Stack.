from pydantic import BaseModel, Field
from typing import List, Optional


# ==============================================================================
# 1. MODELOS DE DOMINIO (Representan los datos crudos del JSON)
#    Estos modelos deben coincidir exactamente con la estructura de worldcup.json
# ==============================================================================

class TeamInfo(BaseModel):
    """Representa la información de un equipo en el JSON."""
    name: str
    code: str

class GoalInfo(BaseModel):
    """Representa un gol en el JSON."""
    name: str
    minute: int
    offset: Optional[int] = None
    owngoal: Optional[bool] = False
    penalty: Optional[bool] = False

class MatchInfo(BaseModel):
    """Representa un partido completo con todos sus detalles del JSON."""
    num: int
    date: str
    team1: TeamInfo
    team2: TeamInfo
    score1: int
    score2: int
    goals1: List[GoalInfo] = []
    goals2: List[GoalInfo] = []
    group: Optional[str] = None

class RoundInfo(BaseModel):
    """Representa una ronda o fase del torneo."""
    name: str
    matches: List[MatchInfo]

class WorldCupData(BaseModel):
    """El objeto raíz que contiene todos los datos del mundial."""
    name: str
    rounds: List[RoundInfo]

# ==============================================================================
# 2. MODELOS DE API (Representan los datos que se envían al frontend)
#    Estos son los modelos que el endpoint /analisis devolverá.
# ==============================================================================

class ApiGoal(BaseModel):
    """Modelo simplificado de un gol para la API."""
    player: str = Field(..., alias="name")  # Mapea 'name' del JSON a 'player' en la API
    minute: int
    team_code: Optional[str] = None # Added for timeline reconstruction

class ApiMatch(BaseModel):
    """Modelo de partido procesado y limpio para la API."""
    team_a: str
    team_b: str
    team_a_code: str
    team_b_code: str
    score_a: int
    score_b: int
    
    global_id: str # Unique ID: {year}-{id}

    goals: List[ApiGoal]
    year: str
    competition: str
    id: int
    date: str
    stage: str

class TeamStats(BaseModel):
    """Modelo para las estadísticas de un equipo."""
    wins: int
    losses: int
    draws: int
    total_matches: int
    win_percentage: float
    loss_percentage: float
    draw_percentage: float
    goals_for: int
    goals_against: int


class TeamGroupInfo(BaseModel):
    """Representa la información de un equipo en el JSON."""
    name: str
    code: str

class GroupInfo(BaseModel):
    """Representa un grupo en el JSON."""
    name: str
    teams: List[TeamGroupInfo]

class WorldCupGroupData(BaseModel):
    """El objeto raíz que contiene todos los datos de los grupos del mundial."""
    name: str

class RivalStats(BaseModel):
    """Estadísticas contra un rival específico."""
    opponent_code: str
    opponent_name: str
    matches: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    win_percentage: float

class TeamTrendStats(BaseModel):
    """Estadísticas de un equipo en un año específico."""
    year: str
    stats: TeamStats

class PlayerStats(BaseModel):
    """Estadísticas agregadas de un jugador (extraído de eventos de gol)."""
    name: str # ID natural por ahora
    team_code: str
    total_goals: int
    matches_with_goal: int # Cantidad de partidos donde anotó
    first_goal_year: str   # Año del primer gol registrado
    last_goal_year: str    # Año del último gol registrado
    years_played: List[str] # Años donde anotó (proxy de actividad)
    goals_by_match: List[Dict[str, Any]] = [] # Detalle de goles: {matchId, minute, year}
