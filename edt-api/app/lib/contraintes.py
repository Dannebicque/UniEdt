def contraintes_par_semaine(data: dict, week_number: int) -> dict:
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
    creneaux = range(1, 7)
    result = {}

    for prof, value in data.items():
        contraintes = value.get("availability", [])
        # Cherche s'il y a des contraintes "disponible" pour la semaine
        dispo = [c for c in contraintes if (int(c.get("week")) == week_number or int(c.get("week")) == 99) and c.get("status") == "disponible"]
        indispo = [c for c in contraintes if (int(c.get("week")) == week_number or int(c.get("week")) == 99) and c.get("status") == "indisponible"]

        # Par défaut, tout est disponible sauf si "disponible" existe
        if dispo:
            # Tout est indisponible sauf les créneaux explicitement disponibles
            tableau = {jour: {c: True for c in creneaux} for jour in jours}
            for c in dispo:
                jour = c.get("day", "")
                if jour in jours:
                    for slot in c.get("creneaux", []):
                        if slot in creneaux:
                            tableau[jour][slot] = False
        else:
            # Tout est disponible, on ne bloque que les créneaux explicitement indisponibles
            tableau = {jour: {c: False for c in creneaux} for jour in jours}

        # Les indisponibilités prennent le dessus
        for c in indispo:
            jour = c.get("day", "")
            if jour in jours:
                for slot in c.get("creneaux", []):
                    if slot in creneaux:
                        tableau[jour][slot] = True

        result[prof] = tableau
    return result


    # result = {}
    # for key, value in data.items():
    #     contraintes = value.get("availability", [])
    #
    #     #triater le cas disponible, calculer les jours et créneaux d'indisponibilité en conséquence
    #
    #
    #     result[key] = {}
    #     for c in contraintes:
    #         if c.get("week") == week_number or c.get("week") == 99:
    #             day = c.get("day", '')
    #             if day not in result[key]:
    #                 result[key][day] = {}
    #             for slot in c.get("creneaux", []):
    #                 result[key][day][slot] = c.get("commentaire") or "blocked"
    # return result