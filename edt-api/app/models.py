from typing import List, Optional, Dict, Union, Literal
from pydantic import BaseModel, EmailStr

# --- Semaine ---
class Day(BaseModel):
    day: str
    date: str  # Format ISO: YYYY-MM-DD
    isHoliday: bool

class WeekFile(BaseModel):
    week: int
    days: List[Day]
    semesters: List[str]  # Liste des semestres associés à cette semaine

# --- Contraintes / Professeurs ---
class Availability(BaseModel):
    day: str
    creneaux: List[int]
    recurrence: str  # "weekly" ou date ISO
    status: str  # "disponible" ou "indisponible"

class Professor(BaseModel):
    key: str
    name: str
    email: EmailStr
    service: int
    type: str  # "permanent" ou "vacataire"
    availability: Optional[List[Availability]]

# Pour le fichier contraintes.json (dictionnaire de professeurs)
ProfessorsFile = Dict[str, Professor]

class UpdateTypeRequest(BaseModel):
    type: Literal["jour", "creneau"]
    jour: str
    semestre: str
    semaine: int
    nouveauType: str
    creneau: Optional[int] = None

    def get_creneaux(self) -> List[int]:
        if self.type == "jour":
            return [1, 2, 3, 4, 5, 6]
        elif self.type == "creneau" and self.creneau:
            return [self.creneau]
        return []

# --- Événements ---
class Event(BaseModel):
    code: str
    nom: str
    date: Optional[str]  # Format ISO
    creneaux: List[int]
    description: Optional[str]
    semaine: int
    semestre: str
    type: str  # "FIXE", "INFO", "BLOQUANT"
    jour: str

# --- Cours à placer ---
class CourseToPlace(BaseModel):
    id: Union[str, int]
    matiere: str
    professor: str
    semester: str
    groupIndex: int
    type: str = "CM"
    isVacataire: bool = False
    groupCount: Optional[int]
    date: Optional[str]
    creneau: Optional[int]
    room: Optional[str]
    color: Optional[str]
    blocked: bool = False

# --- Cours à placer ---
class EventToPlace(BaseModel):
    code: str
    nom: str
    date: Optional[str]  # Format ISO: YYYY-MM-DD
    jour: str  # "HH:MM"
    creneaux: List[int]
    room: Optional[str] = None
    description: Optional[str]
    semaine: int
    semestre: str
    type: str

# --- Salles ---
class SalleAffectation(BaseModel):
    td: Optional[str]
    tp: Optional[str]

class SallesFile(BaseModel):
    PGO: SalleAffectation
    RHU: SalleAffectation
    CM: List[str]
    TD: List[str]
    TP: List[str]