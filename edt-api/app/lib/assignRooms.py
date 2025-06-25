from collections import defaultdict
from copy import deepcopy

def assign_rooms_to_week(courses_json, salles_json):
    salles_specifiques = salles_json.copy()
    salles_generiques = {
        "CM": salles_json.get("CM", []),
        "TD": salles_json.get("TD", []),
        "TP": salles_json.get("TP", [])
    }

    salle_occupee = defaultdict(set)
    last_room_for_group = {}

    result = deepcopy(courses_json)
    for cours in result:
        creneau = cours["creneau"]
        groupe = cours.get("groupe")
        matiere = cours.get("code")  # ou "matiere" selon ton modèle
        type_cours = cours["type"].upper()  # "CM", "TD", "TP"
        salle_assignee = None

        # 1. Salle spécifique (groupe, matière, type)
        if groupe and matiere:
            spec = salles_specifiques.get(groupe, {}).get(matiere, {}).get(type_cours.lower())
            if spec and spec not in salle_occupee[creneau]:
                salle_assignee = spec

        # 2. Salle précédente du groupe (si possible)
        if not salle_assignee and groupe and last_room_for_group.get(groupe):
            prev_salle = last_room_for_group[groupe]
            if prev_salle in salles_generiques.get(type_cours, []) and prev_salle not in salle_occupee[creneau]:
                salle_assignee = prev_salle

        # 3. Salle générique du bon type
        if not salle_assignee:
            for salle in salles_generiques.get(type_cours, []):
                if salle not in salle_occupee[creneau]:
                    salle_assignee = salle
                    break

        # Affectation et suivi
        if salle_assignee:
            cours["room"] = salle_assignee
            salle_occupee[creneau].add(salle_assignee)
            if groupe:
                last_room_for_group[groupe] = salle_assignee
        else:
            cours["room"] = None

    return result