import bdd.entity as entity
import sqlite3
import src.bdd.orm as orm

connection = sqlite3.connect('init/bdd.db')

a = entity.Aptitudes(3, "alo2", "alo1")
print(a)
a.save(connection)
print(["*"] == ["*"])
l = entity.Aptitudes.read(entity.Aptitudes, connection)
for b in l:
    print(b)

print("------------------------")
# and entre les logic
palu = {
        "logic" : "or",
        "options" : [
            {
                "logic": "and",
                "options": [
                    {
                        "aptitudes_id": 3
                    },
                    {
                        "aptitudes_nom": "alo1"
                    }
                ]
            },
            {
                "aptitudes_nom": "alo"
            }
        ]
    }

print(orm.is_logic(palu))

# => where (id > 0 and name = `alo`) or id = -1
l = entity.Aptitudes.read(entity.Aptitudes, connection, option=palu, order={"aptitudes_id" : "down"})
for b in l:
    print(b)
