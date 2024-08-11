from interactions import listen, Extension, component_callback, Embed
from interactions.api.events import Component, MemberUpdate, Error

from UserBase import get_user_base
from MyTask import MyTask
from Tool import get_tool

from datetime import datetime
import os
import re


class MyListen(Extension):
    """Classe contenant les Listen."""
    def __init__(self, bot):
        self.bot = bot
        self.tool = get_tool(bot)

    @listen()
    async def on_ready(self):
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
        print(f"Ready\nThis bot is owned by {self.bot.owner}")
        await self.bot.synchronise_interactions()
        MyTask.daily_morning_update.start()
        MyTask.update_calendar.start()
        await MyTask.update_calendar()

    @component_callback(re.compile("day|week"))
    async def on_component(self, ctx: Component):
        """Permet d'écouter les cliques des boutons contenant "day" ou "week"."""
        pattern_day = re.compile("day-")
        pattern_week = re.compile("week-")
        if pattern_day.search(ctx.custom_id):
            await self.tool.get_day_bt(ctx=ctx, jour=ctx.custom_id[4:], modifier=True)
        elif pattern_week.search(ctx.custom_id):
            await self.tool.get_week_bt(ctx, ctx.custom_id[5:], True)
        else:
            await ctx.send("Bouton cliqué mais aucune action définie", ephemeral=True)
            raise ValueError("Bouton cliqué mais aucune action définie (on_component)")

    @listen(MemberUpdate)
    async def on_member_update(self, event: MemberUpdate):
        """Permet de mettre à jour la base de donnée quand un membre met à jour ses rôles."""
        user_base = get_user_base()
        user = event.after
        if not user_base.has_user(user.id):
            user_base.add_user(user.id, self.tool.get_groupes_as_list(user), self.tool.get_filiere_as_filiere(user))
        else:
            user_base.update_user_groups(user.id, self.tool.get_groupes_as_list(user))

    @listen(Error)
    async def on_error(self, error: Error):
        """Permet de faire la gestion des erreurs pour l'ensemble du bot, envoie un message aux admins et prévient l'utilisateur de l'erreur."""
        await self.bot.get_channel(os.getenv("CHANNEL_ID")).send(f"<@&{os.getenv("ADMIN_ID")}>```ERREUR dans : {error.source} - {datetime.now()}\nErreur de type : {type(error.error)}\nArgument de l'erreur : {error.error.args}\nDescription de l'erreur : {error.error}\nLes paramètres de la fonction étais : \n - auteur : {error.ctx.author}\n - serveur :  {error.ctx.guild}\n - message :  {error.ctx.message}\n - channel :  {error.ctx.channel}\n - role member :  {error.ctx.member.roles}```")
        await error.ctx.send(embed=Embed("Une erreur est survenu, les admins sont prévenu."), ephemeral=True)
