from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..lib.data_loader import load_json
from ..lib.json_updater import JsonUpdater
from ..lib.paths import get_data_dir
from ..models import CourseToPlace

class CourseUpdateRequest(BaseModel):
    updates: dict

router = APIRouter(prefix="/courses", tags=["Courses"])

@router.get("/{week_number}", response_model=list[CourseToPlace])
async def get_courses_for_week(week_number: int):
    courses: dict[int, list[dict]] = load_json(f"cours/cours_{week_number}")

    if courses is None:
        raise HTTPException(status_code=404, detail="No courses for this week")
    return [CourseToPlace(**c) for c in courses]

@router.put("/update/{course_id}/{week_number}")
async def update_course(course_id: int, week_number: int, req: CourseUpdateRequest):
    data_path = get_data_dir() / f"cours/cours_{week_number}.json"
    updater = JsonUpdater(str(data_path))
    updated = updater.update_by_field("id", course_id, req.updates)
    if updated:
        return {"message": "Cours mis à jour", "updated": updated}
    raise HTTPException(status_code=404, detail="Cours non trouvé")

@router.delete("/delete/{course_id}/{week_number}")
async def delete_course(course_id: int, week_number: int):
    data_path = get_data_dir() / f"cours/cours_{week_number}.json"
    updater = JsonUpdater(str(data_path))
    deleted = updater.init_creneau_date(course_id)
    if deleted:
        return {"message": "Cours supprimé", "deleted": deleted}
    raise HTTPException(status_code=404, detail="Cours non trouvé")