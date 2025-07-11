# programmation/utils/mappings.py

SEMESTRE_MAPPING = {
    ('S1', 'BUT1'): "S1",
    ('S3', 'DEV-FI'): "S3-DEV-FI",
    ('S3', 'DEV-FC'): "S3-DEV-FC",
    ('S3', 'CREACOM'): "S3-COMM",
    ('S5', 'DEV-FI'): "S5-DEV-FI",
    ('S5', 'DEV-FC'): "S5-DEV-FC",
    ('S5', 'CREACOM'): "S5-COMM",
}
GROUPE_MAPPING = {
    "A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8,
    "AB": 1, "CD": 3, "EF": 5, "GH": 7, "ALL": 1
}
TYPE_TO_GROUPCOUNT = {
    "TP": lambda sem: 1,
    "TD": lambda sem: 2,
    "CM": lambda sem: 8 if sem == "S1" else 4
}
COLOR_MAPPING = {
    "BUT1": "#FF5733",
    "S3-DEV-FI": "#026613", "S3-DEV-FC": "#4AB05C", "S3-COMM": "#4AB05C",
    "S5-DEV-FI": "#112997", "S5-DEV-FC": "#4258C0", "S5-COMM": "#4258C0",
}
