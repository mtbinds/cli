from sqlite3 import Connection
from typing import Any, Type


class AbstractEntity:

    def to_json(self) -> dict[str, Any]:
        return vars(self)

    def __str__(self):
        return str(self.to_json())

    @staticmethod
    def to_object(args: tuple[str]):
        pass


def transform_for_sql(text):
    if not isinstance(text, str): return str(text)
    return "'{}'".format(text)


def parse_option(key, value, symbol="="):
    """
    :param key: nom de la variable a imposer une condition
    :param value: valeur pouvant etre un dictionnaire ou une valeur normal
    :param symbol: symbol utilisé lors de la contidion
    :return:
    """
    print("key : {}, value : {}".format(key, value))
    if not isinstance(value, dict):
        return key + symbol + transform_for_sql(value)

    if value.keys().__contains__("value") and (value.keys().__contains__("symbol") or symbol != "="):
        """{"symbol" : ">", "value" : 0} => where [key] > 0
           {"symbol" : ">", "value" : 0, "equals" : True} => where [key] >= 0
        """
        if value.keys().__contains__("equals") and value.get("equals"):
            if value.keys().__contains__("symbol"):
                return parse_option(key, value.get("value"), value.get("symbole") + "=")
            else:
                return parse_option(key, value.get("value"), symbol + "=")
        return parse_option(key, value.get("value"), value.get("symbol"))
    elif value.keys().__contains__("min") and value.keys().__contains__("max"):
        """{"min" : 0, "max" : 3} => where [key] > 0 and [key] < 3
           {"min" : 0, "max" : 3, "equals" : True} => where [key] >= 0 and [key] <= 3
        """
        if value.keys().__contains__("equals") and value.get("equals"):
            return parse_option(key, value.get("min"), ">=") + " and " + parse_option(key, value.get("max"), "<=")
        return parse_option(key, value.get("min"), ">") + " and " + parse_option(key, value.get("max"), "<")
    elif value.keys().__contains__("contain"):
        """ {"competences_id" : {"contain" : "alo"}} => where instr(competences_id, 'alo') > 0
        """
        return "instr({}, {}) > 0".format(key, transform_for_sql(value.get("contain")))


def parse_order(key, type: str):
    if type.lower() == "asc" or type.lower() == "up":
        return key + " " + "ASC"
    elif type.lower() == "desc" or type.lower() == "down":
        return key + " " + "DESC"


def query(type: Type, connection: Connection, keys: list[str] = ["*"],
          option: dict[str, Any] = {}, group: list[str] = [], size: int = -1, order: dict = {}, logic: str = "AND") -> \
        list[tuple] or list[type.__class__]:
    """
            cette fonction retourne une liste d'objet lié a une requete
            :param type: classe demandé en retour (valable que si keys = ["*"]
            :param connection: instance de la base de donnée sqlite
            :param keys: permet de choisir les champs de retour de la requete
            :param option: permet de choisir des options, exmeple where id = 0 => {"id" : 0}
            :return: retourne soit une liste de tuple (basé sur keys) soit une liste de d'objet lié a type
            """

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
        option_sql = " where {}".format(" {} ".format(logic).join(parse_option(k, v) for k, v in option.items()))

    if bool(order):
        """
        order = {"id" : "down"} -> order by id ASC
        order = {"id" : "up", "name" : "down"} -> order by id ASC, name DESC
        """
        order_sql = " ORDER BY {}".format(", ".join(parse_order(k, v) for k, v in order.items()))

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
            array.append(type.to_object(row))
        return array
