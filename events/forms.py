from __future__ import annotations
from datetime import datetime
from typing import Any, List

from django import forms
from django.core.exceptions import ValidationError

from .constants import SEMESTRES, SEMESTRES_EXTRA
from .utils import date_from_semaine_jour, semaine_jour_from_date

_H_CHOICES: list[tuple[str, str]] = [
    ("1", "08h00"), ("2", "09h30"), ("3", "11h00"),
    ("4", "14h00"), ("5", "15h30"), ("6", "17h00"),
]


class EventForm(forms.Form):
    nom = forms.CharField(
        label="Nom de l’évènement",
        error_messages={"required": "Le nom est obligatoire"},
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    semaine_complete = forms.BooleanField(label="Semaine complète ?", required=False)
    date_precise     = forms.BooleanField(label="Date précise ?",     required=False)
    date = forms.DateField(
        label="Date", required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )

    semaine = forms.IntegerField(
        label="Semaine", min_value=1, max_value=52, required=False,
        widget=forms.NumberInput(attrs={"class": "form-control w-100"})
    )
    jour = forms.ChoiceField(
        label="Jour", required=False,
        choices=[(j, j) for j in ("lundi", "mardi", "mercredi", "jeudi", "vendredi")],
        widget=forms.Select(attrs={"class": "form-select"})
    )

    plage = forms.ChoiceField(
        label="Plage horaire", initial="journee",
        widget=forms.RadioSelect, choices=[
            ("journee", "Journée"),
            ("matin",    "Matin"),
            ("apm",      "Après-midi"),
            ("horaires", "Horaires"),
        ]
    )
    horaires = forms.MultipleChoiceField(
        label="Horaires détaillés", required=False,
        choices=_H_CHOICES, widget=forms.CheckboxSelectMultiple
    )

    description = forms.CharField(
        label="Description", required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "style": "height:120px"})
    )
    type = forms.ChoiceField(
        label="Type", choices=[("FIXE", "FIXE"), ("INFO", "INFO")],
        widget=forms.Select(attrs={"class": "form-select"})
    )
    semestre = forms.ChoiceField(
        label="Semestre", choices=[(s, s) for s in SEMESTRES],
        widget=forms.Select(attrs={"class": "form-select"})
    )

    # ---------- validation ----------
    def clean(self) -> dict[str, Any]:
        cleaned: dict[str, Any] = super().clean()

        # 1) Semaine complète
        if cleaned.get("semaine_complete"):
            semaine = cleaned.get("semaine")
            if not semaine:
                raise ValidationError("Merci de saisir la semaine")
            cleaned |= {
                "mode_semaine_complete": True,
                "semaine_calc": semaine,
                "jour_calc":    None,
                "date_calc":    None,
                "creneaux":     [1, 2, 3, 4, 5, 6],
            }
        # 2) Mode normal
        else:
            use_date = cleaned.get("date_precise")
            d, sem, j = cleaned.get("date"), cleaned.get("semaine"), cleaned.get("jour")

            if use_date:
                if not d:
                    raise ValidationError("Merci de choisir une date précise")
                sem_calc, jour_calc = semaine_jour_from_date(d)
                cleaned["date_calc"] = d.isoformat()
            else:
                if not (sem and j):
                    raise ValidationError("Semaine et jour obligatoires")
                d2 = date_from_semaine_jour(sem, j.lower())
                sem_calc, jour_calc = sem, j.lower()
                cleaned["date_calc"] = d2.isoformat()

            cleaned["semaine_calc"] = sem_calc
            cleaned["jour_calc"]    = jour_calc

            p = cleaned["plage"]
            if p == "journee":   cleaned["creneaux"] = [1, 2, 3, 4, 5, 6]
            elif p == "matin":   cleaned["creneaux"] = [1, 2, 3]
            elif p == "apm":     cleaned["creneaux"] = [4, 5, 6]
            else:                # horaires détaillés
                hrs = cleaned.get("horaires")
                if not hrs:
                    raise ValidationError("Choisis au moins un horaire")
                cleaned["creneaux"] = sorted(int(v) for v in hrs)

        # Duplication par groupes
        sel_sem = cleaned["semestre"]
        cleaned["semestres_target"] = SEMESTRES_EXTRA.get(sel_sem, [sel_sem])

        cleaned["code"] = datetime.now().strftime("%Y%m%d%H%M%S")
        return cleaned


class EventEditForm(forms.Form):
    nom = forms.CharField(label="Nom", widget=forms.TextInput(attrs={"class": "form-control"}))
    date = forms.DateField(
        label="Date", widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )
    horaires = forms.MultipleChoiceField(
        label="Horaires", choices=_H_CHOICES, widget=forms.CheckboxSelectMultiple
    )
    description = forms.CharField(
        label="Description", required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "style": "height:120px"})
    )
    type = forms.ChoiceField(
        label="Type", choices=[("FIXE", "FIXE"), ("INFO", "INFO")],
        widget=forms.Select(attrs={"class": "form-select"})
    )
    semestre = forms.ChoiceField(
        label="Semestre",
        choices=[(s, s) for s in SEMESTRES_EXTRA["ALL"]],
        widget=forms.Select(attrs={"class": "form-select"})
    )

    def clean(self) -> dict[str, Any]:
        cleaned = super().clean()
        d = cleaned["date"]
        sem_calc, jour_calc = semaine_jour_from_date(d)
        cleaned["semaine_calc"] = sem_calc
        cleaned["jour_calc"]    = jour_calc
        cleaned["creneaux"]     = sorted(int(v) for v in cleaned["horaires"])
        return cleaned
