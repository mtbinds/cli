import sqlite3

from src.bdd.entity import Competences, Etudiant, Enseignant, Domaines, Evaluations, Aptitudes, Matieres, SyllabusMatieres, Syllabus, Validations
from src.bdd.orm import connect

def insert(Entity, *args):
    e = Entity(*args)
    e.save()
    print(Entity.__name__ + " inserted !");  

def select_all(Entity):
    rows = Entity.read_all(Entity)

    for row in rows:
        print(row)

if __name__ == '__main__':
    # Database connection
    database = 'init/bdd.db'
    connect(sqlite3.connect(database))

    # Insert
    insert(Etudiant, "1", "Musk", "Elon")
    insert(Syllabus, "1", "formation_initiale", "1")
    insert(Enseignant, "1", "Pigne", "Yohann")
    insert(Domaines, "1", "D1")
    insert(Competences, "1", "1", "C4", 1)
    insert(Aptitudes, 1, "1", "C4")
    insert(Matieres, 1, 1, 1) # Erreur ici, matiere_nom devrait etre un string
    insert(SyllabusMatieres, 1, 1)
    insert(Evaluations, 1, 1, 1, "Maîtriser l’écriture des tests et la couverture du code")
    insert(Validations, 1, 1, 1, 1, 3)

    # Select
    select_all(Etudiant)
    select_all(Syllabus)
    select_all(Enseignant)
    select_all(Domaines)
    select_all(Competences)
    select_all(Aptitudes)
    select_all(Matieres)
    select_all(Evaluations)
    select_all(Validations)