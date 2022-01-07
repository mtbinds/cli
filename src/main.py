import bdd.entity as entity
import sqlite3

connection = sqlite3.connect('init/bdd.db')

a = entity.Domaines("alo2", "alo")
print(a)
a.save(connection)
print(["*"] == ["*"])
l = entity.Syllabus.read(entity.Syllabus, connection, option={"syllabus_id" : 0, "syllabus_nom" : "nom"})
for b in l:
    print(b)
