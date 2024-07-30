from interactions import ActionRow, Button, ButtonStyle, Client, Embed, Intents, listen, slash_command, SlashContext, OptionType, slash_option, SlashCommandChoice, Task, TimeTrigger, OrTrigger, IntervalTrigger
from interactions.api.events import Component, MemberUpdate
from TrainWreck import GroupFilter, get_embeds, Filiere, Group, Timing, Filter, FiliereFilter, TimeFilter, get_events, filter_events, ascii, get_user_base, UserBase, user_base, get_ics, User, Subscription
from dotenv import load_dotenv
import os
from datetime import datetime, date, timedelta
import re


load_dotenv("cle.env")

token = os.getenv("TOKEN_BOT_DISCORD")
server = os.getenv("SERVER_ID")
bot = Client(token=token, intents=Intents.DEFAULT | Intents.GUILD_MEMBERS, sync_interactions=True)
channel = None


@listen(Component)
async def on_component(event: Component):
    """Fonction permettant d'écouter les cliques des boutons"""
    #try:
    ctx = event.ctx
    pattern_day = re.compile("day-")
    pattern_week = re.compile("week-")
    if pattern_day.search(ctx.custom_id):
         await get_day_bt(ctx,ctx.custom_id[4:])
    elif pattern_week.search(ctx.custom_id):
        await get_week_bt(ctx,ctx.custom_id[5:])
    else:
        await ctx.send("Bouton cliqué mais aucune action définie")
    #except BaseException as error:
        #await send_error("on_component",error, event.ctx, bouton = event.ctx.custom_id)


@listen(MemberUpdate)
async def on_member_update(event: MemberUpdate):
    user_base = get_user_base()
    user = event.after
    if not user_base.has_user(user.id):
        user_base.add_user(user.id, get_groupes_as_list(user), get_filiere_as_filiere(user))
    else :
        user_base.update_user_groups(user.id, get_groupes_as_list(user))

        
@slash_command(name="get_day", description="Permet d'avoir l'emploi du temps pour une journée", scopes=server)
@slash_option(
    name="jour",
    description="Quel jour ? (DD-MM-YYYY)",
    required=True,
    opt_type=OptionType.STRING
)
async def get_day(ctx: SlashContext, jour : str):
    """Fonction qui permet d'obtenir l'edt d'une journée spécifique"""
    #try:
    await get_day_bt(ctx, jour)
    #except BaseException as error:
    #    await send_error("get_day",error, ctx, jour=jour)



async def get_day_bt(ctx, jour : str):
    """Fonction qui permet d'obtenir l'edt d'une journée spécifique"""
    try :
        date_formater = datetime.strptime(jour, "%d-%m-%Y").date()
        events = filter_events(get_events(), [TimeFilter(date_formater, Timing.DURING), get_filiere(ctx.author), get_groupes(ctx.author)] )
        embeds = get_embeds(events)
        await ctx.send(embeds=embeds)
    except ValueError:
        await ctx.send(embeds=[create_error_embed(f"La valeur `{jour}` ne correspond pas à une date")])
    #except BaseException as error:
        #await send_error("get_day_bt",error, ctx, jour=jour)


@slash_command(name="today", description="Permet d'avoir l'emploie du temps pour aujourd'hui", scopes=server)
async def today(ctx: SlashContext):
    """Fonction qui permet d'obtenir l'edt d'ajourd'hui"""
    #try:
    events = filter_events(get_events(), [TimeFilter(date.today(), Timing.DURING), get_filiere(ctx.author), get_groupes(ctx.author)] )
    embeds = get_embeds(events)
    button = Button(
        style=ButtonStyle.PRIMARY,
        custom_id = "day-" + (date.today() + timedelta(days=1)).strftime("%d-%m-%Y"),
        label = "Demain"
    )

    action_row = ActionRow(button)
    await ctx.send(embeds=embeds, components=[action_row])
    #except BaseException as error:
        #await send_error("today", error, ctx)



@slash_command(name="tomorrow", description="Permet d'avoir l'emploie du temps pour demain", scopes=server)
async def tomorrow(ctx: SlashContext):
    """Fonction qui permet d'obtenir l'edt de demain"""
    #try:
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
    #except BaseException as error:
        #await send_error("tomorrow", error, ctx)



@slash_command(name="info", description="Donne les infos sur l'utilisateur.", scopes=server)
async def info(ctx: SlashContext):
    """Fonction qui permet d'afficher le nom, la filière et les groupes de la personne"""
    #try:
    str_role = ""
    for groupe in get_groupes_as_list(ctx.author):
        str_role += groupe.value + ", "
    str_role = str_role.removesuffix(", ")
    await ctx.send(f"Vous êtes {get_name(ctx.author)}!\nVotre filière est {get_filiere_as_filiere(ctx.author).value} et vos groupes {"sont" if len(get_groupes_as_list(ctx.author)) > 1 else "est"} {str_role}.")
    #except BaseException as error:
        #await send_error("info",error, ctx)



@slash_command(name="get_week", description="Permet d'avoir l'emploi du temps pour une semaine", scopes=server)
@slash_option(
    name="semaine",
    description="Quel semaine ? (DD-MM-YYYY)",
    required=True,
    opt_type=OptionType.STRING
)
async def get_week(ctx: SlashContext, semaine : str):
    """Fonction qui permet d'obtenir l'edt d'une semaine spécifique"""
    #try:
    await get_week_bt(ctx, semaine)
    #except BaseException as error:
        #await send_error("get_week",error, ctx, semaine=semaine)


async def get_week_bt(ctx: SlashContext, semaine : str):
    """Fonction qui permet d'obtenir l'edt d'une semaine spécifique"""
    #try:
    date_formater = datetime.strptime(semaine, "%d-%m-%Y").date()
    embeds, monday_date = get_week_embeds(date_formater, ctx)
    await ctx.send(embeds=embeds)
    #except BaseException as error:
        #await send_error("get_week_bt",error, ctx, semaine=semaine)


@slash_command(name="week", description="Permet d'avoir l'emploie du temps pour la semaine", scopes=server)
async def week(ctx: SlashContext):
    """Fonction qui permet d'obtenir l'edt de cette semaine"""
    #try:
    date_formater = date.today()
    embeds, monday_date = get_week_embeds(date_formater, ctx)
    button = Button(
        style=ButtonStyle.PRIMARY,
        custom_id = "week-" + (monday_date + timedelta(days=7)).strftime("%d-%m-%Y"),
        label = "Semaine prochaine"
    )
    action_row = ActionRow(button)
    await ctx.send(embeds=embeds, components=[action_row])
    #except BaseException as error:
        #await send_error("week",error, ctx)


def get_week_embeds(date_formater, ctx):
    days_since_monday = date_formater.weekday()
    monday_date = date_formater - timedelta(days=days_since_monday)
    sunday_date = monday_date + timedelta(days=6)
    events = filter_events(
        get_events(),
        [TimeFilter(monday_date, Timing.AFTER), TimeFilter(sunday_date, Timing.BEFORE), get_filiere(ctx.author),
         get_groupes(ctx.author)])
    return get_embeds(events), monday_date


@slash_command(name="about", description="Affiche la page 'About'", scopes=server)
async def about(ctx :SlashContext):
    """Affiche le Contenu de README.md"""
    #try:
    with open("README.md", "r", encoding="utf-8") as f:
        l = f.read()
    await ctx.send(ascii + l )
    #except BaseException as error:
        #await send_error("about",error, ctx)

@slash_command(name="test", description="Test command", scopes=server)
async def test(ctx :SlashContext):
    await ctx.send("yes")

@slash_command(name="dm", description="tries to dm the user", scopes=server)
async def dm(ctx :SlashContext):
    """tries to dm the user"""
    #try:
    user = bot.get_user(ctx.author.id)
    await user.send("👀 est ce que ça a marché ?")
    await ctx.send("done :)")
    #except BaseException as error:
       #await send_error("dm",error, ctx)

@slash_command(name="ics", description="Génère le ics", scopes=server)
async def ics(ctx :SlashContext):
    """Génère le ics"""
    #try:
    get_ics([get_filiere(ctx.author), get_groupes(ctx.author)])
    await ctx.send("Voici votre fichier ics", files=["output/calendar.ics"])
    #except BaseException as error:
       #await send_error("ics",error, ctx)

@slash_command(name="subscribe", description="Permet de s'abonner aux mises a jour automatiques", scopes=server)
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
    await ctx.send(embed=Embed(f"Abonnements de {get_name(ctx.author)}", f"- Mise à Jour Quotidienne : {'✅' if (user_base.is_user_subscribed(id, Subscription.DAILY)) else '❌'}\n- Mise à Jour Hebdomadaire : {'✅' if (user_base.is_user_subscribed(id, Subscription.WEEKLY)) else '❌'}"))


@slash_command(name="unsubscribe", description="Permet de se desabonner aux mises a jour automatiques", scopes=server)
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
    await ctx.send(embed=Embed(f"Abonnements de {get_name(ctx.author)}", f"- Mise à Jour Quotidienne : {'✅' if (user_base.is_user_subscribed(id, Subscription.DAILY)) else '❌'}\n- Mise à Jour Hebdomadaire : {'✅' if (user_base.is_user_subscribed(id, Subscription.WEEKLY)) else '❌'}"))
    
@slash_command(name="check_subscription", description="Permet de consulter ses abonnements aux services de Mise à Jour", scopes=server)
async def check_subscription(ctx :SlashContext):
    user_base = get_user_base()
    id = ctx.author_id
    await ctx.send(embed=Embed(f"Abonnements de {get_name(ctx.author)}", f"- Mise à Jour Quotidienne : {'✅' if (user_base.is_user_subscribed(id, Subscription.DAILY)) else '❌'}\n- Mise à Jour Hebdomadaire : {'✅' if (user_base.is_user_subscribed(id, Subscription.WEEKLY)) else '❌'}"))


async def send_daily_update(user):
    events = filter_events(get_events(), [TimeFilter(date.today(), Timing.DURING), get_filiere(user), get_groupes(user)] )
    embeds = get_embeds(events)
    await user.send(embeds=embeds)

async def send_weekly_update(user):
    days_since_monday = datetime.today().weekday()
    monday_date = datetime.today() - timedelta(days=days_since_monday)
    sunday_date = monday_date + timedelta(days=6)
    events = filter_events(
        get_events(),
        [TimeFilter(monday_date, Timing.AFTER), TimeFilter(sunday_date, Timing.BEFORE), get_filiere(user),
         get_groupes(user)])
    await user.send(embeds=get_embeds(events))

@Task.create(TimeTrigger(hour=6, minute=0, utc=False))
async def daily_morning_update():
    user_base = get_user_base()
    if datetime.today().weekday() == 0:
        for id in user_base.weekly_subscribed_users:
            await send_daily_update(bot.get_user(id))
    for id in user_base.daily_subscribed_users:
        await send_daily_update(bot.get_user(id))


def get_name(author) -> str:
    """Permet d'obtenir le nickname si défini sinon le username"""
    return author.display_name

def get_filiere(author) -> FiliereFilter:
    """Fonction qui permet d'avoir le filtre filière d'un utilisateur, renvoie un filtre neutre si pas définie"""
    if is_Guild_Chan(author):
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
    if is_Guild_Chan(author):
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
    """Fonction qui renvoie un filtre des groupe d'un utilisateur"""
    if is_Guild_Chan(author):
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
    """Fonction qui renvoie un filtre des groupe d'un utilisateur"""
    if is_Guild_Chan(author):
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

def is_Guild_Chan(author) -> bool:
    return "Member" in str(type(author))


def create_error_embed(message:str) -> Embed:
    return Embed(":warning: Erreur: ", message, 0x992d22)


async def send_error(channel_name, error, ctx, semaine=None, jour=None, bouton=None):
    global channel
    if not channel:
        channel = bot.get_channel(os.getenv("CHANNEL_ID"))
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
    await bot.synchronise_interactions()
    daily_morning_update.start()
    get_events()



async def changement_event(embeds : list[Embed]):
    global channel
    if not channel:
        channel = bot.get_channel(os.getenv("CHANNEL_ID"))
    await channel.send(embeds=embeds)

bot.start()

