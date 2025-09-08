from fastapi import APIRouter
import json
from ..lib.paths import get_data_dir
import math

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

@router.get("/previsionnel")
async def synthese_previsionnel():
    data_dir = get_data_dir() / "cours"
    synthese = {}

    for file in data_dir.glob("cours_*.json"):
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
            cours_list = data if isinstance(data, list) else data.get("cours", [])
            for cours in cours_list:
                matiere = cours.get("matiere")
                enseignant = cours.get("professor")

                if not matiere or not enseignant:
                    continue
                if matiere not in synthese:
                    synthese[matiere] = {}
                if enseignant not in synthese[matiere]:
                    synthese[matiere][enseignant] = {}
                    synthese[matiere][enseignant]['edt'] = {"CM": 0, "TD": 0, "TP": 0}
                    synthese[matiere][enseignant]['previ'] = {"CM": 0, "TD": 0, "TP": 0, "nbCM": 0, "nbTD": 0, "nbTP": 0, "totCM": 0, "totTD": 0, "totTP": 0}

                if cours.get("date"): #on regarde si le cours est placé
                    synthese[matiere][enseignant]['edt'][cours.get("type")]+= float(cours.get("duree") or 1.5)

    #on récupère le fichier previ.json et on construit un tableau identique à synthèse pour comparaison, on a en plus le nombre de groupe
    with open(get_data_dir() / "previ.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        for enseignant in data[0]['professeurs']:
            for matiere in data[0]['professeurs'][enseignant]['matieres']:
                if matiere not in synthese:
                    synthese[matiere] = {}

                if enseignant not in synthese[matiere]:
                    synthese[matiere][enseignant] = {}
                    synthese[matiere][enseignant]["previ"] = {"CM": 0, "TD": 0, "TP": 0, "nbCM": 0, "nbTD": 0, "nbTP": 0, "totCM": 0, "totTD": 0, "totTP": 0}
                    synthese[matiere][enseignant]["edt"] = {"CM": 0, "TD": 0, "TP": 0}

                donnees = data[0]["professeurs"][enseignant]["matieres"][matiere]
                synthese[matiere][enseignant]["previ"]["CM"] += safe_float(donnees["heures"]["CM"])
                synthese[matiere][enseignant]["previ"]["TD"] += safe_float(donnees["heures"]["TD"])
                synthese[matiere][enseignant]["previ"]["TP"] += safe_float(donnees["heures"]["TP"])
                synthese[matiere][enseignant]["previ"]["nbCM"] += safe_float(donnees["groupe"]["CM"])
                synthese[matiere][enseignant]["previ"]["nbTD"] += safe_float(donnees["groupe"]["TD"])
                synthese[matiere][enseignant]["previ"]["nbTP"] += safe_float(donnees["groupe"]["TP"])
                synthese[matiere][enseignant]["previ"]["totCM"] += safe_float(donnees["groupe"]["CM"]) * safe_float(donnees["heures"]["CM"])
                synthese[matiere][enseignant]["previ"]["totTD"] += safe_float(donnees["groupe"]["TD"]) * safe_float(donnees["heures"]["TD"])
                synthese[matiere][enseignant]["previ"]["totTP"] += safe_float(donnees["groupe"]["TP"]) * safe_float(donnees["heures"]["TP"])
    print(synthese)
    return synthese

def safe_float(val):
    if val is None:
        return 0.0
    if isinstance(val, str):
        val = val.replace(",", ".")

    if val == "":
        return 0.0

    if math.isnan(val) or math.isinf(val):
        return 0.0

    try:
        return float(val)
    except (TypeError, ValueError):
        return 0.0