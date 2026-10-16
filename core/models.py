"""
Core Data Schemas and Collections for Institut, Salle, Matiere, Enseignant, Classe, and EmploiDuTemps.
"""
from dataclasses import dataclass
from typing import Optional

GOUVERNORATS = [
    ('tunis', 'Tunis'),
    ('ariana', 'Ariana'),
    ('ben_arous', 'Ben Arous'),
    ('manouba', 'Manouba'),
    ('nabeul', 'Nabeul'),
    ('zaghouan', 'Zaghouan'),
    ('bizerte', 'Bizerte'),
    ('beja', 'Béja'),
    ('jendouba', 'Jendouba'),
    ('kef', 'Le Kef'),
    ('siliana', 'Siliana'),
    ('sousse', 'Sousse'),
    ('monastir', 'Monastir'),
    ('mahdia', 'Mahdia'),
    ('sfax', 'Sfax'),
    ('kairouan', 'Kairouan'),
    ('kasserine', 'Kasserine'),
    ('sidi_bouzid', 'Sidi Bouzid'),
    ('gabes', 'Gabès'),
    ('medenine', 'Médenine'),
    ('tataouine', 'Tataouine'),
    ('gafsa', 'Gafsa'),
    ('tozeur', 'Tozeur'),
    ('kebili', 'Kébili'),
]

NIVEAUX = [(i, f"Niveau {i}") for i in range(1, 7)]

SALLE_TYPES = [
    ('normale', 'Salle de classe (normale)'),
    ('informatique', 'Salle informatique'),
    ('sport', 'Salle de sport'),
]

MATIERES_PAR_DEFAUT = [
    "Français",
    "Mathématiques",
    "Sciences",
    "Histoire & Géographie",
    "Anglais",
    "Arts",
    "Sport",
    "Informatique",
]

JOURS_SEMAINE = [
    ('lundi', 'Lundi'),
    ('mardi', 'Mardi'),
    ('mercredi', 'Mercredi'),
    ('jeudi', 'Jeudi'),
    ('vendredi', 'Vendredi'),
    ('samedi', 'Samedi'),
]

CRENEAUX_HORAIRES = [
    ('08h00 - 10h00', '08h00 - 10h00'),
    ('10h15 - 12h15', '10h15 - 12h15'),
    ('14h00 - 16h00', '14h00 - 16h00'),
    ('16h15 - 18h00', '16h15 - 18h00'),
]

@dataclass
class Institut:
    id: str
    nom: str
    region: str
    ville: str
    date_creation: str

@dataclass
class Salle:
    id: str
    institut_id: str
    numero: str
    type: str = 'normale'
    is_broken: bool = False
    broken_duration: str = ''

@dataclass
class Matiere:
    id: str
    nom: str
    niveaux: list
    volume_horaire: int = 4

@dataclass
class Enseignant:
    id: str
    institut_id: str
    nom: str
    matiere_id: Optional[str] = None
    schedule_text: str = ''

@dataclass
class Classe:
    id: str
    institut_id: str
    niveau: int
    nom: str

@dataclass
class EmploiDuTemps:
    id: str
    classe_id: str
    seances: dict
    date_modification: str = ''
    commentaire: str = ''
