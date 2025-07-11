"""
Constantes réutilisables par tout le module events.
"""
from pathlib import Path
from datetime import date

# 01/09/2025 = lundi de la semaine 1
LUNDI_ONE: date = date(2025, 9, 1)

# Dossier commun aux fichiers JSON
BASE_DIR = Path(__file__).resolve().parent.parent  # UniEDT_2025/
DOSSIERS_JSON: Path = BASE_DIR.parent / "datas"
DOSSIERS_JSON.mkdir(exist_ok=True)

# Liste « de base » (inchangée)
SEMESTRES_BASE = [
    "S1",
    "S3FI",  "S3DEV",  "S3COM",
    "S5FI",  "S5DEV",  "S5COM",
]

# Groupes additionnels → liste des semestres réellement créés
SEMESTRES_EXTRA = {
    "ALL":  SEMESTRES_BASE,
    "FI":   ["S1", "S3FI", "S5FI"],        # ← NOUVEAU
    "S3FC": ["S3DEV", "S3COM"],
    "S5FC": ["S5DEV", "S5COM"],
}

# Options disponibles côté formulaire (base + groupes)
SEMESTRES = SEMESTRES_BASE + list(SEMESTRES_EXTRA.keys())

