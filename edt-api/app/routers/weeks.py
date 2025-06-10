from fastapi import APIRouter, HTTPException
from ..lib.data_loader import load_json
from ..models import WeekFile

router = APIRouter(prefix="/weeks", tags=["Weeks"])

@router.get("/{week_number}", response_model=WeekFile)
async def get_week(week_number: int):
    week = load_json(f"semaines/semaine_{week_number}")   # { "1": { ... }, ... }
    if not week:
        raise HTTPException(status_code=404, detail="Week not found")
    return WeekFile(number=week_number, **week)