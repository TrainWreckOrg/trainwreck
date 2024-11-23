import json
from urllib.error import URLError
from urllib.request import urlretrieve

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
from sender import send, get_error_log_chan, send_error
from Enums import Filiere

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
        await send(get_error_log_chan(),"Exécution de `update_calendar`")


        arguement  = await self.tool.get_arguement()

        maj = arguement.get("maj_ics")
        if maj != "True" and datetime.now() >= datetime.strptime(maj, "%d-%m-%Y %H:%M:%S"):
            calendar = Calendar(False, arguement)
            set_calendar(calendar)
            await send(get_error_log_chan(),"Désactivation de la mise à jour des ics.")
            return

        old_calendar = Calendar(False, arguement)
        new_calendar = Calendar(True, arguement)
        sup, add, mod, changed_id = changed_events(old_calendar, new_calendar)
        overlap_list = overlap(new_calendar, arguement)

        await send(get_error_log_chan(),f"Fichier du {datetime.now()}", files=["data/INGE.ics", "data/MIAGE.ics"])
        if changed_id:
            await send(get_error_log_chan(),f"l'id d'un cours a changé : {changed_id}")

        serveur = self.bot.user.guilds[0]


        embeds, ping_list_str = self.get_embeds_maj(sup, add, mod, overlap_list)

        await self.site_fac_exam()

        if len(embeds):
            ping_chan = self.bot.get_channel(os.getenv("PING_CHANGE_CHANNEL_ID"))
            ping_liste = f"Il y a eu des modifications dans l'EDT ||{ping_list_str}||"
            # await ping_chan.send(ping_liste, embeds=embeds, ephemeral=False, allowed_mentions=AllowedMentions(roles=serveur.roles))
            await send(ping_chan,ping_liste, embeds=embeds, ephemeral=False)


    async def site_fac_exam(self):
        try:
            urlretrieve(
                "https://www.univ-orleans.fr/fr/sciences-techniques/etudiant/examens-reglementationrse/examens/examens-licences",
                "siteFac.html")
        except URLError as exception:
            await send_error(exception)

        try:
            with open("siteFac.html", 'r') as fichier:
                contenu = fichier.read()
        except Exception as exception:
            await send_error(exception)

        bloc_inge = """<li style="line-height:normal;margin-bottom:8.25pt;margin-left:42.0pt;tab-stops:list 36.0pt;"><span style="color:#2CB7C5;font-family:&quot;Century Gothic&quot;,sans-serif;"><strong>L3 INFORMATIQUE ING&nbsp;:</strong></span><span style="color:#2CB7C5;font-family:&quot;Century Gothic&quot;,sans-serif;font-size:12.0pt;"><strong><o:p></o:p></strong></span></li>"""
        bloc_miage = """<li style="line-height:normal;margin-bottom:8.25pt;margin-left:42.0pt;tab-stops:list 36.0pt;"><span style="color:#2CB7C5;font-family:&quot;Century Gothic&quot;,sans-serif;"><strong>L3 INFORMATIQUE MIAGE&nbsp;:&nbsp;&nbsp;</strong></span><span style="color:#2CB7C5;font-family:&quot;Century Gothic&quot;,sans-serif;font-size:12.0pt;"><strong><o:p></o:p></strong></span></li>"""

        if contenu.find(bloc_inge) == -1:
            chan = self.bot.get_channel(os.getenv("PING_CHANGE_CHANNEL_ID"))
            role_inge = self.tool.get_roles(self.bot.guilds[0])[Filiere.INGE].mention
            await send(chan, f"{role_inge} il y a les dates d'exam ici -> https://www.univ-orleans.fr/fr/sciences-techniques/etudiant/examens-reglementationrse/examens/examens-licences", ephemeral=False)

        if contenu.find(bloc_miage) == -1:
            chan = self.bot.get_channel(os.getenv("PING_CHANGE_CHANNEL_ID"))
            role_miage = self.tool.get_roles(self.bot.guilds[0])[Filiere.MIAGE].mention
            await send(chan, f"{role_miage} il y a les dates d'exam ici -> https://www.univ-orleans.fr/fr/sciences-techniques/etudiant/examens-reglementationrse/examens/examens-licences", ephemeral=False)

        os.remove("siteFac.html")



    def get_embeds_maj(self,sup, add,mod,overlap_list):

        embeds: list[Embed] = []
        ping_liste = set()

        serveur = self.bot.user.guilds[0]

        if len(sup) > 0:
            descstr = ""
            for event in sup:
                ping = self.tool.ping_liste(event, serveur)
                ping_liste.add(ping)
                tmp = f"- {ping} {event.str_day()}\n"
                if len(descstr + tmp) > 4096:
                    embeds.append(Embed(title="Événements supprimés :", description=descstr, color=0xEd4245))
                    descstr = ""
                descstr += tmp

            embeds.append(Embed(title="Événements supprimés :", description=descstr, color=0xEd4245))

        if len(add) > 0:
            descstr = ""
            for event in add:
                ping = self.tool.ping_liste(event, serveur)
                ping_liste.add(ping)
                tmp = f"- {ping} {event.str_day()}\n"
                if len(descstr + tmp) > 4096:
                    embeds.append(Embed(title="Événements ajoutés :", description=descstr, color=0x57f287))
                    descstr = ""
                descstr += tmp
            embeds.append(Embed(title="Événements ajoutés :", description=descstr, color=0x57f287))

        if len(mod) > 0:
            descstr = ""
            for (old, new) in mod:
                ping = self.tool.ping_liste(old, serveur)
                if old.group != new.group:
                    ping += f" {self.tool.ping_liste(new, serveur)}"
                ping_liste.add(ping)
                tmp = f"- {ping}\n    - {old.str_day(new)}\n   - ⇓\n   - {new.str_day(old)}\n"
                if len(descstr + tmp) > 4096:
                    embeds.append(Embed(title="Événements modifiés :", description=descstr, color=0x5865f2))
                    descstr = ""
                descstr += tmp
            embeds.append(Embed(title="Événements modifiés :", description=descstr, color=0x5865f2))

        if len(overlap_list) > 0:
            descstr = ""
            for (event1, event2) in overlap_list:
                ping = self.tool.ping_liste(event1, serveur)
                if event1.group != event2.group:
                    ping += f" {self.tool.ping_liste(event2, serveur)}"
                ping_liste.add(ping)
                tmp = f"- {ping}\n    - {event1.str_day()}\n   - {event2.str_day()}\n"
                if len(descstr + tmp) > 4096:
                    embeds.append(Embed(title="CHEVAUCHEMENT DE COURS DÉTECTÉ :", description=descstr, color=0xEd4245))
                    descstr = ""
                descstr += tmp
            embeds.append(Embed(title="CHEVAUCHEMENT DE COURS DÉTECTÉ :", description=descstr, color=0xEd4245))

        ping_list_str = ""
        for ping in ping_liste:
            ping_list_str += ping

        return embeds, ping_list_str






    @Task.create(TimeTrigger(hour=6, minute=0, seconds=0, utc=False))
    async def daily_morning_update(self) -> None:
        """Permet d'envoyer les EDT automatiquement."""
        await send(get_error_log_chan(), "Exécution de `daily_morning_update`")

        argument = await self.tool.get_arguement()
        if argument.get("send_daily_state") == "False":
            await send(get_error_log_chan(), "Exécution de `daily_morning_update` à été désactivée")
            return
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
        await send(ctx,"Envoie des messages automatique.", auto_ephemeral=True)
        await self.daily_morning_update()

    @slash_command(name="update_force", description="Force la mise à jour du calendrier",
                   default_member_permissions=Permissions.ADMINISTRATOR, contexts=[ContextType.GUILD])
    async def update_force(self, ctx: SlashContext):
        """Fonction qui permet de forcer la mise à jour du calendrier."""
        # Elle est ici parce que ailleurs, il y aurait des problèmes d'import circulaire (je pense).
        await send(ctx,"Mise à jour du calendrier.", auto_ephemeral=True)
        await self.update_calendar()