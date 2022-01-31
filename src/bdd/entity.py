from sqlite3 import Connection
from typing import Any, Type

from src.bdd.orm import ORM, AbstractEntity, context


class BdoEntity(AbstractEntity):
    """
    cette classe est la base de toute les entité lié a notre application, elle va aussi servir ORM en mappant les objet pour les sauvegarder en base de donnée
    ou transformer se qu'il y a en base de donnée en objet
    """

    @staticmethod
    def read_all(type: Type[AbstractEntity], connection: Connection = context()) -> list[type.__class__]:
        """
        fonction qui retourne une liste d'objet lié a type
        :param type: classe demandé en retour dans la liste
        :param connection: instance de la base de donnée sqlite
        :return:
        """
        return BdoEntity.read(type, connection)

    @staticmethod
    def exist(type: Type[AbstractEntity], connection: Connection = False,
              option: dict[str, Any] = {}) -> bool:
        return len(BdoEntity.read(type, connection, option=option)) >= 1

    @staticmethod
    def read(type: Type[AbstractEntity], connection: Connection = False, keys: list[str] = ["*"],
             option: dict[str, Any] = {}, group: list[str] = [], size: int = -1, order: dict = {}, link: bool = False,
             logic: str = "AND") -> list[tuple] or list[type.__class__]:
        return ORM.query(type, connection, keys, option, group, size, order, logic, link=link)

    @staticmethod
    def readFirst(type: Type[AbstractEntity], connection: Connection = False, keys: list[str] = ["*"],
                  option: dict[str, Any] = {}, group: list[str] = [], size: int = -1, order: dict = {},
                  link: bool = False,
                  logic: str = "AND") -> tuple or type.__class__ or None:
        list = ORM.query(type, connection, keys, option, group, size, order, logic, link=link)

        if len(list) > 0:
            return list[0]
        else:
            return None

    def save(self, connection: Connection = context()) -> None:
        """
        permet de sauvegarder en base de donnée un objet
        :param connection: instance d'une base de donnée sqlite
        :return:
        """
        json = self.to_json()
        sql = "INSERT OR REPLACE INTO {}({}) VALUES({})".format(self.get_table_name(), ','.join(json.keys()),
                                                                ','.join(
                                                                    ORM.transform_for_sql(k) for k in json.values()))

        if not connection:
            connection = context()
        print(sql)
        print(connection)
        cursor = connection.cursor()

        cursor.execute(sql)
        connection.commit()


class Aptitudes(BdoEntity):

    def __init__(self, aptitudes_id: int, competences_id: str or AbstractEntity, aptitudes_nom: str,
                 connection: Connection = context(),
                 link=False) -> None:
        super().__init__()
        self.aptitudes_id = aptitudes_id
        if not connection:
            connection = context()
        if link:
            self.competences_id = Competences.readFirst(Competences, connection,
                                                        option={"competences_id": competences_id})
        else:
            self.competences_id = competences_id
        self.aptitudes_nom = aptitudes_nom

    @staticmethod
    def to_object(args: tuple[str], link=False):
        if len(args) != 3: return False
        return Aptitudes(int(args[0]), args[1], args[2], link=link)

    def get_key(self):
        return self.aptitudes_id


class Competences(BdoEntity):

    def __init__(self, competences_id: str, domaines_id: str or AbstractEntity, competences_nom: str,
                 competences_seuil: float,
                 connection: Connection = context(), link=False) -> None:
        super().__init__()
        self.competences_id = competences_id
        if not connection:
            connection = context()
        if link:
            self.domaines_id = Domaines.readFirst(Domaines, connection, option={"domaines_id": domaines_id})
        else:
            self.domaines_id = domaines_id
        self.competences_nom = competences_nom
        self.competences_seuil = competences_seuil

    @staticmethod
    def to_object(args: tuple[str], link=False):
        if len(args) != 4: return False
        return Competences(args[0], args[1], args[2], float(args[3]), link=link)

    def get_key(self):
        return self.competences_id


class Domaines(BdoEntity):

    def __init__(self, domaines_id: str, domaines_nom: str, connection: Connection = context(), link=False) -> None:
        super().__init__()
        if not connection:
            connection = context()
        self.domaines_id = domaines_id
        self.domaines_nom = domaines_nom

    @staticmethod
    def to_object(args: tuple[str], link=False):
        if len(args) != 2: return False
        return Domaines(args[0], args[1], link=link)

    def get_key(self):
        return self.domaines_id


class Evaluations(BdoEntity):

    def __init__(self, evaluations_id: int, matiere_id: int or AbstractEntity, aptitudes_id: int or AbstractEntity,
                 evaluations_nom: str,
                 connection: Connection = context(), link=False) -> None:
        super().__init__()
        self.evaluations_id = evaluations_id
        if not connection:
            connection = context()
        if link:
            self.matiere_id = Matieres.readFirst(Matieres, connection, option={"matiere_id": matiere_id})
            self.aptitudes_id = Aptitudes.readFirst(Aptitudes, connection, option={"aptitudes_id": aptitudes_id})
        else:
            self.matiere_id = matiere_id
            self.aptitudes_id = aptitudes_id

        self.evaluations_nom = evaluations_nom

    @staticmethod
    def to_object(args: tuple[str], link=False):
        if len(args) != 4: return False
        return Evaluations(int(args[0]), int(args[1]), int(args[2]), args[3], link=link)

    def get_key(self):
        return self.evaluations_id


class Matieres(BdoEntity):

    def __init__(self, matieres_id: int, matieres_nom: int, enseignant_id: int or AbstractEntity,
                 connection: Connection = context(),
                 link=False) -> None:
        super().__init__()
        self.matieres_id = matieres_id
        if not connection:
            connection = context()
        self.matieres_nom = matieres_nom
        if link:
            self.enseignant_id = Enseignant.readFirst(Enseignant, connection, option={"enseignant_id": enseignant_id})
        else:
            self.enseignant_id = enseignant_id

    @staticmethod
    def to_object(args: tuple[str], link=False):
        if len(args) != 3: return False
        return Matieres(int(args[0]), args[1], int(args[1]), link=link)

    def get_key(self):
        return self.matieres_id


class Etudiant(BdoEntity):

    def __init__(self, etudiant_id: str, etudiant_prenom: str, etudiant_nom: str, connection: Connection = context(),
                 link=False) -> None:
        super().__init__()
        self.etudiant_id = etudiant_id
        if not connection:
            connection = context()
        self.etudiant_prenom = etudiant_prenom
        self.etudiant_nom = etudiant_nom

    @staticmethod
    def to_object(args: tuple[str], link=False):
        if len(args) != 3: return False
        return Etudiant(args[0], args[1], args[2], link=link)

    def get_key(self):
        return self.etudiant_id


class Syllabus(BdoEntity):

    def __init__(self, syllabus_id: int, syllabus_nom: str, etudiant_id: str or AbstractEntity,
                 connection: Connection = context(),
                 link=False) -> None:
        super().__init__()
        self.syllabus_id = syllabus_id
        if not connection:
            connection = context()
        self.syllabus_nom = syllabus_nom
        if link:
            self.etudiant_id = Etudiant.readFirst(Etudiant, connection, option={"etudiant_id": etudiant_id})
        else:
            self.etudiant_id = etudiant_id

    @staticmethod
    def to_object(args: tuple[str], link=False):
        if len(args) != 3: return False
        return Syllabus(int(args[0]), args[1], str(args[2]), link=link)

    def get_key(self):
        return self.syllabus_id


class Enseignant(BdoEntity):

    def __init__(self, enseignant_id: int, enseignant_nom: str, enseignant_prenom: str,
                 connection: Connection = context(), link=False) -> None:
        super().__init__()
        self.enseignant_id = enseignant_id
        if not connection:
            connection = context()
        self.enseignant_nom = enseignant_nom
        self.enseignant_prenom = enseignant_prenom

    @staticmethod
    def to_object(args: tuple[str], link=False):
        if len(args) != 3: return False
        return Enseignant(int(args[0]), args[1], args[2], link=link)

    def get_key(self):
        return self.enseignant_id


class Validations(BdoEntity):

    def __init__(self, validations_id: int, aptitudes_id: int or AbstractEntity, evaluations_id: int or AbstractEntity,
                 etudiant_id: int or AbstractEntity,
                 validation_resultat: int, connection: Connection = context(), link=False) -> None:
        super().__init__()
        self.validations_id = validations_id
        if not connection:
            connection = context()
        self.validation_resultat = validation_resultat
        if link:
            self.aptitudes_id = Matieres.readFirst(Aptitudes, connection, option={"aptitudes_id": aptitudes_id})
            self.evaluations_id = Evaluations.readFirst(Evaluations, connection,
                                                        option={"evaluations_id": evaluations_id})
            self.etudiant_id = Etudiant.readFirst(Etudiant, connection, option={"etudiant_id": etudiant_id})
        else:
            self.aptitudes_id = aptitudes_id
            self.evaluations_id = evaluations_id
            self.etudiant_id = etudiant_id

    @staticmethod
    def to_object(args: tuple[str], link=False):
        if len(args) != 5: return False
        return Validations(int(args[0]), int(args[1]), int(args[2]), int(args[3]), int(args[4]), link=link)

    def get_key(self):
        return self.validations_id


class SyllabusMatieres(BdoEntity):

    def __init__(self, matiere_id: int or AbstractEntity, syllabus_id: int or AbstractEntity,
                 connection: Connection = context(), link=False) -> None:
        super().__init__()
        self.matiere_id = matiere_id
        if not connection:
            connection = context()
        self.syllabus_id = syllabus_id
        if link:
            self.matiere_id = Matieres.readFirst(Matieres, connection, option={"matiere_id": matiere_id})
            self.syllabus_id = Syllabus.readFirst(Syllabus, connection, option={"syllabus_id": syllabus_id})
        else:
            self.matiere_id = matiere_id
            self.syllabus_id = syllabus_id

    @staticmethod
    def to_object(args: tuple[str], link=False):
        if len(args) != 2: return False
        return SyllabusMatieres(int(args[0]), int(args[1]), link=link)
