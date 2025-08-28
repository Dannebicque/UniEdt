from fastapi import APIRouter
import json
from ..lib.paths import get_data_dir

router = APIRouter(prefix="/synthese", tags=["Synthese"])

@router.get("/matiere-groupes")
async def synthese_matiere_groupes():
    data_dir = get_data_dir() / "cours"
    synthese = {}

    for file in data_dir.glob("cours_*.json"):
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
            cours_list = data if isinstance(data, list) else data.get("cours", [])
            for cours in cours_list:
                matiere = cours.get("matiere")
                groupe = cours.get("groupIndex")
                type = cours.get("type")

                if not matiere or not groupe or not type:
                    continue
                if matiere not in synthese:
                    synthese[matiere] = {}
                if type not in synthese[matiere]:
                    synthese[matiere][type] = {}
                if groupe not in synthese[matiere][type]:
                    synthese[matiere][type][groupe] = {"places": 0, "non_places": 0}

                if cours.get("date"):
                    synthese[matiere][type][groupe]["places"] += 1
                else:
                    synthese[matiere][type][groupe]["non_places"] += 1

    return synthese