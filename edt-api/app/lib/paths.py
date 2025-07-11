from pathlib import Path
from app.config import settings

def get_data_dir() -> Path:
    root = Path(__file__).resolve().parents[2]
    data_dir = settings.data_dir
    return (root / data_dir).resolve()
