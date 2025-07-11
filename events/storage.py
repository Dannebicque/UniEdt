import json
from pathlib import Path
from typing import TypedDict, Literal

from .constants import DOSSIERS_JSON

TypeEvt = Literal["INFO", "FIXE"]

class Evenement(TypedDict):
    code: str
    nom: str
    type: TypeEvt
    semaine: int
    jour: str
    creneaux: list[int]
    date: str        # ISO YYYY-MM-DD
    semestre: str
    description: str | None

_JSON_PATH: Path = DOSSIERS_JSON / "evenements.json"

def load_events() -> list[Evenement]:
    if not _JSON_PATH.exists():
        return []
    with _JSON_PATH.open(encoding="utf-8") as f:
        return json.load(f)

def save_event(evt: Evenement) -> None:
    evts = load_events()
    evts.append(evt)
    with _JSON_PATH.open("w", encoding="utf-8") as f:
        json.dump(evts, f, indent=2, ensure_ascii=False)

def save_events(evts: list[Evenement]) -> None:
    """Remplace complètement le fichier (utile pour update / delete)."""
    with _JSON_PATH.open("w", encoding="utf-8") as f:
        json.dump(evts, f, indent=2, ensure_ascii=False)


def update_event(code: str, new_evt: Evenement) -> None:
    evts = load_events()
    for i, e in enumerate(evts):
        if e["code"] == code:
            evts[i] = new_evt
            save_events(evts)
            return
    raise ValueError("Évènement introuvable")


def delete_event(code: str) -> None:
    evts = [e for e in load_events() if e["code"] != code]
    save_events(evts)