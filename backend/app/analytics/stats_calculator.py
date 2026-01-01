from typing import List, Dict
from app.core.entities import ApiMatch, TeamStats

def calculate_team_stats(matches: List[ApiMatch], team_code: str) -> TeamStats:
    """
    Calcula las estadísticas de victorias, derrotas y empates para un equipo específico.

    Args:
        matches: La lista completa de partidos.
        team_code: El código del equipo para el cual calcular las estadísticas.

    Returns:
        Un objeto TeamStats con las estadísticas calculadas.
    """
    wins = 0
    losses = 0
    draws = 0
    goals_for = 0
    goals_against = 0
    
    team_matches = [m for m in matches if m.team_a_code == team_code or m.team_b_code == team_code]
    
    if not team_matches:
        return TeamStats(wins=0, losses=0, draws=0, total_matches=0, win_percentage=0, loss_percentage=0, draw_percentage=0, goals_for=0, goals_against=0)

    for match in team_matches:
        is_team_a = match.team_a_code == team_code
        
        if match.score_a == match.score_b:
            draws += 1
        elif (is_team_a and match.score_a > match.score_b) or (not is_team_a and match.score_b > match.score_a):
            wins += 1
        else:
            losses += 1
            
        if is_team_a:
            goals_for += match.score_a
            goals_against += match.score_b
        else:
            goals_for += match.score_b
            goals_against += match.score_a
            
    total_matches = len(team_matches)
    win_percentage = (wins / total_matches) * 100 if total_matches > 0 else 0
    loss_percentage = (losses / total_matches) * 100 if total_matches > 0 else 0
    draw_percentage = (draws / total_matches) * 100 if total_matches > 0 else 0

    return TeamStats(
        wins=wins,
        losses=losses,
        draws=draws,
        total_matches=total_matches,
        win_percentage=win_percentage,
        loss_percentage=loss_percentage,
        draw_percentage=draw_percentage,
        goals_for=goals_for,
        goals_against=goals_against
    )

def calculate_team_trends(matches: List[ApiMatch], team_code: str) -> List[Dict]:
    """Calcula estadísticas desglosadas por año para un equipo."""
    team_matches = [m for m in matches if m.team_a_code == team_code or m.team_b_code == team_code]
    
    # Agrupar por año
    years = sorted(list(set(m.year for m in team_matches)))
    trends = []
    
    for year in years:
        year_matches = [m for m in team_matches if m.year == year]
        # Reutilizamos la lógica de team_stats para el subconjunto de partidos
        year_stats = calculate_team_stats(year_matches, team_code)
        trends.append({
            "year": year,
            "stats": year_stats
        })
    
    return trends

def calculate_top_rivals(matches: List[ApiMatch], team_code: str) -> List[Dict]:
    """Calcula estadísticas contra todos los rivales históricos."""
    team_matches = [m for m in matches if m.team_a_code == team_code or m.team_b_code == team_code]
    
    rivals_data = {} # opponent_code -> {matches, wins, draws, losses, goals_for, goals_against, name}
    
    for match in team_matches:
        is_team_a = match.team_a_code == team_code
        opponent_code = match.team_b_code if is_team_a else match.team_a_code
        opponent_name = match.team_b if is_team_a else match.team_a
        
        if opponent_code not in rivals_data:
            rivals_data[opponent_code] = {
                "matches": 0, "wins": 0, "draws": 0, "losses": 0,
                "goals_for": 0, "goals_against": 0, "name": opponent_name
            }
            
        data = rivals_data[opponent_code]
        data["matches"] += 1
        
        if match.score_a == match.score_b:
            data["draws"] += 1
        elif (is_team_a and match.score_a > match.score_b) or (not is_team_a and match.score_b > match.score_a):
            data["wins"] += 1
        else:
            data["losses"] += 1
            
        if is_team_a:
            data["goals_for"] += match.score_a
            data["goals_against"] += match.score_b
        else:
            data["goals_for"] += match.score_b
            data["goals_against"] += match.score_a

    # Convertir a lista de objetos
    results = []
    for code, data in rivals_data.items():
        total = data["matches"]
        results.append({
            "opponent_code": code,
            "opponent_name": data["name"],
            "matches": total,
            "wins": data["wins"],
            "draws": data["draws"],
            "losses": data["losses"],
            "goals_for": data["goals_for"],
            "goals_against": data["goals_against"],
            "win_percentage": (data["wins"] / total) * 100 if total > 0 else 0
        })
        
    # Ordenar por cantidad de partidos (o victorias) descendente
    results.sort(key=lambda x: x["matches"], reverse=True)
    return results