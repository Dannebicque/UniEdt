import os
from pathlib import Path

def get_data_dir() -> Path:
    root = Path(__file__).resolve().parents[2]
    return Path(os.getenv("DATA_DIR", root / "../data")).resolve()