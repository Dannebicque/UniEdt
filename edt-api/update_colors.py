import json
from pathlib import Path

def load_semester_colors():
    data_globale_path = Path(__file__).resolve().parent.parent / "data" / "data_globale.json"
    with open(data_globale_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {k: v["color"] for k, v in data["semesters"].items() if "color" in v}

def main():
    semester_colors = load_semester_colors()
    data_dir = Path(__file__).resolve().parent.parent / "data" / "cours"
    for file in data_dir.glob("*.json"):
        with open(file, "r", encoding="utf-8") as f:
            try:
                courses = json.load(f)
            except Exception as e:
                print(f"Erreur lecture {file}: {e}")
                continue

        changed = False
        for course in courses:
            semestre = course.get("semester")
            color = semester_colors.get(semestre, "#CCCCCC")
            if course.get("color") != color:
                course["color"] = color
                changed = True

        if changed:
            with open(file, "w", encoding="utf-8") as f:
                json.dump(courses, f, ensure_ascii=False, indent=2)
            print(f"Fichier mis à jour: {file}")

if __name__ == "__main__":
    main()