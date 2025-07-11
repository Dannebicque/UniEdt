from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
from ..lib.data_loader import load_json
from ..models import WeekFile
import os
import json


router = APIRouter(prefix="/semesters", tags=["Semesters"])

ROOT = Path(__file__).resolve().parents[2]          # → dossier racine projet
DATA_DIR = Path(os.getenv("DATA_DIR", ROOT / "../data-GEA"))


@router.get("/liste")
async def get_all_weeks():
    configData = load_json(f"data_globale")  # { "1": { ... }, ... }
    if not configData or not configData.get("semesters"):
        raise HTTPException(status_code=404, detail="Data Globale not found")

    return JSONResponse(content=configData.get("semesters"))

@router.get("/{week_number}", response_model=WeekFile)
async def get_week(week_number: int):
    week = load_json(f"semaines/semaine_{week_number}")   # { "1": { ... }, ... }
    if not week:
        raise HTTPException(status_code=404, detail="Week not found")
    return WeekFile(number=week_number, **week)