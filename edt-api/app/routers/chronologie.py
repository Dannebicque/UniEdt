from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from ..lib.paths import get_data_dir
from app.lib.convertCourses import cours_to_chronologie

from pathlib import Path
import os
import json
from typing import Optional, List

router = APIRouter(prefix="/chronologie", tags=["chronologie"])

DATA_COURS_DIR = get_data_dir() / f"cours/"


@router.get("/")
async def get_chronologie(
    professeur: Optional[str] = Query(None),
    semestre: Optional[str] = Query(None),
    matiere: Optional[str] = Query(None)
):
    cours_list = []
    if not DATA_COURS_DIR.exists():
        raise HTTPException(status_code=404, detail="Dossier data/cours introuvable")

    for file_name in os.listdir(DATA_COURS_DIR):
        if file_name.endswith(".json"):
            file_path = DATA_COURS_DIR / file_name
            with open(file_path, "r", encoding="utf-8") as f:
                ## extraire le numéro de semaine du nom de fichier
                week_number = file_name.split("_")[1].split(".")[0]
                data = json.load(f)
                if isinstance(data, list):
                    cours_items = data
                else:
                    cours_items = data.get("cours", [])
                for cours in cours_items:
                    # Filtrage selon les critères
                    if professeur and cours.get("professor") != professeur:
                        continue
                    if semestre and cours.get("semester") != semestre:
                        continue
                    if matiere and cours.get("matiere") != matiere:
                        continue
                    if cours.get("date") and cours.get("creneau"):
                        cours_list.append(cours_to_chronologie(cours, week_number))

    # Tri par date puis créneau
    cours_list.sort(key=lambda x: (x["date"], x["heure"]))
    return JSONResponse(content=cours_list)