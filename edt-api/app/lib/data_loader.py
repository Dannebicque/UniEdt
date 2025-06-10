# app/lib/data_loader.py
from pathlib import Path
import json, os
from functools import lru_cache

ROOT = Path(__file__).resolve().parents[2]          # → dossier racine projet
DATA_DIR = Path(os.getenv("DATA_DIR", ROOT / "../data"))

@lru_cache
def load_json(name: str):
    file_path = DATA_DIR / f"{name}.json"
    with file_path.open(encoding="utf-8") as f:
        return json.load(f)

if __name__ == "__main__":
    print(DATA_DIR)
    data = load_json("contraintes")
    print(data)