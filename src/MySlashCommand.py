from interactions import Client, slash_command, SlashContext, OptionType, slash_option, SlashCommandChoice, Permissions, \
    Embed, EmbedFooter, User, contexts, Extension, Button, ButtonStyle, ActionRow, ContextType, AutocompleteContext
from datetime import datetime, date, timedelta
import os

from TrainWreck import get_ics, get_embeds
from Enums import Subscription, RoleEnum, colors
from UserBase import get_user_base, nuke
from Calendar import get_calendar
from Tool import get_tool
from Filter import *


class MySlashCommand(Extension):
    """Classe contenant les commandes."""
    def __init__(self, bot: Client):
        self.bot = bot
        self.tool = get_tool(bot)

    @slash_command(name="get_day", description="Envoie votre EDT pour un jour donné. Si une personne est donnée, donne le sien.")
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
    async def get_day(self, ctx: SlashContext, jour: str, personne: User = None) -> None:
        """Fonction qui permet d'obtenir l'EDT d'une journée spécifique, ou d'un autre utilisateur s'il est spécifié."""
        await self.tool.get_day_bt(ctx, jour, False, personne)

    @slash_command(name="today", description="Envoie votre EDT du jour.")
    async def today(self, ctx: SlashContext) -> None:
        """Fonction qui permet d'obtenir l'EDT d'aujourd'hui."""
        await self.tool.get_day_bt(ctx, date.today().strftime("%d-%m-%Y"), False)

    @slash_command(name="tomorrow", description="Envoie votre EDT de demain.")
    async def tomorrow(self, ctx: SlashContext) -> None:
        """Fonction qui permet d'obtenir l'EDT de demain."""
        await self.tool.get_day_bt(ctx, (date.today() + timedelta(days=1)).strftime("%d-%m-%Y"), False)

    @slash_command(name="get_week", description="Envoie votre EDT pour la semaine de la date. Si une personne est donnée, donne le sien.")
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
    async def get_week(self, ctx: SlashContext, semaine: str, personne: User = None) -> None:
        """Fonction qui permet d'obtenir l'EDT d'une semaine spécifique, ou d'un autre utilisateur s'il est spécifié."""
        await self.tool.get_week_bt(ctx, semaine, False, personne)

    @slash_command(name="week", description="Envoie votre EDT de la semaine.")
    async def week(self, ctx: SlashContext) -> None:
        """Fonction qui permet d'obtenir l'EDT de cette semaine."""
        await self.tool.get_week_bt(ctx, date.today().strftime("%d-%m-%Y"), False)

    @slash_command(name="next_week", description="Envoie votre EDT de la semaine prochaine.")
    async def next_week(self, ctx: SlashContext) -> None:
        """Fonction qui permet d'obtenir l'EDT de la semaine prochaine."""
        await self.tool.get_week_bt(ctx, (date.today() + timedelta(days=7)).strftime("%d-%m-%Y"), False)

    @slash_command(name="help", description="Affiche la page d'Aide.")
    async def help(self, ctx: SlashContext) -> None:
        """Affiche le Contenu de HELP.md."""
        with open("data/HELP.md", "r", encoding="utf-8") as f:
            help_file = f.read()

        embed = Embed(description=help_file, footer=EmbedFooter(
            "Les EDT sont fournis a titre informatif uniquement -> Veuillez vous référer à votre page personnelle sur l'ENT.",
            self.bot.user.avatar_url), color=colors[2])

        repo = Button(
            style=ButtonStyle.URL,
            label="Repository bot",
            url="https://github.com/TrainWreckOrg/trainwreck"
        )

        vincent = Button(
            style=ButtonStyle.URL,
            label="Github Vincent",
            url="https://github.com/VincentGonnet"
        )

        action_row = ActionRow(repo, vincent)
        ephemeral = False
        if self.tool.is_guild_chan(ctx.author):
            ephemeral = not ctx.author.has_role(self.tool.get_roles(ctx.guild)[RoleEnum.PERMA]) # Permanent si la personne à le rôle
        await ctx.send(embed=embed, components=action_row, ephemeral=ephemeral)

    @slash_command(name="ics", description="Envoie un fichier ICS importable dans la plupart des applications de calendrier.")
    @slash_option(
        name="debut",
        description="Quelle est la date de début ? (DD-MM-YYYY)",
        required=True,
        opt_type=OptionType.STRING,
        autocomplete=True
    )
    @slash_option(
        name="fin",
        description="Quelle est la date de fin ? (DD-MM-YYYY)",
        required=True,
        opt_type=OptionType.STRING,
        autocomplete=True
    )
    async def ics(self, ctx: SlashContext, debut: str, fin: str) -> None:
        """Génère le fichier ICS entre deux dates."""
        try:
            date_debut = datetime.strptime(debut, "%d-%m-%Y").date()
            date_fin = datetime.strptime(fin, "%d-%m-%Y").date()
            filename = str(ctx.author.id)
            get_ics(filter_events(get_calendar().get_events(),
                                  [TimeFilter(date_debut, Timing.AFTER), TimeFilter(date_fin, Timing.BEFORE),
                                   self.tool.get_filiere(ctx.author), self.tool.get_groupes(ctx.author)]),
                    filename=filename
                    )

            ephemeral = False
            if self.tool.is_guild_chan(ctx.author):
                ephemeral = not ctx.author.has_role(self.tool.get_roles(ctx.guild)[RoleEnum.PERMA])  # Permanent si la personne a le rôle

            await ctx.send("Voici votre fichier ics (:warning: : Le calendrier n'est pas mis a jour dynamiquement)", files=[f"{filename}.ics"], ephemeral=ephemeral)
            os.remove(f"{filename}.ics")
        except ValueError:
            await ctx.send(embeds=[self.tool.create_error_embed(f"La valeur `{debut}` ou `{fin}` ne correspond pas à une date.")], ephemeral=True)

    @ics.autocomplete("debut")
    async def autocomplete(self, ctx: AutocompleteContext):

        days_since_monday = date.today().weekday()
        monday_date = date.today() - timedelta(days=days_since_monday)
        next_monday = monday_date + timedelta(days=7)
        await ctx.send(
            choices=[
                {
                    "name": f"Lundi de cette semaine",
                    "value": f"{monday_date.strftime("%d-%m-%Y")}",
                },
                {
                    "name": f"Lundi de la semaine prochaine",
                    "value": f"{next_monday.strftime("%d-%m-%Y")}",
                }
            ]
        )

    @ics.autocomplete("fin")
    async def autocomplete(self, ctx: AutocompleteContext):

        days_since_monday = date.today().weekday()
        monday_date = date.today() - timedelta(days=days_since_monday)
        sunday_date = monday_date + timedelta(days=6)
        next_sunday = sunday_date + timedelta(days=7)
        await ctx.send(
            choices=[
                {
                    "name": f"Dimanche de cette semaine",
                    "value": f"{sunday_date.strftime("%d-%m-%Y")}",
                },
                {
                    "name": f"Dimanche de la semaine prochaine",
                    "value": f"{next_sunday.strftime("%d-%m-%Y")}",
                }
            ]
        )


    @slash_command(name="subscribe",
                   description="Vous permet de vous abonner à l'envoi de l'EDT dans vos DM, de manière quotidienne ou hebdomadaire.")
    @slash_option(
        name="service",
        description="Mise a jour Quotidienne `DAILY`, Hebdomadaire `WEEKLY`, ou les deux `BOTH`.",
        required=False,
        opt_type=OptionType.STRING,
        choices=[
            SlashCommandChoice(name="Daily", value="DAILY"),
            SlashCommandChoice(name="Weekly", value="WEEKLY"),
            SlashCommandChoice(name="Both", value="BOTH")
        ]
    )
    @slash_option(
        name="ics",
        description="L'envoie du fichier ICS, Quotidienne `DAILY`, Hebdomadaire `WEEKLY`, ou les deux `BOTH`.",
        required=False,
        opt_type=OptionType.STRING,
        choices=[
            SlashCommandChoice(name="Daily", value="DAILY"),
            SlashCommandChoice(name="Weekly", value="WEEKLY"),
            SlashCommandChoice(name="Both", value="BOTH")
        ]
    )
    async def subscribe(self, ctx: SlashContext, service: str = "None", ics: str = "None") -> None:
        """Permet de s'abonnée à l'envoi automatique de l'EDT."""
        user_base = get_user_base()
        id = ctx.author_id
        if not user_base.has_user(ctx.author_id):
            user_base.add_user(id, self.tool.get_groupes_as_list(ctx.author), self.tool.get_filiere_as_filiere(ctx.author))
        match service:
            case "DAILY":
                user_base.user_subscribe(id, Subscription.DAILY)
                await self.tool.subscription_role(id, Subscription.DAILY, True)
            case "WEEKLY":
                user_base.user_subscribe(id, Subscription.WEEKLY)
                await self.tool.subscription_role(id, Subscription.WEEKLY, True)
            case "BOTH":
                user_base.user_subscribe(id, Subscription.BOTH)
                await self.tool.subscription_role(id, Subscription.BOTH, True)

        match ics:
            case "DAILY":
                user_base.user_subscribe_ics(id, Subscription.DAILY_ICS)
                await self.tool.subscription_role(id, Subscription.DAILY_ICS, True)
            case "WEEKLY":
                await self.tool.subscription_role(id, Subscription.WEEKLY_ICS, True)
                user_base.user_subscribe_ics(id, Subscription.WEEKLY_ICS)
            case "BOTH":
                await self.tool.subscription_role(id, Subscription.BOTH_ICS, True)
                user_base.user_subscribe_ics(id, Subscription.BOTH_ICS)

        if service == "None" and ics == "None":
            await ctx.send("Vous devez sélectionner une option pour vous abonner.\n Par exemple : pour recevoir l'emploi du temps de la semaine le lundi, avec un fichier ics, et l'emploi du temps du jour tout les jours, sans ics : `/subscribe service: Both ics: Weekly`", ephemeral=True)
        else:
            await self.tool.check_subscription(ctx)

    @slash_command(name="unsubscribe", description="Vous permet de vous désabonner à l'envoi de l'EDT dans vos DM.")
    @slash_option(
        name="service",
        description="mise a jour Quotidienne `DAILY`, Hebdomadaire `WEEKLY`, ou les deux `BOTH`.",
        required=False,
        opt_type=OptionType.STRING,
        choices=[
            SlashCommandChoice(name="Daily", value="DAILY"),
            SlashCommandChoice(name="Weekly", value="WEEKLY"),
            SlashCommandChoice(name="Both", value="BOTH")
        ]
    )
    @slash_option(
        name="ics",
        description="L'envoie du fichier ICS, Quotidienne `DAILY`, Hebdomadaire `WEEKLY`, ou les deux `BOTH`.",
        required=False,
        opt_type=OptionType.STRING,
        choices=[
            SlashCommandChoice(name="Daily", value="DAILY"),
            SlashCommandChoice(name="Weekly", value="WEEKLY"),
            SlashCommandChoice(name="Both", value="BOTH")
        ]
    )
    async def unsubscribe(self, ctx: SlashContext, service: str = "None", ics: str = "None") -> None:
        """Permet de se désabonnée à l'envoi automatique de l'EDT."""
        user_base = get_user_base()
        id = ctx.author_id
        if not user_base.has_user(ctx.author_id):
            user_base.add_user(id, self.tool.get_groupes_as_list(ctx.author), self.tool.get_filiere_as_filiere(ctx.author))
        match service:
            case "DAILY":
                user_base.user_unsubscribe(id, Subscription.DAILY)
                await self.tool.subscription_role(id, Subscription.DAILY, False)
            case "WEEKLY":
                user_base.user_unsubscribe(id, Subscription.WEEKLY)
                await self.tool.subscription_role(id, Subscription.WEEKLY, False)
            case "BOTH":
                user_base.user_unsubscribe(id, Subscription.BOTH)
                await self.tool.subscription_role(id, Subscription.BOTH, False)

        match ics:
            case "DAILY":
                user_base.user_unsubscribe_ics(id, Subscription.DAILY_ICS)
                await self.tool.subscription_role(id, Subscription.DAILY_ICS, False)
            case "WEEKLY":
                user_base.user_unsubscribe_ics(id, Subscription.WEEKLY_ICS)
                await self.tool.subscription_role(id, Subscription.WEEKLY_ICS, False)
            case "BOTH":
                user_base.user_unsubscribe_ics(id, Subscription.BOTH_ICS)
                await self.tool.subscription_role(id, Subscription.BOTH_ICS, False)
        await self.tool.check_subscription(ctx)

    @slash_command(name="check_subscription",
                   description="Vous permet de consulter à quels service d'envoi d'EDT vous êtes inscrit.")
    async def check_subscription(self, ctx: SlashContext) -> None:
        """Permet d'afficher quel sont les abonnements d'un utilisateur."""
        await self.tool.check_subscription(ctx)

    @slash_command(name="exam", description="Vous permet de consulter la liste des exams.")
    async def exam(self, ctx: SlashContext) -> None:
        """Permet d'obtenir la liste des exams."""
        exams = get_calendar().get_exams()
        embeds = get_embeds(exams, ctx.author)
        if not exams:
            embeds[0].description = "Aucun examens"
        embeds.insert(0, Embed(title="EXAMENS", description="ATTENTION CETTE LISTE D'EXAMS N'EST PEUT-ÊTRE PAS A JOUR MERCI DE VERIFIER SUR LE SITE DE L’UNIVERSITÉ !\nCERTAINS EXAMS (CONTRÔLE EN DÉBUT DE TD/TP) NOUS ONT ETE RAPPORTER ET AJOUTER DONC NE SONT PAS SUR LE SITE.", color=colors[0]))

        embeds[-1].footer.text = f"Commande fait par {ctx.author.display_name}\nLes emploi du temps sont fournis a titre informatif uniquement.\n-> Veuillez vous référer à votre page personnelle sur l'ENT."

        universite = Button(
            style=ButtonStyle.URL,
            label="Site de l'université",
            url="https://www.univ-orleans.fr/fr/sciences-techniques/etudiant/examens-reglementationrse/examens-20232024"
        )

        ephemeral = False
        if self.tool.is_guild_chan(ctx.author):
            ephemeral = not ctx.author.has_role( self.tool.get_roles(ctx.guild)[RoleEnum.PERMA])  # Permanent si la personne a le rôle

        # Au cas où, il y a plus de 10 embeds, ça les envoie en plusieurs messages
        cut = embeds
        for i in range(0,len(embeds),10):
            await ctx.send(embeds=cut[:10], components=universite, ephemeral=ephemeral)
            cut = cut[10:]

    @slash_command(name="wipe", description="Enlève tout les rôles.", default_member_permissions=Permissions.ADMINISTRATOR, contexts=[ContextType.GUILD])
    async def wipe(self, ctx: SlashContext) -> None:
        """Fonction qui permet d'enlever tous les attribués"""
        await ctx.send(":warning: Vous êtes sur le point de supprimer les rôles est vous sûr", components=Button(style=ButtonStyle.BLURPLE, custom_id="delete-role", label="OUI"),  ephemeral=True)

    @slash_command(name="userscan", description="Permet d'ajouter tout les membres dans la BD.",
                   default_member_permissions=Permissions.ADMINISTRATOR)
    @contexts(guild=True, bot_dm=False)
    async def userscan(self, ctx: SlashContext) -> None:
        """Permet de scanner tous les membres du serveur et de mettre à jour la BD."""
        await self.tool.userscan(ctx)

    @slash_command(name="nuke", description="Permet de nuke la BD.",
                   default_member_permissions=Permissions.ADMINISTRATOR)
    @contexts(guild=True, bot_dm=False)
    async def nuke(self, ctx: SlashContext) -> None:
        """Permet de vider la BD."""
        nuke()
        await ctx.send("La BD à été nuke.", ephemeral=True)

    @slash_command(name="bd", description="Permet d'obtenir' BD.",
                   default_member_permissions=Permissions.ADMINISTRATOR)
    @contexts(guild=True, bot_dm=False)
    async def bd(self, ctx: SlashContext) -> None:
        """Permet d'obtenir la BD."""
        await ctx.send("Voici la BD.", file="data/UserBase.pkl", ephemeral=False)

    @slash_command(name="test_change", description="Permet de modifier le ics.",
                   default_member_permissions=Permissions.ADMINISTRATOR)
    @contexts(guild=True, bot_dm=False)
    async def test_change(self, ctx: SlashContext) -> None:
        """Permet d'obtenir la BD."""
        with open("data/INGE_OLD.ics", "r") as file_source:
            content = file_source.read()

        with open("data/INGE.ics", "w") as file_prod:
            file_prod.write(content)

        await ctx.send("Le fichier ics à été modifier.", ephemeral=False)
