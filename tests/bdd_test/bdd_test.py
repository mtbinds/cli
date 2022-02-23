# ------------------------------------------------
# Imports
# ------------------------------------------------
import datetime
import sqlite3
import sys
import traceback
from pathlib import Path
from sqlite3 import Error


# Répertoire Root
def get_project_root() -> Path:
    return Path(__file__).parent.parent.parent


root = get_project_root()


# ---------------------------------------------------
# Définissons maintenant quelques fonctions pour l'accès à la base de données SQLite
# ---------------------------------------------------
def create_connection(db_file):
    # -------------------------------------------------------
    """ Créer une connexion à une base de données SQLite
    :param db_file: Nom/chemin du fichier de base de données SQLite
    :return: Connexion ou Aucune en cas d'erreur.
    """
    # -------------------------------------------------------

    conn = None

    # Essayons d'ouvrir la base de données. Se créera automatiquement s'il n'est pas trouvé.
    try:
        conn = sqlite3.connect(db_file)
        # print(sqlite3.version) #pyselite version
        # print(sqlite3.sqlite_version) #SQLLite engine version
        return conn
    except Error as e:
        print(e)
        return None


def close_connection(conn):
    # -------------------------------------------------------
    """ Fermer une connexion de base de données à une base de données SQLite
    :param conn: Param de connexion
    :return: True-Success, False-Error
    """
    # -------------------------------------------------------

    # Essayons de fermer notre connexion à la base de données
    try:
        conn.close()
        return True;
    except Error as e:
        print(e)
        return False


def create_table(conn, create_table_sql):
    # ----------------------------------------------------------
    """
     créer une table à partir de create_table_sql
    :param conn: Param de connexion
    :param create_table_sql: type CREATE TABLE
    :return: True-Success, False-Error
    """
    # ----------------------------------------------------------
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
        return True
    except Error as e:
        print(e)
        return False


def execute(conn, sql):
    # ----------------------------------------------------------
    """ Exécuter une requête d'action SQL qui ne renvoie pas de résultats
    :param conn: Param de connexion
    :param sql: Requête d'action SQL
    :return: True-Success, False-Error
    """
    # ----------------------------------------------------------
    try:
        c = conn.cursor()
        c.execute(sql)
        return True
    except Error as e:
        print(e)
        return False


def execute_query(conn, sql):
    # ----------------------------------------------------------
    """ Exécuter une requête SQL qui renvoie des résultats
    :param conn: Param de connexion
    :param sql: Requête SQL en attente de résultats
    :return: Curseur résultant ou Aucun
    """
    # ----------------------------------------------------------
    try:
        c = conn.cursor()
        c.execute(sql)
        return c
    except Error as e:
        print(e)
        return None


# ------------------------------------------------
# Variables au niveau du programme
# ------------------------------------------------
dashes = "--------------------------------------------------"

# ---------------------------------------------------
# Le programme principal
# ---------------------------------------------------
if __name__ == '__main__':
    # ------------------------------------------------
    # Tests
    # ------------------------------------------------
    try:  # Try (tests)

        # Messages de sortie vers STDOUT pour la journalisation
        begintime = datetime.datetime.now()
        print("Début du programme principal - " + str(begintime.strftime("%H:%M:%S")))

        # Définir les variables de travail

        dbfile = str(root) + "/src/init/bdd.db"  # Chemin de la base de données
        # dbfile = ""./src/init/bdd.db""

        # -- Création de table Etudiant (Pour le test )...une table suffit
        sqletudiant = """ CREATE TABLE IF NOT EXISTS Etudiant(
      etudiant_id VARCHAR(255) PRIMARY KEY NOT NULL,
      etudiant_nom VARCHAR(20),
      etudiant_prenom VARCHAR(20)
      );"""

        # Connect to database
        conn1 = create_connection(dbfile)

        # Résultat de création de table
        if create_table(conn1, sqletudiant):
            print("La table Etudiant a bien été créée.")
        else:
            print("La table Etudiant n'a pas été créée (Erreur).")

        # Test avecrequete
        cursor1 = execute_query(conn1, "select * from Etudiant")

        # Si nous obtenons des résultats de données, récupérez et affichez les enregistrements
        if cursor1 != None:
            rows = cursor1.fetchall()
            # Itérer et générer des lignes de données
            for row in rows:
                print(row)
        else:
            print("Table vide !")

        # Fermer la connection
        if conn1 != False:
            close_connection(conn1)
            # En cas de tests valides
            exitcode = 0
            exitmessage = 'Les tests de la base de données ont bien été réalisés avec succès !'

    # ------------------------------------------------
    # Gérer les exceptions
    # ------------------------------------------------
    except Exception as ex:  # Manipuler les exceptions
        exitcode = 99  # Le code de retour pour stdout
        exitmessage = str(ex)  # Le message de sortie pour stdout
        print('Traceback Info')  # Informations de trace de sortie for stdout
        traceback.print_exc()

    # ------------------------------------------------
    # Effectuer toujours la partie finale
    # ------------------------------------------------
    finally:  # Partie finale

        print('ExitCode:' + str(exitcode))
        print('ExitMessage:' + exitmessage)
        endtime = datetime.datetime.now()
        print("Fin du programme principal - " + str(endtime.strftime("%H:%M:%S")))
        print("Temps d'exécution - " + str(endtime - begintime))
        print(dashes)

        # Sortie du script
        sys.exit(exitcode)
