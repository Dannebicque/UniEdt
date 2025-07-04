from typing import List, Optional, Dict, Union
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
    name: str
    email: EmailStr
    service: int
    type: str  # "permanent" ou "vacataire"
    availability: List[Availability]

# Pour le fichier contraintes.json (dictionnaire de professeurs)
ProfessorsFile = Dict[str, Professor]

# --- Événements ---
class Event(BaseModel):
    id: int
    name: str
    date: str  # Format ISO
    time: str  # "HH:MM"
    creneaux: List[int]
    location: str
    description: Optional[str]
    semaine: int
    semester: str

# --- Cours à placer ---
class CourseToPlace(BaseModel):
    id: int
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
    code: int
    nom: str
    date: str  # Format ISO: YYYY-MM-DD
    jour: str  # "HH:MM"
    creneaux: List[int]
    room: Optional[str] = None
    description: Optional[str]
    semaine: int
    semestre: str

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