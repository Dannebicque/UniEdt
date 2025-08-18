from fastapi import APIRouter, HTTPException
from ..lib.data_loader import load_json, save_json
from ..models import UpdateTypeRequest, Event
from uuid import uuid4

router = APIRouter(prefix="/statistiques", tags=["Statistiques"])

@router.get("/{week_number}")
async def get_stats_for_week(week_number: int):
    # Compte le nombre de cours dans le fichier cours_{week_number}.json en utilisant load_json et compte le nombre d'élément placés (date != null sur le nombre de créeanxu à placer
    courses: dict[int, list[dict]] = load_json(f"cours/cours_{week_number}")

    if courses is None:
        raise HTTPException(status_code=404, detail="No courses for this week")

    total = len(courses)
    places = sum(1 for course in courses if course.get("date") and course.get("creneau"))
    return {"total": total, "placed": places}