import copy
from sqlite3 import Connection
from typing import Any, Type


def transform_for_sql(text):
    if not isinstance(text, str): return str(text)
    return "'{}'".format(text)

def parse_option(key, value, symbol = "="):
    """
    :param key: nom de la variable a imposer une condition
    :param value: valeur pouvant etre un dictionnaire ou une valeur normal
    :param symbol: symbol utilisé lors de la contidion
    :return:
    """
    if not isinstance(value, dict):
        return key + symbol + transform_for_sql(value)

    if value.keys().__contains__("value") and value.keys().__contains__("symbol"):
        """{"symbol" : ">", "value" : 0} => where [key] > 0
           {"symbol" : ">", "value" : 0, "equals" : True} => where [key] >= 0
        """
        if value.keys().__contains__("equals") and value.get("equals"):
            return parse_option(key, value.get("value"), value.get("symbole") + "=")
        return parse_option(key, value.get("value"), value.get("symbol"))
    elif value.keys().__contains__("min") and value.keys().__contains__("max"):
        """{"min" : 0, "max" : 3} => where [key] > 0 and [key] < 3
           {"min" : 0, "max" : 3, "equals" : True} => where [key] >= 0 and [key] <= 3
        """
        if value.keys().__contains__("equals") and value.get("equals"):
            return parse_option(key, value.get("min"), ">=") + " and " + parse_option(key, value.get("max"), "<=")
        return parse_option(key, value.get("min"), ">") + " and " + parse_option(key, value.get("max"), "<")

def parse_order(key, type : str):
    if type.lower() == "asc" or type.lower() == "up":
        return key + " " + "ASC"
    elif type.lower() == "desc" or type.lower() == "down":
        return key + " " + "DESC"



class AbstractEntity:

    def to_json(self) -> dict[str, Any]:
        return vars(self)

    def __str__(self):
        return str(self.to_json())

    @staticmethod
    def to_object(args: tuple[str]):
        pass


class BdoEntity(AbstractEntity):
    """
    cette classe est la base de toute les entité lié a notre application, elle va aussi servir ORM en mappant les objet pour les sauvegarder en base de donnée
    ou transformer se qu'il y a en base de donnée en objet
    """

    @staticmethod
    def read_all(type: Type[AbstractEntity], connection: Connection) -> list[type.__class__]:
        """
        fonction qui retourne une liste d'objet lié a type
        :param type: classe demandé en retour dans la liste
        :param connection: instance de la base de donnée sqlite
        :return:
        """
        return BdoEntity.read(type, connection)

    @staticmethod
    def read(type: Type[AbstractEntity], connection: Connection, keys: list[str] = ["*"],
             option: dict[str, Any] = {}) -> list[tuple] or list[type.__class__]:
        """
        cette fonction retourne une liste d'objet lié a une requete
        :param type: classe demandé en retour (valable que si keys = ["*"]
        :param connection: instance de la base de donnée sqlite
        :param keys: permet de choisir les champs de retour de la requete
        :param option: permet de choisir des options, exmeple where id = 0 => {"id" : 0}
        :return: retourne soit une liste de tuple (basé sur keys) soit une liste de d'objet lié a type
        """
        sql = "SELECT {} from {}".format(",".join(keys), type.__name__)

        if bool(option):
            order = False
            if option.keys().__contains__("order"):
                order = option.get("order")
                del option["order"]
            sql += " where {}".format(" AND ".join(parse_option(k, v) for k, v in option.items()))
            print(order)
            if bool(order) and isinstance(order, dict):
                """
                "order" : {"id" : "up"} -> order by id ASC
                "order" : {"id" : "up", "name" : "down"} -> order by id ASC, name DESC
                """
                sql += " order by {}".format(", ".join(parse_order(k, v) for k, v in order.items()))

        print(sql)
        cursor = connection.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()

        if keys != ["*"]: # si tout les param sont pas demandé je ne peux construire les objets
            return result
        else:
            list = []
            for row in result:
                list.append(type.to_object(row))
            return list

    def get_table_name(self) -> str:
        return self.__class__.__name__

    def save(self, connection: Connection) -> None:
        """
        permet de sauvegarder en base de donnée un objet
        :param connection: instance d'une base de donnée sqlite
        :return:
        """
        json = self.to_json()
        sql = "INSERT OR REPLACE INTO {}({}) VALUES({})".format(self.get_table_name(), ','.join(json.keys()),
                                                                ','.join(transform_for_sql(k) for k in json.values()))
        print(sql)
        cursor = connection.cursor()
        cursor.execute(sql)
        connection.commit()


class Aptitudes(BdoEntity):

    def __init__(self, aptitudes_id: int, competences_id: str, aptitudes_nom: str) -> None:
        super().__init__()
        self.aptitudes_id = aptitudes_id
        self.competences_id = competences_id
        self.aptitudes_nom = aptitudes_nom

    @staticmethod
    def to_object(args: tuple[str]):
        if len(args) != 3: return False
        return Aptitudes(int(args[0]), args[1], args[2])


class Competences(BdoEntity):

    def __init__(self, competences_id: str, domaines_id: str, competences_nom: str, competences_seuil: float) -> None:
        super().__init__()
        self.competences_id = competences_id
        self.domaines_id = domaines_id
        self.competences_nom = competences_nom
        self.competences_seuil = competences_seuil

    @staticmethod
    def to_object(args: tuple[str]):
        if len(args) != 4: return False
        return Competences(args[0], args[1], args[2], float(args[3]))


class Domaines(BdoEntity):

    def __init__(self, domaines_id: str, domaines_nom: str) -> None:
        super().__init__()
        self.domaines_id = domaines_id
        self.domaines_nom = domaines_nom

    @staticmethod
    def to_object(args: tuple[str]):
        if len(args) != 2: return False
        return Domaines(args[0], args[1])


class Evaluations(BdoEntity):

    def __init__(self, evaluations_id: int, matiere_id: int, aptitudes_id: int, evaluations_nom: str) -> None:
        super().__init__()
        self.evaluations_id = evaluations_id
        self.matiere_id = matiere_id
        self.aptitudes_id = aptitudes_id
        self.evaluations_nom = evaluations_nom

    @staticmethod
    def to_object(args: tuple[str]):
        if len(args) != 4: return False
        return Evaluations(int(args[0]), int(args[1]), int(args[2]), args[3])


class Matieres(BdoEntity):

    def __init__(self, matieres_id: int, matieres_nom: int, enseignant_id: int) -> None:
        super().__init__()
        self.matieres_id = matieres_id
        self.matieres_nom = matieres_nom
        self.enseignant_id = enseignant_id

    @staticmethod
    def to_object(args: tuple[str]):
        if len(args) != 3: return False
        return Matieres(int(args[0]), args[1], int(args[1]))


class Etudiant(BdoEntity):

    def __init__(self, etudiant_id: str, etudiant_prenom: str, etudiant_nom: str) -> None:
        super().__init__()
        self.etudiant_id = etudiant_id
        self.etudiant_prenom = etudiant_prenom
        self.etudiant_nom = etudiant_nom

    @staticmethod
    def to_object(args: tuple[str]):
        if len(args) != 3: return False
        return Etudiant(args[0], args[1], args[2])


class Syllabus(BdoEntity):

    def __init__(self, syllabus_id: int, syllabus_nom: str, etudiant_id: str) -> None:
        super().__init__()
        self.syllabus_id = syllabus_id
        self.syllabus_nom = syllabus_nom
        self.etudiant_id = etudiant_id

    @staticmethod
    def to_object(args: tuple[str]):
        if len(args) != 3: return False
        return Syllabus(int(args[0]), args[1], str(args[2]))


class Enseignant(BdoEntity):

    def __init__(self, enseignant_id: int, enseignant_nom: str, enseignant_prenom: str) -> None:
        super().__init__()
        self.enseignant_id = enseignant_id
        self.enseignant_nom = enseignant_nom
        self.enseignant_prenom = enseignant_prenom

    @staticmethod
    def to_object(args: tuple[str]):
        if len(args) != 3: return False
        return Enseignant(int(args[0]), args[1], args[2])


class Validations(BdoEntity):

    def __init__(self, validations_id: int, aptitudes_id: int, evaluations_id: int, etudiant_id: int,
                 validation_resultat: int) -> None:
        super().__init__()
        self.validations_id = validations_id
        self.aptitudes_id = aptitudes_id
        self.evaluations_id = evaluations_id
        self.etudiant_id = etudiant_id
        self.validation_resultat = validation_resultat

    @staticmethod
    def to_object(args: tuple[str]):
        if len(args) != 5: return False
        return Validations(int(args[0]), int(args[1]), int(args[2]), int(args[3]), int(args[4]))


class SyllabusMatieres(BdoEntity):

    def __init__(self, matiere_id: int, syllabus_id: int) -> None:
        super().__init__()
        self.matiere_id = matiere_id
        self.syllabus_id = syllabus_id

    @staticmethod
    def to_object(args: tuple[str]):
        if len(args) != 2: return False
        return SyllabusMatieres(int(args[0]), int(args[1]))
