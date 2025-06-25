import sys
import json
from pathlib import Path

from app.lib.assignRooms import assign_rooms_to_week
from app.lib.paths import get_data_dir

def main():
    if len(sys.argv) != 2:
        print("Usage: python test_assign_rooms.py <week_number>")
        sys.exit(1)

    week_number = sys.argv[1]
    data_path = get_data_dir() / f"cours/cours_{week_number}.json"
    salles_path = get_data_dir() / "salles.json"
    try:
        with open(data_path, "r", encoding="utf-8") as f:
            courses = json.load(f)
        with open(salles_path, "r", encoding="utf-8") as f:
            salles = json.load(f)
    except Exception as e:
        print(f"Erreur de lecture: {e}")
        sys.exit(1)

    updated_courses = assign_rooms_to_week(courses, salles)

    print(json.dumps(updated_courses, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()