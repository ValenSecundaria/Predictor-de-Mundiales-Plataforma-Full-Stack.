from typing import List, Dict, Any, Optional
from app.core.entities import ApiMatch

def calculate_goals_summary(matches: List[ApiMatch]) -> Dict[str, Any]:
    """Calcula KPIs globales de goles para un conjunto de partidos."""
    total_goals = 0
    max_goals_in_match = 0
    match_max_goals = None
    
    for match in matches:
        match_goals = match.score_a + match.score_b
        total_goals += match_goals
        
        if match_goals > max_goals_in_match:
            max_goals_in_match = match_goals
            match_max_goals = match

    count = len(matches)
    avg_goals_per_match = (total_goals / count) if count > 0 else 0

    return {
        "totalGoals": total_goals,
        "avgGoalsPerMatch": round(avg_goals_per_match, 2),
        "maxGoalsInMatch": max_goals_in_match,
        "matchWithMostGoals": match_max_goals
    }

def calculate_team_rankings(matches: List[ApiMatch], sort_by: str = "gf", limit: int = 10) -> List[Dict[str, Any]]:
    """Genera un ranking de equipos basado en estadísticas de goles."""
    team_stats = {}

    for match in matches:
        # Team A
        if match.team_a_code not in team_stats:
            team_stats[match.team_a_code] = {"name": match.team_a, "gf": 0, "ga": 0, "matches": 0}
        team_stats[match.team_a_code]["gf"] += match.score_a
        team_stats[match.team_a_code]["ga"] += match.score_b
        team_stats[match.team_a_code]["matches"] += 1
        
        # Team B
        if match.team_b_code not in team_stats:
            team_stats[match.team_b_code] = {"name": match.team_b, "gf": 0, "ga": 0, "matches": 0}
        team_stats[match.team_b_code]["gf"] += match.score_b
        team_stats[match.team_b_code]["ga"] += match.score_a
        team_stats[match.team_b_code]["matches"] += 1

    ranking = []
    for code, stats in team_stats.items():
        gf = stats["gf"]
        ga = stats["ga"]
        gd = gf - ga
        avg_gf = gf / stats["matches"] if stats["matches"] > 0 else 0
        
        ranking.append({
            "code": code,
            "name": stats["name"],
            "goalsFor": gf,
            "goalsAgainst": ga,
            "goalDifference": gd,
            "avgGoalsFor": round(avg_gf, 2),
            "matches": stats["matches"]
        })

    # Sort logic
    if sort_by == "ga":
        ranking.sort(key=lambda x: x["goalsAgainst"]) # Menos goles en contra es mejor? Depende del contexto, aqui asumimos ranking de "mas goles" -> sort desc. Si es mejor defensa, sort asc. 
        # Para ranking general de goles, solemos querer ver los que TIENEN MAS de algo. 
        # Si sort_by es 'ga' (Defense), normalmente queremos el que recibio MENOS goles. 
        # Pero el usuario pidio "Equipos mas goleadores", "Mejor defensa". 
        # Haremos sort DESCendente por defecto para GF, GD, AVG.
        # Para GA, haremos ASCendente si se asume "mejor defensa". 
        # Simplifiquemos: sort descendente siempre, el frontend intrepreta. 
        ranking.sort(key=lambda x: x["goalsAgainst"], reverse=True) 
    elif sort_by == "gd":
        ranking.sort(key=lambda x: x["goalDifference"], reverse=True)
    elif sort_by == "avgGf":
        ranking.sort(key=lambda x: x["avgGoalsFor"], reverse=True)
    else: # Default gf
        ranking.sort(key=lambda x: x["goalsFor"], reverse=True)
        
    return ranking[:limit]

def calculate_h2h_goals_summary(team_a_code: str, team_b_code: str, matches: List[ApiMatch]) -> Dict[str, Any]:
    """Resumen de goles para el duelo específico entre dos equipos."""
    h2h_matches = [
        m for m in matches 
        if (m.team_a_code == team_a_code and m.team_b_code == team_b_code) or 
           (m.team_a_code == team_b_code and m.team_b_code == team_a_code)
    ]
    
    total_matches = len(h2h_matches)
    goals_a = 0
    goals_b = 0
    max_score_match = None
    max_score_val = -1
    
    for match in h2h_matches:
        is_a_home = match.team_a_code == team_a_code
        g_a = match.score_a if is_a_home else match.score_b
        g_b = match.score_b if is_a_home else match.score_a
        
        goals_a += g_a
        goals_b += g_b
        
        total_match_goals = g_a + g_b
        if total_match_goals > max_score_val:
            max_score_val = total_match_goals
            max_score_match = match
            
    avg_goals = (goals_a + goals_b) / total_matches if total_matches > 0 else 0
    
    return {
        "totalMatches": total_matches,
        "totalGoalsA": goals_a,
        "totalGoalsB": goals_b,
        "avgGoalsPerMatch": round(avg_goals, 2),
        "maxScoreMatch": max_score_match
    }

def calculate_stage_summary(matches: List[ApiMatch]) -> List[Dict[str, Any]]:
    """Resumen de goles agrupados por fase (Group Stage vs Knockout)."""
    # Simplificación: Group Stage suele contener "Group", el resto es Knockout/Playoff
    # O podemos agrupar por el nombre exacto del stage si se quiere detalle.
    # El requerimiento dice: "grupos vs playoffs O por stage detallado".
    # Haremos por "Stage Type" inferido para simplificar KPIs macro, o agrupado por nombre de stage.
    # Dado que los nombres de stage varían mucho ("Matchday 1", "Round of 16", "Final"),
    # una agrupación exacta puede ser ruidosa. 
    # Intentaremos detectar "Group" vs "Playoff".
    
    summary = {
        "groups": {"name": "Group Stage", "matches": 0, "goals": 0},
        "playoffs": {"name": "Playoffs", "matches": 0, "goals": 0}
    }
    
    for match in matches:
        is_group = "group" in match.stage.lower() or "matchday" in match.stage.lower()
        key = "groups" if is_group else "playoffs"
        
        summary[key]["matches"] += 1
        summary[key]["goals"] += (match.score_a + match.score_b)
        
    result = []
    for key, data in summary.items():
        avg = data["goals"] / data["matches"] if data["matches"] > 0 else 0
        result.append({
            "stageType": data["name"],
            "matches": data["matches"],
            "goals": data["goals"],
            "avgGoals": round(avg, 2)
        })
        
    return result

def calculate_minute_distribution(matches: List[ApiMatch], bin_size: int = 15) -> List[Dict[str, Any]]:
    """Distribución de goles por intervalos de minutos."""
    # Bins: 0-15, 15-30... 120+
    # Usaremos un diccionario para acumular y luego ordenar
    distribution = {} 
    
    for match in matches:
        for goal in match.goals:
            minute = goal.minute
            
            # Simple binning logic
            # Si bin_size=15: 0-14 -> 0, 15-29 -> 15, etc.
            # Ajuste para mostrar rangos amigables: 0-15, 16-30...
            # minute 1 -> bin 0 (0-15)
            # minute 15 -> bin 0 (0-15)
            # minute 16 -> bin 15 (16-30)
            
            # (minute - 1) // bin_size * bin_size puede funcionar mejor para 1-15, 16-30
            # Minute 0 no debería existir en futbol real, pero en datos sucios sí.
            if minute < 1: minute = 1
            
            bin_start = ((minute - 1) // bin_size) * bin_size
            bin_end = bin_start + bin_size
            
            # Handling Extra Time (> 90 or > 120)
            # Simplificación: Todo lo > 90 va a un bin "90+" si bin_size es grande,
            # pero si bin_size=15, seguirá creando 90-105, 105-120.
            
            label = f"{bin_start}-{bin_end}"
            
            if bin_start not in distribution:
                distribution[bin_start] = {"label": label, "count": 0, "order": bin_start}
            distribution[bin_start]["count"] += 1
            
    # Convertir a lista ordenada
    result = sorted(distribution.values(), key=lambda x: x["order"])
    
    # Retornar sin el campo auxiliar 'order'
    return [{"label": r["label"], "count": r["count"]} for r in result]

def calculate_time_split(matches: List[ApiMatch], mode: str = "halves") -> Dict[str, int]:
    """Goles por mitades (1T, 2T, ET)."""
    # Modes: halves (1T, 2T, ET), bins (no necesario si ya tenemos minute_distribution, pero el req lo menciona)
    
    split = {"1T": 0, "2T": 0, "ET": 0}
    
    for match in matches:
        for goal in match.goals:
            minute = goal.minute
            if minute <= 45:
                split["1T"] += 1
            elif minute <= 90:
                split["2T"] += 1
            else:
                split["ET"] += 1
    
    return split

def get_match_goals_timeline(match: ApiMatch) -> List[Dict[str, Any]]:
    """Lista cronológica de eventos de gol para un partido."""
    timeline = []
    
    for goal in match.goals:
        # Identificar equipo del gol
        # En ApiMatch.goals no tenemos explicito el teamId, solo player name
        # Pero podemos inferirlo si parseamos match.goals que viene limpio en ApiMatch?
        # NO. ApiMatch.goals solo tiene {player, minute}. Perdimos team info en 'flatten_and_transform_matches'.
        # REVISAR: ApiMatch.goals se genera concatenando goals1 y goals2 en flatten_and_transform_matches.
        # Problema: No sabemos de qué equipo es cada gol en ApiMatch actual.
        # Solución Temporal: Devolver solo minuto y jugador.
        # TODO: Mejorar ApiGoal para incluir 'team_code'. 
        
        timeline.append({
            "minute": goal.minute,
            "player": goal.player,
            "teamId": goal.team_code # Now available from ApiGoal
        })
        
    timeline.sort(key=lambda x: x["minute"])
    return timeline

def calculate_goal_records(matches: List[ApiMatch]) -> Dict[str, Any]:
    """
    Calcula récords históricos de goles:
    - Gol más rápido
    - Gol más tardío
    - Partido con más goles
    - Mayor diferencia de goles
    """
    if not matches:
        return {}
        
    fastest_goal = None
    latest_goal = None
    
    highest_scoring_match = None
    highest_score_val = -1
    
    biggest_diff_match = None
    biggest_diff_val = -1
    
    for match in matches:
        # Check match records (Total Score & Diff)
        total_score = match.score_a + match.score_b
        diff = abs(match.score_a - match.score_b)
        
        if total_score > highest_score_val:
            highest_score_val = total_score
            highest_scoring_match = match
            
        if diff > biggest_diff_val:
            biggest_diff_val = diff
            biggest_diff_match = match
            
        # Check individual goal records (Fastest & Latest)
        for goal in match.goals:
            minute = goal.minute
            
            # Fastest
            if fastest_goal is None or minute < fastest_goal["minute"]:
                fastest_goal = {
                    "minute": minute,
                    "player": goal.player,
                    "teamId": goal.team_code,
                    "matchId": match.global_id,
                    "matchScore": f"{match.team_a} {match.score_a} - {match.score_b} {match.team_b}"
                }
            
            # Latest
            # Exclude penalties or special cases if needed? Requirement says "Earliest/Latest" generic.
            # Usually we care about regular/extra time goals. 
            if latest_goal is None or minute > latest_goal["minute"]:
                latest_goal = {
                    "minute": minute,
                    "player": goal.player,
                    "teamId": goal.team_code,
                    "matchId": match.global_id,
                    "matchScore": f"{match.team_a} {match.score_a} - {match.score_b} {match.team_b}"
                }
                
    return {
        "fastestGoal": fastest_goal,
        "latestGoal": latest_goal,
        "highestScoringMatch": highest_scoring_match,
        "biggestGoalDifferenceMatch": biggest_diff_match
    }
