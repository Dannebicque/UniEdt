import os
import json
from django.shortcuts import render, redirect
from django.conf import settings
from .forms import EnseignantForm

# Chemin absolu vers le fichier JSON
DOSSIER_JSON = "/home/pgommery/UniEDT2025/datas"
JSON_PATH = "/home/pgommery/UniEDT2025/datas/contraintes.json"

# Lecture du fichier JSON
def lire_donnees():
    if not os.path.exists(JSON_PATH):
        return {}
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# Écriture dans le fichier JSON
def ecrire_donnees(data):
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# Affichage de la liste des enseignants (triée par nom)
def liste_enseignants(request):
    enseignants = lire_donnees()
    enseignants_trie = dict(sorted(enseignants.items(), key=lambda x: x[1].get("name", "")))
    return render(request, "enseignants/list.html", {"enseignants": enseignants_trie})

# Ajout d’un enseignant
def ajouter_enseignant(request):
    if request.method == "POST":
        form = EnseignantForm(request.POST)
        if form.is_valid():
            data = lire_donnees()
            code = form.cleaned_data["code"].upper()
            data[code] = {
                "name": f'{form.cleaned_data["prenom"]} {form.cleaned_data["nom"]}',
                "email": form.cleaned_data["email"],
                "telephone": form.cleaned_data["telephone"],
                "service": form.cleaned_data["service"],
                "type": form.cleaned_data["type"],
                "availability": []
            }
            ecrire_donnees(data)
            return redirect("liste_enseignants")
    else:
        form = EnseignantForm()
    return render(request, "enseignants/form.html", {"form": form, "action": "Ajouter"})

# Modification d’un enseignant
def modifier_enseignant(request, code):
    data = lire_donnees()
    enseignant = data.get(code.upper())
    if not enseignant:
        return redirect("liste_enseignants")

    # Séparer prénom et nom (si possible)
    try:
        prenom, nom = enseignant["name"].split(" ", 1)
    except ValueError:
        prenom = enseignant["name"]
        nom = ""

    initial = {
        "code": code,
        "prenom": prenom,
        "nom": nom,
        "email": enseignant["email"],
        "telephone": enseignant.get("telephone", ""),
        "service": enseignant["service"],
        "type": enseignant["type"],
    }

    if request.method == "POST":
        form = EnseignantForm(request.POST, readonly_code=True)
        if form.is_valid():
            data[code] = {
                "name": f'{form.cleaned_data["prenom"]} {form.cleaned_data["nom"]}',
                "email": form.cleaned_data["email"],
                "telephone": form.cleaned_data["telephone"],
                "service": form.cleaned_data["service"],
                "type": form.cleaned_data["type"],
                "availability": enseignant.get("availability", [])
            }
            ecrire_donnees(data)
            return redirect("liste_enseignants")
    else:
        form = EnseignantForm(initial=initial, readonly_code=True)

    return render(request, "enseignants/form.html", {"form": form, "action": "Modifier"})

# Suppression d’un enseignant
def supprimer_enseignant(request, code):
    data = lire_donnees()
    if code in data:
        del data[code]
        ecrire_donnees(data)
    return redirect("liste_enseignants")


# Page de confirmation avant suppression
def confirmer_suppression_enseignant(request, code):
    data = lire_donnees()
    enseignant = data.get(code)
    if not enseignant:
        return redirect("liste_enseignants")

    if request.method == "POST":
        if "confirmer" in request.POST:
            del data[code]
            ecrire_donnees(data)
        return redirect("liste_enseignants")

    return render(request, "enseignants/confirmer_suppression.html", {
        "code": code,
        "enseignant": enseignant
    })

def label_creneau(index):
    mapping = {
        1: "08h00",
        2: "09h30",
        3: "11h00",
        4: "14h00",
        5: "15h30",
        6: "17h00"
    }
    return mapping.get(index, f"C{index}")

def contraintes_enseignant(request, code):
    enseignants = lire_donnees()
    if code not in enseignants:
        return redirect('liste_enseignants')

    enseignant = enseignants[code]

    # Initialisation de availability si absente
    if "availability" not in enseignant:
        enseignant["availability"] = []

    if request.method == "POST" and "ajouter_contrainte" in request.POST:
        # Lecture des champs semaine et jour avec fallback si désactivés
        if "toutes_semaines" in request.POST:
            semaine = 99
        else:
            semaine = request.POST.get("semaine")
            if not semaine or not semaine.isdigit():
                semaine = 99
            else:
                semaine = int(semaine)

        if "tous_jours" in request.POST:
            jour = "ALL"
        else:
            jour = request.POST.get("jour")

        statut = request.POST.get("statut", "indisponible")
        commentaire = request.POST.get("commentaire", "").strip()

        # Lecture des créneaux cochés
        if "select_all_creneaux" in request.POST:
            creneaux = [1, 2, 3, 4, 5, 6]
        else:
            creneaux = []
            for i in range(1, 7):
                if request.POST.get(f"creneau_{i}"):
                    creneaux.append(i)

        if creneaux:
            contrainte = {
                "status": statut,
                "week": semaine,
                "day": jour,
                "creneaux": creneaux
            }
            if commentaire:
                contrainte["commentaire"] = commentaire

            enseignant["availability"].append(contrainte)
            enseignants[code] = enseignant
            ecrire_donnees(enseignants)
            return redirect('contraintes_enseignant', code=code)

    # Préparation du nom/prénom
    nom_prenom = enseignant.get("name", "")
    nom, prenom = (nom_prenom.split()[0], nom_prenom.split()[1]) if " " in nom_prenom else (nom_prenom, "")

    # Créneaux pour affichage dans le formulaire
    creneaux_labels = [
        (1, "08h00"),
        (2, "09h30"),
        (3, "11h00"),
        (4, "14h00"),
        (5, "15h30"),
        (6, "17h00"),
    ]

    return render(request, "enseignants/contraintes.html", {
        "code": code,
        "nom": nom,
        "prenom": prenom,
        "enseignant": enseignant,
        "creneaux_labels": creneaux_labels
    })


def supprimer_contrainte(request, code, index):
    filepath = os.path.join(DOSSIER_JSON, "contraintes.json")
    enseignants = lire_donnees()

    if code in enseignants:
        availability = enseignants[code].get("availability", [])
        if 0 <= index < len(availability):
            del availability[index]
            enseignants[code]["availability"] = availability
            ecrire_donnees(enseignants)

    return redirect("contraintes_enseignant", code=code)


def modifier_contrainte(request, code, index):
    data = lire_donnees()
    enseignant = data.get(code.upper())
    if not enseignant:
        return redirect("liste_enseignants")

    try:
        index = int(index)
        contrainte = enseignant["availability"][index]
    except (ValueError, IndexError):
        return redirect("contraintes_enseignant", code=code)

    try:
        prenom, nom = enseignant["name"].split(" ", 1)
    except ValueError:
        prenom = enseignant["name"]
        nom = ""

    if request.method == "POST":
        statut = request.POST.get("statut")
        semaine = 99 if "toutes_semaines" in request.POST else request.POST.get("semaine")
        jour = "ALL" if "tous_jours" in request.POST else request.POST.get("jour")
        commentaire = request.POST.get("commentaire", "").strip()
        creneaux = [i for i in range(1, 7) if request.POST.get(f"creneau_{i}")]

        contrainte_maj = {
            "week": semaine,
            "day": jour,
            "creneaux": creneaux,
           "status": statut,
            "commentaire": commentaire
        }
        enseignant["availability"][index] = contrainte_maj
        data[code] = enseignant
        ecrire_donnees(data)
        return redirect("contraintes_enseignant", code=code)

    creneaux_labels = [
        (1, "08h00"),
        (2, "09h30"),
        (3, "11h00"),
        (4, "14h00"),
        (5, "15h30"),
        (6, "17h00")
    ]

    return render(request, "enseignants/modifier_contrainte.html", {
        "code": code,
        "nom": nom,
        "prenom": prenom,
        "index": index,
        "contrainte": contrainte,
        "jours": ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"],
        "creneaux_labels": creneaux_labels,
    })

