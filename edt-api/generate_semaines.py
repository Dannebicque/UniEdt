import os
import json
from datetime import datetime, timedelta

def get_jours_feries_france(year):
    # Calcul de Pâques (algorithme de Meeus/Jones/Butcher)
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    paques = datetime(year, month, day)
    # Jours fériés fixes et mobiles
    jours = {
        datetime(year, 1, 1),    # Jour de l'an
        datetime(year, 5, 1),    # Fête du Travail
        datetime(year, 5, 8),    # Victoire 1945
        datetime(year, 7, 14),   # Fête nationale
        datetime(year, 8, 15),   # Assomption
        datetime(year, 11, 1),   # Toussaint
        datetime(year, 11, 11),  # Armistice
        datetime(year, 12, 25),  # Noël
        paques + timedelta(days=1),   # Lundi de Pâques
        paques + timedelta(days=39),  # Ascension
        paques + timedelta(days=50),  # Lundi de Pentecôte
    }
    return {d.strftime("%Y-%m-%d") for d in jours}

DATA_DIR = "../data/semaines"
START_DATE = datetime(2024, 9, 2)
DAYS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
LISTE_S_IMPAIRES = ["S1", "S3", "S5"]
LISTE_S_PAIRES = ["S2", "S4", "S6"]

os.makedirs(DATA_DIR, exist_ok=True)

for week in range(1, 53):
    days = []
    for i, day_name in enumerate(DAYS):
        date = START_DATE + timedelta(weeks=week-1, days=i)
        jours_feries = get_jours_feries_france(date.year)
        is_holiday = date.strftime("%Y-%m-%d") in jours_feries
        days.append({
            "day": day_name,
            "date": date.strftime("%Y-%m-%d"),
            "isHoliday": is_holiday
        })

    # Détermination du semestre selon la date du lundi
    monday_date = START_DATE + timedelta(weeks=week - 1)
    premiere_fevrier = datetime(monday_date.year, 2, 1)
    if monday_date < premiere_fevrier:
        semesters = LISTE_S_IMPAIRES
    else:
        semesters = LISTE_S_PAIRES

    semaine = {
        "week": week,
        "days": days,
        "semesters": semesters
    }
    filename = os.path.join(DATA_DIR, f"semaine_{week}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(semaine, f, ensure_ascii=False, indent=4)
print("Fichiers semaines générés dans le dossier data.")