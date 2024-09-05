from http.client import HTTPException
from abc import ABC, abstractmethod

import sentry_sdk
from interactions import Client, ActionRow, Button, ButtonStyle, SlashContext, Guild, Role, Embed, User, Member, \
    ModalContext, ContextMenuContext, ComponentContext, GuildText

from TrainWreck import get_embeds, get_ics
from UserBase import get_user_base
from Calendar import get_calendar
from Filter import *
from Enums import RoleEnum, Group, colors, Subscription


from datetime import datetime, date, timedelta
from enum import Enum
import os

from src.Enums import Annee
from src.UserBase import DBUser


class Serveur:
    def __init__(self, guild : Guild):
        self.guild = guild
        self.annee = None

        if guild.name == "L3 Informatique":
            self.annee = Annee.L3

        if guild.name == "L2 Informatique":
            self.annee = Annee.L2

        self.roles = {}
        for role in self.guild.roles:
            if role.name in Group:
                for groupe in Group:
                    if groupe.value == role.name:
                        self.roles[groupe] = role
            if role.name in Filiere:
                for filiere in Filiere:
                    if filiere.value == role.name:
                        self.roles[filiere] = role
            if role.name in Subscription:
                for sub in Subscription:
                    if sub.value == role.name:
                        self.roles[sub] = role
            if role.name in RoleEnum:
                for roleEnum in RoleEnum:
                    if roleEnum.value == role.name:
                        self.roles[roleEnum] = role

        for channel in self.guild.channels:
            if channel.name == "changement-edt":
                self.channel_changement_edt = channel



class BDServeur:
    def __init__(self, bot: Client):
        self.bot = bot
        self.serveur_list = []
        self.annee: dict[Annee, list[Serveur]] = {}
        self.guild : dict[Guild, Serveur] = {}

        for guild in bot.guilds:
            serveur = Serveur(guild)
            self.serveur_list.append(serveur)
            self.annee[serveur.annee].append(serveur)
            self.guild[guild] = serveur

    def get_annee(self, annee_demand : Annee) -> list[Serveur]:
        return self.annee.get(annee_demand)

    def get_serveur(self, guild : Guild) -> Serveur:
        return self.guild.get(guild)

    def get_roles(self, guild : Guild) -> dict[Enum, Role]:
        return self.guild.get(guild).roles

    def get_master_serveur(self) -> Serveur:
        return self.get_serveur(self.bot.get_guild(os.getenv("SERVEUR_ID")))



bd_serveur : BDServeur

def get_bd_serveur(bot: Client) -> BDServeur:
    global bd_serveur
    if bd_serveur is None:
        bd_serveur = BDServeur(bot)
    return bd_serveur





class Tool(ABC):
    """Classe regroupant plusieurs méthodes utiles."""
    def __init__(self, bot: Client):
        self.bot = bot
        self.serveur = get_bd_serveur(bot)

    def get_subscription(self, author: User | Member) -> list[Subscription]:
        """Fonction qui permet d'avoir la liste de subscription d'un utilisateur."""
        sub = []
        if self.is_guild_chan(author):
            if author.has_role(self.serveur.get_roles(author.guild)[Subscription.DAILY]):
                sub.append(Subscription.DAILY)
            if author.has_role(self.serveur.get_roles(author.guild)[Subscription.WEEKLY]):
                sub.append(Subscription.WEEKLY)
            if author.has_role(self.serveur.get_roles(author.guild)[Subscription.DAILY_ICS]):
                sub.append(Subscription.DAILY_ICS)
            if author.has_role(self.serveur.get_roles(author.guild)[Subscription.WEEKLY_ICS]):
                sub.append(Subscription.WEEKLY_ICS)

        elif get_user_base().has_user(author.id):
            if get_user_base().is_user_subscribed(author.id, Subscription.DAILY):
                sub.append(Subscription.DAILY)
            if get_user_base().is_user_subscribed(author.id, Subscription.WEEKLY):
                sub.append(Subscription.WEEKLY)
            if get_user_base().is_user_subscribed_ics(author.id, Subscription.DAILY_ICS):
                sub.append(Subscription.DAILY_ICS)
            if get_user_base().is_user_subscribed_ics(author.id, Subscription.WEEKLY_ICS):
                sub.append(Subscription.WEEKLY_ICS)

        return sub

    def get_filiere_as_filiere(self, author: User | Member) -> Filiere:
        """Fonction qui permet d'avoir la filière d'un utilisateur, renvoie UKNW si pas définie."""
        if self.is_guild_chan(author):
            if author.has_role(self.serveur.get_roles(author.guild)[Filiere.INGE]):
                return Filiere.INGE
            if author.has_role(self.serveur.get_roles(author.guild)[Filiere.MIAGE]):
                return Filiere.MIAGE
        elif get_user_base().has_user(author.id):
            return get_user_base().get_user(author.id).filiere
        return Filiere.UKNW
    
    def get_filiere(self, author: User | Member) -> FiliereFilter | Filter:
        """Fonction qui permet d'avoir le filtre filière d'un utilisateur, renvoie un filtre neutre si pas défini."""
        match self.get_filiere_as_filiere(author) :
            case Filiere.INGE:
                return FiliereFilter(Filiere.INGE)
            case Filiere.MIAGE:
                return FiliereFilter(Filiere.MIAGE)
            case _:
                return Filter()

    def get_groupes_as_list(self, author: User | Member) -> list[Group]:
        """Fonction qui renvoie la liste des groupes d'un utilisateur."""
        out = [Group.CM]
        if self.is_guild_chan(author):
            for role in author.roles:
                for gr in Group:
                    if role.name == gr.value:
                        out.append(gr)
            return out
        elif get_user_base().has_user(author.id):
            return get_user_base().get_user(author.id).groups
        else :
            return out

    def get_groupes(self, author: User | Member) -> Filter | GroupFilter:
        """Fonction qui renvoie un filtre des groupes d'un utilisateur."""
        groups = self.get_groupes_as_list(author)
        if groups == [Group.CM]:
            return Filter()
        else:
            return GroupFilter(groups)

    def is_guild_chan(self, author: User | Member) -> bool:
        """Permet de savoir si l'auteur est un member (si l'action a été fait dans un serveur ou en MP)."""
        return "Member" in str(type(author))

    def create_error_embed(self, message: str) -> Embed:
        """Permet de créer un Embed d'erreur."""
        return Embed(":warning: Erreur: ", message, colors[0])

    async def send_error(self, exception: BaseException) -> None:
        """Permet de faire la gestion des erreurs pour l'ensemble du bot, envoie un message aux admins et prévient l'utilisateur de l'erreur."""
        guild = self.bot.user.guilds[0]
        print(exception)
        sentry_sdk.capture_exception(exception)
        await self.bot.get_channel(os.getenv("ERROR_CHANNEL_ID")).send(
            f"{(self.serveur.get_roles(guild)[RoleEnum.ADMIN]).mention} {exception}")

    async def get_day_bt(self, ctx: SlashContext | ModalContext | ContextMenuContext | ComponentContext, jour: str, modifier: bool, personne: User = None) -> None:
        """Fonction qui permet d'obtenir l'EDT d'une journée spécifique.
            Jour : Le jour que l'on souhaite obtenir.
            Modifier : Si l'on doit modifier le message d'origine ou bien en envoyer un nouveau.
            Personne : La personne dont laquelle on veut savoir l'emploi du temps."""
        try:
            author = ctx.author if (personne is None) else personne

            date_formater = datetime.strptime(jour, "%d-%m-%Y").date()

            filiere = self.get_filiere(author)
            groupe = self.get_groupes(author)

            events: list[Event] = filter_events(get_calendar(self.serveur.get_serveur(ctx.guild).annee).get_events(),
                                       [TimeFilter(date_formater, Timing.DURING), filiere,
                                        groupe])
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

            ephemeral = False
            if self.is_guild_chan(ctx.author):
                ephemeral = not ctx.author.has_role(self.serveur.get_roles(ctx.guild)[RoleEnum.PERMA])  # Permanent si la personne a le rôle

            if personne is None:
                action_row = ActionRow(precedent, suivant)
                if modifier:
                    await ctx.edit_origin(embeds=embeds, components=[action_row])
                else:
                    await ctx.send(embeds=embeds, components=[action_row], ephemeral=ephemeral)
            else:
                if modifier:
                    await ctx.edit_origin(embeds=embeds)
                else:
                    await ctx.send(embeds=embeds, ephemeral=ephemeral)

        except ValueError:
            await ctx.send(embeds=[self.create_error_embed(f"La valeur `{jour}` ne correspond pas à une date au format DD-MM-YYYY")], ephemeral=True)

    async def get_week_bt(self, ctx: SlashContext | ModalContext | ContextMenuContext | ComponentContext, semaine: str, modifier: bool, personne: User = None):
        """Fonction qui permet d'obtenir l'EDT d'une semaine spécifique.
                    Semaine : La semaine que l'on souhaite obtenir.
                    Modifier : Si l'on doit modifier le message d'origine ou bien en envoyer un nouveau.
                    Personne : La personne dont laquelle on veut savoir l'emploi du temps."""
        try:
            author = ctx.author if (personne is None) else personne

            date_formater = datetime.strptime(semaine, "%d-%m-%Y").date()
            days_since_monday = date_formater.weekday()
            monday_date = date_formater - timedelta(days=days_since_monday)
            sunday_date = monday_date + timedelta(days=6)
            events: list[Event] = filter_events(get_calendar(self.serveur.get_serveur(ctx.guild).annee).get_events(), [TimeFilter(monday_date, Timing.AFTER), TimeFilter(sunday_date, Timing.BEFORE), self.get_filiere(author), self.get_groupes(author)])

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

            ephemeral = False
            if self.is_guild_chan(ctx.author):
                ephemeral = not ctx.author.has_role(
                    self.serveur.get_roles(ctx.guild)[RoleEnum.PERMA])  # Permanent si la personne a le rôle

            if personne is None:
                action_row = ActionRow(precedent, suivant)
                if modifier:
                    await ctx.edit_origin(embeds=embeds, components=[action_row])
                else:
                    await ctx.send(embeds=embeds, components=[action_row], ephemeral=ephemeral)
            else:
                if modifier:
                    await ctx.edit_origin(embeds=embeds)
                else:
                    await ctx.send(embeds=embeds, ephemeral=ephemeral)
        except ValueError:
            await ctx.send(embeds=[self.create_error_embed(f"La valeur `{semaine}` ne correspond pas à une date au format DD-MM-YYYY")], ephemeral=True)

    async def send_daily_update(self, bd_user: DBUser, ics: bool):
        """Permet d'envoyer les EDT automatiquement pour le jour."""
        try:
            user : User = self.bot.get_user(bd_user.id)
            events = filter_events(get_calendar(bd_user.annee).get_events(), [TimeFilter(date.today(), Timing.DURING), self.get_filiere(user), self.get_groupes(user)])
            embeds = get_embeds(events, user, date.today())
            if ics:
                filename = str(user.id)
                get_ics(events, filename=filename)
                await user.send("Bonjour voici votre EDT pour aujourd'hui.\n:warning: : Le calendrier n'est pas mis a jour dynamiquement", embeds=embeds, files=[f"{filename}.ics"], ephemeral=False)
                os.remove(f"{filename}.ics")
            else:
                await user.send("Bonjour voici votre EDT pour aujourd'hui.\n:warning: : Le calendrier n'est pas mis a jour dynamiquement", embeds=embeds, ephemeral=False)
        except HTTPException as exception:
            await self.bot.get_channel(os.getenv("ERROR_CHANNEL_ID")).send(
                f"Problème d'envoie avec `{bd_user.id}` -> {exception}")

    async def send_weekly_update(self, db_user: DBUser, ics: bool):
        """Permet d'envoyer les EDT automatiquement pour la semaine."""
        try:
            user : User = self.bot.get_user(db_user.id)
            days_since_monday = date.today().weekday()
            monday_date = date.today() - timedelta(days=days_since_monday)
            sunday_date = monday_date + timedelta(days=6)
            events = filter_events (get_calendar(db_user.annee).get_events(), [TimeFilter(monday_date, Timing.AFTER), TimeFilter(sunday_date, Timing.BEFORE), self.get_filiere(user), self.get_groupes(user)])
            embeds = get_embeds(events, user, monday_date, sunday_date)

            if ics:
                filename = str(user.id)
                get_ics(events, filename=filename)
                await user.send("Bonjour voici votre EDT pour la semaine.\n:warning: : Le calendrier n'est pas mis a jour dynamiquement", embeds=embeds, files=[f"{filename}.ics"], ephemeral=False)
                os.remove(f"{filename}.ics")
            else:
                await user.send("Bonjour voici votre EDT pour la semaine.\n:warning: : Le calendrier n'est pas mis a jour dynamiquement", embeds=embeds, ephemeral=False)
        except HTTPException as exception:
            await self.bot.get_channel(os.getenv("ERROR_CHANNEL_ID")).send(
                f"Problème d'envoie avec `{db_user.id}` -> {exception}")

    async def check_subscription(self, ctx: SlashContext) -> None:
        """Permet d'afficher quel sont les abonnements d'un utilisateur."""
        user_base = get_user_base()
        id = ctx.author_id

        ephemeral = False
        if self.is_guild_chan(ctx.author):
            ephemeral = not ctx.author.has_role(self.serveur.get_roles(ctx.guild)[RoleEnum.PERMA])  # Permanent si la personne a le rôle

        await ctx.send(
            embed=Embed(f"Abonnements de {ctx.author.display_name}",
                f"- Mise à Jour Quotidienne : {'✅' if (user_base.is_user_subscribed(id, Subscription.DAILY)) else '❌'}\n"
                f"- Mise à Jour Hebdomadaire : {'✅' if (user_base.is_user_subscribed(id, Subscription.WEEKLY)) else '❌'}\n"
                f"- Mise à Jour Quotidienne ICS: {'✅' if (user_base.is_user_subscribed_ics(id, Subscription.DAILY_ICS)) else '❌'}\n"
                f"- Mise à Jour Hebdomadaire ICS: {'✅' if (user_base.is_user_subscribed_ics(id, Subscription.WEEKLY_ICS)) else '❌'}\n"
                f":warning: vous devez avoir vous mp ouvert ou déjà avoir mp le bot. "
                ),
            ephemeral=ephemeral
        )

    async def subscription_role(self, user_id: int, subscription : Subscription, ajout:bool):
        """Permet d'ajouter / supprimer le role de la subscription à un utilisateur."""
        guild_object = self.bot.guilds[0]
        user_guild = self.bot.get_member(user_id, self.bot.guilds[0])
        if ajout:
            match subscription:
                case Subscription.DAILY:
                    if not user_guild.has_role(self.serveur.get_roles(guild_object)[subscription]):
                        await user_guild.add_role(self.serveur.get_roles(guild_object)[subscription])
                case Subscription.WEEKLY:
                    if not user_guild.has_role(self.serveur.get_roles(guild_object)[subscription]):
                        await user_guild.add_role(self.serveur.get_roles(guild_object)[subscription])
                case Subscription.BOTH:
                    if not user_guild.has_role(self.serveur.get_roles(guild_object)[Subscription.DAILY]):
                        await user_guild.add_role(self.serveur.get_roles(guild_object)[Subscription.DAILY])
                    if not user_guild.has_role(self.serveur.get_roles(guild_object)[Subscription.WEEKLY]):
                        await user_guild.add_role(self.serveur.get_roles(guild_object)[Subscription.WEEKLY])

                case Subscription.DAILY_ICS:
                    await self.subscription_role(user_id, Subscription.DAILY, ajout)
                    if not user_guild.has_role(self.serveur.get_roles(guild_object)[subscription]):
                        await user_guild.add_role(self.serveur.get_roles(guild_object)[subscription])
                case Subscription.WEEKLY_ICS:
                    await self.subscription_role(user_id, Subscription.WEEKLY, ajout)
                    if not user_guild.has_role(self.serveur.get_roles(guild_object)[subscription]):
                        await user_guild.add_role(self.serveur.get_roles(guild_object)[subscription])
                case Subscription.BOTH_ICS:
                    await self.subscription_role(user_id, Subscription.BOTH, ajout)
                    if not user_guild.has_role(self.serveur.get_roles(guild_object)[Subscription.DAILY_ICS]):
                        await user_guild.add_role(self.serveur.get_roles(guild_object)[Subscription.DAILY_ICS])
                    if not user_guild.has_role(self.serveur.get_roles(guild_object)[Subscription.WEEKLY_ICS]):
                        await user_guild.add_role(self.serveur.get_roles(guild_object)[Subscription.WEEKLY_ICS])
        else:
            match subscription:
                case Subscription.DAILY:
                    await self.subscription_role(user_id, Subscription.DAILY_ICS, ajout)
                    if user_guild.has_role(self.serveur.get_roles(guild_object)[subscription]):
                        await user_guild.remove_role(self.serveur.get_roles(guild_object)[subscription])
                case Subscription.WEEKLY:
                    await self.subscription_role(user_id, Subscription.WEEKLY_ICS, ajout)
                    if user_guild.has_role(self.serveur.get_roles(guild_object)[subscription]):
                        await user_guild.remove_role(self.serveur.get_roles(guild_object)[subscription])
                case Subscription.BOTH:
                    await self.subscription_role(user_id, Subscription.BOTH_ICS, ajout)
                    if user_guild.has_role(self.serveur.get_roles(guild_object)[Subscription.DAILY]):
                        await user_guild.remove_role(self.serveur.get_roles(guild_object)[Subscription.DAILY])
                    if user_guild.has_role(self.serveur.get_roles(guild_object)[Subscription.WEEKLY]):
                        await user_guild.remove_role(self.serveur.get_roles(guild_object)[Subscription.WEEKLY])

                case Subscription.DAILY_ICS:
                    if user_guild.has_role(self.serveur.get_roles(guild_object)[subscription]):
                        await user_guild.remove_role(self.serveur.get_roles(guild_object)[subscription])
                case Subscription.WEEKLY_ICS:
                    if user_guild.has_role(self.serveur.get_roles(guild_object)[subscription]):
                        await user_guild.remove_role(self.serveur.get_roles(guild_object)[subscription])
                case Subscription.BOTH_ICS:
                    if user_guild.has_role(self.serveur.get_roles(guild_object)[Subscription.DAILY_ICS]):
                        await user_guild.remove_role(self.serveur.get_roles(guild_object)[Subscription.DAILY_ICS])
                    if user_guild.has_role(self.serveur.get_roles(guild_object)[Subscription.WEEKLY_ICS]):
                        await user_guild.remove_role(self.serveur.get_roles(guild_object)[Subscription.WEEKLY_ICS])

    def get_chan_error_log(self, ctx) -> GuildText | None:
        """Permet d'avoir le chan d'erreur/log"""
        if self.is_guild_chan(ctx.author):
            for chan in ctx.guild.channels:
                if chan.name == "error-log":
                    return chan
        return self.bot.get_channel(os.getenv("ERROR_CHANNEL_ID"))


    @abstractmethod
    def ping_liste(self, event: Event, guild: Guild) -> str:
        pass





class ToolL3(Tool):
    def __init__(self, bot: Client):
        super().__init__(bot)

    def ping_liste(self, event: Event, guild: Guild) -> str:
        """Permet d'avoir une liste de mention pour un Event."""
        roles = self.serveur.get_roles(guild)
        if event.group == Group.CM:
            event : EventL3
            if event.isINGE and event.isMIAGE:
                return f"{roles[Filiere.INGE].mention} {roles[Filiere.MIAGE].mention}"
            elif event.isINGE:
                return f"{roles[Filiere.INGE].mention}"
            else:
                return f"{roles[Filiere.MIAGE].mention}"
        else:
            return f"{roles.get(event.group).mention}"





class ToolL2(Tool):
    def __init__(self, bot: Client):
        super().__init__(bot)

    def ping_liste(self, event: Event, guild: Guild) -> str:
        """Permet d'avoir une liste de mention pour un Event."""
        roles = self.serveur.get_roles(guild)
        if event.group == Group.CM:
            return "@everyone"
        else:
            return f"{roles.get(event.group).mention}"



tool : dict[Annee | None : Tool] = {}

def get_tool(bot : Client, guild:Guild) -> Tool:
    """Permet d'obtenir un objet Tool."""
    global tool

    annee = get_bd_serveur(bot).get_serveur(guild).annee

    if tool.get(annee) is None:
        match annee:
            case Annee.L3:
                tool[annee] = ToolL3(bot)
            case Annee.L2:
                tool[annee] = ToolL2(bot)
            case Annee.UKNW:
                tool[None] = Tool(bot)

    return tool[Annee]
