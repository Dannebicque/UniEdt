# app/lib/data_loader.py
from pathlib import Path
import json, os
from functools import lru_cache
from app.lib.paths import get_data_dir

DATA_DIR = get_data_dir()

def load_json(name: str):
    file_path = DATA_DIR / f"{name}.json"
    with file_path.open(encoding="utf-8") as f:
        return json.load(f)

def save_json(name: str, data:dict):
    file_path = DATA_DIR / f"{name}.json"
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    print(DATA_DIR)
    data = load_json("contraintes")
    print(data)