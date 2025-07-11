import os
import json
import requests

# --------------------
# 1. SYNTHÈSE ÉTUDIANTS
# --------------------

SYNTH_GROUPES = [
    ("S1", "BUT1", list("ABCDEFGH")),
    ("S3", "DEV-FI", list("ABCD")),
    ("S3", "DEV-FC", ["E", "F"]),
    ("S3", "CREACOM", ["G", "H"]),
    ("S5", "DEV-FI", list("ABCD")),
    ("S5", "DEV-FC", ["E", "F"]),
    ("S5", "CREACOM", ["G", "H"]),
]

TD_MAP = {
    "AB": ["A", "B"], "CD": ["C", "D"], "EF": ["E", "F"], "GH": ["G", "H"]
}

def get_groupes(semestre, parcours, type_cours, groupes_str):
    """Retourne la liste des groupes impactés selon la règle de l'entrée"""
    if type_cours == "CM" and groupes_str == "ALL":
        for s, p, groupes in SYNTH_GROUPES:
            if s == semestre and p == parcours:
                return groupes
    elif type_cours == "TD":
        groupes = []
        if groupes_str:
            for part in groupes_str.split(","):
                part = part.strip()
                groupes.extend(TD_MAP.get(part, [part]))
        return groupes
    elif type_cours == "TP":
        if groupes_str:
            return [g.strip() for g in groupes_str.split(",")]
    return []

def synthese_etudiants_data(programmation_path):
    """Retourne un dict {(semestre, parcours, groupe): [nb cours par semaine 1-23]}"""
    synthese = {}
    for semestre, parcours, groupes in SYNTH_GROUPES:
        for groupe in groupes:
            synthese[(semestre, parcours, groupe)] = [0] * 23  # S1 à S23

    with open(programmation_path, encoding="utf8") as f:
        data = json.load(f)

    for entry in data:
        semestre = entry.get("semestre")
        parcours = entry.get("parcours")
        type_cours = entry.get("type")
        groupes_str = entry.get("groupes")
        for i in range(1, 24):  # S1 à S23 inclus
            key = f"Sem{i}"
            nb = entry.get(key)
            if nb is not None:
                groupes = get_groupes(semestre, parcours, type_cours, groupes_str)
                for groupe in groupes:
                    if (semestre, parcours, groupe) in synthese:
                        synthese[(semestre, parcours, groupe)][i-1] += nb
    return synthese

# --------------------
# 2. SYNTHÈSE PROFS
# --------------------

def get_profs_from_contraintes(contraintes_path):
    with open(contraintes_path, encoding="utf8") as f:
        data = json.load(f)
    return sorted(data.keys())

def synthese_profs_data(programmation_path, contraintes_path):
    profs = get_profs_from_contraintes(contraintes_path)
    synthese = {prof: [0] * 23 for prof in profs}

    with open(programmation_path, encoding="utf8") as f:
        data = json.load(f)
    for entry in data:
        code_prof = entry.get("code_prof")
        if code_prof in synthese:
            for i in range(1, 24):  # S1 à S23
                key = f"Sem{i}"
                nb = entry.get(key)
                if nb is not None:
                    synthese[code_prof][i-1] += nb
    return synthese, profs

def previ_profs_data_from_url(export_url, profs):
    previ = {prof: 0 for prof in profs}
    response = requests.get(export_url)
    response.raise_for_status()
    data = response.json()
    for block in data:
        for prof_data in block.get("profs", []):
            code_prof = prof_data.get("code", "")
            if code_prof in previ:
                previ[code_prof] += int(prof_data.get("cm", 0)) + int(prof_data.get("td", 0)) + int(prof_data.get("tp", 0))
    return previ

def dispo_profs_par_semaine(contraintes_path, profs):
    """
    Retourne un dict { prof: [dispo_s1, ..., dispo_s23] }
    - Si le prof a des contraintes "disponible" : dispo = somme des créneaux pour les semaines concernées, 0 ailleurs.
    - Sinon : dispo = 25 - créneaux "indisponible" pour chaque semaine concernée, 25 ailleurs.
    """
    import json
    with open(contraintes_path, encoding="utf8") as f:
        data = json.load(f)
    result = {}
    for prof in profs:
        prof_data = data.get(prof, {})
        contraintes = prof_data.get("availability", [])
        # Est-ce qu'il y a AU MOINS une contrainte "disponible" ?
        has_dispo = any(c.get("status") == "disponible" for c in contraintes)
        dispo_weeks = [25] * 23  # valeur par défaut
        if has_dispo:
            # Par défaut tout à 0, puis on remplit les semaines concernées
            dispo_weeks = [0] * 23
            for c in contraintes:
                if c.get("status") != "disponible":
                    continue
                # Prise en compte du format int/str
                week_field = c.get("week", 99)
                if week_field == 99 or week_field == "99":
                    weeks = list(range(1, 24))
                else:
                    weeks = [int(week_field)]
                nb_creneaux = len(c.get("creneaux", []))
                for w in weeks:
                    if not (1 <= w <= 23):
                        continue
                    dispo_weeks[w-1] += nb_creneaux
        else:
            # Mode "indisponible" ou aucune contrainte
            for c in contraintes:
                if c.get("status") != "indisponible":
                    continue
                week_field = c.get("week", 99)
                if week_field == 99 or week_field == "99":
                    weeks = list(range(1, 24))
                else:
                    weeks = [int(week_field)]
                day_field = c.get("day", 99)
                if day_field == 99 or day_field == "99":
                    days = list(range(1, 6))
                else:
                    days = [day_field]
                nb_creneaux = len(c.get("creneaux", []))
                nb_creneaux_total = nb_creneaux * len(days)
                for w in weeks:
                    if not (1 <= w <= 23):
                        continue
                    dispo_weeks[w-1] -= nb_creneaux_total
            # On évite les dispos négatives
            dispo_weeks = [max(0, d) for d in dispo_weeks]
        result[prof] = dispo_weeks
    return result
