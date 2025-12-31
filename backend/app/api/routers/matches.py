from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.core.entities import ApiMatch

router = APIRouter(prefix="/api/v1/matches", tags=["matches"])

# Placeholder storage, populated at app startup
MATCHES_STORE: List[ApiMatch] = []

@router.get("", response_model=Dict[str, Any])
def get_matches(
    worldcupId: Optional[str] = Query(None, description="Filter by World Cup Year (e.g., '1990')"),
    stage: Optional[str] = Query(None, description="Filter by stage/round (e.g., 'Group A', 'Final')"),
    teamA: Optional[str] = Query(None, description="Filter by Team A code or name"),
    teamB: Optional[str] = Query(None, description="Filter by Team B code or name"),
    dateFrom: Optional[str] = Query(None, description="Filter matches after/on this date (YYYY-MM-DD)"),
    dateTo: Optional[str] = Query(None, description="Filter matches before/on this date (YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="Page number"),
    pageSize: int = Query(20, ge=1, le=100, description="Items per page")
):
    """
    Search and filter matches with pagination.
    """
    if not MATCHES_STORE:
        raise HTTPException(status_code=503, detail="Data not loaded yet")

    filtered_matches = MATCHES_STORE

    # --- Filters ---
    if worldcupId:
        filtered_matches = [m for m in filtered_matches if m.year == worldcupId]
    
    if stage:
        # Case insensitive partial match
        filtered_matches = [m for m in filtered_matches if stage.lower() in m.stage.lower()]

    if teamA:
        tA = teamA.lower()
        filtered_matches = [m for m in filtered_matches if tA in m.team_a.lower() or tA in m.team_a_code.lower()]
    
    if teamB:
        tB = teamB.lower()
        filtered_matches = [m for m in filtered_matches if tB in m.team_b.lower() or tB in m.team_b_code.lower()]

    if dateFrom or dateTo:
        try:
            # Helper to parse dates strictly if needed, but simple string comparison works for YYYY-MM-DD
            # However, the source format might vary. Assuming standard ISO or consistent format from cleaner.
            # Based on inspection, dates are strings. Let's try flexible parsing or string comparison if format matches.
            # Ideally data should be normalized to YYYY-MM-DD.
            pass
        except ValueError:
            pass # Ignore invalid dates for now or raise error
        
        if dateFrom:
             filtered_matches = [m for m in filtered_matches if m.date >= dateFrom]
        if dateTo:
             filtered_matches = [m for m in filtered_matches if m.date <= dateTo]


    # --- Sorting ---
    # Default sort by date desc, then id desc
    filtered_matches.sort(key=lambda x: (x.date, x.id), reverse=True)

    # --- Pagination ---
    total_items = len(filtered_matches)
    total_pages = (total_items + pageSize - 1) // pageSize
    
    start_idx = (page - 1) * pageSize
    end_idx = start_idx + pageSize
    
    paginated_data = filtered_matches[start_idx:end_idx]

    return {
        "data": paginated_data,
        "meta": {
            "total": total_items,
            "page": page,
            "pageSize": pageSize,
            "totalPages": total_pages
        }
    }

@router.get("/{year}/{match_id}", response_model=ApiMatch)
def get_match_by_id(year: str, match_id: int):
    """
    Get a specific match by its Year and ID (Match Number).
    """
    if not MATCHES_STORE:
        raise HTTPException(status_code=503, detail="Data not loaded yet")

    match = next((m for m in MATCHES_STORE if m.year == year and m.id == match_id), None)
    
    if not match:
        raise HTTPException(status_code=404, detail=f"Match {match_id} in {year} not found")
        
    return match
