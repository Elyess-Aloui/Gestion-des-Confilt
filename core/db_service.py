"""
=============================================================================
 MODULE : db_service.py
 DESCRIPTION : Service de gestion de la Base de Données NoSQL (Documents).
 ARCHITECTURE :
   - Support Hybride : MongoDB natif (via PyMongo) OU Moteur NoSQL JSON local (TinyNoSQL).
   - Relations : Références Manuelles (Manual References) entre collections NoSQL.
=============================================================================
"""

import os
import json
import uuid
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. INITIALISATION & DÉTECTION DE PYMONGO
# ---------------------------------------------------------------------------
HAS_PYMONGO = False
try:
    import pymongo
    HAS_PYMONGO = True
except ImportError:
    HAS_PYMONGO = False

# Répertoire de stockage des fichiers NoSQL au format JSON
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'nosql_data'
DATA_DIR.mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# 2. CLASSE TinyNoSQLCollection : MOTEUR NoSQL ORIENTÉ DOCUMENTS (JSON)
# ---------------------------------------------------------------------------
class TinyNoSQLCollection:
    """
    Simule une collection NoSQL (type MongoDB) sur un fichier JSON local.
    Fournit les opérations CRUD de base : insert_one, find, find_one, update_one, delete_one.
    """
    def __init__(self, name):
        self.name = name
        self.file_path = DATA_DIR / f"{name}.json"
        # Si le fichier de la collection n'existe pas encore, on l'initialise avec une liste vide
        if not self.file_path.exists():
            self._save([])

    def _load(self):
        """Charge l'ensemble des documents JSON depuis le fichier."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []

    def _save(self, data):
        """Persiste la liste des documents JSON dans le fichier avec indentation."""
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def insert_one(self, doc):
        """
        Insère un document dans la collection.
        Génère automatiquement un UUID pour '_id' si non fourni, ainsi qu'une date 'created_at'.
        """
        docs = self._load()
        if '_id' not in doc:
            doc['_id'] = str(uuid.uuid4())
        doc['id'] = str(doc['_id'])
        doc['created_at'] = doc.get('created_at', datetime.now().isoformat())
        docs.append(doc)
        self._save(docs)
        return doc['id']

    def find(self, query=None):
        """
        Recherche des documents correspondant aux filtres donnés (query sous forme de dictionnaire).
        Si query est None, renvoie tous les documents de la collection.
        """
        docs = self._load()
        if not query:
            for d in docs:
                if '_id' in d: d['id'] = str(d['_id'])
            return docs
        result = []
        for d in docs:
            match = True
            for k, v in query.items():
                if d.get(k) != v:
                    match = False
                    break
            if match:
                if '_id' in d: d['id'] = str(d['_id'])
                result.append(d)
        return result

    def find_one(self, query):
        """Recherche et retourne le premier document correspondant au filtre query."""
        results = self.find(query)
        if results:
            doc = results[0]
            if '_id' in doc: doc['id'] = str(doc['_id'])
            return doc
        return None

    def update_one(self, query, update_fields):
        """
        Met à jour le premier document correspondant au filtre query.
        Prend en charge l'opérateur NoSQL standard '$set' ou un dictionnaire direct.
        """
        docs = self._load()
        updated = False
        for d in docs:
            match = True
            for k, v in query.items():
                if d.get(k) != v:
                    match = False
                    break
            if match:
                if '$set' in update_fields:
                    d.update(update_fields['$set'])
                else:
                    d.update(update_fields)
                updated = True
                break
        if updated:
            self._save(docs)
        return updated

    def delete_one(self, query):
        """Supprime le premier document correspondant au filtre query."""
        docs = self._load()
        new_docs = []
        deleted = False
        for d in docs:
            match = True
            for k, v in query.items():
                if d.get(k) != v:
                    match = False
                    break
            if match and not deleted:
                deleted = True
            else:
                new_docs.append(d)
        if deleted:
            self._save(new_docs)
        return deleted


# ---------------------------------------------------------------------------
# 3. GESTIONNAIRE DE CONNEXION NoSQL (Hybride MongoDB / JSON)
# ---------------------------------------------------------------------------
class NoSQLManager:
    """
    Gère la connexion à MongoDB si le serveur est actif,
    ou bascule automatiquement sur le stockage JSON local TinyNoSQL.
    """
    def __init__(self):
        self.use_mongo = False
        self.client = None
        self.db = None
        if HAS_PYMONGO:
            try:
                # Tentative de ping sur le serveur MongoDB local (port 27017)
                self.client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=1000)
                self.client.admin.command('ping')
                self.db = self.client['school_nosql_db']
                self.use_mongo = True
            except Exception:
                # Si MongoDB n'est pas démarré, bascule en mode JSON
                self.use_mongo = False

    def get_collection(self, name):
        """Retourne la collection demandée (soit Wrapper MongoDB, soit TinyNoSQLCollection)."""
        if self.use_mongo:
            return MongoCollectionWrapper(self.db[name])
        return TinyNoSQLCollection(name)


class MongoCollectionWrapper:
    """
    Adaptateur pour la bibliothèque PyMongo afin d'assurer
    une API identique et compatible avec TinyNoSQLCollection.
    """
    def __init__(self, mongo_col):
        self.col = mongo_col

    def insert_one(self, doc):
        if '_id' not in doc:
            doc['_id'] = str(uuid.uuid4())
        doc['id'] = str(doc['_id'])
        doc['created_at'] = doc.get('created_at', datetime.now().isoformat())
        self.col.insert_one(doc)
        return doc['id']

    def find(self, query=None):
        query = query or {}
        res = list(self.col.find(query))
        for d in res:
            if '_id' in d: d['id'] = str(d['_id'])
        return res

    def find_one(self, query):
        doc = self.col.find_one(query)
        if doc and '_id' in doc:
            doc['id'] = str(doc['_id'])
        return doc

    def update_one(self, query, update_fields):
        if '$set' not in update_fields:
            update_fields = {'$set': update_fields}
        res = self.col.update_one(query, update_fields)
        return res.modified_count > 0

    def delete_one(self, query):
        res = self.col.delete_one(query)
        return res.deleted_count > 0


# Instance unique globale du gestionnaire NoSQL
db_manager = NoSQLManager()

def get_db():
    """Accesseur vers l'instance du gestionnaire de base de données."""
    return db_manager


# ---------------------------------------------------------------------------
# 4. ACCESSEURS DE COLLECTIONS NoSQL
# ---------------------------------------------------------------------------

def users_col():
    """Collection 'users' : Comptes utilisateurs et hashs de mots de passe."""
    return db_manager.get_collection('users')

def instituts_col():
    """Collection 'instituts' : Établissements scolaires (nom, région, ville)."""
    return db_manager.get_collection('instituts')

def salles_col():
    """Collection 'salles' : Salles de cours, type, état de panne et durée."""
    return db_manager.get_collection('salles')

def matieres_col():
    """Collection 'matieres' : Liste des matières enseignées (Maths, Physique...)."""
    col = db_manager.get_collection('matieres')
    # Si la collection est vide, initialisation automatique avec les matières par défaut
    if not col.find():
        from .models import MATIERES_PAR_DEFAUT
        for nom in MATIERES_PAR_DEFAUT:
            col.insert_one({
                'nom': nom,
                'niveaux': ['1', '2', '3', '4', '5', '6'],
                'volume_horaire': 4
            })
    return col

def get_all_matieres():
    """
    Récupère toutes les matières et formate l'affichage des niveaux.
    """
    matieres = matieres_col().find()
    for m in matieres:
        m['niveaux'] = m.get('niveaux', ['1', '2'])
        if isinstance(m['niveaux'], str):
            m['niveaux'] = [n.strip() for n in m['niveaux'].split(',') if n.strip()]
        # Formater les niveaux pour affichage lisible
        m['niveaux_display'] = ", ".join([f"Niveau {n}" for n in m['niveaux']])
        m['volume_horaire'] = m.get('volume_horaire', 4)
    return matieres


def enseignants_col():
    """Collection 'enseignants' : Enseignants, lien institut_id, matière et planning."""
    return db_manager.get_collection('enseignants')

def classes_col():
    """Collection 'classes' : Classes, lien institut_id et niveau scolaire."""
    return db_manager.get_collection('classes')

def emplois_du_temps_col():
    """Collection 'emplois_du_temps' : Plannings hebdomadaires des classes."""
    return db_manager.get_collection('emplois_du_temps')

def emplois_du_temps_enseignants_col():
    """Collection 'emplois_du_temps_enseignants' : Plannings manuels des enseignants."""
    return db_manager.get_collection('emplois_du_temps_enseignants')

def absence_claims_col():
    """Collection 'absence_claims' : Réclamations d'absence déposées par les enseignants."""
    return db_manager.get_collection('absence_claims')


# ---------------------------------------------------------------------------
# 5. RÉSOLUTEURS DE RÉFÉRENCES MANUELLES (Manual References / Link Resolvers)
# ---------------------------------------------------------------------------
# En NoSQL orienté documents, il n'y a pas de jointures SQL ('JOIN').
# Les fonctions ci-dessous réalisent la jointure applicative entre documents.

def resolve_institut(institut_id):
    """
    Récupère le document complet d'un institut à partir de son identifiant '_id'.
    """
    if not institut_id:
        return None
    return instituts_col().find_one({'_id': institut_id})

def get_enseignants_for_institut(institut_id):
    """
    Jointure NoSQL Enseignants <-> Institut & Emploi du Temps :
    1. Récupère tous les enseignants ayant 'institut_id' = institut_id.
    2. Récupère l'institut correspondant et l'attache au document enseignant.
    3. Attache le nombre de séances configurées dans son emploi du temps manuel.
    """
    enseignants = enseignants_col().find({'institut_id': institut_id})
    inst = resolve_institut(institut_id)
    emplois = {emp['teacher_id']: emp for emp in emplois_du_temps_enseignants_col().find()}
    for e in enseignants:
        e['institut'] = inst
        e['niveaux'] = e.get('niveaux', 'Niveau 1, Niveau 2')
        e['volume_horaire'] = e.get('volume_horaire', 18)
        emp = emplois.get(e['id'])
        e['emploi_du_temps'] = emp
        nb_seances = 0
        if emp and isinstance(emp.get('seances'), dict):
            for jour, slots in emp['seances'].items():
                if isinstance(slots, dict):
                    for slot_key, data in slots.items():
                        if isinstance(data, dict) and (data.get('classe_id') or data.get('matiere_id') or data.get('salle_id')):
                            nb_seances += 1
        e['nb_seances'] = nb_seances
    return enseignants

def get_salles_for_institut(institut_id):
    """
    Jointure NoSQL Salles <-> Institut :
    1. Récupère les salles de l'école (institut_id).
    2. Attache les informations de l'institut.
    3. Ajoute un libellé formaté pour le type de salle et garantit 'capacite'.
    """
    salles = salles_col().find({'institut_id': institut_id})
    inst = resolve_institut(institut_id)
    type_dict = {
        'normale': 'Salle de classe (normale)',
        'informatique': 'Salle informatique',
        'sport': 'Salle de sport'
    }
    for s in salles:
        s['institut'] = inst
        s['type_display'] = type_dict.get(s.get('type', 'normale'), 'Normale')
        s['capacite'] = s.get('capacite', 30)
    return salles

def get_classes_for_institut(institut_id):
    """
    Jointure NoSQL Classes <-> Institut & Emploi du Temps :
    1. Récupère les classes associées à l'institut.
    2. Attache les données de l'école.
    3. Associe l'emploi du temps de chaque classe depuis la collection 'emplois_du_temps'.
    """
    classes_list = classes_col().find({'institut_id': institut_id})
    inst = resolve_institut(institut_id)
    emplois = {emp['classe_id']: emp for emp in emplois_du_temps_col().find()}
    for c in classes_list:
        c['institut'] = inst
        c['niveau_display'] = f"Niveau {c.get('niveau')}"
        emp = emplois.get(c['id'])
        c['emploi_du_temps'] = emp
        # Compter les séances programmées
        nb_seances = 0
        if emp and isinstance(emp.get('seances'), dict):
            for jour, slots in emp['seances'].items():
                if isinstance(slots, dict):
                    for slot_key, data in slots.items():
                        if isinstance(data, dict) and (data.get('matiere_id') or data.get('enseignant_id') or data.get('salle_id')):
                            nb_seances += 1
        c['nb_seances'] = nb_seances
    return classes_list


def get_classe_timetable(classe_id):
    """Récupère l'emploi du temps d'une classe."""
    emp = emplois_du_temps_col().find_one({'classe_id': classe_id})
    if not emp:
        return {'classe_id': classe_id, 'seances': {}, 'commentaire': ''}
    return emp


def save_classe_timetable(classe_id, seances, commentaire=''):
    """Enregistre ou met à jour l'emploi du temps d'une classe."""
    col = emplois_du_temps_col()
    existing = col.find_one({'classe_id': classe_id})
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    if existing:
        col.update_one(
            {'classe_id': classe_id},
            {
                'seances': seances,
                'commentaire': commentaire,
                'date_modification': now_str
            }
        )
    else:
        col.insert_one({
            'classe_id': classe_id,
            'seances': seances,
            'commentaire': commentaire,
            'date_modification': now_str
        })


def get_populated_classe_timetable(classe_id):
    """
    Récupère l'emploi du temps d'une classe avec les noms/objets complets
    de la matière, de l'enseignant et de la salle pour chaque séance.
    """
    emp = get_classe_timetable(classe_id)
    seances_raw = emp.get('seances', {})

    # Mappages pour résolution rapide
    matieres_map = {m['id']: m for m in matieres_col().find()}
    teachers_map = {t['id']: t for t in enseignants_col().find()}
    salles_map = {s['id']: s for s in salles_col().find()}

    populated_seances = {}
    for jour, slots in seances_raw.items():
        populated_seances[jour] = {}
        if isinstance(slots, dict):
            for slot_key, slot_val in slots.items():
                if isinstance(slot_val, dict):
                    m_id = slot_val.get('matiere_id', '')
                    t_id = slot_val.get('enseignant_id', '')
                    s_id = slot_val.get('salle_id', '')

                    matiere = matieres_map.get(m_id)
                    teacher = teachers_map.get(t_id)
                    salle = salles_map.get(s_id)

                    populated_seances[jour][slot_key] = {
                        'matiere_id': m_id,
                        'enseignant_id': t_id,
                        'salle_id': s_id,
                        'matiere': matiere,
                        'matiere_nom': matiere.get('nom') if matiere else '',
                        'enseignant': teacher,
                        'enseignant_nom': teacher.get('nom') if teacher else '',
                        'salle': salle,
                        'salle_numero': salle.get('numero') if salle else '',
                    }

    return {
        'classe_id': classe_id,
        'seances': populated_seances,
        'commentaire': emp.get('commentaire', ''),
        'date_modification': emp.get('date_modification', '')
    }


def get_teacher_timetable(teacher_id):
    """Récupère l'emploi du temps manuel d'un enseignant."""
    emp = emplois_du_temps_enseignants_col().find_one({'teacher_id': teacher_id})
    if not emp:
        return {'teacher_id': teacher_id, 'seances': {}, 'commentaire': ''}
    return emp


def save_teacher_timetable(teacher_id, seances, commentaire=''):
    """Enregistre ou met à jour l'emploi du temps manuel d'un enseignant."""
    col = emplois_du_temps_enseignants_col()
    existing = col.find_one({'teacher_id': teacher_id})
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    if existing:
        col.update_one(
            {'teacher_id': teacher_id},
            {
                'seances': seances,
                'commentaire': commentaire,
                'date_modification': now_str
            }
        )
    else:
        col.insert_one({
            'teacher_id': teacher_id,
            'seances': seances,
            'commentaire': commentaire,
            'date_modification': now_str
        })


def get_populated_teacher_timetable(teacher_id, school_id):
    """
    Récupère l'emploi du temps manuel d'un enseignant avec les détails
    de la classe, de la matière et de la salle pour chaque séance.
    """
    emp = get_teacher_timetable(teacher_id)
    seances_raw = emp.get('seances', {})

    classes_in_school = classes_col().find({'institut_id': school_id})
    classes_map = {c['id']: c for c in classes_in_school}
    matieres_map = {m['id']: m for m in matieres_col().find()}
    salles_map = {s['id']: s for s in salles_col().find()}

    populated_seances = {}
    for jour, slots in seances_raw.items():
        populated_seances[jour] = {}
        if isinstance(slots, dict):
            for slot_key, slot_val in slots.items():
                if isinstance(slot_val, dict):
                    c_id = slot_val.get('classe_id', '')
                    m_id = slot_val.get('matiere_id', '')
                    s_id = slot_val.get('salle_id', '')

                    classe = classes_map.get(c_id)
                    matiere = matieres_map.get(m_id)
                    salle = salles_map.get(s_id)

                    populated_seances[jour][slot_key] = {
                        'classe_id': c_id,
                        'matiere_id': m_id,
                        'salle_id': s_id,
                        'classe': classe,
                        'classe_nom': f"Niveau {classe.get('niveau')} - {classe.get('nom')}" if classe else '',
                        'matiere': matiere,
                        'matiere_nom': matiere.get('nom') if matiere else '',
                        'salle': salle,
                        'salle_numero': salle.get('numero') if salle else '',
                    }

    return {
        'teacher_id': teacher_id,
        'seances': populated_seances,
        'commentaire': emp.get('commentaire', ''),
        'date_modification': emp.get('date_modification', '')
    }


def get_enseignant_timetable(teacher_id, school_id):
    """Alias / compatibilité pour get_populated_teacher_timetable."""
    pop = get_populated_teacher_timetable(teacher_id, school_id)
    return pop.get('seances', {})

def get_latest_conflict_report():
    """Récupère le dernier rapport de conflits sauvegardé (par n8n ou manuel)."""
    col = db_manager.get_collection('conflict_reports')
    return col.find_one({'_id': 'latest'})


def save_conflict_report(report):
    """Sauvegarde/écrase le dernier rapport de conflits."""
    col = db_manager.get_collection('conflict_reports')
    existing = col.find_one({'_id': 'latest'})
    if existing:
        col.update_one({'_id': 'latest'}, report)
    else:
        report['_id'] = 'latest'
        col.insert_one(report)
