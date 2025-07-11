from datetime import datetime
from django import template

register = template.Library()

_HEURES = {
    1: "08h00", 2: "09h30", 3: "11h00",
    4: "14h00", 5: "15h30", 6: "17h00",
}

@register.filter
def format_date_fr(iso_str: str) -> str:
    """'2025-10-03' → '03/10/2025'"""
    try:
        d = datetime.fromisoformat(iso_str).date()
        return d.strftime("%d/%m/%Y")
    except Exception:
        return iso_str   # au cas où

@register.filter
def creneau_label(creneaux):
    """
    Transforme [1,2,3] → 'Matin', etc.
    """
    if not isinstance(creneaux, (list, tuple)):
        return creneaux

    s = set(creneaux)
    if s == {1, 2, 3}:
        return "Matin"
    if s == {4, 5, 6}:
        return "Après-midi"
    if s == {1, 2, 3, 4, 5, 6}:
        return "Toute la journée"

    return ", ".join(_HEURES[c] for c in sorted(s))
