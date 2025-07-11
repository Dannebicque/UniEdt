# constants.py
# Fichier de constantes communes à toutes les applications Django du projet UniEDT

from pathlib import Path
from datetime import date

# Date du lundi de la semaine 1
LUNDI_ONE: date = date(2025, 9, 1)

# Répertoire de base du projet
BASE_DIR = Path(__file__).resolve().parent.parent  # UniEDT_2025/

# Répertoire commun aux fichiers JSON (datas/)
DOSSIERS_JSON: Path = BASE_DIR.parent / "datas"
DOSSIERS_JSON.mkdir(exist_ok=True)

# Liste des semestres proposée dans les formulaires
SEMESTRES: list[str] = ["S1", "S3FI", "S3DEV", "S3COM", "S5FI", "S5DEV", "S5COM"]

# Autres constantes globales éventuelles peuvent être ajoutées ici

