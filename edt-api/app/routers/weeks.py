from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
from ..lib.data_loader import load_json
from ..models import WeekFile
import os
import json


router = APIRouter(prefix="/weeks", tags=["Weeks"])

ROOT = Path(__file__).resolve().parents[2]          # → dossier racine projet
DATA_DIR = Path(os.getenv("DATA_DIR", ROOT / "../data-GEA"))


@router.get("/liste")
async def get_all_weeks():
    folder = DATA_DIR / "semaines/"
    result = []
    for filename in os.listdir(folder):
        if filename.endswith(".json"):
            week_number = int(filename.split("_")[1].split(".")[0])
            with open(os.path.join(folder, filename), encoding="utf-8") as f:
                data = json.load(f)
                days = data.get("days", [])
                if days and len(days) >= 5:
                    result.append({
                        "value": week_number,
                        "label": f"Semaine {week_number} ({days[0]['date']} au {days[4]['date']})"
                    })
    # Tri par numéro de semaine
    result.sort(key=lambda x: x["value"])
    return JSONResponse(content=result)

@router.get("/complet")
async def get_all_weeks_full():
    folder = DATA_DIR / "semaines/"
    result = []
    for filename in os.listdir(folder):
        if filename.endswith(".json"):
            week_number = int(filename.split("_")[1].split(".")[0])
            with open(os.path.join(folder, filename), encoding="utf-8") as f:
                data = json.load(f)
                result.append({
                    "value": week_number,
                    "label": f"Semaine {week_number} ({data['days'][0]['date']} au {data['days'][-1]['date']})",
                    "data-GEA": data
                })
    # Tri par numéro de semaine
    result.sort(key=lambda x: x["value"])
    return JSONResponse(content=result)



@router.get("/{week_number}", response_model=WeekFile)
async def get_week(week_number: int):
    week = load_json(f"semaines/semaine_{week_number}")   # { "1": { ... }, ... }
    if not week:
        raise HTTPException(status_code=404, detail="Week not found")
    return WeekFile(number=week_number, **week)

@router.put("/{week_number}/update", response_model=WeekFile)
async def update_week(week_number: int, updated_data: dict):
    file_path = DATA_DIR / f"semaines/semaine_{week_number}.json"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Week not found")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(updated_data, f, ensure_ascii=False, indent=2)
    return WeekFile(number=week_number, **updated_data)