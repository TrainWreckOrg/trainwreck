from interactions import Client, listen, Extension, component_callback, Embed, ComponentContext
from interactions.api.events import MemberUpdate, Error, Startup
from dotenv import load_dotenv
from datetime import datetime
import os
import re

from UserBase import get_user_base
from MyTask import MyTask
from Tool import get_tool
from Enums import RoleEnum, Filiere, Group
from src.Tool import get_bd_serveur

load_dotenv("keys.env")


class MyListen(Extension):
    """Classe contenant les Listen."""
    def __init__(self, bot: Client):
        self.bot = bot

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
        get_bd_serveur(self.bot)
        if not MyTask.daily_morning_update.running:
            MyTask.daily_morning_update.start()
            await self.bot.get_channel(os.getenv("ERROR_CHANNEL_ID")).send("Démarrage de la Task `daily_morning_update`")
        if not MyTask.update_calendar.running:
            MyTask.update_calendar.start()
            await self.bot.get_channel(os.getenv("ERROR_CHANNEL_ID")).send("Démarrage de la Task `update_calendar`")
        await MyTask.update_calendar()
        print(f"Ready\nThis bot is owned by {self.bot.owner}")
        await self.bot.get_channel(os.getenv("ERROR_CHANNEL_ID")).send("Démarrage du bot v1")

    @component_callback(re.compile("day|week"))
    async def on_component(self, ctx: ComponentContext) -> None:
        """Permet d'écouter les cliques des boutons contenant "day" ou "week"."""
        pattern_day = re.compile("day-")
        pattern_week = re.compile("week-")
        if pattern_day.search(ctx.custom_id):
            await get_tool(self.bot, ctx.guild).get_day_bt(ctx=ctx, jour=ctx.custom_id[4:], modifier=True)
        elif pattern_week.search(ctx.custom_id):
            await get_tool(self.bot, ctx.guild).get_week_bt(ctx, ctx.custom_id[5:], True)
        else:
            await ctx.send("Bouton cliqué mais aucune action définie", ephemeral=True)
            raise ValueError("Bouton cliqué mais aucune action définie (on_component)")

    @listen(MemberUpdate)
    async def on_member_update(self, event: MemberUpdate) -> None:
        """Permet de mettre à jour la base de donnée quand un membre met à jour ses rôles."""
        user_base = get_user_base()
        user = event.after
        if not user_base.has_user(user.id):
            user_base.add_user(user.id, get_tool(self.bot, event.guild).get_groupes_as_list(user), get_tool(self.bot, event.guild).get_filiere_as_filiere(user))
        else:
            user_base.update_user(user.id, get_tool(self.bot, event.guild).get_groupes_as_list(user), get_tool(self.bot, event.guild).get_filiere_as_filiere(user))

    @listen(Error)
    async def on_error(self, error: Error) -> None:
        """Permet de faire la gestion des erreurs pour l'ensemble du bot, envoie un message aux admins et prévient l'utilisateur de l'erreur."""
        await self.bot.get_channel(os.getenv("ERROR_CHANNEL_ID")).send(
            f"{(get_bd_serveur(self.bot).get_master_serveur().roles[RoleEnum.ADMIN]).mention}"
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
        await error.ctx.send(embed=Embed("Une erreur est survenu, les admins sont prévenu."), ephemeral=True)

    @component_callback(re.compile("delete-role"))
    async def wipe_bt(self, ctx: ComponentContext):
        """Permet d'enlever les rôles de Filière et de Groupe à tout le monde"""
        for user in ctx.guild.members:
            for filiere in Filiere:
                if filiere in [Filiere.UKNW]:
                    continue
                if user.has_role(get_bd_serveur(self.bot).get_roles(ctx.guild)[filiere]):
                    await user.remove_role(get_bd_serveur(self.bot).get_roles(ctx.guild)[filiere])
            for group in get_bd_serveur(self.bot).get_serveur(ctx.guild).group:
                if group in [Group.CM, Group.UKNW]:
                    continue
                if user.has_role(get_bd_serveur(self.bot).get_roles(ctx.guild)[group]):
                    await user.remove_role(get_bd_serveur(self.bot).get_roles(ctx.guild)[group])
        await ctx.send("Les membres du serveur n'ont plus de rôle.", ephemeral=False)