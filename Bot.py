from interactions import ActionRow, ButtonStyle, Client, Embed, Intents, listen
from interactions import slash_command, SlashContext, OptionType, slash_option
from interactions import Button, ButtonStyle
from interactions.api.events import Component

from dotenv import load_dotenv
import os
from HorrendousTimeTableExtractor import getCalendar, Filiere, TD, TP, TDAnglais
load_dotenv("cle.env")

from interactions import Button, ButtonStyle
from interactions.api.events import Component

token = os.getenv("TOKEN_BOT_DISCORD")
server = os.getenv("SERVER_ID")

bot = Client(intents=Intents.DEFAULT)
limite = 2

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

@slash_command(name="setlimite", description="Permet de règler le nombre d'embed à afficher (default = 2)", scopes=server)
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

@slash_command(name="bt", description="Permet d'avoir un bouton.", scopes=server)
async def setLimite(ctx: SlashContext):
    embed = Embed()
    embed.title = "Titre"
    embed.description = "Description"
    
    button = Button(
        style=ButtonStyle.PRIMARY,
        custom_id = "123467890",
        label = "Bouton."
    )
    

    action_row = ActionRow(button)
    await ctx.send(embeds=[embed], components=[action_row])

@listen(Component)
async def on_component(event: Component):
    ctx = event.ctx

    match ctx.custom_id:
        case "123467890":
            await ctx.send("You clicked it!")







def getName(author) -> str:
    """Permet d'obtenir le nickname si défini sinon le username"""
    return author.nickname if author.nickname else author.username


def getFilere(author) -> Filiere:
    print(Filiere.INGE.value)
    for role in author.roles:
        if role.name == Filiere.INGE.value:
            return Filiere.INGE
        if role.name == Filiere.MIAGE.value:
            return Filiere.MIAGE
    return None


def getGroupeTP(author) -> TP:
    for role in author.roles:
        for tp in TP:
            if role.name == tp.value:
                return tp
        
    return None


def getGroupeTD(author) -> TD:
    for role in author.roles:
        for td in TD:
            if role.name == td.value:
                return td
    return None

def getGroupeTDAnglais(author) -> TDAnglais:
    for role in author.roles:
        for tda in TDAnglais:
            if role.name == tda.value:
                return tda
    return None

bot.start(token)
