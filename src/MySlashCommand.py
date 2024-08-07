from interactions import slash_command, SlashContext, OptionType, slash_option, SlashCommandChoice, Permissions, Embed, \
    EmbedFooter, User, contexts, Extension, AutocompleteContext, Button, ButtonStyle, ActionRow
from Tool import get_tool

from Enums import Subscription
from Calendar import get_calendar
from TrainWreck import get_ics, get_embeds
from UserBase import get_user_base
from Filter import *

from datetime import datetime, date, timedelta


class MySlashCommand(Extension):
    def __init__(self, bot):
        self.bot = bot
        self.tool = get_tool(bot)

    @slash_command(name="test", description="Test command")
    async def test(self, ctx: SlashContext):
        await ctx.send(
            f"{self.tool.ping_liste(Event(datetime.now(), datetime.now(), "Cours", Group.TD1I, "Ta mère", "Ton père", True, False, "007"))}, you got poked by {ctx.author.mention}!")


    @slash_command(name="info", description="Envoie des infos sur vos groupes, et filière. Si une personne est donnée, donne ses informations")
    @slash_option(
        name="personne",
        description="Quel utilisateur ?",
        required=False,
        opt_type=OptionType.USER
    )
    async def info(self, ctx: SlashContext, personne: User = None):
        """Fonction qui permet d'afficher le nom, la filière et les groupes de la personne"""
        author = ctx.author if (personne is None) else personne
        you_are = personne is None
        str_role = ""
        for groupe in self.tool.get_groupes_as_list(author):
            str_role += groupe.value + ", "
        str_role = str_role.removesuffix(", ")
        await ctx.send(
            f"{"Vous êtes" if you_are else "Informations sur"} {author.display_name}!\n{"Votre" if you_are else "Sa"} filière est {self.tool.get_filiere_as_filiere(ctx.author).value} et {"vos" if you_are else "ses"} groupes {"sont" if len(self.tool.get_groupes_as_list(ctx.author)) > 1 else "est"} {str_role}.")






    @slash_command(name="get_day",
                   description="Envoie votre EDT pour un jour donné. Si une personne est donnée, donne l'EDT de cette personne")
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
    async def get_day(self, ctx: SlashContext, jour: str, personne: User = None):
        """Fonction qui permet d'obtenir l'EDT d'une journée spécifique"""
        # try:
        await self.tool.get_day_bt(ctx, jour, False, personne)
        # except BaseException as error:
        #    await send_error("get_day",error, ctx, jour=jour)

    """
    @get_day.autocomplete("jour")
    async def autocomplete(self, ctx: AutocompleteContext):
        choices=[]
        string_option_input = ctx.input_text  # can be empty/None
        # you can use ctx.kwargs.get("name") to get the current state of other options - note they can be empty too

        
        # Faire le process


        # make sure you respond within three seconds
        await ctx.send(
            choices=[
                {
                    "name": f"{string_option_input}a",
                    "value": f"{string_option_input}a",
                },
                {
                    "name": f"{string_option_input}b",
                    "value": f"{string_option_input}b",
                },
                {
                    "name": f"{string_option_input}c",
                    "value": f"{string_option_input}c",
                },
            ]
        )

    """



    @slash_command(name="today", description="Envoie votre EDT du jour")
    async def today(self, ctx: SlashContext):
        """Fonction qui permet d'obtenir l'EDT d'ajourd'hui"""
        # try:
        await self.tool.get_day_bt(ctx, date.today().strftime("%d-%m-%Y"), False)

        # except BaseException as error:
        # await send_error("today", error, ctx)

    @slash_command(name="tomorrow", description="Envoie votre EDT du lendemain")
    async def tomorrow(self, ctx: SlashContext):
        """Fonction qui permet d'obtenir l'EDT de demain"""
        # try:
        await self.tool.get_day_bt(ctx, (date.today() + timedelta(days=1)).strftime("%d-%m-%Y"), False)
        # except BaseException as error:
        # await send_error("tomorrow", error, ctx)















    @slash_command(name="get_week",
                   description="Envoie votre EDT pour la semaine de la date, si une personne est donnée, donne le sien")
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
    async def get_week(self, ctx: SlashContext, semaine: str, personne: User = None):
        """Fonction qui permet d'obtenir l'EDT d'une semaine spécifique"""
        # try:
        await self.tool.get_week_bt(ctx, semaine, False, personne)
        # except BaseException as error:
        # await send_error("get_week",error, ctx, semaine=semaine)

    @slash_command(name="week", description="Envoie votre EDT de la semaine")
    async def week(self, ctx: SlashContext):
        """Fonction qui permet d'obtenir l'EDT de cette semaine"""
        # try:
        await self.tool.get_week_bt(ctx, date.today().strftime("%d-%m-%Y"), False)
        # except BaseException as error:
        # await send_error("week",error, ctx)

    @slash_command(name="userscan", description="Permet d'ajouter tout les membres dans la BD",
                   default_member_permissions=Permissions.ADMINISTRATOR)
    @contexts(guild=True, bot_dm=False)
    async def userscan(self, ctx: SlashContext):
        guild = ctx.guild
        user_base = get_user_base()
        for user in guild.members:
            if not user_base.has_user(user.id):
                user_base.add_user(user.id, self.tool.get_groupes_as_list(user), self.tool.get_filiere_as_filiere(user))
            else:
                user_base.update_user_groups(user.id, self.tool.get_groupes_as_list(user))
        await ctx.send("Les membres du serveur ont été ajoutée et mit à jour")


    @slash_command(name="help", description="Affiche la page d'Aide")
    async def help(self, ctx: SlashContext):
        """Affiche le Contenu de HELP.md"""
        # try:
        with open("HELP.md", "r", encoding="utf-8") as f:
            help = f.read()
        embed = Embed(description=help, footer=EmbedFooter(
            "Les EDT sont fournis a titre informatif uniquement -> Veuillez vous référer à votre page personnelle sur l'ENT",
            self.bot.user.avatar_url), color=0xd8a74c)
        repo = Button(
            style=ButtonStyle.URL,
            label="Repo bot",
            url="https://github.com/Kaawan-d20/trainwreck"
        )

        vincent = Button(
            style=ButtonStyle.URL,
            label="Github Vincent",
            url="https://github.com/VincentGonnet"
        )

        action_row = ActionRow(repo, vincent)
        await ctx.send(embed=embed, components=action_row)
        # except BaseException as error:
        # await send_error("about",error, ctx)

    @slash_command(name="ics",
                   description="Envoie un fichier ICS importable dans la plupart des applications de calendrier")
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
    async def ics(self, ctx: SlashContext, debut: str, fin: str):
        """Génère l'ics"""
        try:
            date_debut = datetime.strptime(debut, "%d-%m-%Y").date()
            date_fin = datetime.strptime(fin, "%d-%m-%Y").date()
            get_ics(filter_events(get_calendar().get_events(),
                                  [TimeFilter(date_debut, Timing.AFTER), TimeFilter(date_fin, Timing.BEFORE),
                                   self.tool.get_filiere(ctx.author), self.tool.get_groupes(ctx.author)]))
            await ctx.send("Voici votre fichier ics", files=["output/calendar.ics"])
        except ValueError:
            await ctx.send(embeds=[self.tool.create_error_embed(f"La valeur `{debut}` ou `{fin}` ne correspond pas à une date")])
        # except BaseException as error:
        # await send_error("ics",error, ctx)














    @slash_command(name="subscribe",
                   description="Vous permet de vous abonner à l'envoi de l'EDT dans vos DM, de manière quotidienne ou hebdomadaire")
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
    async def subscribe(self, ctx: SlashContext, service: str):
        user_base = get_user_base()
        id = ctx.author_id
        if not user_base.has_user(ctx.author_id):
            user_base.add_user(id, self.tool.get_groupes_as_list(ctx.author), self.tool.get_filiere_as_filiere(ctx.author))
        match service:
            case "DAILY":
                user_base.user_subscribe(id, Subscription.DAILY)
            case "WEEKLY":
                user_base.user_subscribe(id, Subscription.WEEKLY)
            case "BOTH":
                user_base.user_subscribe(id, Subscription.BOTH)
        await ctx.send(embed=Embed(f"Abonnements de {ctx.author.display_name}",
                                   f"- Mise à Jour Quotidienne : {'✅' if (user_base.is_user_subscribed(id, Subscription.DAILY)) else '❌'}\n- Mise à Jour Hebdomadaire : {'✅' if (user_base.is_user_subscribed(id, Subscription.WEEKLY)) else '❌'}"))

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
    async def unsubscribe(self, ctx: SlashContext, service: str):
        user_base = get_user_base()
        id = ctx.author_id
        if not user_base.has_user(ctx.author_id):
            user_base.add_user(id, self.tool.get_groupes_as_list(ctx.author), self.tool.get_filiere_as_filiere(ctx.author))
        match service:
            case "DAILY":
                user_base.user_unsubscribe(id, Subscription.DAILY)
            case "WEEKLY":
                user_base.user_unsubscribe(id, Subscription.WEEKLY)
            case "BOTH":
                user_base.user_unsubscribe(id, Subscription.BOTH)
        await ctx.send(embed=Embed(f"Abonnements de {ctx.author.display_name}",
                                   f"- Mise à Jour Quotidienne : {'✅' if (user_base.is_user_subscribed(id, Subscription.DAILY)) else '❌'}\n- Mise à Jour Hebdomadaire : {'✅' if (user_base.is_user_subscribed(id, Subscription.WEEKLY)) else '❌'}"))

    @slash_command(name="check_subscription",
                   description="Vous permet de consulter à quels service d'envoi d'EDT vous êtes inscrit")
    async def check_subscription(self, ctx: SlashContext):
        user_base = get_user_base()
        id = ctx.author_id
        await ctx.send(embed=Embed(f"Abonnements de {ctx.author.display_name}",
                                   f"- Mise à Jour Quotidienne : {'✅' if (user_base.is_user_subscribed(id, Subscription.DAILY)) else '❌'}\n- Mise à Jour Hebdomadaire : {'✅' if (user_base.is_user_subscribed(id, Subscription.WEEKLY)) else '❌'}"))


    @slash_command(name="exam", description="Vous permet de consulter la liste des exams")
    async def exam(self, ctx: SlashContext):
        exams = get_calendar().get_exams()
        embeds = get_embeds(exams, ctx.author)
        if not exams:
            embeds[0].description = "Aucun examens"
        embeds.insert(0, Embed(title="EXAMENS", description="ATTENTION CETTE LISTE D'EXAMS N'EST PEUT ETRE PAS A JOUR MERCI DE VERIFIER SUR LE SITE DE L'UNIVERSITE", color=0xc62139))

        universite = Button(
            style=ButtonStyle.URL,
            label="Site de l'université",
            url="https://www.univ-orleans.fr/fr/sciences-techniques/etudiant/examens-reglementationrse/examens-20232024"
        )

        await ctx.send(embeds=embeds, components=universite)


























