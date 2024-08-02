from interactions import ActionRow, Button, ButtonStyle, Client, Intents, listen, slash_command, SlashContext, OptionType, slash_option, SlashCommandChoice, Task, TimeTrigger, OrTrigger, Guild, Role, Permissions, Embed, EmbedFooter, User, contexts
from interactions.api.events import Component, MemberUpdate


from Enums import Filiere, Group, Timing, Subscription, ascii_logo
from Calendar import get_calendar, Calendar, changed_events
from TrainWreck import get_embeds, get_ics
from UserBase import get_user_base
from Filter import *

from datetime import datetime, date, timedelta
from dotenv import load_dotenv
from enum import Enum
import os
import re

load_dotenv("cle.env")
token = os.getenv("TOKEN_BOT_DISCORD")
bot = Client(token=token, intents= Intents.ALL, sync_interactions=True) #TODO : enleve ALL


@listen(Component)
async def on_component(event: Component):
    """Fonction permettant d'écouter les cliques des boutons"""
    #try:
    ctx = event.ctx
    pattern_day = re.compile("day-")
    pattern_week = re.compile("week-")
    if pattern_day.search(ctx.custom_id):
        await get_day_bt(ctx,ctx.custom_id[4:], True)
    elif pattern_week.search(ctx.custom_id):
        await get_week_bt(ctx,ctx.custom_id[5:], True)
    else:
        await ctx.send("Bouton cliqué mais aucune action définie")
        raise ValueError("Bouton cliqué mais aucune action définie")
    #except BaseException as error:
        #await send_error("on_component",error, event.ctx, bouton = event.ctx.custom_id)


async def get_day_bt(ctx, jour : str, modifier: bool, personne: User = None):
    """Fonction qui permet d'obtenir l'EDT d'une journée spécifique"""
    try:
        author = ctx.author if (personne is None) else personne

        date_formater = datetime.strptime(jour, "%d-%m-%Y").date()

        events :list[Event] = []
        if author.id == os.getenv("BOT_ID"):
            events = filter_events(get_calendar().get_events(), [TimeFilter(date_formater, Timing.DURING)])
        else :
            events = filter_events(get_calendar().get_events(), [TimeFilter(date_formater, Timing.DURING), get_filiere(author), get_groupes(author)])
        embeds = get_embeds(events, author, date_formater)

        precedent = Button(
            style=ButtonStyle.PRIMARY,
            custom_id="day-" + (date_formater - timedelta(days=1)).strftime("%d-%m-%Y"),
            label="Jour précédent"
        )

        suivant = Button(
            style=ButtonStyle.PRIMARY,
            custom_id="day-" + (date_formater + timedelta(days=1)).strftime("%d-%m-%Y"),
            label="Jour suivant"
        )

        if personne is None:
            action_row = ActionRow(precedent, suivant)
            if modifier:
                await ctx.edit_origin(embeds=embeds, components=[action_row])
            else:
                await ctx.send(embeds=embeds, components=[action_row])
        else:
            if modifier:
                await ctx.edit_origin(embeds=embeds)
            else:
                await ctx.send(embeds=embeds)

    except ValueError:
        await ctx.send(embeds=[create_error_embed(f"La valeur `{jour}` ne correspond pas à une date")], )
    # except BaseException as error:
    # await send_error("get_day_bt",error, ctx, jour=jour)


@slash_command(name="get_day", description="Envoie votre EDT pour un jour donné. Si une personne est donnée, donne l'EDT de cette personne")
@slash_option(
    name="jour",
    description="Quel jour ? (DD-MM-YYYY)",
    required=True,
    opt_type=OptionType.STRING
)
@slash_option(
    name="personne",
    description="Quel utilisateur ?",
    required=False,
    opt_type=OptionType.USER
)
async def get_day(ctx: SlashContext, jour : str, personne: User = None):
    """Fonction qui permet d'obtenir l'EDT d'une journée spécifique"""
    #try:
    await get_day_bt(ctx, jour, False, personne)
    #except BaseException as error:
    #    await send_error("get_day",error, ctx, jour=jour)


@slash_command(name="today", description="Envoie votre EDT du jour")
async def today(ctx: SlashContext):
    """Fonction qui permet d'obtenir l'EDT d'ajourd'hui"""
    #try:
    await get_day_bt(ctx, date.today().strftime("%d-%m-%Y"), False)

    #except BaseException as error:
        #await send_error("today", error, ctx)


@slash_command(name="tomorrow", description="Envoie votre EDT du lendemain")
async def tomorrow(ctx: SlashContext):
    """Fonction qui permet d'obtenir l'EDT de demain"""
    #try:
    await get_day_bt(ctx, (date.today() + timedelta(days=1)).strftime("%d-%m-%Y"), False)
    #except BaseException as error:
        #await send_error("tomorrow", error, ctx)



@slash_command(name="info", description="Envoie des infos sur vos groupes, et filière. Si une personne est donnée, donne ses informations")
@slash_option(
    name="personne",
    description="Quel utilisateur ?",
    required=False,
    opt_type=OptionType.USER
)
async def info(ctx: SlashContext, personne:User = None):
    """Fonction qui permet d'afficher le nom, la filière et les groupes de la personne"""
    #try:
    author = ctx.author if (personne is None) else personne
    you_are = personne is None
    str_role = ""
    for groupe in get_groupes_as_list(author):
        str_role += groupe.value + ", "
    str_role = str_role.removesuffix(", ")
    await ctx.send(f"{"Vous êtes" if you_are else "Informations sur"} {author.display_name}!\n{"Votre" if you_are else "Sa"} filière est {get_filiere_as_filiere(ctx.author).value} et {"vos" if you_are else "ses"} groupes {"sont" if len(get_groupes_as_list(ctx.author)) > 1 else "est"} {str_role}.")
    #except BaseException as error:
        #await send_error("info",error, ctx)


async def get_week_bt(ctx: SlashContext, semaine : str, modifier: bool, personne: User = None):
    """Fonction qui permet d'obtenir l'EDT d'une semaine spécifique"""
    try:
        author = ctx.author if (personne is None) else personne

        date_formater = datetime.strptime(semaine, "%d-%m-%Y").date()
        days_since_monday = date_formater.weekday()
        monday_date = date_formater - timedelta(days=days_since_monday)
        sunday_date = monday_date + timedelta(days=6)
        events :list[Event] = []
        if author.id == os.getenv("BOT_ID"):
            events = filter_events(get_calendar().get_events(),[TimeFilter(monday_date, Timing.AFTER), TimeFilter(sunday_date, Timing.BEFORE)])
        else :
            events = filter_events(get_calendar().get_events(), [TimeFilter(monday_date, Timing.AFTER), TimeFilter(sunday_date, Timing.BEFORE), get_filiere(author), get_groupes(author)])

        embeds = get_embeds(events, author, monday_date, sunday_date)

        precedent = Button(
            style=ButtonStyle.PRIMARY,
            custom_id="week-" + (monday_date - timedelta(days=1)).strftime("%d-%m-%Y"),
            label="Semaine précédente"
        )

        suivant = Button(
            style=ButtonStyle.PRIMARY,
            custom_id="week-" + (sunday_date + timedelta(days=1)).strftime("%d-%m-%Y"),
            label="Semaine suivante"
        )

        if personne is None:
            action_row = ActionRow(precedent, suivant)
            if modifier:
                await ctx.edit_origin(embeds=embeds, components=[action_row])
            else:
                await ctx.send(embeds=embeds, components=[action_row])
        else:
            if modifier:
                await ctx.edit_origin(embeds=embeds)
            else:
                await ctx.send(embeds=embeds)
    except ValueError:
        await ctx.send(embeds=[create_error_embed(f"La valeur `{semaine}` ne correspond pas à une date")], )
    #except BaseException as error:
        #await send_error("get_week_bt",error, ctx, semaine=semaine)


@slash_command(name="get_week", description="Envoie votre EDT pour la semaine de la date, si une personne est donnée, donne le sien")
@slash_option(
    name="semaine",
    description="Quel semaine ? (DD-MM-YYYY)",
    required=True,
    opt_type=OptionType.STRING
)
@slash_option(
    name="personne",
    description="Quel utilisateur ?",
    required=False,
    opt_type=OptionType.USER
)
async def get_week(ctx: SlashContext, semaine : str, personne:User = None):
    """Fonction qui permet d'obtenir l'EDT d'une semaine spécifique"""
    #try:
    await get_week_bt(ctx, semaine, False, personne)
    #except BaseException as error:
        #await send_error("get_week",error, ctx, semaine=semaine)


@slash_command(name="week", description="Envoie votre EDT de la semaine")
async def week(ctx: SlashContext):
    """Fonction qui permet d'obtenir l'EDT de cette semaine"""
    #try:
    await get_week_bt(ctx, date.today().strftime("%d-%m-%Y"), False)
    #except BaseException as error:
        #await send_error("week",error, ctx)


@slash_command(name="help", description="Affiche la page d'Aide")
async def help(ctx :SlashContext):
    """Affiche le Contenu de HELP.md"""
    #try:
    with open("HELP.md", "r", encoding="utf-8") as f:
        help = f.read()
    await ctx.send(embed = Embed(description=help, footer=EmbedFooter("Les EDT sont fournis a titre informatif uniquement -> Veuillez vous référer à votre page personnelle sur l'ENT", bot.user.avatar_url), color=0xd8a74c))
    #except BaseException as error:
        #await send_error("about",error, ctx)

@slash_command(name="ics", description="Envoie un fichier ICS importable dans la plupart des applications de calendrier")
@slash_option(
    name="debut",
    description="Quelle est la date de début ? (DD-MM-YYYY)",
    required=True,
    opt_type=OptionType.STRING
)
@slash_option(
    name="fin",
    description="Quelle est la date de fin ? (DD-MM-YYYY)",
    required=True,
    opt_type=OptionType.STRING
)
async def ics(ctx :SlashContext, debut : str, fin : str):
    """Génère l'ics"""
    try:
        date_debut = datetime.strptime(debut, "%d-%m-%Y").date()
        date_fin = datetime.strptime(fin, "%d-%m-%Y").date()
        get_ics(filter_events(get_calendar().get_events(), [TimeFilter(date_debut, Timing.AFTER), TimeFilter(date_fin, Timing.BEFORE), get_filiere(ctx.author), get_groupes(ctx.author)]))
        await ctx.send("Voici votre fichier ics", files=["output/calendar.ics"])
    except ValueError:
        await ctx.send(embeds=[create_error_embed(f"La valeur `{debut}` ou `{fin}` ne correspond pas à une date")])
    #except BaseException as error:
       #await send_error("ics",error, ctx)

@slash_command(name="subscribe", description="Vous permet de vous abonner à l'envoi de l'EDT dans vos DM, de manière quotidienne ou hebdomadaire")
@slash_option(
    name="service",
    description="mise a jour Quotidienne `DAILY`, Hebdomadaire `WEEKLY`, ou les deux `BOTH`",
    required=True,
    opt_type=OptionType.STRING,
    choices=[
        SlashCommandChoice(name="Daily", value="DAILY"),
        SlashCommandChoice(name="Weekly", value="WEEKLY"),
        SlashCommandChoice(name="Both", value="BOTH")
    ]
)
async def subscribe(ctx :SlashContext, service: str):
    user_base = get_user_base()
    id = ctx.author_id
    if not user_base.has_user(ctx.author_id):
        user_base.add_user(id, get_groupes_as_list(ctx.author), get_filiere_as_filiere(ctx.author))
    match service:
        case "DAILY":
            user_base.user_subscribe(id, Subscription.DAILY)
        case "WEEKLY":
            user_base.user_subscribe(id, Subscription.WEEKLY)
        case "BOTH":
            user_base.user_subscribe(id, Subscription.BOTH)
    await ctx.send(embed=Embed(f"Abonnements de {ctx.author.display_name}", f"- Mise à Jour Quotidienne : {'✅' if (user_base.is_user_subscribed(id, Subscription.DAILY)) else '❌'}\n- Mise à Jour Hebdomadaire : {'✅' if (user_base.is_user_subscribed(id, Subscription.WEEKLY)) else '❌'}"))


@slash_command(name="unsubscribe", description="Vous permet de vous desabonner à l'envoi de l'EDT dans vos DM")
@slash_option(
    name="service",
    description="mise a jour Quotidienne `DAILY`, Hebdomadaire `WEEKLY`, ou les deux `BOTH`",
    required=True,
    opt_type=OptionType.STRING,
    choices=[
        SlashCommandChoice(name="Daily", value="DAILY"),
        SlashCommandChoice(name="Weekly", value="WEEKLY"),
        SlashCommandChoice(name="Both", value="BOTH")
    ]
)
async def unsubscribe(ctx :SlashContext, service: str):
    user_base = get_user_base()
    id = ctx.author_id
    if not user_base.has_user(ctx.author_id):
        user_base.add_user(id, get_groupes_as_list(ctx.author), get_filiere_as_filiere(ctx.author))
    match service:
        case "DAILY":
            user_base.user_unsubscribe(id, Subscription.DAILY)
        case "WEEKLY":
            user_base.user_unsubscribe(id, Subscription.WEEKLY)
        case "BOTH":
            user_base.user_unsubscribe(id, Subscription.BOTH)
    await ctx.send(embed=Embed(f"Abonnements de {ctx.author.display_name}", f"- Mise à Jour Quotidienne : {'✅' if (user_base.is_user_subscribed(id, Subscription.DAILY)) else '❌'}\n- Mise à Jour Hebdomadaire : {'✅' if (user_base.is_user_subscribed(id, Subscription.WEEKLY)) else '❌'}"))
    
@slash_command(name="check_subscription", description="Vous permet de consulter à quels service d'envoi d'EDT vous êtes inscrit")
async def check_subscription(ctx :SlashContext):
    user_base = get_user_base()
    id = ctx.author_id
    await ctx.send(embed=Embed(f"Abonnements de {ctx.author.display_name}", f"- Mise à Jour Quotidienne : {'✅' if (user_base.is_user_subscribed(id, Subscription.DAILY)) else '❌'}\n- Mise à Jour Hebdomadaire : {'✅' if (user_base.is_user_subscribed(id, Subscription.WEEKLY)) else '❌'}"))


async def send_daily_update(user):
    events = filter_events(get_calendar().get_events(), [TimeFilter(date.today(), Timing.DURING), get_filiere(user), get_groupes(user)] )
    embeds = get_embeds(events, user, date.today())
    await user.send(embeds=embeds)

async def send_weekly_update(user):
    days_since_monday = datetime.today().weekday()
    monday_date = datetime.today() - timedelta(days=days_since_monday)
    sunday_date = monday_date + timedelta(days=6)

    events = filter_events (get_calendar().get_events(), [TimeFilter(monday_date, Timing.AFTER), TimeFilter(sunday_date, Timing.BEFORE), get_filiere(user), get_groupes(user)])
    ics_file = get_ics(events)
    await user.send(embeds=get_embeds(events, user, monday_date, sunday_date), files=["output/calendar.ics"])

@Task.create(TimeTrigger(hour=6, minute=0, utc=False))
async def daily_morning_update():
    user_base = get_user_base()
    if datetime.today().weekday() == 0:
        for id in user_base.weekly_subscribed_users:
            await send_daily_update(bot.get_user(id))
    if datetime.today().weekday() > 4:  # Si on est le week end
        for id in user_base.daily_subscribed_users:
            await send_daily_update(bot.get_user(id))


def ping_liste(event):
    global roles
    ping = ""
    if event.group == Group.CM:
        if event.isINGE and event.isMIAGE:
            ping += f"<@&{roles[Filiere.INGE].id}> <@&{roles[Filiere.MIAGE].id}>"
        elif event.isINGE:
            ping += f"<@&{roles[Filiere.INGE].id}>"
        else:
            ping += f"<@&{roles[Filiere.MIAGE].id}>"
    else:
        ping += f"<@&{roles[event.group].id}>"
    return ping


@Task.create(OrTrigger(
        TimeTrigger(hour=5,  minute=55, utc=False),
        TimeTrigger(hour=7,  minute=0,  utc=False),
        TimeTrigger(hour=8,  minute=0,  utc=False),
        TimeTrigger(hour=10, minute=0,  utc=False), 
        TimeTrigger(hour=12, minute=0,  utc=False), 
        TimeTrigger(hour=14, minute=0,  utc=False), 
        TimeTrigger(hour=16, minute=0,  utc=False), 
        TimeTrigger(hour=18, minute=0,  utc=False), 
        TimeTrigger(hour=20, minute=0,  utc=False)
    ))
async def update_calendar():
    # sup :set[Event]         = set()
    # add :set[Event]         = set()
    # mod :set[(Event,Event)] = set()
    old_calendar = Calendar(False)
    new_calendar = Calendar(True)
    
    sup, add, mod = changed_events(old_calendar, new_calendar)
    embeds : list[Embed] = []

    if len(sup) > 0:
        descstr = ""
        for event in sup:
            descstr += f"- {ping_liste(event)} {str(event)}\n"
        embeds.append(Embed(title="Événements supprimés :", description=descstr, color=0xEd4245))

    if len(add) > 0:
        descstr = ""
        for event in add:
            descstr += f"- {ping_liste(event)} {str(event)}\n"
        embeds.append(Embed(title="Événements ajoutés :", description=descstr, color=0x57f287))

    if len(mod) > 0:
        descstr = ""
        for (old, new) in mod:
            ping = ping_liste(old)
            if old.group != new.group:
                ping += f" {ping_liste(new)}"
            descstr += f"- {ping} {str(old)} → {str(new)}\n"
        embeds.append(Embed(title="Événements modifiés :", description=descstr, color=0x5865f2))

    if len(embeds):
        global ping_chan
        await ping_chan.send(embeds=embeds)
        

@slash_command(name="userscan", description="Permet d'ajouter tout les membres dans la BD", default_member_permissions= Permissions.ADMINISTRATOR)
@contexts(guild=True, bot_dm=False)
async def userscan(ctx :SlashContext):
    guild = ctx.guild
    user_base = get_user_base()
    for user in guild.members:
        if not user_base.has_user(user.id):
            user_base.add_user(user.id, get_groupes_as_list(user), get_filiere_as_filiere(user))
        else:
            user_base.update_user_groups(user.id, get_groupes_as_list(user))
    await ctx.send("Les membres du serveur ont été ajoutée et mit à jour")


def get_filiere(author) -> FiliereFilter:
    """Fonction qui permet d'avoir le filtre filière d'un utilisateur, renvoie un filtre neutre si pas défini"""
    if is_guild_chan(author):
        roles = author.roles
        for role in roles:
            if role.name == Filiere.INGE.value:
                return FiliereFilter(Filiere.INGE)
            if role.name == Filiere.MIAGE.value:
                return FiliereFilter(Filiere.MIAGE)
    elif get_user_base().has_user(author.id):
        return FiliereFilter(get_user_base().get_user(author.id).filiere)
    return Filter()

def get_filiere_as_filiere(author) -> Filiere:
    """Fonction qui permet d'avoir la filière d'un utilisateur, renvoie UKNW si pas définie"""
    if is_guild_chan(author):
        roles = author.roles
        for role in roles:
            if role.name == Filiere.INGE.value:
                return Filiere.INGE
            if role.name == Filiere.MIAGE.value:
                return Filiere.MIAGE
    elif get_user_base().has_user(author.id):
        return get_user_base().get_user(author.id).filiere
    return Filiere.UKNW

def get_groupes(author) -> GroupFilter:
    """Fonction qui renvoie un filtre des groupes d'un utilisateur"""
    if is_guild_chan(author):
        out = [Group.CM]
        for role in author.roles:
            for gr in Group:
                if role.name == gr.value:
                    out.append(gr)
        return GroupFilter(out)
    elif get_user_base().has_user(author.id):
        return GroupFilter(get_user_base().get_user(author.id).groups)
    else :
        return GroupFilter([Group.CM])

def get_groupes_as_list(author) -> list[Group]:
    """Fonction qui renvoie un filtre des groupes d'un utilisateur"""
    if is_guild_chan(author):
        out = [Group.CM]
        for role in author.roles:
            for gr in Group:
                if role.name == gr.value:
                    out.append(gr)
        return out
    elif get_user_base().has_user(author.id):
        return get_user_base().get_user(author.id).groups
    else :
        return [Group.CM]

def is_guild_chan(author) -> bool:
    return "Member" in str(type(author))


def create_error_embed(message:str) -> Embed:
    return Embed(":warning: Erreur: ", message, 0x992d22)


async def send_error(channel_name, error, ctx, semaine=None, jour=None, bouton=None):
    global channel
    message_erreur = f"ERREUR dans : {channel_name} - {datetime.now()}\nErreur de type : {type(error)}\nArgument de l'erreur : {error.args}\nDescription de l'erreur : {error}\nLes paramètres de la fonction étais : \n - auteur : {ctx.author}\n - serveur :  {ctx.guild}\n - message :  {ctx.message}\n - channel :  {ctx.channel}\n - role member :  {ctx.member.roles}"
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
    """Fonction qui dit quand le bot est opérationnel au démarrage du programme"""
    print("Ready")
    print(f"This bot is owned by {bot.owner}")
    await bot.synchronise_interactions()
    daily_morning_update.start()
    await update_calendar()
    update_calendar.start()



@listen(MemberUpdate)
async def on_member_update(event: MemberUpdate):
    user_base = get_user_base()
    user = event.after
    if not user_base.has_user(user.id):
        user_base.add_user(user.id, get_groupes_as_list(user), get_filiere_as_filiere(user))
    else :
        user_base.update_user_groups(user.id, get_groupes_as_list(user))


bot.start()

channel = bot.get_channel(os.getenv("CHANNEL_ID"))
ping_chan = bot.get_channel(os.getenv("PING_CHAN"))
serveur : Guild = bot.get_guild(os.getenv("SERVEUR_ID"))
roles : dict[Enum:Role] = {}

for role in serveur.roles:
    if role.name in Group:
        for groupe in Group:
            if groupe.value == role.name:
                roles[groupe] = role
    if role.name in Filiere:
        for filiere in Filiere:
            if filiere.value == role.name:
                roles[filiere] = role