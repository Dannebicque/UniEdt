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
    for sheet_name, df_raw in sheets_raw.items():
        print("Traitement de la feuille :", sheet_name)
        header_row = int(df_raw.iloc[0, 2])  # C1
        df = pd.read_excel(excel_path, sheet_name=sheet_name, header=header_row-1)
        a1 = int(df_raw.iloc[0, 0])
        b1 = int(df_raw.iloc[0, 1])

        colonnes_semaines = [col for col in df.columns if str(col).startswith('S')]
        for col in colonnes_semaines:
            semaine_num = str(col)[1:]  # Retire le "S"
            objets = []
            for idx in range(a1, b1 + 1):
                if idx - header_row < 0 or idx - header_row >= len(df):
                    continue
                row = df.iloc[idx - header_row]
                if str(row.iloc[0]).strip().upper() != "X":
                    continue
                if pd.notna(row[col]):
                    cell_value = row[col]
                    groupes = str(row.get('NB Groupes TD', '1')).split(',')
                    print(groupes)
                    for groupe in groupes:
                        groupe = groupe.strip()
                        print(groupe)
                        print(listeGroupes[groupe])
                        if pd.notna(cell_value):
                            try:
                                val = float(cell_value)
                                if val % 1.5 == 0:
                                    for i in range(int(val // 1.5)):
                                        obj = {
                                            "id": int(f"{hash(sheet_name) % 10000}{semaine_num}{idx + 1}{groupe if groupe.isdigit() else 0}{math.floor(random.randint(1, 999999) * math.fabs(math.sin(idx + int(semaine_num))))}"),                                            "matiere": row.get('matière', ''),
                                            "professor": row.get('Code enseignant', ''),
                                            "semester": sheet_name,
                                            "groupIndex": listeGroupes[groupe], # on fera la conversion après
                                            "type": row.get('Type Cours', ''),
                                            "groupCount": 8 if row.get('Type Cours', '') == 'CM' else 2 if row.get('Type Cours', '') == 'TD' else 1 if row.get('Type Cours','') == 'TP' else len(groupes),
                                            "date": None,
                                            "creneau": None,
                                            "room": None,
                                            "color": None, #on ajoutera après
                                            "isVacataire":  row.get('Code enseignant', '') in isVacataire, # on ajoutera après
                                        }
                                        objets.append(obj)
                                else:
                                    obj = {
                                        "id": int(f"{hash(sheet_name) % 10000}{semaine_num}{idx + 1}{groupe if groupe.isdigit() else 0}{math.floor(random.randint(1, 999999) * math.fabs(math.sin(idx + int(semaine_num))))}"),
                                        "matiere": row.get('matière', ''),
                                        "matiere": row.get('matière', ''),
                                        "professor": row.get('Code enseignant', ''),
                                        "semester": sheet_name,
                                        "groupIndex": listeGroupes[groupe],
                                        "type": row.get('Type Cours', ''),
                                        "groupCount": 8 if row.get('Type Cours', '') == 'CM' else 2 if row.get('Type Cours', '') == 'TD' else 1 if row.get('Type Cours', '') == 'TP' else len(groupes),
                                        "date": None,
                                        "creneau": None,
                                        "room": None,
                                        "color": None, #on ajoutera après
                                        "isVacataire": row.get('Code enseignant', '') in isVacataire, # on ajoutera après
                                        "duree": val
                                    }
                                    objets.append(obj)
                            except Exception:
                                # Si la valeur n'est pas un nombre, ignorer ou gérer selon besoin
                                pass
            nom_fichier = f"data-test/cours_{semaine_num}.json"
            if os.path.exists(nom_fichier):
                with open(nom_fichier, 'r', encoding='utf-8') as f:
                    anciens_objets = json.load(f)
            else:
                anciens_objets = []

            anciens_objets.extend(objets)

            with open(nom_fichier, 'w', encoding='utf-8') as f:
                json.dump(anciens_objets, f, ensure_ascii=False, indent=2)