import bdd.entity as entity
import sqlite3

connection = sqlite3.connect('init/bdd.db')

a = entity.Domaines("alo2", "alo")
print(a)
a.save(connection)
print(["*"] == ["*"])
l = entity.Syllabus.read(entity.Syllabus, connection,
                         option={"syllabus_id" : {"min" : 0, "max" : 3, "equals" : True}, "syllabus_nom" : "nom",
                                 "order" : {"syllabus_id" : "up", "syllabus_nom" : "down"}})
for b in l:
    print(b)
