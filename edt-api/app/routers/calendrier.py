from fastapi import APIRouter, HTTPException
from ..lib.data_loader import load_json, save_json
from ..models import UpdateTypeRequest, Event
from uuid import uuid4

router = APIRouter(prefix="/calendrier", tags=["Events"])

@router.post("/updateType", response_model=list[int])
async def update_type(req: UpdateTypeRequest):
    events = load_json('events')
    creneaux = req.get_creneaux()
    updated = False

    for event in events:
        if (
            event["jour"] == req.jour
            and event["semester"] == req.semestre
            and event["semaine"] == req.semaine
            and any(c in event["creneaux"] for c in creneaux)
        ):
            event["nom"] = req.nouveauType
            updated = True

    if not updated:
        # Ajoute un nouvel événement si aucun n’a été mis à jour
        new_event = Event(
            id= str(uuid4()), # id clé aléatoire unique à générer,
            nom=req.nouveauType,
            type="FIXE",
            semaine=req.semaine,
            jour=req.jour,
            creneaux=creneaux,
            date="",
            semester=req.semestre,
            description=None,
        )
        events.append(new_event.dict())

    save_events(events)
    return creneaux

def save_events(events):
    # On filtre les événements dont le nom n'est pas vide
    events = [event for event in events if event.get('nom')]
    save_json('events', events)