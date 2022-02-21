import sqlite3
import sys

from src.bdd.entity import Etudiant, Syllabus
from src.bdd.orm import connect
from src.command import Command, CommandManager, help_command, student_command

if __name__ == '__main__':
    connect(sqlite3.connect('init/bdd.db'))

    e = Etudiant("1", "test1", "test2")
    etu = Etudiant("2", "test1", "test2")
    etu.save()
    s = Syllabus(0, "syl1", e)
    print(s)

    s.save()
    print(["*"] == ["*"])
    l = Syllabus.read(Syllabus, link=True)
    for b in l:
        print(b)

    manager = CommandManager()

    c_help = Command("help")
    c_student = Command("student")

    c1 = Command({
        "names": ["menfou"],
        "regex": "\w+",
        "description": "palu menfou",
        "visible": True
    })

    manager.register_command(c_help, help_command)
    manager.register_command(c_student, student_command)
    manager.register_command(c1)
    if len(sys.argv) > 1:
        manager.exec_command(sys.argv[1])
