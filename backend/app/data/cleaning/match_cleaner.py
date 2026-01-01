from typing import List
from app.core.entities import WorldCupData, ApiMatch, ApiGoal

def flatten_and_transform_matches(world_cup_data: WorldCupData, year: str, competition: str = "World Cup") -> List[ApiMatch]:
    """
    Toma los datos crudos del mundial y los transforma en una lista plana de partidos
    con el formato que espera la API y el frontend.

    Args:
        world_cup_data: El objeto Pydantic con todos los datos del torneo.
        year: El año del mundial.
        competition: El nombre de la competición (por defecto "World Cup").

    Returns:
        Una lista de objetos ApiMatch.
    """
    processed_matches: List[ApiMatch] = []

    for round_data in world_cup_data.rounds:
        for match_info in round_data.matches:
            # Combina los goles de ambos equipos en una sola lista
            all_goals = match_info.goals1 + match_info.goals2

            api_match = ApiMatch(
                team_a=match_info.team1.name,
                team_b=match_info.team2.name,
                team_a_code=match_info.team1.code,
                team_b_code=match_info.team2.code,
                score_a=match_info.score1,
                score_b=match_info.score2,
                goals=[
                    ApiGoal(name=g.name, minute=g.minute, team_code=match_info.team1.code) for g in match_info.goals1
                ] + [
                    ApiGoal(name=g.name, minute=g.minute, team_code=match_info.team2.code) for g in match_info.goals2
                ],
                year=year,
                competition=competition,
                id=match_info.num,
                global_id=f"{year}-{match_info.num}",
                date=match_info.date,
                stage=round_data.name
            )
            processed_matches.append(api_match)

    return processed_matches


def filter_matches_by_team(matches: List[ApiMatch], team_code: str) -> List[ApiMatch]:
    """
    Filtra una lista de partidos para devolver solo aquellos en los que participó un equipo específico.

    Args:
        matches: Una lista de objetos ApiMatch.
        team_code: El código del equipo por el cual filtrar.

    Returns:
        Una lista de objetos ApiMatch filtrada.
    """
    filtered_matches: List[ApiMatch] = []
    for match in matches:
        if match.team_a_code == team_code or match.team_b_code == team_code:
            filtered_matches.append(match)
    return filtered_matches