from fastapi import APIRouter
from ..lib.data_loader import load_json, save_json
from ..lib.contraintes import contraintes_par_semaine
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

@router.get("/contraintes/{week_number}")
async def list_contraintes_professors(week_number: int):
    # Exemple de lecture du fichier
    data = load_json("contraintes")

    result = contraintes_par_semaine(data, week_number)

    # Résultat en JSON
    return result

@router.get("/complet")
async def list_complet_professors():
    # Exemple de lecture du fichier
    data = load_json("contraintes")

    # Résultat en JSON
    return data

@router.put("/{intervenant_id}/update", response_model=Professor)
async def update_professor(intervenant_id: str, updated_data: Professor):
    # Exemple de mise à jour d'un intervenant
    data = load_json("contraintes")

    if intervenant_id not in data:
        raise HTTPException(status_code=404, detail="Intervenant not found")

    # Mettre à jour les données de l'intervenant
    data[intervenant_id].update(updated_data.dict())

    # Enregistrer les modifications (à implémenter)
    save_json("contraintes", data)

    return Professor(**data[intervenant_id])

@router.post("/add", response_model=Professor)
async def add_professor(new_professor: Professor):
    # Exemple d'ajout d'un nouvel intervenant
    data = load_json("contraintes")

    # Ajouter le nouvel intervenant
    data[new_professor.key] = new_professor.dict()

    # Enregistrer les modifications (à implémenter)
    save_json("contraintes", data)

    return Professor(**data[new_professor.key])
