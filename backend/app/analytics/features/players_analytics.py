from typing import List, Dict, Any, Optional
from app.core.entities import ApiMatch, PlayerStats

def extract_and_aggregate_players(matches: List[ApiMatch]) -> List[PlayerStats]:
    """
    Extrae y agrega estadísticas de jugadores basándose ÚNICAMENTE en eventos de gol.
    Nota: Esto solo detecta jugadores QUE HAN ANOTADO GOLES. 
    Jugadores sin goles no aparecerán porque el dataset original no tiene lineups completas.
    """
    players_dict: Dict[str, Dict[str, Any]] = {}
    
    # Key = "PlayerName_TeamCode" (para diferenciar homónimos en distintos equipos si fuera necesario, 
    # aunque en selecciones históricas nombre suele bastar. Usaremos Name+Team para seguridad)
    
    for match in matches:
        year = match.year
        
        for goal in match.goals:
            # Normalizar nombre? Por ahora raw.
            p_name = goal.player.strip()
            # team_code is now available in ApiGoal
            p_team = goal.team_code if goal.team_code else "UNKNOWN"
            
            # Limpieza básica de caracteres raros si hiciera falta (e.g. "' " prefix in JSON)
            if p_name.startswith("'"): p_name = p_name.replace("'", "").strip()
            
            key = f"{p_name}_{p_team}"
            
            if key not in players_dict:
                players_dict[key] = {
                    "name": p_name,
                    "team_code": p_team,
                    "total_goals": 0,
                    "matches_with_goal_ids": set(),
                    "goals_details": [],
                    "years": set()
                }
            
            entry = players_dict[key]
            entry["total_goals"] += 1
            entry["matches_with_goal_ids"].add(match.global_id)
            entry["years"].add(year)
            
            entry["goals_details"].append({
                "matchId": match.global_id,
                "minute": goal.minute,
                "year": year,
                "opponent": match.team_b if match.team_a_code == p_team else match.team_a,
                "stage": match.stage
            })

    # Convert to List[PlayerStats]
    result = []
    for key, data in players_dict.items():
        sorted_years = sorted(list(data["years"]))
        
        stats = PlayerStats(
            name=data["name"],
            team_code=data["team_code"],
            total_goals=data["total_goals"],
            matches_with_goal=len(data["matches_with_goal_ids"]),
            first_goal_year=sorted_years[0] if sorted_years else "",
            last_goal_year=sorted_years[-1] if sorted_years else "",
            years_played=sorted_years,
            goals_by_match=data["goals_details"]
        )
        result.append(stats)
        
    return result

def filter_players(
    players: List[PlayerStats], 
    team_id: Optional[str] = None, 
    min_goals: int = 0,
    search: Optional[str] = None
) -> List[PlayerStats]:
    """Filtra la lista de jugadores."""
    filtered = players
    
    if team_id:
        filtered = [p for p in filtered if p.team_code == team_id]
        
    if min_goals > 0:
        filtered = [p for p in filtered if p.total_goals >= min_goals]
        
    if search:
        s = search.lower()
        filtered = [p for p in filtered if s in p.name.lower()]
        
    return filtered
