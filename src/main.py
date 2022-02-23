import sqlite3
from pathlib import Path

from src.bdd.orm import connect
from src.command import *

root = Path(__file__).parent
print(root)
if __name__ == '__main__':
    connect(sqlite3.connect(str(root) + '/init/bdd.db'))
    e = Etudiant("1", "test1", "test2")
    etu = Etudiant("2", "test1", "test2")
    etu.save()
    s = Syllabus(0, "syl1", e)
    '''
    print(s)
    '''
    s.save()
    l = Syllabus.read(Syllabus, link=True)
    '''
    for b in l:
        print(b)
    '''
    manager = CommandManager()

    c_help = Command("help")
    c_student = Command("student")
    c_competences = Command("competence")
    c_domaines = Command("domaine")
    c_evaluations = Command("evaluation")
    c_matieres = Command("matiere")
    c_syllabus = Command("syllabus")
    c_validations = Command("validation")

    c1 = Command({
        "names": ["menfou"],
        "regex": "\w+",
        "description": "palu menfou",
        "visible": True
    })

    manager.register_command(c_help, help_command)
    manager.register_command(c_student, student_command)
    manager.register_command(c_competences, competence_command)
    manager.register_command(c_domaines, domaine_command)
    manager.register_command(c_evaluations, evaluation_command)
    manager.register_command(c_matieres, matiere_command)
    manager.register_command(c_syllabus, syllabus_command)
    manager.register_command(c_validations, validation_command)
    manager.register_command(c1)

    print("========================================")
    '''
    Gestion des Command Line Arguments
    '''
    if(len(sys.argv) > 1) :
        manager.exec_command(sys.argv[1])
    else :
        print('Not enough arguments, please try again as follow : py command.py [command] [parameter(s)]')