from __future__ import annotations
from datetime import datetime
from typing import List
from urllib.parse import urlencode

from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.dateparse import parse_date
from django.urls import reverse
from django.views.decorators.http import require_POST

from .constants import SEMESTRES, SEMESTRES_EXTRA
from .forms import EventForm, EventEditForm
from .storage import load_events, save_event, update_event, delete_event
from .utils import date_from_semaine_jour


# pondération créneaux
def _w(cr: List[int]) -> int:
    order = [
        {1,2,3,4,5,6}, {1,2,3}, {1}, {2}, {3},
        {4,5,6}, {4}, {5}, {6}
    ]
    s = set(cr)
    for idx, pat in enumerate(order):
        if s == pat:
            return idx
    return 9


# nouvelle redirection « back »
def _back(request, fallback="events:home"):
    nxt = request.GET.get("next") or request.POST.get("next")
    if nxt:
        # si next ne commence pas par '/', on le considère comme chaîne de requête
        if not nxt.startswith("/"):
            nxt = reverse("events:home") + ("?" + nxt if nxt else "")
        return redirect(nxt)
    ref = request.META.get("HTTP_REFERER")
    if ref:
        return redirect(ref)
    return redirect(reverse(fallback))


# ╔═ HOME ════════════════════════════════════════════════════════════════╗
def home(request):
    # ----- ajout -----
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            targets = d["semestres_target"]

            if d.get("mode_semaine_complete"):
                semaine, base = d["semaine_calc"], d["code"]
                for sem in targets:
                    for idx, j in enumerate(("lundi","mardi","mercredi","jeudi","vendredi")):
                        save_event({
                            "code": f"{base}{sem}{idx}",
                            "nom": d["nom"], "type": d["type"],
                            "semaine": semaine, "jour": j,
                            "creneaux": [1,2,3,4,5,6],
                            "date": date_from_semaine_jour(semaine, j).isoformat(),
                            "semestre": sem,
                            "description": d["description"] or None,
                        })
            else:
                for sem in targets:
                    save_event({
                        "code": f"{d['code']}{sem}",
                        "nom": d["nom"], "type": d["type"],
                        "semaine": d["semaine_calc"], "jour": d["jour_calc"],
                        "creneaux": d["creneaux"], "date": d["date_calc"],
                        "semestre": sem,
                        "description": d["description"] or None,
                    })
            messages.success(request, "Évènement(s) enregistré(s) ✔")
            return redirect(request.path + ("?" + request.GET.urlencode() if request.GET else ""))

    else:
        form = EventForm()

    # ----- filtres -----
    evts = load_events()
    dmin = parse_date(request.GET.get("date_min") or "")
    dmax = parse_date(request.GET.get("date_max") or "")
    sem = request.GET.get("semestre") or ""

    if dmin:
        evts = [e for e in evts if parse_date(e["date"]) >= dmin]
    if dmax:
        evts = [e for e in evts if parse_date(e["date"]) <= dmax]

    if sem:
        if sem in SEMESTRES_EXTRA:  # groupe (ALL, FI, S3FC, …)
            evts = [e for e in evts if e["semestre"] in SEMESTRES_EXTRA[sem]]
        else:  # semestre “réel”
            evts = [e for e in evts if e["semestre"] == sem]

    evts.sort(key=lambda e: (parse_date(e["date"]), e["semestre"], _w(e["creneaux"])))

    return render(request, "events/home.html", {
        "form": form,
        "events": evts,
        "semestres": SEMESTRES,
        "filters": {
            "date_min": dmin.isoformat() if dmin else "",
            "date_max": dmax.isoformat() if dmax else "",
            "semestre": sem,
        },
        "current_query": request.GET.urlencode(),
    })


# ╔═ ÉDITION ═════════════════════════════════════════════════════════════╗
def edit_event(request, code: str):
    evt = next((e for e in load_events() if e["code"] == code), None)
    if not evt:
        messages.error(request, "Évènement introuvable")
        return _back(request)

    if request.method == "POST":
        form = EventEditForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            update_event(code, {
                "code": code,
                "nom": d["nom"], "type": d["type"],
                "semaine": d["semaine_calc"], "jour": d["jour_calc"],
                "creneaux": d["creneaux"], "date": d["date"].isoformat(),
                "semestre": d["semestre"],
                "description": d["description"] or None,
            })
            messages.success(request, "Évènement mis à jour ✔")
            return _back(request)
    else:
        init = {
            "nom": evt["nom"], "date": evt["date"],
            "horaires": [str(c) for c in evt["creneaux"]],
            "description": evt["description"], "type": evt["type"],
            "semestre": evt["semestre"],
        }
        form = EventEditForm(initial=init)

    return render(request, "events/edit.html",
                  {"form": form, "next": request.GET.get("next", "")})


# ╔═ SUPPRESSION ═════════════════════════════════════════════════════════╗
@require_POST
def delete_event_view(request, code: str):
    delete_event(code)
    messages.success(request, "Évènement supprimé ✔")
    return _back(request)
