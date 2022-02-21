import re
import sys

import json
from src.bdd.entity import Etudiant


class Command:
    """
    La structure des commandes contenant son nom, un regex (regex = définie la syntaxe, sa description
    et visible (true = met en valeur la commande)
    """

    def __init__(self, data: dict or str):
        """
        Constructeur par défaut

        @param json: Dictionnaire contenant les paramètres de la commande
        @type json: Dictionnaire
        """
        if isinstance(data, str):  # si un str alors je charge un fichier json
            if re.search("\./json/\w+\.json", data):  # si je donne le path alors je le charge sans modification
                f = open(data)
                self.init(json.load(f))
            else:  # sinon je tente de le trouver par moi même
                f = open("./json/" + data + ".json")
                self.init(json.load(f))
        elif isinstance(data, dict):
            self.init(data)

    def init(self, data):
        if data.__contains__("names"):
            self.names = data["names"]

        if data.__contains__("regex"):
            self.regex = data["regex"]

        if data.__contains__("description"):
            self.description = data["description"]

        if data.__contains__("visible"):
            self.visible = data["visible"]
        pass

    def __str__(self):
        """
        ToString() version python

        @return: Décrit la commande dans une chaîne de caractères
        @rtype: Une chaîne de caractères
        """
        return "name : " + str(self.names) + ", regex : " + self.regex + ", description : " + self.description


class CommandManager:
    """
    Permet la gestion / manipulation des commandes
    """

    def __init__(self, commands=None):
        """
        Par défaut attend un tableau, si il n'y en a pas, il le créer lui-même

        @param commands: Un tableau de commandes
        @type commands: Un tableau de commandes
        """
        if commands is None:
            commands = []
        self.commands = commands

    def register_command(self, command: Command, code=lambda parameter: print("parameter : " + str(parameter))):
        """
        Permet de d'enregistrer une commande en interne

        @param command: Une commande
        @type command: Une commande
        @param code: La fonction qui sera exécutée quand la commande sera apelée
        @type code: Une fonction (lambda)
        @return:
        @rtype:
        """

        self.commands.append({
            "command": command,
            "code": code
        })

    def get_command_by_names(self, name: str, parameter=sys.argv[2:]):
        """
        Permet d'avoir une commande selon le nom passé en paramètre

        @param name: Une chaîne de caractères contenant le nom de la commande
        @type name: String
        @param parameter: Défini les paramètres de la commande soit une chaine de caractères
        @type parameter: Tableau de String
        @return: Un dictionnaire (json) soit vide soit contenant la commande
        @rtype: Dictionnaire
        """
        for data in self.commands:
            if data["command"].names.__contains__(name) and (re.search(data["command"].regex, ' '.join(parameter)) or (
                    len(parameter) > 0 and parameter[0] == "--help")):
                return data
        return {}

    def exec_command(self, name: str, parameter=sys.argv[2:]):
        """
        Récupère la commande et l'exécute

        @param name: Une chaîne de caractères contenant le nom de la commande
        @type name: String
        @param parameter: Option de commande demandé par l'utilisateur
        @type parameter: Tableau de String
        @return:
        @rtype:
        """
        data = self.get_command_by_names(name, parameter)
        if data.__contains__("command") and data.__contains__("code"):
            command = data["command"]
            code = data["code"]
            code({
                "parameter": parameter,
                "manager": self,
                "command": command
            })
        else:
            print("not found")


def base_command(context, base_run, help_run, fail_run=lambda context: print("Error : \n\t" + vars(context))):
    if context.__contains__("parameter"):
        param = context["parameter"]
        if len(param) > 0 and param[0] == "--help":
            help_run(context)
        elif not base_run(context):
            fail_run(context)

    else:
        fail_run(context)


def help_command(context):
    """
    Fonction d'aide par défaut

    @param context: Décrit le contexte de l'application actuelle
    @type context: Dictionnaire
    @return:
    @rtype:
    """

    def run(context):
        if context.__contains__("manager"):
            manager = context["manager"]
            for data in manager.commands:
                print(data["command"])
            return True
        return False

    base_command(context, run, lambda context: print("on affiche help"))


def make_query(parameter):
    option = {}
    group = []
    size = -1
    order = {}

    actual = "-o"

    for p in parameter:
        if re.search("-\w", p):  # switch de mode, -o option, -order order, -size size, -g group
            actual = p
        elif re.search("\w\=\w", p):
            split = p.split("=")
            if actual == "-o":
                option[split[0]] = split[1]  # -o id=1 name=alo
            elif actual == "-order":  # -order id=up
                order[split[0]] = split[1]
        else:
            if actual == "-size":  # -size 1
                size = int(p)
            elif actual == "-g":  # -g id name
                group.append(p)
    return option, group, size, order


def student_command(context):
    """
    fonction quand une requete du style
        - student -o etudiant_prenom=test2 -order etudiant_id=down
        - student
    est utilisé en argument
    :param context:
    :return:
    """

    def run(context):
        if context.__contains__("parameter"):
            parameter = context["parameter"]
            option, group, size, order = make_query(parameter)
            query = Etudiant.read(Etudiant, option=option, group=group, size=size, order=order)
            for entity in query:
                print(entity)
            return True
        return False

    def help(context):
        print("help")

    def fail(context):
        print("error")

    base_command(context, run, help)


'''
Optionnel -> Description de comment sera notre json

fichier : help.json
{
    "names": ["help"],
    "regex": "",
    "description": "",
    "visible": true
}

register_command("help.json", lambda);


help

for (command in commands):
    if command.names.contain(help):
        command.exec();
'''
def main():
    manager = CommandManager()
    '''
    onlyfiles = [f for f in listdir("./commands") if isfile(join("./commands", f))]
    for fileName in onlyfiles:    
        with open('commands/'+fileName) as file:
            data = json.load(file)
        c = Command(data)
        manager.register_command(c)
    '''
    
    '''
    Enregistrement des commandes via leurs fichiers JSON
    '''
    with open('commands/help.json') as file:
        data = json.load(file)
    c = Command(data)
    manager.register_command(c, help)
    
    with open('commands/test.json') as file:
        data = json.load(file)
    c = Command(data)
    manager.register_command(c)
    
    '''
    Gestion des Command Line Arguments
    '''
    if(len(sys.argv) > 2):
        param = ""
        for i in range(2, len(sys.argv)):
            param += " "+sys.argv[i] 
        manager.exec_command(sys.argv[1],param)
    else :
        if(len(sys.argv) > 1) :
            manager.exec_command(sys.argv[1])
        else :
            print('Not enough arguments, please try again as follow : py command.py [command] [parameter(s)]')
    

if __name__ == "__main__":
    main()