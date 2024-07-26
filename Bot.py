from email.policy import default
from interactions import ActionRow, ButtonStyle, Client, Embed, Intents, listen
from interactions import slash_command, SlashContext, OptionType, slash_option
from interactions import Button, ButtonStyle
from interactions.api.events import Component
from interactions import Button, ButtonStyle
from interactions.api.events import Component

from HorrendousTimeTableExtractor import getCalendar, Filiere, Group
from dotenv import load_dotenv
import os
import datetime


load_dotenv("cle.env")


token = os.getenv("TOKEN_BOT_DISCORD")
server = os.getenv("SERVER_ID")

bot = Client(token=token,intents=Intents.DEFAULT, sync_interactions=True)
limite = 2



@listen()
async def on_message_create(event):
    """This event is called when a message is sent in a channel the bot can see"""
    print(f"message received: {event.message.jump_url}")





@slash_command(name="bonjour", description="Te dit bonjour.", scopes=server)
async def bonjour(ctx: SlashContext):
    await ctx.send(f"Bonjour {getName(ctx.author)}!")


@slash_command(name="bouton", description="Permet d'avoir un bouton.", scopes=server)
async def bouton(ctx: SlashContext):
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
        case _:
            await ctx.send(ctx.custom_id)
        



@slash_command(name="date", description="Permet d'avoir l'emploi du temps pour une journée'", scopes=server)
@slash_option(
    name="date",
    description="Quel jour ?",
    required=True,
    opt_type=OptionType.STRING
)
async def date(ctx: SlashContext, date : str):
    date_formater = datetime.datetime.strptime(date, "%Y-%m-%d")
    await ctx.send("EDT du " + date_formater.strftime("%A, %d %B %Y"))


@slash_command(name="day", description="Permet d'avoir l'emploie du temps pour aujourd'hui", scopes=server)
async def day(ctx: SlashContext):
    embed = Embed()
    embed.title = "Titre"
    embed.description = "Description"
    
    button = Button(
        style=ButtonStyle.PRIMARY,
        custom_id = "day-" + (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d"),
        label = "Demain"
    )
    
    action_row = ActionRow(button)
    await ctx.send(embeds=[embed], components=[action_row])


@slash_command(name="demain", description="Permet d'avoir l'emploie du temps pour demain", scopes=server)
async def demain(ctx: SlashContext):
    embed = Embed()
    embed.title = "Titre"
    embed.description = "Description"
    
    button = Button(
        style=ButtonStyle.PRIMARY,
        custom_id = "day-" + datetime.datetime.date(datetime.datetime.now()).strftime("%Y-%m-%d"),
        label = "Ajourd'hui"
    )
    
    action_row = ActionRow(button)
    await ctx.send(embeds=[embed], components=[action_row])




@slash_command(name="edt", description="L'emploi du temps en fonction de la limite.", scopes=server)
async def edt(ctx: SlashContext):
    compteur = 0
    calendar = getCalendar()
    global limite
    for day in calendar:
        if compteur >= limite:
            break
        compteur+=1
        await ctx.send(embed=day)


@slash_command(name="get_info", description="Donne les infos sur l'utilisateur.", scopes=server)
async def get_info(ctx: SlashContext):
    str_role = ""
    for groupe in getGroupe(ctx.author):
        str_role += groupe.value + ", "
    await ctx.send(f"Vous êtes {getName(ctx.author)}!\nVotre filière est {getFiliere(ctx.author).value} et vos groupes sont {str_role}.") 


@slash_command(name="semaine", description="Permet d'avoir l'emploi du temps pour une semaine", scopes=server)
@slash_option(
    name="date",
    description="Quel semaine ?",
    required=True,
    opt_type=OptionType.STRING
)
async def semaine(ctx: SlashContext, date : str):
    date = datetime.datetime.strptime(date, "%Y-%m-%d")
    
    days_since_monday = date.weekday() - 2
    monday_date = date - datetime.timedelta(days=days_since_monday)

    await ctx.send("EDT du " + monday_date.strftime("%Y-%m-%d"))


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




@slash_command(name="week", description="Permet d'avoir l'emploie du temps pour la semaine", scopes=server)
async def week(ctx: SlashContext):
    embed = Embed()
    embed.title = "Titre"
    embed.description = "Description"
    

    today = datetime.date.today()
    days_until_next_monday = (7 - today.weekday() + 0) % 7
    if days_until_next_monday == 0:
        days_until_next_monday = 7
    next_monday = today + datetime.timedelta(days=days_until_next_monday)


    button = Button(
        style=ButtonStyle.PRIMARY,
        custom_id = "week-" + next_monday.strftime("%Y-%m-%d"),
        label = "Semaine prochaine"
    )
    
    action_row = ActionRow(button)
    await ctx.send(embeds=[embed], components=[action_row])






def getName(author) -> str:
    """Permet d'obtenir le nickname si défini sinon le username"""
    return author.nickname if author.nickname else author.username


def getFiliere(author) -> Filiere:
    print(Filiere.INGE.value)
    for role in author.roles:
        if role.name == Filiere.INGE.value:
            return Filiere.INGE
        if role.name == Filiere.MIAGE.value:
            return Filiere.MIAGE
    return None


def getGroupe(author) -> list[Group]:
    out = []
    for role in author.roles:
        for gr in Group:
            if role.name == gr.value:
                out.append(gr)
    return out


@listen() 
async def on_ready():
    """Fonction qui dit quand le bot est opérationel au démarage du programme"""
    print("Ready")
    print(f"This bot is owned by {bot.owner}")
    await bot.synchronise_interactions()


bot.start()
