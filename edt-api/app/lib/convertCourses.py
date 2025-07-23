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

def get_groupe(type_cours, groupe_num, semestre, tabGroupes=None):
    if tabGroupes is None:
        return f"{type_cours} {groupe_num}"

    # tester si on trouve semestre, type_cours et groupe_num dans tabGroupes
    if semestre in tabGroupes:
        groupes = tabGroupes[semestre]
        print(f"Recherche de {type_cours} dans {groupes}")
        if type_cours in groupes:
            print(f"Recherche de {groupe_num} dans {groupes[type_cours]}")
            groupe_info = groupes[type_cours].get(int(groupe_num))
            if groupe_info:
                print(f"Groupe trouvé: {groupe_info}")
                return f"{type_cours} {groupe_info}"

    return f"{type_cours} {groupe_num}"

def cours_to_chronologie(cours, semaine_num, tabGroupes=None):
    jour = cours.get("date")
    creneau = int(cours.get("creneau"))
    type_cours = cours.get("type")
    groupe = str(cours.get("groupIndex"))
    date = get_date_from_semaine(semaine_num, jour)
    heure = CRENEAU_HEURES.get(creneau, "??:??")
    semestre = cours.get("semester")
    groupe_label = get_groupe(type_cours, groupe, semestre, tabGroupes)
    return {
        "date": date,
        "jour": jour,
        "heure": heure,
        "professor": cours.get("professor"),
        "matiere": cours.get("matiere"),
        "type": type_cours,
        "groupe": groupe_label,
        "groupeIndex": groupe,
        "salle": cours.get("room"),
        "semester": semestre
    }