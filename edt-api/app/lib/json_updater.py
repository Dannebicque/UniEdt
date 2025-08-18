import json
from typing import Any, Dict, List, Union

class JsonUpdater:
    def __init__(self, filepath: str):
        self.filepath = filepath
        with open(filepath, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

    def update_by_key(self, key: str, updates: Dict[str, Any]) -> bool:
        """Met à jour les valeurs d'un élément identifié par sa clé (ex: 'DAN')."""
        if key in self.data:
            self.data[key].update(updates)
            self._save()
            return True
        return False

    def update_by_field(self, field: str, value: Any, updates: Dict[str, Any]) -> int:
        """Met à jour les objets d'une liste où field == value."""
        if not isinstance(self.data, list):
            return 0
        count = 0
        for obj in self.data:
            if str(obj.get(field)) == str(value):
                print(f"Updating {field}={value} in {obj}")
                obj.update(updates)
                count += 1
        if count:
            self._save()
        return count

    def _save(self):
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def init_creneau_date(self, course_id):
        # met le créneau et la date à null pour le cours course_id
        if not isinstance(self.data, list):
            return 0
        count = 0
        for course in self.data:
            if str(course.get("id")) == str(course_id):
                course["creneau"] = None
                course["date"] = None
                count += 1

        if count:
            self._save()
        return count


