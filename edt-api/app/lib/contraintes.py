def contraintes_par_semaine(data: dict, week_number: int) -> dict:
    result = {}
    for key, value in data.items():
        contraintes = value.get("availability", [])
        result[key] = {}
        for c in contraintes:
            if c.get("week") == week_number or c.get("week") == 99:
                day = c.get("day", '')
                if day not in result[key]:
                    result[key][day] = {}
                for slot in c.get("creneaux", []):
                    result[key][day][slot] = c.get("commentaire") or "blocked"
    return result