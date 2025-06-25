# Outil de construction des EDT

## Présentation

 ...todo...

## Execution

Lancer la partie API de l'application avec la commande suivante :

```bash
./start.sh
```

## Schéma des données stockées en fichier JSON

### Fichiers "semaine"

Fichier nommé : `semaine_xx.json`, où xx est le numéro de la semaine (1 à 52).

```json
{
    "week": 1,
    "days": [
        {
            "day": "Lundi",
            "date": "2024-09-02",
            "isHoliday": false
        },
        {
            "day": "Mardi",
            "date": "2024-09-03",
            "isHoliday": false
        },
        {
            "day": "Mercredi",
            "date": "2024-09-04",
            "isHoliday": false
        },
        {
            "day": "Jeudi",
            "date": "2024-09-05",
            "isHoliday": false
        },
        {
            "day": "Vendredi",
            "date": "2024-09-06",
            "isHoliday": false
        }
    ],
  "semesters": ["S1", "S3", "S5"]
}
```

### Fichiers "Contraintes"

Fichier nommé : `contraintes.json` (fichier unique).

**Le fichier de contrainte sert aussi de fichier liste des professeurs.**

```json
{
    "DAN": {
        "name": "David A",
        "email": "david.a@mail.com",
        "service": 192,
        "type": "permanent",
        "availability": [
            {
                "day": "Lundi",
                "creneaux": [1, 2, 3],
                "recurrence": "weekly",
                "status": "indisponible"
            },
            {
                "day": "Mardi",
                "creneaux": [1, 2],
                "recurrence": "12/03/2025",
                "status": "indisponible"
            }
        ],
    },
    "JBA": {
        "name": "Julie B",
        "email": "julie.b@mail.com",
        "service": 192, # max si vacataire
        "type": "vacataire",
        "availability": [
            {
            "day": "Vendredi",
            "creneaux": [4, 5],
            "recurrence": "weekly",
            "status": "disponible"
        }
        ],
    }
}
```

### Fichiers "événements"

Fichier nommé : `evenements.json` (fichier unique)

```json
[
    {
        "id": 1, #trouver un moyen de générer des id uniques
        "name": "Réunion de rentrée",
        "date": "2024-09-02",
        "time": "10:00",
        "creneaux": [1], # numéro du créneau dans la journée
        "location": "A101",
        "description": "Réunion pour présenter les objectifs de l'année.",
        "semaine": 1,
        "semester": "s1"
    }
]
```

### Fichiers "cours à placer"

Fichier nommé : `cours_xx.json`, xx est le numéro de semaine

```json
[
  {
    "id": 1, #trouver un moyen de générer des id uniques
    "matiere": "WR118",
    "professor": "DAN",
    "semester": "S1",
    "groupIndex": 1,
    "type": "CM",
    "groupCount": 1, # si besoin
    "date": null, # date, vide si pas placé
    "creneau": null, # numéro du créneau dans la journée
    "room": null,
    "color": "#FF5733",
    "isVacataire": false,
  },
  {
    "id": 2, #trouver un moyen de générer des id uniques
    "matiere": "WR118",
    "professor": "DAN",
    "semester": "S1",
    "groupIndex": 1,
    "type": "TD",
    "groupCount": 1, # si besoin, pour les CM particuliers
    "date": null, # date, vide si pas placé
    "creneau": null, # numéro du créneau dans la journée
    "room": null,
    "color": "#FF5733",
    "isVacataire": false,
  }
]
```

### Fichier "salles"

Fichier nommé : `salles.json` (fichier unique)

```json
{
  "WR118": {
    "PGO": {
      "td": "H205",
      "tp": "H008"
    },
    "RHU": {
      "td": "H201",
      "tp": "H007"
    }
  },
  "CM": [
    "H018",
    "Amphi 1"
  ],
  "TD": [
    "H101",
    "H103"
  ],
  "TP": [
    "H007",
    "H008"
  ]
}
```

### Fichier "data globale"

Fichier nommé : `data_globale.json` (fichier unique)

```json
{
  "semesters": {
    "S1": {
      "color": "#FF5733",
      "nbTp": 8,
      "groupesTp": [
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
        "G",
        "H"
      ],
      "groupesTd": [
        "AB",
        "CD",
        "EF",
        "GH"
      ],
      "nbTd": 4,
      "matieres": [
        "WR101",
        "WR102",
        "WR103",
        "WR104"
      ]
    },
    "S3-Dev-FI": {
      "color": "#148027",
      "nbTp": 4,
      "nbTd": 2,
      "groupesTp": [
        "A",
        "B",
        "C",
        "D"
      ],
      "groupesTd": [
        "AB",
        "CD"
      ],
      "matieres": [
        "WR301",
        "WR302",
        "WR303",
        "WR304"
      ]
    },
    "S5-DEV-FI": {
      "color": "#223cb8",
      "nbTp": 2,
      "nbTd": 1,
      "groupesTp": [
        "A",
        "B"
      ],
      "groupesTd": [
        "AB"
      ],
      "matieres": [
        "WR301",
        "WR302",
        "WR303",
        "WR304"
      ]
    }
  }
}

```

