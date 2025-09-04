import pandas as pd
import json
import glob
import math
import os
import random

listeGroupes = {
    "CM": 1,
    "A1": 1,
    "A2": 2,
    "B1": 3,
    "B2": 4,
    "C1": 5,
    "C2": 6,
    "D1": 7,
    "D2": 8,
    "A": 1,
    "B": 3,
    "C": 5,
    "D": 7,
    "GC2F2-1": 1,
    "GC2F2-2": 2,
    "GEMA2-A1": 3,
    "GEMA2-A2": 4,
    "GEMA2-B1": 5,
    "GEMA2-B2": 6,
    "GPRH2-1": 7,
    "GPRH2-2": 8,
    "GC2F2": 1,
    "GEMA2-A": 3,
    "GEMA2-B": 5,
    "GPRH2": 7,
    "GEMA2-FC-1": 1,
    "GEMA2-FC-2": 2,
    "GEMA2-FC": 1,
    "GEMA3-FI-1":1,
    "GEMA3-FI-2":2,
    "GEMA3-FI":1,
    "GEMA3-FC-1": 1,
    "GEMA3-FC-2": 2,
    "GEMA3-FC": 1,
    "GCCF3-1":1,
    "GCCF3-2":2,
    "GCCF3":1,
    "GPRH3-1":1,
    "GPRH3-2":2,
    "GPRH3":1
}

isVacataire = [
"ABDELLATIF",
"ABEL",
"ADRIEN",
"ALEXANDRA",
"ARISTIDE",
"AUDREY",
"CARO-GROS",
"CLOTILDE",
"CORALIE",
"CYRIL",
"DAMIEN-LEGLAND",
"EMMANUELLE",
"ERIC",
"FRANCOIS",
"HERVE",
"JEAN-FRANCOIS",
"JULIEN",
"LAETITIA",
"LAURENCE",
"LYSIANE",
"MICHEL",
"NATHALIE",
"PASCALE",
"PERRINE",
"PHILIPPE",
"RACHEL",
"SONIA",
"STEPHANIE",
"TEDDY",
"VIRGINIE"
]

excel_files = glob.glob('2025_2026_EDT_GEA.xlsx')

for excel_path in excel_files:
    sheets_raw = pd.read_excel(excel_path, sheet_name=None, header=None)
    objets = []
    result = {"professeurs": {}, "matieres": {}}
    for sheet_name, df_raw in sheets_raw.items():
        print("Traitement de la feuille :", sheet_name)
        header_row = int(df_raw.iloc[0, 2])  # C1
        df = pd.read_excel(excel_path, sheet_name=sheet_name, header=header_row-1)
        a1 = int(df_raw.iloc[0, 0])
        b1 = int(df_raw.iloc[0, 1])

        for idx in range(a1, b1 + 1):
            if idx - header_row < 0 or idx - header_row >= len(df):
                continue
            row = df.iloc[idx - header_row]
            if str(row.iloc[0]).strip().upper() != "X":
                continue
            else:
                #traitement de la ligne. Création d'un objet global, qui va contenir le prof, puis ses matières, puis pour chaque matière les heures CM, TD et TP et le nombre de groupe affectésqueeze
                prof = str(row.iloc[4]).strip().upper()
                matiere = str(row.iloc[1]).strip().upper()

                #### Ajout dans la partie professeurs
                # tester, si le prof existe déjà dans le dictionnaire des professeurs
                if prof not in result["professeurs"]:
                    result["professeurs"][prof] = {"matieres": {}}

                if matiere not in result["professeurs"][prof]["matieres"]:
                    result["professeurs"][prof]["matieres"][matiere] = {"heures": {"CM": 0, "TD": 0, "TP": 0}, "groupe": {"CM": 0, "TD": 0, "TP": 0}}

                # on ajout
                type_cours = str(row.iloc[5]).strip().upper()
                result["professeurs"][prof]["matieres"][matiere]["heures"][type_cours] = float(row.iloc[6])
                print(row.iloc[7])
                result["professeurs"][prof]["matieres"][matiere]["groupe"][type_cours] = len(str(row.iloc[7]).split(","))

                # tester si la matière existe déjà dans le dictionnaire des matières
                if matiere not in result["matieres"]:
                    result["matieres"][matiere] = {"profs": {}}



    nom_fichier = f"data-test/previ.json"
    if os.path.exists(nom_fichier):
        with open(nom_fichier, 'r', encoding='utf-8') as f:
            anciens_objets = json.load(f)
    else:
        anciens_objets = []

    anciens_objets.append(result)

    with open(nom_fichier, 'w', encoding='utf-8') as f:
        json.dump(anciens_objets, f, ensure_ascii=False, indent=2)