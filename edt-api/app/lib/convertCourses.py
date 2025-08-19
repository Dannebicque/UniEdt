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
        if type_cours in groupes:
            groupe_info = groupes[type_cours].get(int(groupe_num))
            if groupe_info:
                return f"{type_cours} {groupe_info}"

    return f"{type_cours} {groupe_num}"

def cours_to_chronologie(cours, semaine_num, tabGroupes=None, tabProfesseurs=None):
    jour = cours.get("date")
    creneau = int(cours.get("creneau"))
    type_cours = cours.get("type")
    groupe = str(cours.get("groupIndex"))
    date = get_date_from_semaine(semaine_num, jour)

    heure = cours.get("heureDebut")
    if heure:
        heure = heure.replace("h", ":")
    else:
        heure = CRENEAU_HEURES.get(creneau, "??:??")

    semestre = cours.get("semester")
    groupe_label = get_groupe(type_cours, groupe, semestre, tabGroupes)

    # Calcule l'heure de fin du cours. Par défaut c'est 1h30, mais si durée n'est pas null, alors prendre cette valeur. La durée est définie en flotant dans ce cas
    heure_fin = heure
    if cours.get("duree"):
# La durée est exprimée en heures (float), ex: 1.5 = 1h30
        duree = float(cours.get("duree"))
        heures = int(duree)
        minutes = int((duree - heures) * 60)
        heure_fin = str(int(heure_fin.split(":")[0]) + heures) + ":" + str(int(heure_fin.split(":")[1]) + minutes).zfill(2)
    else:
        heure_fin = str(int(heure_fin.split(":")[0]) + 1) + ":" + str(int(heure_fin.split(":")[1]) + 30).zfill(2)

    return {
        "date": date,
        "jour": jour,
        "heure": heure,
        "heureFin": heure_fin,
        "professor": tabProfesseurs.get(cours.get("professor")),
        "matiere": cours.get("matiere"),
        "type": type_cours,
        "groupe": groupe_label,
        "groupeIndex": groupe,
        "salle": cours.get("room"),
        "semester": semestre
    }