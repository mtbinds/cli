import bdd.entity as entity
import sqlite3

connection = sqlite3.connect('init/bdd.db')

a = entity.Domaines("alo2", "alo")
print(a)
a.save(connection)
print(["*"] == ["*"])
l = entity.Domaines.real_all(entity.Domaines, connection)
for b in l:
    print(b)

syl = entity.Syllabus(0, "nom", "pr17262")
syl.save(connection)
l = entity.Syllabus.read(entity.Syllabus, connection)
for b in l:
    print(b)
