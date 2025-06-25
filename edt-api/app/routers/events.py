from fastapi import APIRouter, HTTPException
from ..lib.data_loader import load_json
from ..models import CourseToPlace

router = APIRouter(prefix="/events", tags=["Events"])

@router.get("/{week_number}", response_model=list[CourseToPlace])
async def get_courses_for_week(week_number: int):
    events: dict[int, list[dict]] = load_json(f"events")
    if events is None:
        raise HTTPException(status_code=404, detail="No courses for this week")
    # todo: Parocur le fichier pour calculer les évents de la seamaine demandée
    # todo: FIXE = bloquant, INFO = informatif, on peut y mettre des cours
    return []
