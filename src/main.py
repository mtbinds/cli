import sqlite3

from src.bdd.entity import Etudiant, Syllabus
from src.bdd.orm import connect

connect(sqlite3.connect('init/bdd.db'))

e = Etudiant("1", "test1", "test2")
s = Syllabus(0, "syl1", e)
print(s)

s.save()
print(["*"] == ["*"])
l = Syllabus.read(Syllabus, link=True)
for b in l:
    print(b)
