from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
from ..lib.data_loader import load_json
from ..models import WeekFile
import os
import json


router = APIRouter(prefix="/config-globale", tags=["Config"])

ROOT = Path(__file__).resolve().parents[2]          # → dossier racine projet
DATA_DIR = Path(os.getenv("DATA_DIR", ROOT / "../data"))


@router.get("/")
async def get_all_config():
    configData = load_json(f"data_globale")  # { "1": { ... }, ... }
    if not configData:
        raise HTTPException(status_code=404, detail="Data Globale not found")

    return JSONResponse(content=configData)
