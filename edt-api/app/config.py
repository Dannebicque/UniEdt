# app/config.py
import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# 4.1  Déterminer quel fichier .env charger
_stage = os.getenv("ENV", "local")
env_file = Path(__file__).resolve().parent.parent / f".env.{_stage}"
#       -> .env.local ou .env.production
#       -> fallback : .env si aucun des deux n’existe
if not env_file.exists():
    env_file = Path(__file__).resolve().parent.parent / ".env"

load_dotenv(env_file, override=False)          # remplit os.environ

# 4.2  Pydantic v2 pour exposer les variables typées
class Settings(BaseSettings):
    env: str = "local"
    url_front: str = "http://localhost:3000"  # port par défaut de Vite
    debug: bool = False
    data_dir: Path = Path("../data")

    model_config = SettingsConfigDict(
        env_file=str(env_file),
        env_file_encoding="utf-8",
    )

settings = Settings()
