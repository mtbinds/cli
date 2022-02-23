# CLI

- Année : M2 IWOCS
- Projet groupe non alternant

## Auteurs

<h3>Groupe CLI</h3>

|Nom|Prénom|login|email|
|--|--|--|--| 
| Bourgeaux | Maxence | bm142013 | maxence.bourgeaux@etu.univ-lehavre.fr |
| Guyomar | Robin | gr161657 | robin.guyomar@etu.univ-lehavre.fr |
| Labbe | Alexis | la172685 | alexis.labbe@etu.univ-lehavre.fr |
| Planchon | Richard | pr172488 | richard.planchon@etu.univ-lehavre.fr |
| Taoualit | Madjid | tm177375 | madjid.taoualit@etu.univ-lehavre.fr |

## Objectif

Construire et développer un CLI pouvant manipuler une base de données.

## Présentation de la base de données

### Schéma

Voici ci-dessous le schéma général du projet que nous avons dessiné lors de la réunion globale.

![schema](https://cdn.discordapp.com/attachments/679677634291957792/946105567485763634/Untitled_Diagram.drawio.png)

### Diagramme de classe

![diagramme de classe](https://cdn.discordapp.com/attachments/679677634291957792/946112358873460836/Untitled_Diagram.drawio_1.png)

## Commandes

Un CLI est un système de commande textuel.

Nous devions donc trouver une structure pour nos commandes, nous avions plusieurs choix devant nous. Le premier était l'utilisation de formats type xml, json ou encore csv. Des formats très classique quand on veut stocker de l'information.

Le deuxième était de stocker les commandes en base de données. Ce format est intéressant car il est plus performant que les fichiers individuels, mais il est moins visuel lors de sa création.

Nous avons donc décidé de partir sur une structure de commandes basée sur des fichiers json.

### JSON

Nos Json ont plusieurs attributs :

- `names` : nom des commandes permettant de les utiliser
- `regex` : expression régulière pour match si la commande est bien utilisée
- `description` : une description de la commande pour donner plus d'informations lors de la commande help
- `visible` : booléen permettant de mettre en avant ou non une commande via la commande help

```json
{
  "names": [
    "aide",
    "help"
  ],
  "regex": "",
  "description": "une description",
  "visible": false
}
```

### Python

En python, l'objet Command prend un dictionnaire ou un chemin d'un fichier json et est stocké dans le Manager.

```python    
c_help = Command("help")
```

Pour faciliter l'écriture en python des commandes, nous avons créé une fonction `base_command(context, base_function, help_function, fail_function)`

Nous reviendrons sur le contexte lors du Manager.

```python
def base_command(context, base_run, help_run, fail_run=lambda context: print("Error : \n\t" + vars(context))):
    if context.__contains__("parameter"):
        param = context["parameter"]
        if len(param) > 0 and param[0] == "--help":
            help_run(context)
        elif not base_run(context):
            fail_run(context)
    else:
        fail_run(context)
```

Cette fonction permet de créer des exécutions de commandes simplifiées, en gérant pour nous l'argument `--help` et le cas d'erreur.

À noter que `base_run` est un **Prédicat** et doit donc retourner un booléen.

### Gestion des commandes - Manager

Le manager de commandes est un système qui va gérer entièrement les commandes. Il stocke les commandes en les liant à une fonction python pour les exécuter lors de son appel.

#### Contexte

Pour faciliter l'accès à certaines ressources dans les commandes, nous avons mis en place un système de contexte, nous permettant de savoir l'état actuel de l'application. Ce contexte est actuellement constitué de :

- `parameter` : tableau de chaîne de caractères donnant les paramètres voulus pour la commande
- `manager` : le manager en lui-même pour avoir accès aux autres commandes par exemple
- `command` : la commande actuellement exécutée

Ce contexte est donc envoyer à chaque commande exécutée.

#### Enregistrement de commandes

Pour utiliser des commandes, il nous faut bien les enregistrer à un moment. Il existe une fonction dans le Manager nous permettant de faire ça simplement : `register_command(Command, function)`.

```python
manager = CommandManager()
def help_command(context):
    def run(context):
        if context.__contains__("manager"):
            manager = context["manager"]
            for data in manager.commands:
                if data["command"].visible:
                    print(data["command"])
            return True
        return False

    base_command(context, run, lambda ctx: print("on affiche help"))


manager.register_command(c_help, help_command)
```

#### Exécution de commandes

L'exécution des commandes peut se faire via la fonction `exec_command(nom, [arguments])`.

```python
import sys

manager.exec_command(sys.argv[1], sys.argv[2:])
```

## ORM SQLite

Nous avons décidé de créer un ORM maison, pour éviter toute dépendance dans ce projet. On ne va pas rentrer dans les détails de cet ORM.

### Connection

Tout ORM dois être connecté à une base de données pour pouvoir le manipuler, ici nous pouvons le faire via la fonction static `connect(Connection)`

```python
import sqlite3

root = Path(__file__).parent
connect(sqlite3.connect(str(root) + '/init/bdd.db'))
```

### AbstractEntity

AbstractEntity est une classe abstraite désignant les entités utilisables par l'ORM. Nous avons 3 fonctions à redéfinir lors de la création d'un fils de cette classe.

- `to_object(args: tuple[str], link=False)` : permettant de transformer les résultats d'une requête en objet
- `get_key(self)` : permettant de connaître le nom de l'id lié à cette table
- `save(self, connection: Connection)` : permettant de sauvegarder en base de donnée

### Requêtes

Les requêtes seraient extrêmement longues à expliquer, sachant que ce n'est pas le sujet premier de ce projet, veuillez retrouver [ici](./src/bdd/orm.py) le code qui est entièrement documenté avec des exemples.

