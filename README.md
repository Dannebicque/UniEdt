# Outil de construction des EDT

## Présentation

 ...todo...

## Execution

...todo...

## Schéma des données stockées en fichier JSON

### Fichiers "semaine"

Fichier nommé : `semaine_xx.json`, où xx est le numéro de la semaine (1 à 52).

```json
{
    "week": 1,
    "jours": {
        "Lundi": "02\/09\/2024",
        "Mardi": "03\/09\/2024",
        "Mercredi": "04\/09\/2024",
        "Jeudi": "05\/09\/2024",
        "Vendredi": "06\/09\/2024"
    },
    "days": [
        {
            "day": "Lundi",
            "date": "2024-09-02",
            "dateFr": "02\/09\/2024",
            "isHoliday": false
        },
        {
            "day": "Mardi",
            "date": "2024-09-03",
            "dateFr": "03\/09\/2024",
            "isHoliday": false
        },
        {
            "day": "Mercredi",
            "date": "2024-09-04",
            "dateFr": "04\/09\/2024",
            "isHoliday": false
        },
        {
            "day": "Jeudi",
            "date": "2024-09-05",
            "dateFr": "05\/09\/2024",
            "isHoliday": false
        },
        {
            "day": "Vendredi",
            "date": "2024-09-06",
            "dateFr": "06\/09\/2024",
            "isHoliday": false
        }
    ]
}
```

### Fichiers "Contraintes"

Fichier nommé : `contraintes.json` (fichier unique)

```json
{
    "DAN": [
        {
            "day": "Lundi",
            "creneaux": [1, 2, 3],
            "recurrence": "weekly"
            "type": "indisponibilité"
        },
        {
            "day": "Mardi",
            "creneaux": [1, 2],
            "recurrence": "12/03/2025"
            "type": "indisponibilité"
        }
    ],
    "JBA": [
        {
            "day": "Vendredi",
            "creneaux": [4, 5],
            "recurrence": "weekly",
            "type": "disponibilité"
        }
    ]
}
```

### Fichiers "événements"

Fichier nommé : `evenements.json` (fichier unique)

```json

```

### Fichiers "cours à placer"

Fichier nommé : `cours_xx.json`, xx est le numéro de semaine

```json

```
