# programmation/utils/export_semaines.py

import json
import os
from datetime import datetime
from collections import defaultdict
from django.conf import settings

from .mappings import SEMESTRE_MAPPING, GROUPE_MAPPING, TYPE_TO_GROUPCOUNT, COLOR_MAPPING

PROGRAMMATION = os.path.join(settings.DATA_PATH, "programmation.json")
CONTRAINTES = os.path.join(settings.DATA_PATH, "contraintes.json")

def load_enseignants_type():
    with open(CONTRAINTES, encoding="utf-8") as f:
        data = json.load(f)
    return {code.upper(): d["type"].lower() for code, d in data.items()}

def semestre_format(semestre, parcours):
    return SEMESTRE_MAPPING.get((semestre, parcours), f"{semestre}-{parcours}")

def color_for_parcours(semestre, parcours):
    sem_code = semestre_format(semestre, parcours)
    if sem_code in COLOR_MAPPING:
        return COLOR_MAPPING[sem_code]
    if parcours in COLOR_MAPPING:
        return COLOR_MAPPING[parcours]
    return "#000000"

def groupIndex_from_str(groupes_str):
    if not groupes_str:
        return []
    return [GROUPE_MAPPING.get(g, 0) for g in groupes_str.replace(" ", "").split(",") if g]

def groupCount_for_type(type_cours, semestre):
    return TYPE_TO_GROUPCOUNT[type_cours](semestre)

def is_vacataire(type_prof):
    return type_prof == "vacataire"

def get_id_for_week(week, id_counters):
    now = datetime.now()
    base = now.strftime("%Y%m%d%H%M%S")
    zzz = id_counters[week]
    id_str = f"{base}{zzz:03d}"
    id_counters[week] = (zzz + 1) % 1000
    return id_str

def export_cours_for_semaines(semaines, overwrite_files=False):
    with open(PROGRAMMATION, encoding="utf-8") as f:
        programmation = json.load(f)
    enseignants_type = load_enseignants_type()
    id_counters = defaultdict(int)
    result = {}
    for sem in semaines:
        cours_list = []
        file_path = os.path.join(settings.DATA_PATH,"semaines", f"cours_{sem:02d}.json")
        if os.path.exists(file_path) and not overwrite_files:
            result[sem] = "exists"
            continue
        for ligne in programmation:
            key = f"Sem{sem}"
            nb = ligne.get(key)
            if nb is None or nb == 0:
                continue
            sem_code = semestre_format(ligne["semestre"], ligne["parcours"])
            color = color_for_parcours(ligne["semestre"], ligne["parcours"])
            groupes = ligne.get("groupes") or "ALL"
            groupIndex = groupIndex_from_str(groupes)
            groupCount = groupCount_for_type(ligne["type"], sem_code)
            prof_type = enseignants_type.get(ligne["code_prof"].upper(), "permanent")
            vacataire = is_vacataire(prof_type)
            for _ in range(nb):
                for g_idx in groupIndex or [1]:
                    id_value = get_id_for_week(sem, id_counters)  # id unique pour chaque cours/groupe
                    cours = {
                        "id": id_value,
                        "matiere": ligne["code_matiere"],
                        "professor": ligne["code_prof"],
                        "type": ligne["type"],
                        "semester": sem_code,
                        "groupIndex": g_idx,
                        "groupCount": groupCount,
                        "date": None,
                        "creneau": None,
                        "room": None,
                        "color": color,
                        "isVacataire": vacataire,
                        "fixed": 0
                    }
                    cours_list.append(cours)
        with open(file_path, "w", encoding="utf-8") as out:
            json.dump(cours_list, out, indent=2, ensure_ascii=False)
        result[sem] = len(cours_list)
    return result
