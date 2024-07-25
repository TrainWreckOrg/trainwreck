from interactions import Client, Intents, listen, slash_command, SlashContext, OptionType, slash_option
from dotenv import load_dotenv
import os
from enum import Enum
from HorrendousTimeTableExtractor import getCalendar
load_dotenv("cle.env")

token = os.getenv("TOKEN_BOT_DISCORD")
server = os.getenv("SERVER_ID")

bot = Client(intents=Intents.DEFAULT)
limite = 7


@listen() 
async def on_ready():
    """Fonction qui dit quand le bot est opérationel au démarage du programme"""
    print("Ready")
    print(f"This bot is owned by {bot.owner}")


@listen()
async def on_message_create(event):
    """This event is called when a message is sent in a channel the bot can see"""
    print(f"message received: {event.message.jump_url}")


@slash_command(name="bonjour", description="Te dit bonjour.", scopes=server)
async def my_command(ctx: SlashContext):
    await ctx.send(f"Bonjour {getName(ctx.author)}!")


@slash_command(name="get_info", description="Donne les infos sur l'utilisateur.", scopes=server)
async def today(ctx: SlashContext):
    await ctx.send(f"Vous êtes {getName(ctx.author)}!\nVotre filière est {getFilere(ctx.author).value} et votre groupe est {getGroupeTP(ctx.author).value} et votre groupe d'anglais est {getGroupeTDAnglais(ctx.author).value} .")

@slash_command(name="edt", description="L'emploi du temps en fonction de la limite.", scopes=server)
async def today(ctx: SlashContext):
    compteur = 0
    calendar = getCalendar()
    global limite
    for day in calendar:
        if compteur >= limite:
            break
        compteur+=1
        await ctx.send(embed=day)



@slash_command(name="setlimite", description="My first command :)", scopes=server)
@slash_option(
    name="nlimite",
    description="Combien d'embed afficher ?",
    required=True,
    opt_type=OptionType.INTEGER
)
async def setLimite(ctx: SlashContext, nlimite : int):
    global limite
    limite = nlimite
    await ctx.send("Limite Modifier")








def getName(author) -> str:
    """Permet d'obtenir le nickname si défini sinon le username"""
    return author.nickname if author.nickname else author.username



class InvalideRole(Exception):
    def __init__(self, message):
        super().__init__(message)


class Filiere(Enum):
    INGE = "Ingé"
    MIAGE = "Miage"

def getFilere(author):
    print(Filiere.INGE.value)
    for role in author.roles:
        if role.name == Filiere.INGE.value:
            return Filiere.INGE
        if role.name == Filiere.MIAGE.value:
            return Filiere.MIAGE
    raise InvalideRole("Vous n'avez pas de rôle indiquant votre filière.")



class TP(Enum):
    TPAI = "TP A Inge"
    TPBI = "TP B Inge"
    TPCI = "TP C Inge"
    TPDI = "TP D Inge"
    TPAM = "TP A Miage"
    TPBM = "TP B Miage"
    TPCM = "TP C Miage"
    TPDM = "TP D Miage"


def getGroupeTP(author):
    for role in author.roles:
        for tp in TP:
            if role.name == tp.value:
                return tp
        
    raise InvalideRole("Vous n'avez pas de rôle indiquant votre groupe de TP.")


class TD(Enum):
    TD1I = "TD 1 Inge"
    TD2I = "TD 2 Inge"
    TD1M = "TD 1 Miage"
    TD2M = "TD 2 Miage"
    


def getGroupeTD(author):
    for role in author.roles:
        for td in TD:
            if role.name == td.value:
                return td
    raise InvalideRole("Vous n'avez pas de rôle indiquant votre groupe de TD.")


class TDAnglais(Enum):
    TDA1I = "TD 1 Inge Anglais"
    TDA2I = "TD 2 Inge Anglais"
    TDA3I = "TD 3 Inge Anglais"
    TDA1M = "TD 1 Miage Anglais"
    TDA2M = "TD 2 Miage Anglais"
    TDA3M = "TD 3 Miage Anglais"

def getGroupeTDAnglais(author):
    for role in author.roles:
        for tda in TDAnglais:
            if role.name == tda.value:
                return tda
    raise InvalideRole("Vous n'avez pas de rôle indiquant votre groupe de TD d'anglais.")

bot.start(token)
