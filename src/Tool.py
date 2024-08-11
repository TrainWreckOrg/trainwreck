from interactions import ActionRow, Button, ButtonStyle, SlashContext, Guild, Role, Embed, User, Member

from TrainWreck import get_embeds, get_ics
from UserBase import get_user_base
from Calendar import get_calendar
from Filter import *
from Enums import RoleEnum

from datetime import datetime, date, timedelta
from enum import Enum
import os


class Tool:
    """Classe regroupant plusieurs méthodes utiles."""
    def __init__(self, bot):
        self.bot = bot
        self.roles: dict[Enum:Role] = {}

    def get_roles(self):
        """Permet d'obtenir le dictionnaire des Role discord associé aux Enum."""
        if self.roles == {}:
            serveur: Guild = self.bot.get_guild(os.getenv("SERVEUR_ID"))
            for role in serveur.roles:
                if role.name in Group:
                    for groupe in Group:
                        if groupe.value == role.name:
                            self.roles[groupe] = role
                if role.name in Filiere:
                    for filiere in Filiere:
                        if filiere.value == role.name:
                            self.roles[filiere] = role
                if role.name in RoleEnum:
                    for roleEnum in RoleEnum:
                        if roleEnum.value == role.name:
                            self.roles[roleEnum] = role
        return self.roles

    def get_filiere(self, author) -> FiliereFilter:
        """Fonction qui permet d'avoir le filtre filière d'un utilisateur, renvoie un filtre neutre si pas défini."""
        if self.is_guild_chan(author):
            roles = author.roles
            for role in roles:
                if role.name == Filiere.INGE.value:
                    return FiliereFilter(Filiere.INGE)
                if role.name == Filiere.MIAGE.value:
                    return FiliereFilter(Filiere.MIAGE)
        elif get_user_base().has_user(author.id):
            return FiliereFilter(get_user_base().get_user(author.id).filiere)
        return Filter()

    def get_filiere_as_filiere(self, author) -> Filiere:
        """Fonction qui permet d'avoir la filière d'un utilisateur, renvoie UKNW si pas définie."""
        if self.is_guild_chan(author):
            roles = author.roles
            for role in roles:
                if role.name == Filiere.INGE.value:
                    return Filiere.INGE
                if role.name == Filiere.MIAGE.value:
                    return Filiere.MIAGE
        elif get_user_base().has_user(author.id):
            return get_user_base().get_user(author.id).filiere
        return Filiere.UKNW

    def get_groupes(self, author) -> GroupFilter:
        """Fonction qui renvoie un filtre des groupes d'un utilisateur."""
        if self.is_guild_chan(author):
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

    def get_groupes_as_list(self, author) -> list[Group]:
        """Fonction qui renvoie la liste des groupes d'un utilisateur."""
        if self.is_guild_chan(author):
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

    def is_guild_chan(self, author) -> bool:
        """Permet de savoir si l'auteur est un member (si l'action a été fait dans un serveur ou en MP)."""
        return "Member" in str(type(author))

    def create_error_embed(self, message:str) -> Embed:
        """Permet de créer un Embed d'erreur."""
        return Embed(":warning: Erreur: ", message, 0x992d22)

    def ping_liste(self, event : Event) -> str:
        """Permet d'avoir une liste de mention pour un Event."""
        roles = self.get_roles()
        if event.group == Group.CM:
            if event.isINGE and event.isMIAGE:
                return f"{roles[Filiere.INGE].mention} {roles[Filiere.MIAGE].mention}"
            elif event.isINGE:
                return f"{roles[Filiere.INGE].mention}>"
            else:
                return f"{roles[Filiere.MIAGE].mention}"
        else:
            return f"{roles.get(event.group).mention}"

    async def get_day_bt(self, ctx, jour: str, modifier: bool, personne: User = None, ephemeral: bool= False):
        """Fonction qui permet d'obtenir l'EDT d'une journée spécifique.
            Jour : Le jour que l'on souhaite obtenir.
            Modifier : Si l'on doit modifier le message d'origine ou bien en envoyer un nouveau.
            Personne : La personne dont laquelle on veut savoir l'emploi du temps.
            Ephemeral : Si l'on envoie le message en ephemeral."""
        try:
            author = ctx.author if (personne is None) else personne

            date_formater = datetime.strptime(jour, "%d-%m-%Y").date()

            events: list[Event] = []
            if int(author.id) == int(os.getenv("BOT_ID")):
                events = filter_events(get_calendar().get_events(), [TimeFilter(date_formater, Timing.DURING)])
            else:
                events = filter_events(get_calendar().get_events(),
                                       [TimeFilter(date_formater, Timing.DURING), self.get_filiere(author),
                                        self.get_groupes(author)])
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

    async def get_week_bt(self, ctx: SlashContext, semaine : str, modifier: bool, personne: User = None, ephemeral: bool= False):
        """Fonction qui permet d'obtenir l'EDT d'une semaine spécifique.
                    Semaine : La semaine que l'on souhaite obtenir.
                    Modifier : Si l'on doit modifier le message d'origine ou bien en envoyer un nouveau.
                    Personne : La personne dont laquelle on veut savoir l'emploi du temps.
                    Ephemeral : Si l'on envoie le message en ephemeral."""
        try:
            author = ctx.author if (personne is None) else personne

            date_formater = datetime.strptime(semaine, "%d-%m-%Y").date()
            days_since_monday = date_formater.weekday()
            monday_date = date_formater - timedelta(days=days_since_monday)
            sunday_date = monday_date + timedelta(days=6)
            events :list[Event] = []
            if int(author.id) == int(os.getenv("BOT_ID")):
                events = filter_events(get_calendar().get_events(),[TimeFilter(monday_date, Timing.AFTER), TimeFilter(sunday_date, Timing.BEFORE)])
            else :
                events = filter_events(get_calendar().get_events(), [TimeFilter(monday_date, Timing.AFTER), TimeFilter(sunday_date, Timing.BEFORE), self.get_filiere(author), self.get_groupes(author)])

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

    async def send_daily_update(self, user):
        """Permet d'envoyer les EDT automatiquement pour le jour."""
        events = filter_events(get_calendar().get_events(), [TimeFilter(date.today(), Timing.DURING), self.get_filiere(user), self.get_groupes(user)] )
        embeds = get_embeds(events, user, date.today())
        ics_file = get_ics(events)
        await user.send(embeds=embeds, files=["output/calendar.ics"], ephemeral=False)

    async def send_weekly_update(self, user):
        """Permet d'envoyer les EDT automatiquement pour la semaine."""
        days_since_monday = date.today().weekday()
        monday_date = date.today() - timedelta(days=days_since_monday)
        sunday_date = monday_date + timedelta(days=6)

        events = filter_events (get_calendar().get_events(), [TimeFilter(monday_date, Timing.AFTER), TimeFilter(sunday_date, Timing.BEFORE), self.get_filiere(user), self.get_groupes(user)])
        ics_file = get_ics(events)
        await user.send(embeds=get_embeds(events, user, monday_date, sunday_date), files=["output/calendar.ics"], ephemeral=False)


tool: Tool = None


def get_tool(bot) -> Tool:
    """Permet d'obtenir un objet Tool."""
    global tool
    if tool is None:
        tool = Tool(bot)
    return tool
