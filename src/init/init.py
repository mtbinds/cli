import sqlite3

connection = sqlite3.connect('bdd.db')
cursor = connection.cursor()
sql_file = open("init.sql")
sql_as_string = sql_file.read()
cursor.executescript(sql_as_string)
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(cursor.fetchall())
