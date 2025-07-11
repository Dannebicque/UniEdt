from django import template

register = template.Library()

@register.filter(name="creneau_label")
def creneau_label(index):
    mapping = {
        1: "08h00",
        2: "09h30",
        3: "11h00",
        4: "14h00",
        5: "15h30",
        6: "17h00"
    }
    return mapping.get(index, f"C{index}")
