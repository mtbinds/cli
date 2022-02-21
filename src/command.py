import re
import json
import sys
from os import listdir
from os.path import isfile, join

class Command:
    """
    La structure des commandes contenant son nom, un regex (regex = définie la syntaxe, sa description
    et visible (true = met en valeur la commande)
    """

    def __init__(self, json: dict):
        """
        Constructeur par défaut

        @param json: Dictionnaire contenant les paramètres de la commande
        @type json: Dictionnaire
        """

        if json.__contains__("names"):
            self.names = json["names"]

        if json.__contains__("regex"):
            self.regex = json["regex"]

        if json.__contains__("description"):
            self.description = json["description"]

        if json.__contains__("visible"):
            self.visible = json["visible"]
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

    def get_command_by_names(self, name: str, parameter=""):
        """
        Permet d'avoir une commande selon le nom passé en paramètre

        @param name: Une chaîne de caractères contenant le nom de la commande
        @type name: String
        @param parameter: Défini les paramètres de la commande soit une chaine de caractères
        @type parameter: String
        @return: Un dictionnaire (json) soit vide soit contenant la commande
        @rtype: Dictionnaire
        """
        for json in self.commands:
            if json["command"].names.__contains__(name) and re.search(json["command"].regex, parameter):
                return json
        return {}

    def exec_command(self, name: str, parameter=""):
        """
        Récupère la commande et l'exécute

        @param name: Une chaîne de caractères contenant le nom de la commande
        @type name: String
        @param parameter: Option de commande demandé par l'utilisateur
        @type parameter: String
        @return:
        @rtype:
        """
        json = self.get_command_by_names(name, parameter)
        if json.__contains__("command") and json.__contains__("code"):
            command = json["command"]
            code = json["code"]
            code({
                "parameter": parameter,
                "manager": self,
                "command" : command
            })
        else:
            print("not found")


def help(context):
    """
    Fonction d'aide par défaut

    @param context: Décrit le contexte de l'application actuelle
    @type context: Dictionnaire
    @return:
    @rtype:
    """
    if context.__contains__("manager"):
        manager = context["manager"]
        for json in manager.commands:
            print(json["command"])



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