from interactions import Client, Task, TimeTrigger, OrTrigger, Embed, Extension, slash_command, SlashContext, \
    Permissions, AllowedMentions
from datetime import datetime
from dotenv import load_dotenv
import os

from Calendar import Calendar, changed_events, create_calendar
from UserBase import get_user_base
from Tool import get_tool, get_bd_serveur
from Enums import Subscription, RoleEnum, Annee

load_dotenv("keys.env")


class MyTask(Extension):
    """Classe contenant les Tasks."""
    def __init__(self, bot: Client):
        self.bot = bot

    @Task.create(OrTrigger(
        TimeTrigger(hour=5, minute=55, utc=False),  # juste avant l'envoi automatique.
        TimeTrigger(hour=7, minute=0, utc=False),
        TimeTrigger(hour=8, minute=0, utc=False),
        TimeTrigger(hour=10, minute=0, utc=False),
        TimeTrigger(hour=12, minute=0, utc=False),
        TimeTrigger(hour=14, minute=0, utc=False),
        TimeTrigger(hour=16, minute=0, utc=False),
        TimeTrigger(hour=18, minute=0, utc=False),
        TimeTrigger(hour=20, minute=0, utc=False)
    ))
    async def update_calendar(self) -> None:
        """Permet de mettre à jour le calendrier et de vérifier qu'il n'y a pas eu de changement."""
        # sup :set[Event]         = set()
        # add :set[Event]         = set()
        # mod :set[(Event,Event)] = set()
        await self.bot.get_channel(os.getenv("ERROR_CHANNEL_ID")).send("Exécution de `update_calendar`")
        for annee in Annee:
            if annee == Annee.UKNW:
                continue

            old_calendar = create_calendar(annee, False)
            new_calendar = create_calendar(annee, True)

            sup, add, mod = changed_events(old_calendar, new_calendar, annee)
            embeds: list[Embed] = []
            ping_liste = ""

            for serveur in get_bd_serveur(self.bot).get_annee(annee):
                guild_object = serveur.guild
                if len(sup) > 0:
                    descstr = ""
                    for event in sup:
                        ping = get_tool(self.bot, guild_object, annee).ping_liste(event, guild_object)
                        ping_liste += ping
                        descstr += f"- {ping} {event.str_day()}\n"
                    embeds.append(Embed(title="Événements supprimés :", description=descstr, color=0xEd4245))

                if len(add) > 0:
                    descstr = ""
                    for event in add:
                        ping = get_tool(self.bot, guild_object, annee).ping_liste(event, guild_object)
                        ping_liste += ping
                        descstr += f"- {ping} {event.str_day()}\n"
                    embeds.append(Embed(title="Événements ajoutés :", description=descstr, color=0x57f287))

                if len(mod) > 0:
                    descstr = ""
                    for (old, new) in mod:
                        ping = get_tool(self.bot, guild_object, annee).ping_liste(old, guild_object)
                        if old.group != new.group:
                            ping += f" {get_tool(self.bot, guild_object, annee).ping_liste(new, guild_object)}"
                        ping_liste += ping
                        descstr += f"- {ping}\n\t- {old.str_day(new)}\n - ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ⇓\n - {new.str_day(old)}\n"
                    embeds.append(Embed(title="Événements modifiés :", description=descstr, color=0x5865f2))

                if len(embeds):
                    ping_liste = f"Il y a eu des modification dans l'EDT ||{ping_liste}||"
                    await serveur.channel_changement_edt.send(ping_liste, embeds=embeds, ephemeral=False)

    @Task.create(TimeTrigger(hour=6, minute=0, seconds=0, utc=False))
    async def daily_morning_update(self) -> None:
        """Permet d'envoyer les EDT automatiquement."""
        await self.bot.get_channel(os.getenv("ERROR_CHANNEL_ID")).send("Exécution de `daily_morning_update`")
        user_base = get_user_base()
        # Pour l'envoi hebdomadaire.
        if datetime.today().weekday() == 0:
            for id in user_base.weekly_subscribed_users:
                user = user_base.get_user(id)
                tool = get_tool(self.bot, annee=user.annee)
                await tool.send_weekly_update(user, user_base.is_user_subscribed_ics(id, Subscription.WEEKLY_ICS))
        # Pour l'envoi quotidien.
        if datetime.today().weekday() <= 4:  # Si on est le week end
            for id in user_base.daily_subscribed_users:
                user = user_base.get_user(id)
                tool = get_tool(self.bot, annee=user.annee)
                await tool.send_daily_update(user, user_base.is_user_subscribed_ics(id, Subscription.WEEKLY_ICS))

    @slash_command(name="send_daily", description="Envoie les messages daily",
                   default_member_permissions=Permissions.ADMINISTRATOR)
    async def send_daily(self, ctx: SlashContext):
        """Fonction qui permet d'envoyer le message automatique."""
        # Elle est ici parce que ailleurs, il y aurait des problèmes d'import circulaire (je pense).
        ephemeral = False
        if get_tool(self.bot, ctx.guild).is_guild_chan(ctx.author):
            ephemeral = not ctx.author.has_role(
                get_bd_serveur(self.bot).get_roles(ctx.guild)[RoleEnum.PERMA])  # Permanent si la personne a le rôle
        await ctx.send("Envoie des messages automatique.", ephemeral=ephemeral)
        await self.daily_morning_update()

    @slash_command(name="update_force", description="Force la mise à jour du calendrier",
                   default_member_permissions=Permissions.ADMINISTRATOR)
    async def update_force(self, ctx: SlashContext):
        """Fonction qui permet de forcer la mise à jour du calendrier."""
        # Elle est ici parce que ailleurs, il y aurait des problèmes d'import circulaire (je pense).
        ephemeral = False
        if get_tool(self.bot, ctx.guild).is_guild_chan(ctx.author):
            ephemeral = not ctx.author.has_role(
                get_bd_serveur(self.bot).get_roles(ctx.guild)[RoleEnum.PERMA])  # Permanent si la personne a le rôle
        await ctx.send("Mise à jour du calendrier.", ephemeral=ephemeral)
        await self.update_calendar()