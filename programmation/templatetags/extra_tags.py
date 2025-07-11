from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    if dictionary is None:
        return None
    if isinstance(dictionary, dict):
        return dictionary.get(key, None)
    return None

@register.filter
def disponibilite_color(nb_dispo):
    if nb_dispo is None:
        return ""
    try:
        nb_dispo = int(nb_dispo)
    except (ValueError, TypeError):
        return ""
    if nb_dispo >= 25:
        return ""
    elif nb_dispo >= 19:
        return "background-color: #f2f2f2;"  # gris très clair
    elif nb_dispo >= 13:
        return "background-color: #d9d9d9;"  # gris clair
    elif nb_dispo >= 7:
        return "background-color: #bfbfbf;"  # gris moyen
    elif nb_dispo >= 1:
        return "background-color: #808080; color: white;"  # gris foncé
    else:
        return "background-color: black; color: red;"  # noir + texte rouge

