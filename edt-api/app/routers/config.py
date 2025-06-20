from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
from ..lib.data_loader import load_json
from ..models import WeekFile
import os
import json
from ..lib.paths import get_data_dir


router = APIRouter(prefix="/config-globale", tags=["Config"])


DATA_DIR = get_data_dir()

@router.get("/")
async def get_all_config():
    configData = load_json(f"data_globale")  # { "1": { ... }, ... }
    if not configData:
        raise HTTPException(status_code=404, detail="Data Globale not found")

    return JSONResponse(content=configData)
