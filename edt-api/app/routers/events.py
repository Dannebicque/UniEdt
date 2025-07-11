from fastapi import APIRouter, HTTPException
from ..lib.data_loader import load_json
from ..models import EventToPlace

router = APIRouter(prefix="/events", tags=["Events"])

@router.get("/{week_number}", response_model=list[EventToPlace])
async def get_courses_for_week(week_number: int):
    events: dict[int, list[dict]] = load_json(f"events")
    if events is None:
        raise HTTPException(status_code=404, detail="No courses for this week")
    # todo: Parcours le fichier pour calculer les évents de la semaine demandée
    # todo: FIXE = bloquant, INFO = informatif, on peut y mettre des cours
    if events is None:
        raise HTTPException(status_code=404, detail="No courses for this week")
    if isinstance(events, dict):
        week_events = events.get(str(week_number), [])
    elif isinstance(events, list):
        # Si events est une liste, on filtre les éléments ayant la bonne semaine
        week_events = [e for e in events if e.get("semaine") is not None and str(e.get("semaine")) == str(week_number)]
    else:
        week_events = []
    return week_events
