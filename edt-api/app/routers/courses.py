from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..lib.data_loader import load_json
from ..lib.json_updater import JsonUpdater
from ..lib.paths import get_data_dir
from ..models import CourseToPlace
import json
from app.lib.assignRooms import assign_rooms_to_week


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
async def update_course(course_id: int|str, week_number: int, req: CourseUpdateRequest):
    data_path = get_data_dir() / f"cours/cours_{week_number}.json"
    updater = JsonUpdater(str(data_path))
    updated = updater.update_by_field("id", course_id, req.updates)
    if updated:
        return {"message": "Cours mis à jour", "updated": updated}
    raise HTTPException(status_code=404, detail="Cours non trouvé")

@router.put("/update/{course_id}/deplace-to-report/{week_number}")
async def update_course_to_report(course_id: str|int, week_number: int, req: CourseUpdateRequest):
    data_path = get_data_dir() / f"cours/cours_{week_number}.json"
    data_path_report = get_data_dir() / f"cours/cours_0.json"

    # Charger les cours de la semaine
    with open(data_path, "r", encoding="utf-8") as f:
        courses = json.load(f)

    # Trouver le cours à déplacer
    course_to_move = None
    for c in courses:
        if str(c.get("id")) == str(course_id):
            course_to_move = c
            break

    if not course_to_move:
        raise HTTPException(status_code=404, detail="Cours non trouvé")

    # Appliquer les updates si besoin
    course_to_move.update(req.updates)

    # Charger les cours à reporter
    try:
        with open(data_path_report, "r", encoding="utf-8") as f:
            report_courses = json.load(f)
    except FileNotFoundError:
        report_courses = []

    # Ajouter le cours à reporter
    report_courses.append(course_to_move)

    # Supprimer le cours de la semaine
    courses = [c for c in courses if str(c.get("id")) != str(course_id)]

    # Sauvegarder les fichiers
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(courses, f, ensure_ascii=False, indent=2)
    with open(data_path_report, "w", encoding="utf-8") as f:
        json.dump(report_courses, f, ensure_ascii=False, indent=2)

    return {"message": "Cours déplacé dans les cours à reporter", "course": course_to_move}

@router.put("/update/{course_id}/deplace-from-report/{week_number}")
async def restore_course_from_report(course_id: str|int, week_number: int, req: CourseUpdateRequest):
    data_path_report = get_data_dir() / "cours/cours_0.json"
    data_path_week = get_data_dir() / f"cours/cours_{week_number}.json"

    # Charger les cours à reporter
    try:
        with open(data_path_report, "r", encoding="utf-8") as f:
            report_courses = json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Aucun cours à reporter trouvé")

    # Trouver le cours à restaurer
    course_to_restore = None
    for c in report_courses:
        if str(c.get("id")) == str(course_id):
            course_to_restore = c
            break

    if not course_to_restore:
        raise HTTPException(status_code=404, detail="Cours non trouvé dans les cours à reporter")

    # Charger les cours de la semaine
    try:
        with open(data_path_week, "r", encoding="utf-8") as f:
            week_courses = json.load(f)
    except FileNotFoundError:
        week_courses = []

    # mettre à jour le cours avec le req
    course_to_restore.update(req.updates)


    # Ajouter le cours à la semaine
    week_courses.append(course_to_restore)

    # Retirer le cours de cours_0.json
    report_courses = [c for c in report_courses if str(c.get("id")) != str(course_id)]

    # Sauvegarder les fichiers
    with open(data_path_week, "w", encoding="utf-8") as f:
        json.dump(week_courses, f, ensure_ascii=False, indent=2)
    with open(data_path_report, "w", encoding="utf-8") as f:
        json.dump(report_courses, f, ensure_ascii=False, indent=2)

    return {"message": "Cours restauré dans la semaine", "course": course_to_restore}

@router.delete("/delete/{course_id}/{week_number}")
async def delete_course(course_id: str|int, week_number: int):
    data_path = get_data_dir() / f"cours/cours_{week_number}.json"
    updater = JsonUpdater(str(data_path))
    deleted = updater.init_creneau_date(course_id)
    if deleted:
        return {"message": "Cours supprimé", "deleted": deleted}
    raise HTTPException(status_code=404, detail="Cours non trouvé")

@router.post("/assign-rooms/{week_number}")
def assign_rooms(week_number: int):
    data_path = get_data_dir() / f"cours/cours_{week_number}.json"
    salles_path = get_data_dir() / f"salles.json"

    try:
        with open(data_path, "r", encoding="utf-8") as f:
            courses = json.load(f)
        with open(salles_path, "r", encoding="utf-8") as f:
            salles = json.load(f)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Erreur de lecture: {e}")

    updated_courses = assign_rooms_to_week(courses, salles)

    try:
        with open(data_path, "w", encoding="utf-8") as f:
            json.dump(updated_courses, f, ensure_ascii=False, indent=2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur d'écriture: {e}")

    return {"message": "Salles affectées et fichier mis à jour."}