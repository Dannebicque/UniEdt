import json
from pathlib import Path
from app.lib.paths import get_data_dir

# Mapping des créneaux vers les heures de début
CRENEAU_HEURES = {
    1: "08:00",
    2: "09:30",
    3: "11:00",
    4: "14:00",
    5: "15:30",
    6: "17:00",
    7: "18:30"
}

def get_date_from_semaine(semaine_num, jour):
    semaine_path = get_data_dir() / f"semaines/semaine_{semaine_num}.json"
    with open(semaine_path, "r", encoding="utf-8") as f:
        semaine_data = json.load(f)
    for day in semaine_data["days"]:
        if day["day"].lower() == jour.lower():
            # Format d/m/Y
            y, m, d = day["date"].split("-")
            return f"{d}/{m}/{y}"
    return None

def get_groupe(type_cours, groupe_num):
    if type_cours == "TP":
        return f"TP {chr(64 + int(groupe_num))}"  # 1 -> A, 2 -> B, etc.
    elif type_cours == "TD":
        if groupe_num == "1":
            return "TD AB"
        elif groupe_num == "2":
            return "TD CD"
        # Ajouter d'autres règles si besoin
    return f"{type_cours} {groupe_num}"

def cours_to_chronologie(cours, semaine_num):
    jour = cours.get("date")
    creneau = int(cours.get("creneau"))
    type_cours = cours.get("type")
    groupe = str(cours.get("groupIndex"))
    date = get_date_from_semaine(semaine_num, jour)
    heure = CRENEAU_HEURES.get(creneau, "??:??")
    groupe_label = get_groupe(type_cours, groupe)
    return {
        "date": date,
        "jour": jour,
        "heure": heure,
        "professor": cours.get("professor"),
        "matiere": cours.get("matiere"),
        "type": type_cours,
        "groupe": groupe_label,
        "salle": cours.get("room"),
        "semester": cours.get("semester")
    }