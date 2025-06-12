from fastapi import APIRouter, HTTPException
from ..lib.data_loader import load_json
from ..models import CourseToPlace

router = APIRouter(prefix="/courses", tags=["Courses"])

@router.get("/{week_number}", response_model=list[CourseToPlace])
async def get_courses_for_week(week_number: int):
    courses: dict[int, list[dict]] = load_json(f"cours/cours_{week_number}")
    if courses is None:
        raise HTTPException(status_code=404, detail="No courses for this week")
    return [CourseToPlace(**c) for c in courses]
