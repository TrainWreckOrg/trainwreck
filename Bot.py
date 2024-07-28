from interactions import ActionRow, ButtonStyle, Client, Embed, Intents, listen
from interactions import slash_command, SlashContext, OptionType, slash_option
from interactions import Button, ButtonStyle
from interactions.api.events import Component
from HorrendousTimeTableExtractor import GroupFilter, get_embeds, Filiere, Group, Timing, FiliereFilter, TimeFilter, get_events, filter_events
from dotenv import load_dotenv
import os
from datetime import datetime, date, timedelta
import re

load_dotenv("cle.env")

token = os.getenv("TOKEN_BOT_DISCORD")
server = os.getenv("SERVER_ID")

bot = Client(token=token,intents=Intents.DEFAULT, sync_interactions=True)


@listen(Component)
async def on_component(event: Component):
    """Fonction permettant d'écouter les cliques des boutons"""
    ctx = event.ctx
    pattern_day = re.compile("day-")
    pattern_week = re.compile("week-")
    if pattern_day.search(ctx.custom_id):
         await get_day_bt(ctx,ctx.custom_id[4:])
    elif pattern_week.search(ctx.custom_id):
        await ctx.send(ctx.custom_id[5:])
    else:
        await ctx.send("Bouton cliqué mais aucune action définie")

        
@slash_command(name="get_day", description="Permet d'avoir l'emploi du temps pour une journée", scopes=server)
@slash_option(
    name="jour",
    description="Quel jour ? (DD-MM-YYYY)",
    required=True,
    opt_type=OptionType.STRING
)
async def get_day(ctx: SlashContext, jour : str):
    """Fonction qui permet d'obtenir l'edt d'une journée spécifique"""
    await get_day_bt(ctx, jour)


async def get_day_bt(ctx, jour : str):
    """Fonction qui permet d'obtenir l'edt d'une journée spécifique"""
    try :
        date_formater = datetime.strptime(jour, "%d-%m-%Y").date()
        events = filter_events(get_events(), [TimeFilter(date_formater, Timing.DURING), get_filiere(ctx.author), get_groupes(ctx.author)] )
        embeds = get_embeds(events)
        await ctx.send(embeds=embeds)
    except ValueError:
        await ctx.send(embeds=[create_error_embed(f"La valeur `{jour}` ne correspond pas à une date")])

@slash_command(name="today", description="Permet d'avoir l'emploie du temps pour aujourd'hui", scopes=server)
async def today(ctx: SlashContext):
    """Fonction qui permet d'obtenir l'edt d'ajourd'hui"""
    
    events = filter_events(get_events(), [TimeFilter(date.today(), Timing.AFTER), TimeFilter(date.today(), Timing.BEFORE),get_filiere(ctx.author), get_groupes(ctx.author)] )
    embeds = get_embeds(events)
    button = Button(
        style=ButtonStyle.PRIMARY,
        custom_id = "day-" + (date.today() + timedelta(days=1)).strftime("%d-%m-%Y"),
        label = "Demain"
    )
    
    action_row = ActionRow(button)
    await ctx.send(embeds=embeds, components=[action_row])


@slash_command(name="tomorrow", description="Permet d'avoir l'emploie du temps pour demain", scopes=server)
async def tomorrow(ctx: SlashContext):
    """Fonction qui permet d'obtenir l'edt de demain"""

    events = filter_events(
        get_events(),
        [TimeFilter(date.today() + timedelta(days=1), Timing.AFTER), TimeFilter(date.today() + timedelta(days=1), Timing.BEFORE), get_filiere(ctx.author),
         get_groupes(ctx.author)])
    embeds = get_embeds(events)
    button = Button(
        style=ButtonStyle.PRIMARY,
        custom_id = "day-" + date.today().strftime("%d-%m-%Y"),
        label = "Ajourd'hui"
    )
    
    action_row = ActionRow(button)
    await ctx.send(embeds=embeds, components=[action_row])


@slash_command(name="info", description="Donne les infos sur l'utilisateur.", scopes=server)
async def info(ctx: SlashContext):
    """Fonction qui permet d'afficher le nom, la filière et les groupes de la personne"""
    str_role = ""
    for groupe in get_groupes(ctx.author).groups:
        str_role += groupe.value + ", "
    str_role = str_role.removesuffix(", ")
    await ctx.send(f"Vous êtes {get_name(ctx.author)}!\nVotre filière est {get_filiere(ctx.author).filiere.value} et vos groupes sont {str_role}.")


@slash_command(name="get_week", description="Permet d'avoir l'emploi du temps pour une semaine", scopes=server, )
@slash_option(
    name="semaine",
    description="Quel semaine ? (DD-MM-YYYY)",
    required=True,
    opt_type=OptionType.STRING
)
async def get_week(ctx: SlashContext, semaine : str):
    """Fonction qui permet d'obtenir l'edt d'une semaine spécifique"""
    date_formater = datetime.strptime(semaine, "%d-%m-%Y").date()
    days_since_monday = date_formater.weekday()
    monday_date = date_formater - timedelta(days=days_since_monday)
    sunday_date = monday_date + timedelta(days=6)
    events = filter_events(
        get_events(),
        [TimeFilter(monday_date, Timing.AFTER), TimeFilter(sunday_date, Timing.BEFORE), get_filiere(ctx.author),
         get_groupes(ctx.author)])
    embeds = get_embeds(events)
    await ctx.send(embeds=embeds)


@slash_command(name="week", description="Permet d'avoir l'emploie du temps pour la semaine", scopes=server)
async def week(ctx: SlashContext):
    """Fonction qui permet d'obtenir l'edt de cette semaine"""
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
        custom_id = "week-" + next_monday.strftime("%d-%m-%Y"),
        label = "Semaine prochaine"
    )
    
    action_row = ActionRow(button)
    await ctx.send(embeds=[embed], components=[action_row])



def get_name(author) -> str:
    """Permet d'obtenir le nickname si défini sinon le username"""
    return author.nickname if author.nickname else author.username


def get_filiere(author) -> FiliereFilter:
    """Fonction qui permet d'avoir la filière d'un utilisateur, renvoie None si pas définie"""
    for role in author.roles:
        if role.name == Filiere.INGE.value:
            return FiliereFilter(Filiere.INGE)
        if role.name == Filiere.MIAGE.value:
            return FiliereFilter(Filiere.MIAGE)
    return None


def get_groupes(author) -> GroupFilter:
    """Fonction qui renvoie le tableau des groupe d'un utilisateur"""
    out = [Group.CM]
    for role in author.roles:
        for gr in Group:
            if role.name == gr.value:
                out.append(gr)
    return GroupFilter(out)

def create_error_embed(message:str) -> Embed:
    return Embed(":warning: Erreur: ", message, 0x992d22)

@listen() 
async def on_ready():
    """Fonction qui dit quand le bot est opérationel au démarage du programme"""
    print("Ready")
    print(f"This bot is owned by {bot.owner}")
    await bot.synchronise_interactions()


bot.start()
