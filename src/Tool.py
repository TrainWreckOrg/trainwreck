import sentry_sdk
from interactions import Client, ActionRow, Button, ButtonStyle, SlashContext, Guild, Role, Embed, User, Member, \
    ModalContext, ContextMenuContext, ComponentContext

from TrainWreck import get_embeds, get_ics
from UserBase import get_user_base
from Calendar import get_calendar
from Filter import *
from Enums import RoleEnum, Group, colors


from datetime import datetime, date, timedelta
from enum import Enum
import os


class Tool:
    """Classe regroupant plusieurs méthodes utiles."""
    def __init__(self, bot: Client):
        self.guild = None
        self.bot = bot
        self.roles: dict[int, dict[Enum:Role]] = {}

    def get_roles(self, guild: Guild) -> dict[Enum:Role]:
        """Permet d'obtenir le dictionnaire des Role discord associé aux Enum."""
        if self.roles.get(int(guild.id)) is None:
            self.roles[int(guild.id)] = {}
            for role in guild.roles:
                if role.name in Group:
                    for groupe in Group:
                        if groupe.value == role.name:
                            self.roles[int(guild.id)][groupe] = role
                if role.name in Filiere:
                    for filiere in Filiere:
                        if filiere.value == role.name:
                            self.roles[int(guild.id)][filiere] = role
                if role.name in RoleEnum:
                    for roleEnum in RoleEnum:
                        if roleEnum.value == role.name:
                            self.roles[int(guild.id)][roleEnum] = role
        return self.roles.get(int(guild.id))


    def get_filiere_as_filiere(self, author: User | Member) -> Filiere:
        """Fonction qui permet d'avoir la filière d'un utilisateur, renvoie UKNW si pas définie."""
        if self.is_guild_chan(author):
            if author.has_role(self.get_roles(author.guild)[Filiere.INGE]):
                return Filiere.INGE
            if author.has_role(self.get_roles(author.guild)[Filiere.MIAGE]):
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
        else :
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
            f"{(self.get_roles(guild)[RoleEnum.ADMIN]).mention} {exception}")

    def ping_liste(self, event: Event, guild: Guild) -> str:
        """Permet d'avoir une liste de mention pour un Event."""
        roles = self.get_roles(guild)
        if event.group == Group.CM:
            if event.isINGE and event.isMIAGE:
                return f"{roles[Filiere.INGE].mention} {roles[Filiere.MIAGE].mention}"
            elif event.isINGE:
                return f"{roles[Filiere.INGE].mention}>"
            else:
                return f"{roles[Filiere.MIAGE].mention}"
        else:
            return f"{roles.get(event.group).mention}"

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

            events: list[Event] = filter_events(get_calendar().get_events(),
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

            ephemeral = self.is_guild_chan(ctx.author)
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
            await ctx.send(embeds=[self.create_error_embed(f"La valeur `{jour}` ne correspond pas à une date")], ephemeral=True)

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
            events: list[Event] = filter_events(get_calendar().get_events(), [TimeFilter(monday_date, Timing.AFTER), TimeFilter(sunday_date, Timing.BEFORE), self.get_filiere(author), self.get_groupes(author)])

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

            ephemeral = self.is_guild_chan(ctx.author)

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
            await ctx.send(embeds=[self.create_error_embed(f"La valeur `{semaine}` ne correspond pas à une date")], ephemeral=True)

    async def send_daily_update(self, user: User):
        """Permet d'envoyer les EDT automatiquement pour le jour."""
        events = filter_events(get_calendar().get_events(), [TimeFilter(date.today(), Timing.DURING), self.get_filiere(user), self.get_groupes(user)] )
        embeds = get_embeds(events, user, date.today())
        filename = str(user.id)
        ics_file = get_ics(events, filename=filename)
        with open("debug.txt", "a", encoding="UTF-8") as f:
            f.write(f"avant envoi pour {user.id}\n")
        await user.send(":warning: : Le calendrier n'est pas mis a jour dynamiquement", embeds=embeds, files=[f"{filename}.ics"], ephemeral=False)
        with open("debug.txt", "a", encoding="UTF-8") as f:
            f.write(f"après envoi pour {user.id}\n")
        os.remove(f"{filename}.ics")

    async def send_weekly_update(self, user: User):
        """Permet d'envoyer les EDT automatiquement pour la semaine."""
        days_since_monday = date.today().weekday()
        monday_date = date.today() - timedelta(days=days_since_monday)
        sunday_date = monday_date + timedelta(days=6)
        filename = str(user.id)

        events = filter_events (get_calendar().get_events(), [TimeFilter(monday_date, Timing.AFTER), TimeFilter(sunday_date, Timing.BEFORE), self.get_filiere(user), self.get_groupes(user)])
        ics_file = get_ics(events, filename=filename)
        with open("debug.txt", "a", encoding="UTF-8") as f:
            f.write(f"avant envoi pour {user.id}\n")
        await user.send(":warning: : Le calendrier n'est pas mis a jour dynamiquement", embeds=get_embeds(events, user, monday_date, sunday_date), files=[f"{filename}.ics"], ephemeral=False)
        with open("debug.txt", "a", encoding="UTF-8") as f:
            f.write(f"après envoi pour {user.id}\n")
        os.remove(f"{filename}.ics")





tool: Tool | None = None


def get_tool(bot : Client) -> Tool:
    """Permet d'obtenir un objet Tool."""
    global tool
    if tool is None:
        tool = Tool(bot)
    return tool


def get_tool_sans_bot() -> Tool | None:
    """Permet d'obtenir un objet Tool."""
    global tool
    return tool
