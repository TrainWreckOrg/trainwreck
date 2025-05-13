from interactions import Client, listen, Extension, component_callback, Embed, ComponentContext
from interactions.api.events import MemberUpdate, Error, Startup
from dotenv import load_dotenv
from datetime import datetime
import os
import re

from UserBase import get_user_base, nuke
from MyTask import MyTask
from Tool import get_tool
from Enums import RoleEnum, Filiere, Group
from sender import send, get_error_log_chan

load_dotenv("keys.env")


class MyListen(Extension):
    """Classe contenant les Listen."""
    def __init__(self, bot: Client):
        self.bot = bot
        self.tool = get_tool(bot)

    @listen(Startup)
    async def on_ready(self) -> None:
        """Méthode qui dit quand le bot est opérationnel au démarrage du programme,
        synchro les commandes, active les Task et lance la génération du calendrier."""
        print(
            """
            \u001b[2;35m  ______           _       _       __               __   
            \u001b[0m\u001b[2;31m /_  __/________ _(_)___  | |     / /_______  _____/ /__ 
            \u001b[0m\u001b[2;33m  / / / ___/ __ `/ / __ \\ | | /| / / ___/ _ \\/ ___/ //_/ 
            \u001b[0m\u001b[2;36m / / / /  / /_/ / / / / / | |/ |/ / /  /  __/ /__/ ,<    
            \u001b[0m\u001b[2;34m/_/ /_/   \\__,_/_/_/ /_/  |__/|__/_/   \\___/\\___/_/|_|(_)\u001b[0m
            """
        )
        await self.bot.synchronise_interactions()
        nuke()
        await self.tool.userscan(get_error_log_chan())
        if MyTask.daily_morning_update.running:
            MyTask.daily_morning_update.stop()
        if MyTask.update_calendar.running:
            MyTask.update_calendar.stop()

        # if not MyTask.daily_morning_update.running:
        #     MyTask.daily_morning_update.start()
        #     await send(get_error_log_chan(), "Démarrage de la Task `daily_morning_update`")
        # if not MyTask.update_calendar.running:
        #     MyTask.update_calendar.start()
        #     await send(get_error_log_chan(), "Démarrage de la Task `update_calendar`")
        await MyTask.update_calendar()
        print(f"Ready\nThis bot is owned by {self.bot.owner}")
        await send(get_error_log_chan(), "Démarrage du bot fini")


    @component_callback(re.compile("day|week"))
    async def on_component(self, ctx: ComponentContext) -> None:
        """Permet d'écouter les cliques des boutons contenant "day" ou "week"."""
        pattern_day = re.compile("day-")
        pattern_week = re.compile("week-")
        if pattern_day.search(ctx.custom_id):
            await self.tool.get_day_bt(ctx=ctx, jour=ctx.custom_id[4:], modifier=True)
        elif pattern_week.search(ctx.custom_id):
            await self.tool.get_week_bt(ctx, ctx.custom_id[5:], True)
        else:
            await send(ctx,"Bouton cliqué mais aucune action définie", ephemeral=True)
            raise ValueError("Bouton cliqué mais aucune action définie (on_component)")

    @listen(MemberUpdate)
    async def on_member_update(self, event: MemberUpdate) -> None:
        """Permet de mettre à jour la base de donnée quand un membre met à jour ses rôles."""
        user_base = get_user_base()
        user = event.after
        if not user_base.has_user(user.id):
            user_base.add_user(user.id, self.tool.get_groupes_as_list(user), self.tool.get_filiere_as_filiere(user))
        else:
            user_base.update_user(user.id, self.tool.get_groupes_as_list(user), self.tool.get_filiere_as_filiere(user))

    @listen(Error)
    async def on_error(self, error: Error) -> None:
        """Permet de faire la gestion des erreurs pour l'ensemble du bot, envoie un message aux admins et prévient l'utilisateur de l'erreur."""
        await send(get_error_log_chan(),
            f"{(self.tool.get_roles(error.ctx.guild)[RoleEnum.ADMIN]).mention}"
            f"```ERREUR dans : {error.source} - {datetime.now()}\n"
            f"Erreur de type : {type(error.error)}\n"
            f"Argument de l'erreur : {error.error.args}\n"
            f"Description de l'erreur : {error.error}\n"
            f"Les paramètres de la fonction étais : \n"
                f" - auteur : {error.ctx.author}\n"
                f" - serveur :  {error.ctx.guild}\n"
                f" - message :  {error.ctx.message}\n"
                f" - channel :  {error.ctx.channel}\n"
                f" - role member :  {error.ctx.member.roles}```"
        )
        await send(error.ctx,embeds=[Embed("Une erreur est survenue, les admins sont prévenu.")], ephemeral=True)

    @component_callback(re.compile("delete-role"))
    async def wipe_bt(self, ctx: ComponentContext):
        """Permet d'enlever les rôles de Filière et de Groupe à tout le monde"""
        for user in ctx.guild.members:
            for filiere in Filiere:
                if filiere in [Filiere.UKNW]:
                    continue
                if user.has_role(self.tool.get_roles(ctx.guild)[filiere]):
                    await user.remove_role(self.tool.get_roles(ctx.guild)[filiere])
            for group in Group:
                if group in [Group.CM, Group.UKNW]:
                    continue
                if user.has_role(self.tool.get_roles(ctx.guild)[group]):
                    await user.remove_role(self.tool.get_roles(ctx.guild)[group])
        await send(ctx,"Les membres du serveur n'ont plus de rôle.", ephemeral=False)

    @component_callback(re.compile("stop-bot"))
    async def stop_bt(self, ctx: ComponentContext):
        """Permet d'enlever les rôles de Filière et de Groupe à tout le monde"""
        await send(ctx,"Le bot va s'arrêter.", ephemeral=False)
        await self.bot.stop()