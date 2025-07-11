from datetime import date, timedelta
from typing import Literal

from .constants import LUNDI_ONE

# jours en minuscules
Jour = Literal["lundi", "mardi", "mercredi", "jeudi", "vendredi"]

_JOURS_INDEX: dict[Jour, int] = {
    "lundi": 0, "mardi": 1, "mercredi": 2, "jeudi": 3, "vendredi": 4,
}


def date_from_semaine_jour(semaine: int, jour: Jour) -> date:
    if not (1 <= semaine <= 52) or jour not in _JOURS_INDEX:
        raise ValueError("Semaine ou jour invalide")
    delta = timedelta(weeks=semaine - 1, days=_JOURS_INDEX[jour])
    return LUNDI_ONE + delta


def semaine_jour_from_date(d: date) -> tuple[int, Jour]:
    if d < LUNDI_ONE:
        raise ValueError("Date hors calendrier universitaire")
    days_since = (d - LUNDI_ONE).days
    semaine = days_since // 7 + 1
    jour_index = days_since % 7
    if jour_index > 4:
        raise ValueError("Week-end non géré")
    jour = list(_JOURS_INDEX.keys())[jour_index]
    return semaine, jour
