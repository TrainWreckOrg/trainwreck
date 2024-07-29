from interactions import ActionRow, Button, ButtonStyle, Client, Embed, Intents, listen, slash_command, SlashContext, OptionType, slash_option, client, User
from interactions.api.events import Component
from TrainWreck import GroupFilter, get_embeds, Filiere, Group, Timing, FiliereFilter, TimeFilter, get_events, filter_events, ascii
from dotenv import load_dotenv
import os
from datetime import datetime, date, timedelta
import re

load_dotenv("cle.env")

token = os.getenv("TOKEN_BOT_DISCORD")
server = os.getenv("SERVER_ID")
bot = Client(token=token,intents=Intents.DEFAULT, sync_interactions=True)
channel = None


@listen(Component)
async def on_component(event: Component):
    """Fonction permettant d'écouter les cliques des boutons"""
    try:
        ctx = event.ctx
        pattern_day = re.compile("day-")
        pattern_week = re.compile("week-")
        if pattern_day.search(ctx.custom_id):
             await get_day_bt(ctx,ctx.custom_id[4:])
        elif pattern_week.search(ctx.custom_id):
            await get_week_bt(ctx,ctx.custom_id[5:])
        else:
            await ctx.send("Bouton cliqué mais aucune action définie")
    except BaseException as error:
        await send_error("on_component",error, ctx, bouton = event.ctx.custom_id)



        
@slash_command(name="get_day", description="Permet d'avoir l'emploi du temps pour une journée", scopes=server)
@slash_option(
    name="jour",
    description="Quel jour ? (DD-MM-YYYY)",
    required=True,
    opt_type=OptionType.STRING
)
async def get_day(ctx: SlashContext, jour : str):
    """Fonction qui permet d'obtenir l'edt d'une journée spécifique"""
    try:
        await get_day_bt(ctx, jour)
    except BaseException as error:
        await send_error("get_day",error, ctx, jour=jour)



async def get_day_bt(ctx, jour : str):
    """Fonction qui permet d'obtenir l'edt d'une journée spécifique"""
    try :
        date_formater = datetime.strptime(jour, "%d-%m-%Y").date()
        events = filter_events(get_events(), [TimeFilter(date_formater, Timing.DURING), get_filiere(ctx.author), get_groupes(ctx.author)] )
        embeds = get_embeds(events)
        await ctx.send(embeds=embeds)
    except ValueError:
        await ctx.send(embeds=[create_error_embed(f"La valeur `{jour}` ne correspond pas à une date")])
    except BaseException as error:
        await send_error("get_day_bt",error, ctx, jour=jour)


@slash_command(name="today", description="Permet d'avoir l'emploie du temps pour aujourd'hui", scopes=server)
async def today(ctx: SlashContext):
    """Fonction qui permet d'obtenir l'edt d'ajourd'hui"""
    try:
        events = filter_events(get_events(), [TimeFilter(date.today(), Timing.AFTER), TimeFilter(date.today(), Timing.BEFORE),get_filiere(ctx.author), get_groupes(ctx.author)] )
        embeds = get_embeds(events)
        button = Button(
            style=ButtonStyle.PRIMARY,
            custom_id = "day-" + (date.today() + timedelta(days=1)).strftime("%d-%m-%Y"),
            label = "Demain"
        )

        action_row = ActionRow(button)
        await ctx.send(embeds=embeds, components=[action_row])
    except BaseException as error:
        await send_error("today", error, ctx)



@slash_command(name="tomorrow", description="Permet d'avoir l'emploie du temps pour demain", scopes=server)
async def tomorrow(ctx: SlashContext):
    """Fonction qui permet d'obtenir l'edt de demain"""
    try:
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
    except BaseException as error:
        await send_error("tomorrow", error, ctx)



@slash_command(name="info", description="Donne les infos sur l'utilisateur.", scopes=server)
async def info(ctx: SlashContext):
    """Fonction qui permet d'afficher le nom, la filière et les groupes de la personne"""
    try:
        str_role = ""
        for groupe in get_groupes(ctx.author).groups:
            str_role += groupe.value + ", "
        str_role = str_role.removesuffix(", ")
        await ctx.send(f"Vous êtes {get_name(ctx.author)}!\nVotre filière est {get_filiere(ctx.author).filiere.value} et vos groupes sont {str_role}.")
    except BaseException as error:
        await send_error("info",error, ctx)



@slash_command(name="get_week", description="Permet d'avoir l'emploi du temps pour une semaine", scopes=server)
@slash_option(
    name="semaine",
    description="Quel semaine ? (DD-MM-YYYY)",
    required=True,
    opt_type=OptionType.STRING
)
async def get_week(ctx: SlashContext, semaine : str):
    """Fonction qui permet d'obtenir l'edt d'une semaine spécifique"""
    try:
        await get_week_bt(ctx, semaine)
    except BaseException as error:
        await send_error("get_week",error, ctx, semaine=semaine)


async def get_week_bt(ctx: SlashContext, semaine : str):
    """Fonction qui permet d'obtenir l'edt d'une semaine spécifique"""
    try:
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
    except BaseException as error:
        await send_error("get_week_bt",error, ctx, semaine=semaine)


@slash_command(name="week", description="Permet d'avoir l'emploie du temps pour la semaine", scopes=server)
async def week(ctx: SlashContext):
    """Fonction qui permet d'obtenir l'edt de cette semaine"""
    try:
        date_formater = date.today()
        days_since_monday = date_formater.weekday()
        monday_date = date_formater - timedelta(days=days_since_monday)
        sunday_date = monday_date + timedelta(days=6)
        events = filter_events(
            get_events(),
            [TimeFilter(monday_date, Timing.AFTER), TimeFilter(sunday_date, Timing.BEFORE), get_filiere(ctx.author),
             get_groupes(ctx.author)])
        embeds = get_embeds(events)
        button = Button(
            style=ButtonStyle.PRIMARY,
            custom_id = "week-" + (monday_date + timedelta(days=7)).strftime("%d-%m-%Y"),
            label = "Semaine prochaine"
        )
        action_row = ActionRow(button)
        await ctx.send(embeds=embeds, components=[action_row])
    except BaseException as error:
        await send_error("week",error, ctx)



@slash_command(name="about", description="Affiche la page 'About'", scopes=server)
async def about(ctx :SlashContext):
    """Affiche le Contenu de README.md"""
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            l = f.read()
        await ctx.send(ascii + l )
    except BaseException as error:
        await send_error("about",error, ctx)



@slash_command(name="dm", description="tries to dm the user", scopes=server)
async def dm(ctx :SlashContext):
    """tries to dm the user"""
    try:
        dany = bot.get_user(776867184420716584)
        nathan = bot.get_user()
        try :
            await dany.send("👀 est ce que ça a marché ?")
            await ctx.send("done :)")
        except :
            await ctx.send("no :(")
    except BaseException as error:
       await send_error("dm",error, ctx)



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


async def send_error(channel_name, error, ctx, semaine=None, jour=None, bouton=None):
    message_erreur = f"ERREUR dans : {channel_name} - {datetime.now()}\nErreur de type : {type(error)}\nAgrument de l'erreur : {error.args}\nDescription de l'erreur : {error}\nLes paramètres de la fonction étais : \n - auteur : {ctx.author}\n - serveur :  {ctx.guild}\n - message :  {ctx.message}\n - channel :  {ctx.channel}\n - role member :  {ctx.member.roles}"
    if semaine:
        message_erreur += f"\n - semaine : {semaine}"
    if jour:
        message_erreur += f"\n - jour : {jour}"
    if bouton:
        message_erreur += f"\n - id_bouton : {bouton}"
    with open("output/error.log", "a") as f:
        f.write(message_erreur)
    await channel.send(f"<@&{os.getenv("ADMIN_ID")}> " + message_erreur)
    await ctx.send(embeds=[create_error_embed(
        "Une erreur est survenue, veuillez réessayer ultérieurement, l'équipe de modération est avertie du problème")])

@listen()
async def on_ready():
    """Fonction qui dit quand le bot est opérationel au démarage du programme"""
    print("Ready")
    print(f"This bot is owned by {bot.owner}")
    global channel
    channel = bot.get_channel(os.getenv("CHANNEL_ID"))
    await bot.synchronise_interactions()


bot.start()

