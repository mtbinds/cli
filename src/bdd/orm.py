from sqlite3 import Connection
from typing import Any, Type


class Context:
    connection = False


def connect(con: Connection):
    Context.connection = con


def context():
    return Context.connection


class AbstractEntity:

    def to_json(self) -> dict[str, Any]:
        return vars(self)

    def __str__(self):
        json = vars(self).copy()
        for (k, v) in json.items():
            if isinstance(v, AbstractEntity):
                json[k] = v.to_json()
        return str(json)

    @staticmethod
    def to_object(args: tuple[str], link=False):
        pass

    def get_table_name(self) -> str:
        return self.__class__.__name__

    def get_key(self):
        pass

    def save(self, connection: Connection = context()):
        pass


class ORM:

    @staticmethod
    def transform_for_sql(text):
        if isinstance(text, AbstractEntity):
            text.save()
            return ORM.transform_for_sql(text.get_key())
        if not isinstance(text, str): return str(text)
        return "'{}'".format(text)

    @staticmethod
    def parse_option(option: dict[str, Any], logic: str):
        """
        fonction qui va parser les options de recherche
        :param option: le dictionnaire de recherche
        :param logic: la logique de base de recherche (or ou and)
        :return:
        """
        if ORM.is_logic(
                option):  # je regarde si l'option contient une "logic" cad est de la forme {"logic" : "...", "options" : {....}}
            return ORM.parse_logic(option)
        else:  # les options sont "basic" et sont joint par la logique par défauts
            return " {} ".format(logic).join(ORM.parse_unit_option(k, v) for k, v in option.items())

    @staticmethod
    def parse_unit_option(key, value, symbol="="):
        """
        :param key: nom de la variable a imposer une condition
        :param value: valeur pouvant etre un dictionnaire ou une valeur normal
        :param symbol: symbol utilisé lors de la contidion
        :return:
        """
        print("key : {}, value : {}".format(key, value))
        if not isinstance(value, dict):
            return key + symbol + ORM.transform_for_sql(value)

        if value.keys().__contains__("value") and (value.keys().__contains__("symbol") or symbol != "="):
            """{"symbol" : ">", "value" : 0} => where [key] > 0
               {"symbol" : ">", "value" : 0, "equals" : True} => where [key] >= 0
            """
            if value.keys().__contains__("equals") and value.get("equals"):
                if value.keys().__contains__("symbol"):
                    return ORM.parse_unit_option(key, value.get("value"), value.get("symbole") + "=")
                else:
                    return ORM.parse_unit_option(key, value.get("value"), symbol + "=")
            return ORM.parse_unit_option(key, value.get("value"), value.get("symbol"))
        elif value.keys().__contains__("min") and value.keys().__contains__("max"):
            """{"min" : 0, "max" : 3} => where [key] > 0 and [key] < 3
               {"min" : 0, "max" : 3, "equals" : True} => where [key] >= 0 and [key] <= 3
            """
            if value.keys().__contains__("equals") and value.get("equals"):
                return ORM.parse_unit_option(key, value.get("min"), ">=") + " and " + ORM.parse_unit_option(key,
                                                                                                            value.get(
                                                                                                                "max"),
                                                                                                            "<=")
            return ORM.parse_unit_option(key, value.get("min"), ">") + " and " + ORM.parse_unit_option(key,
                                                                                                       value.get("max"),
                                                                                                       "<")
        elif value.keys().__contains__("contain"):
            """ {"competences_id" : {"contain" : "alo"}} => where instr(competences_id, 'alo') > 0
            """
            return "instr({}, {}) > 0".format(key, ORM.transform_for_sql(value.get("contain")))

    @staticmethod
    def parse_order(key, type: str):
        if type.lower() == "asc" or type.lower() == "up":
            return key + " " + "ASC"
        elif type.lower() == "desc" or type.lower() == "down":
            return key + " " + "DESC"

    @staticmethod
    def is_logic(logic: dict):
        return logic.keys().__contains__("logic") and logic.keys().__contains__("options") and isinstance(
            logic.get("logic"), str) and isinstance(logic.get("options"), list) and \
               (logic.get("logic").lower() == "and" or logic.get("logic").lower() == "or")

    @staticmethod
    def parse_logic(value: dict):
        """
        ici prend forme la version "complexe" des options mais qui permet de faire des recherche plus complexe

        imaginons que vous avais un objet Humain composé de
        ID | NAME | AGE | SIZE

        et que l'ont veux faire une recherche sur des humain ayant au minimum 18 ans et que le taille soit > 180
        ou que leur nom soit Michel

        en SQLite on ferais quelque chose comme ça
        select * from Humain where AGE >= 18 and (SIZE >= 180 or NAME = Michel)

        avec les options "basic" on ne pouvais pas faire ça, il y a donc un système pour le faire maintenant.

        si nous voulons faire cette requete voici quelle dictionnaire il va valoir faire

        option = {
            "logic" : "and",
            "options" : [
                { # une option "basic"
                    "AGE" : {
                        "symbol" : ">=",
                        "value" : 18
                    }
                },
                { # une autre option "complex" c'est recursif donc on peux les imbriqué autant qu'on veux
                    "logic" : "or",
                    "options" : [
                        {
                            "SIZE" : {
                                "symbol" : ">=",
                                "value" : 180
                            }
                        },
                        {
                            "NAME" : "MICHEL"
                        }
                    ]
                }
            ]
        }
        :param value:
        :return:
        """
        if ORM.is_logic(value):
            return "(" + " {} ".format(value.get("logic")).join(
                ORM.parse_option(v, value.get("logic")) for v in value.get("options")) + ")"
            pass
        raise ValueError("ORM ERROR : function `parse_logic` : parameter is not a logic object")

    @staticmethod
    def query(type: Type, connection: Connection = context(), keys: list[str] = ["*"],
              option: dict[str, Any] = {}, group: list[str] = [], size: int = -1, order: dict = {},
              logic: str = "AND", link: bool = False) -> \
            list[tuple] or list[type.__class__]:
        """

        :param link:
        :param type: type de retour si keys = [*], et table de recherche {ex : type = A => select * from A}
        :param connection: connection a la bdd
        :param keys: select retournée de la requete sqlite {ex : keys = ["*"] => select * from ...}
        :param option: option de recherche (detail dans parse_option)
        :param group: de quoi grouper un requete {group = ["name"] => select ..... groupe by 'name'}
        :param size: taille de la liste de retour
        :param order: ordre de recherche {order = {"id" : "asc"} => select ......... order by id asc}
        :param logic: logic de base des options and ou or
        :return:
        """

        if not connection:
            connection = context()

        if logic.lower() != "and" and logic.lower() != "or":
            raise ValueError("logic = {}, is not `and` or `or`".format(logic))

        base_sql = "SELECT {} from {}"
        select_sql = ", ".join(keys)
        from_sql = type.__name__
        option_sql = ""
        order_sql = ""
        group_sql = ""

        if bool(option):
            """
            voir parse_option
            """
            option_sql = " where {}".format(ORM.parse_option(option, logic))

        if bool(order):
            """
            order = {"id" : "down"} -> order by id ASC
            order = {"id" : "up", "name" : "down"} -> order by id ASC, name DESC
            """
            order_sql = " ORDER BY {}".format(", ".join(ORM.parse_order(k, v) for k, v in order.items()))

        if bool(group):
            """
            keys=["*", "COUNT(competences_id)"], group = ["competences_id"]) => SELECT *,COUNT(competences_id) from Aptitudes GROUP BY competences_id
            """
            group_sql = " GROUP BY {}".format(", ".join(group))

        sql = base_sql.format(select_sql, from_sql) + option_sql + order_sql + group_sql

        print(sql)
        cursor = connection.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        if size > 0:
            result = result[:size]

        if keys != ["*"]:  # si tout les param sont pas demandé je ne peux construire les objets
            return result
        else:
            array = []
            for row in result:
                array.append(type.to_object(row, link=link))
            return array
