import math
import requests
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def home(request):
    response = requests.get("https://mmi23x02.mmi-troyes.fr/export")
    data = response.json()

    tableau = []
    for matiere in data:
        if not matiere['code_matiere'].startswith('W'):
            continue

        code_matiere = matiere['code_matiere']
        nom_matiere = matiere['nom_matiere']
        semestre = matiere['semestre']
        parcours_raw = matiere['parcours']

        # === Simplification parcours ===
        if 'BUT2' in parcours_raw or 'BUT3' in parcours_raw:
            if 'DEV-FI' in parcours_raw:
                parcours = 'DEV-FI'
            elif 'DEV-FC' in parcours_raw:
                parcours = 'DEV-FC'
            elif 'CREACOM-FC' in parcours_raw:
                parcours = 'CREACOM'
            else:
                parcours = parcours_raw
        elif 'CREACOM-FC' in parcours_raw:
            parcours = 'CREACOM'
        else:
            parcours = parcours_raw

        lead_code = matiere['lead']['code']

        for prof in matiere['profs']:
            bloc_num = 1 if prof['block'] == 'block1' else 2
            cm = prof['cm']
            td = math.ceil(prof['td'] / prof['nbGpTd']) if prof['nbGpTd'] else 0
            tp = math.ceil(prof['tp'] / prof['nbGpTp']) if prof['nbGpTp'] else 0

            tableau.append({
                'code_matiere': code_matiere,
                'nom_matiere': nom_matiere,
                'semestre': semestre,
                'parcours': parcours,
                'bloc': bloc_num,
                'code_prof': prof['code'],
                'nom_prof': f"{prof['prenom']} {prof['nom']}",
                'is_lead': prof['code'] == lead_code,
                'cm': cm,
                'td': td,
                'nbGpTd': prof['nbGpTd'],
                'tp': tp,
                'nbGpTp': prof['nbGpTp'],
            })

    context = {'tableau': tableau}
    return render(request, 'previsionnel/home.html', context)