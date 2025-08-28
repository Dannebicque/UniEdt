from collections import defaultdict
from copy import deepcopy

# Pour MMI
def assign_rooms_to_week_libre(courses_json, salles_json):
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
        # Ajouter un test pour savoir si le paramètrage est groupe prioritaire (GEA) ou classique. Si groupe prioritaire,
        # vérifier si pas un cours qui est défini (dans ce cas salles spécifiques), sinon prendre salle du groupe

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

# Pour GEA
def assign_rooms_to_week_groupe(courses_json, salles_json, groupe_map):
    salles_generiques = {
        "CM": salles_json.get("CM", []),
        "TD": salles_json.get("TD", []),
        "TP": salles_json.get("TP", [])
    }
    salle_occupee = defaultdict(lambda: defaultdict(set))
    result = deepcopy(courses_json)

    for cours in result:
        creneau = cours["creneau"]
        jour= cours["date"]
        matiere = cours.get("matiere")
        type_cours = cours["type"].upper()
        semester = cours.get("semester")
        group_index = cours.get("groupIndex")
        salle_assignee = None

        # 1a. si CM on prend le type par priorité
        if type_cours == "CM":
            salle_assignee = salles_generiques.get("CM")[0]
            cours["room"] = salle_assignee
            salle_occupee[jour][creneau].add(salle_assignee)
            continue

        # 1. Priorité : salle définie pour le cours (matière)
        salles_cours = salles_json.get("cours", {}).get(matiere, {}).get(type_cours, [])
        for salle in salles_cours:
            if salle not in salle_occupee[jour][creneau]:
                salle_assignee = salle
                break

        # 2. Sinon, salle selon le groupe (avec correspondance)
        if not salle_assignee and semester and group_index is not None:
            groupe_code = groupe_map.get(semester, {}).get(group_index)
            if groupe_code:
                salle = salles_json.get("groupes", {}).get(groupe_code, {})
                if salle not in salle_occupee[jour][creneau]:
                    salle_assignee = salle

        # 3. Sinon, salle générique du type
        if not salle_assignee:
            for salle in salles_generiques.get(type_cours, []):
                if salle not in salle_occupee[jour][creneau]:
                    salle_assignee = salle
                    break

        # 4. Si aucune salle, mettre "salle indis."
        if not salle_assignee:
            salle_assignee = "salle indis."

        cours["room"] = salle_assignee
        salle_occupee[jour][creneau].add(salle_assignee)

    return result
