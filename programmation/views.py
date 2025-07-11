# programmation/views.py

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import requests
import json
import os
import math
from .syntheses import synthese_etudiants_data, SYNTH_GROUPES
from .syntheses import synthese_profs_data, previ_profs_data_from_url, dispo_profs_par_semaine

# Chemin de sortie
OUTPUT_FILE = os.path.join(settings.DATA_PATH, "programmation.json")
# URL du fichier export.json
URL_EXPORT = "https://mmi23x02.mmi-troyes.fr/export"
EVENEMENTS_FILE = os.path.join(settings.DATA_PATH, "evenements.json")

def index(request):
    """
    Vue principale affichant le menu des fonctionnalités
    """
    return render(request, "programmation/index.html")


def import_previsionnel(request):
    """
    Vue pour importer le prévisionnel et générer programmation.json
    """
    try:
        if request.method == "POST":
            response = requests.get(URL_EXPORT)
            if response.status_code != 200:
                return HttpResponse(f"Erreur lors du téléchargement du fichier export : {response.status_code}")

            previsionnel = response.json()
            programmation = []

            for matiere in previsionnel:
                code_matiere = matiere["code_matiere"]

                # Exclure les matières qui ne commencent pas par W
                if not code_matiere.startswith("W"):
                    continue

                nom_matiere = matiere["nom_matiere"]
                semestre = matiere["semestre"]

                # Exclure les semestres autres que S1, S3, S5
                if semestre not in ["S1", "S3", "S5"]:
                    continue

                parcours = matiere["parcours"]

                # Simplification des parcours
                if parcours.startswith("BUT2-"):
                    parcours = parcours.replace("BUT2-", "", 1)
                elif parcours.startswith("BUT3-"):
                    parcours = parcours.replace("BUT3-", "", 1)
                if parcours == "CREACOM-FC":
                    parcours = "CREACOM"

                for prof in matiere.get("profs", []):
                    block_str = prof["block"]
                    block = 1 if block_str == "block1" else 2
                    code_prof = prof["code"]

                    types_cours = ["cm", "td", "tp"]
                    for type_cours in types_cours:
                        nb_cours = prof[type_cours]
                        if nb_cours > 0:
                            if type_cours == "cm":
                                nb_groupes = 1
                                nb_cours = int(nb_cours)
                            elif type_cours == "td":
                                nb_groupes = prof["nbGpTd"] if prof["nbGpTd"] != 0 else 1
                                nb_cours = math.ceil(nb_cours / nb_groupes)
                            elif type_cours == "tp":
                                nb_groupes = prof["nbGpTp"] if prof["nbGpTp"] != 0 else 1
                                nb_cours = math.ceil(nb_cours / nb_groupes)

                            ligne = {
                                "code_matiere": code_matiere,
                                "nom_matiere": nom_matiere,
                                "semestre": semestre,
                                "parcours": parcours,
                                "block": block,
                                "code_prof": code_prof,
                                "type": type_cours.upper(),
                                "nb_cours": nb_cours,
                                "nb_groupes": nb_groupes,
                                "groupes": None,
                                "Fixed": 0  # Fixed initialisé à 0
                            }

                            for i in range(1, 53):
                                ligne[f"Sem{i}"] = None

                            programmation.append(ligne)

            # Sauvegarde du fichier programmation.json
            os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
            with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
                json.dump(programmation, outfile, indent=4, ensure_ascii=False)

        return JsonResponse({"message": "Import du prévisionnel effectué avec succès."})
    except Exception as e:
        return JsonResponse({"message": f"Erreur : {str(e)}"})


def partie1(request):
    # Récupération des filtres GET
    semestre_filtre = request.GET.get("semestre", "").upper()
    parcours_filtre = request.GET.get("parcours", "").upper()
    code_filtre = request.GET.get("code", "").upper()
    prof_filtre = request.GET.get("prof", "").upper()
    type_filtre = request.GET.get("type", "").upper()

    # Lecture programmation.json
    with open(OUTPUT_FILE, "r", encoding="utf-8") as infile:
        programmation = json.load(infile)

    # Application des filtres
    if semestre_filtre:
        programmation = [l for l in programmation if l["semestre"].upper() == semestre_filtre]

    if parcours_filtre:
        programmation = [l for l in programmation if l["parcours"].upper() == parcours_filtre]

    if code_filtre:
        programmation = [l for l in programmation if code_filtre in l["code_matiere"].upper()]

    if prof_filtre:
        programmation = [l for l in programmation if prof_filtre in l["code_prof"].upper()]

    if type_filtre:
        programmation = [l for l in programmation if l["type"].upper() == type_filtre]

    # Lecture evenements.json
    with open(EVENEMENTS_FILE, "r", encoding="utf-8") as infile:
        evenements = json.load(infile)

    semaines = range(1, 24)
    semaines_keys = [f"Sem{i}" for i in semaines]

    disponibilites = {}
    mapping = {
        "S1": ("S1", "BUT1"),
        "S3FI": ("S3", "DEV-FI"),
        "S3DEV": ("S3", "DEV-FC"),
        "S3COM": ("S3", "CREACOM"),
        "S5FI": ("S5", "DEV-FI"),
        "S5DEV": ("S5", "DEV-FC"),
        "S5COM": ("S5", "CREACOM"),
    }

    for evt in evenements:
        if evt.get("type") != "FIXE":
            continue  # ignorer si type différent de fixed
        evt_semestre = evt.get("semestre")
        if evt_semestre not in mapping:
            continue
        sem, parcours = mapping[evt_semestre]
        semaine = evt.get("semaine")
        nb_cren = len(evt.get("creneaux", []))
        semaines_evt = range(1, 24) if semaine == 99 else [semaine]
        for sem_evt in semaines_evt:
            key = f"{sem}_{parcours}_{sem_evt}"
            disponibilites[key] = disponibilites.get(key, 0) + nb_cren

    for key in disponibilites:
        disponibilites[key] = max(35 - disponibilites[key], 0)

    for ligne in programmation:
        total = 0
        semaines_values = {}
        for i in semaines:
            key = f"Sem{i}"
            val = ligne.get(key)
            semaines_values[i] = val if val is not None else ""
            if val:
                try:
                    total += int(val)
                except ValueError:
                    pass
        ligne["complet"] = (total == ligne["nb_cours"])
        ligne["depasse"] = (total > ligne["nb_cours"])
        ligne["semestre_parcours"] = f"{ligne['semestre']}_{ligne['parcours']}"
        ligne["semaines_values"] = semaines_values

        sem_parc_week = {}
        for i in semaines:
            sem_parc_week[i] = f"{ligne['semestre']}_{ligne['parcours']}_{i}"
        ligne["sem_parc_week"] = sem_parc_week

    return render(request, "programmation/partie1.html", {
        "programmation": programmation,
        "semaines": semaines,
        "semaines_keys": semaines_keys,
        "disponibilites": disponibilites,
        "semestre_filtre": semestre_filtre,
        "parcours_filtre": parcours_filtre,
        "code_filtre": code_filtre,
        "prof_filtre": prof_filtre,
        "type_filtre": type_filtre,
    })

@csrf_exempt
def update_programmation(request):
    """
    Vue pour mettre à jour une ligne du fichier programmation.json
    """
    if request.method == "POST":
        data = json.loads(request.body)

        with open(OUTPUT_FILE, "r", encoding="utf-8") as infile:
            programmation = json.load(infile)

        updated = False

        for i, ligne in enumerate(programmation):
            if (ligne["code_matiere"] == data["code_matiere"] and
                ligne["code_prof"] == data["code_prof"] and
                ligne["type"] == data["type"] and
                ligne["block"] == data["block"]):

                programmation[i]["Fixed"] = data["Fixed"]
                programmation[i]["groupes"] = data["groupes"]

                # Mise à jour des Sem1..Sem23
                for j in range(1, 24):
                    key = f"Sem{j}"
                    if key in data:
                        valeur = data.get(key)
                        if valeur is not None:
                            try:
                                valeur = int(valeur)
                            except ValueError:
                                valeur = None
                        programmation[i][key] = valeur

                updated = True
                break

        if updated:
            with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
                json.dump(programmation, outfile, indent=4, ensure_ascii=False)

            return JsonResponse({"status": "success", "message": "Ligne mise à jour avec succès."})
        else:
            return JsonResponse({"status": "error", "message": "Ligne non trouvée."})

    return JsonResponse({"status": "error", "message": "Méthode non autorisée."})


@csrf_exempt
def update_all(request):
    if request.method == "POST":
        data = json.loads(request.body)

        # Lecture du fichier complet
        with open(OUTPUT_FILE, "r", encoding="utf-8") as infile:
            programmation = json.load(infile)

        # Remplacement des lignes correspondantes aux filtres actifs
        for ligne_modifiee in data:
            for i, ligne in enumerate(programmation):
                if (ligne["code_matiere"] == ligne_modifiee["code_matiere"] and
                    ligne["code_prof"] == ligne_modifiee["code_prof"] and
                    ligne["type"] == ligne_modifiee["type"] and
                    ligne["block"] == ligne_modifiee["block"]):
                    programmation[i] = ligne_modifiee
                    break

        # Sauvegarde du fichier complet avec les lignes modifiées mises à jour
        with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
            json.dump(programmation, outfile, indent=4, ensure_ascii=False)

        return JsonResponse({"message": "Programmation filtrée enregistrée avec succès."})

    return JsonResponse({"message": "Méthode non autorisée."})



def get_sem_class(semestre):
    if semestre == "S1":
        return "semestre-s1"
    elif semestre == "S3":
        return "semestre-s3"
    elif semestre == "S5":
        return "semestre-s5"
    return ""

def etudiants_1(request):
    programmation_path = os.path.join(settings.DATA_PATH, "programmation.json")
    synthese = synthese_etudiants_data(programmation_path)
    header_weeks = [f"S{i}" for i in range(1, 24)]
    lignes = []
    for semestre, parcours, groupes in SYNTH_GROUPES:
        for groupe in groupes:
            valeurs = synthese[(semestre, parcours, groupe)]
            total = sum(valeurs)
            lignes.append({
                "semestre": semestre,
                "parcours": parcours,
                "groupe": groupe,
                "semaine": valeurs,
                "total": total,
                "sem_class": get_sem_class(semestre)
            })

    context = {
        "header_weeks": header_weeks,
        "lignes": lignes,
    }
    return render(request, "programmation/synthese_etudiants.html", context)


def profs_1(request):
    programmation_path = os.path.join(settings.DATA_PATH, "programmation.json")
    contraintes_path = os.path.join(settings.DATA_PATH, "contraintes.json")
    export_url = "https://mmi23x02.mmi-troyes.fr/export"

    synthese, profs = synthese_profs_data(programmation_path, contraintes_path)
    previ = previ_profs_data_from_url(export_url, profs)
    dispo_semaine = dispo_profs_par_semaine(contraintes_path, profs)

    header_weeks = [f"S{i}" for i in range(1, 24)]
    lignes = []
    for prof in profs:
        previ_prof = previ.get(prof, 0)
        if previ_prof == 0:
            continue
        valeurs = synthese[prof]
        total = sum(valeurs)
        ecart = previ_prof - total
        dispos = dispo_semaine[prof]
        lignes.append({
            "prof": prof,
            "semaine": valeurs,
            "total": total,
            "previ": previ_prof,
            "ecart": ecart,
            "dispos_semaine": dispos
        })
    context = {
        "header_weeks": header_weeks,
        "lignes": lignes,
    }
    return render(request, "programmation/synthese_profs.html", context)

# programmation/views.py

from django import forms
from .utils.export_semaines import export_cours_for_semaines

class ExportSemainesForm(forms.Form):
    semaine = forms.CharField(label="Semaine (1-52 ou ALL)", max_length=5)
    overwrite = forms.BooleanField(label="Écraser les fichiers existants", required=False, initial=False)

def export_semaines_view(request):
    result = None
    if request.method == "POST":
        form = ExportSemainesForm(request.POST)
        if form.is_valid():
            semaine_str = form.cleaned_data["semaine"].strip().upper()
            overwrite = form.cleaned_data["overwrite"]
            if semaine_str == "ALL":
                semaines = list(range(1, 53))
            elif semaine_str.isdigit() and 1 <= int(semaine_str) <= 52:
                semaines = [int(semaine_str)]
            else:
                form.add_error("semaine", "Valeur de semaine incorrecte.")
                return render(request, "programmation/export_semaines.html", {"form": form, "result": result})

            # Premier passage : on ne force pas l'écrasement
            export_feedback = export_cours_for_semaines(semaines, overwrite_files=overwrite)
            # Détermine si confirmation nécessaire
            exists = [sem for sem, val in export_feedback.items() if val == "exists"]
            if exists and not overwrite:
                # Demande de confirmation d'écrasement
                return render(request, "programmation/export_semaines.html", {
                    "form": form,
                    "result": None,
                    "overwrite_required": exists,
                })
            # Sinon, affiche le résultat final
            result = export_feedback
    else:
        form = ExportSemainesForm()
    return render(request, "programmation/export_semaines.html", {"form": form, "result": result})
