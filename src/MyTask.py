import json

from interactions import Client, Task, TimeTrigger, OrTrigger, Embed, Extension, slash_command, SlashContext, \
    Permissions, AllowedMentions, ContextType
from datetime import datetime
from dotenv import load_dotenv
import os

from Calendar import Calendar, changed_events, overlap, set_calendar
from Event import Event
from UserBase import get_user_base
from Tool import get_tool
from Enums import Subscription, RoleEnum

load_dotenv("keys.env")


class MyTask(Extension):
    """Classe contenant les Tasks."""
    def __init__(self, bot: Client):
        self.bot = bot
        self.tool = get_tool(bot)

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
        try:
            await self.bot.get_channel(os.getenv("ERROR_CHANNEL_ID")).send("Exécution de `update_calendar`")
        except:
            pass

        arguement  = await self.tool.get_arguement()
        """if datetime.now() >= datetime(2024,10,24,11,00,00):
            calendar = Calendar(False, arguement)
            set_calendar(calendar)
            try:
                await self.bot.get_channel(os.getenv("ERROR_CHANNEL_ID")).send("Désactivation de la mise à jour des ics.")
            except:
                pass
            return"""

        old_calendar = Calendar(False, arguement)
        new_calendar = Calendar(True, arguement)
        sup, add, mod, changed_id = changed_events(old_calendar, new_calendar)
        overlap_list = overlap(new_calendar, arguement)
        try:
            await self.bot.get_channel(os.getenv("ERROR_CHANNEL_ID")).send(f"Fichier du {datetime.now()}", files=["data/INGE.ics", "data/MIAGE.ics"])
            if changed_id:
                await self.bot.get_channel(os.getenv("ERROR_CHANNEL_ID")).send(f"l'id d'un cours a changé : {changed_id}")
        except:
            pass


        embeds: list[Embed] = []
        ping_liste = set()

        serveur = self.bot.user.guilds[0]

        if len(sup) > 0:
            descstr = ""
            for event in sup:
                ping = self.tool.ping_liste(event, serveur)
                ping_liste.add(ping)
                descstr += f"- {ping} {event.str_day()}\n"
            embeds.append(Embed(title="Événements supprimés :", description=descstr, color=0xEd4245))

        if len(add) > 0:
            descstr = ""
            for event in add:
                ping = self.tool.ping_liste(event, serveur)
                ping_liste.add(ping)
                descstr += f"- {ping} {event.str_day()}\n"
            embeds.append(Embed(title="Événements ajoutés :", description=descstr, color=0x57f287))

        if len(mod) > 0:
            descstr = ""
            for (old, new) in mod:
                ping = self.tool.ping_liste(old, serveur)
                if old.group != new.group:
                    ping += f" {self.tool.ping_liste(new, serveur)}"
                ping_liste.add(ping)
                descstr += f"- {ping}\n    - {old.str_day(new)}\n   - ⇓\n   - {new.str_day(old)}\n"#f"- {ping}\n\t- {old.str_day(new)}\n\t- ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ⇓\n\t- {new.str_day(old)}\n"
            embeds.append(Embed(title="Événements modifiés :", description=descstr, color=0x5865f2))

        if len(overlap_list) > 0:
            descstr = ""
            for (event1, event2) in overlap_list:
                ping = self.tool.ping_liste(event1, serveur)
                if event1.group != event2.group:
                    ping += f" {self.tool.ping_liste(event2, serveur)}"
                ping_liste.add(ping)
                descstr += f"- {ping}\n    - {event1.str_day()}\n   - {event2.str_day()}\n"
            embeds.append(Embed(title="CHEVAUCHEMENT DE COURS DÉTECTÉ :", description=descstr, color=0xEd4245))

        ping_list_str = ""
        for ping in ping_liste:
            ping_list_str += ping

        if len(embeds):
            ping_chan = self.bot.get_channel(os.getenv("PING_CHANGE_CHANNEL_ID"))
            ping_liste = f"Il y a eu des modification dans l'EDT ||{ping_list_str}||"
            await ping_chan.send(ping_liste, embeds=embeds, ephemeral=False, allowed_mentions=AllowedMentions(roles=serveur.roles))

    @Task.create(TimeTrigger(hour=6, minute=0, seconds=0, utc=False))
    async def daily_morning_update(self) -> None:
        """Permet d'envoyer les EDT automatiquement."""
        try:
            await self.bot.get_channel(os.getenv("ERROR_CHANNEL_ID")).send("Exécution de `daily_morning_update`")
        except:
            pass
        user_base = get_user_base()
        # Pour l'envoi hebdomadaire.
        if datetime.today().weekday() == 0:
            for id in user_base.weekly_subscribed_users:
                await self.tool.send_weekly_update(self.bot.get_user(id), user_base.is_user_subscribed_ics(id, Subscription.WEEKLY_ICS))
        # Pour l'envoi quotidien.
        if datetime.today().weekday() <= 4:  # Si on est le week end
            for id in user_base.daily_subscribed_users:
                await self.tool.send_daily_update(self.bot.get_user(id), user_base.is_user_subscribed_ics(id, Subscription.DAILY_ICS))

    @slash_command(name="send_daily", description="Envoie les messages daily",
                   default_member_permissions=Permissions.ADMINISTRATOR, contexts=[ContextType.GUILD])
    async def send_daily(self, ctx: SlashContext):
        """Fonction qui permet d'envoyer le message automatique."""
        # Elle est ici parce que ailleurs, il y aurait des problèmes d'import circulaire (je pense).
        ephemeral = False
        if self.tool.is_guild_chan(ctx.author):
            ephemeral = not ctx.author.has_role(
                self.tool.get_roles(ctx.guild)[RoleEnum.PERMA])  # Permanent si la personne a le rôle
        await ctx.send("Envoie des messages automatique.", ephemeral=ephemeral)
        await self.daily_morning_update()

    @slash_command(name="update_force", description="Force la mise à jour du calendrier",
                   default_member_permissions=Permissions.ADMINISTRATOR, contexts=[ContextType.GUILD])
    async def update_force(self, ctx: SlashContext):
        """Fonction qui permet de forcer la mise à jour du calendrier."""
        # Elle est ici parce que ailleurs, il y aurait des problèmes d'import circulaire (je pense).
        ephemeral = False
        if self.tool.is_guild_chan(ctx.author):
            ephemeral = not ctx.author.has_role(
                self.tool.get_roles(ctx.guild)[RoleEnum.PERMA])  # Permanent si la personne a le rôle
        await ctx.send("Mise à jour du calendrier.", ephemeral=ephemeral)
        await self.update_calendar()