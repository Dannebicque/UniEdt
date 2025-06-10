from fastapi import APIRouter
from ..lib.data_loader import load_json
from ..models import Professor

router = APIRouter(prefix="/intervenants", tags=["Intervenants"])

@router.get("")
async def list_professors():
    # Exemple de lecture du fichier
    data = load_json("contraintes")

    # Transformation
    enseignants = [
        {"key": key, "name": value["name"], "email": value["email"]}
        for key, value in data.items()
    ]

    # Résultat en JSON
    return enseignants
    #profs: list[dict] = load_json("contraintes")
    #return [Professor(**p) for p in profs]
