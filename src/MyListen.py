from interactions import listen, Extension
from interactions.api.events import Component, MemberUpdate

from UserBase import get_user_base

import re
from MyTask import MyTask
from Tool import get_tool



class MyListen(Extension):
    def __init__(self, bot):
        self.bot = bot
        self.tool = get_tool(bot)

    @listen()
    async def on_ready(self):
        """Fonction qui dit quand le bot est opérationnel au démarrage du programme"""
        print("Ready")
        print(f"This bot is owned by {self.bot.owner}")
        await self.bot.synchronise_interactions()
        MyTask.daily_morning_update.start()
        MyTask.update_calendar.start()
        await MyTask.update_calendar()

    @listen(Component)
    async def on_component(self, event: Component):
        """Fonction permettant d'écouter les cliques des boutons"""
        # try:
        ctx = event.ctx
        pattern_day = re.compile("day-")
        pattern_week = re.compile("week-")
        if pattern_day.search(ctx.custom_id):
            await self.tool.get_day_bt(ctx=ctx, jour=ctx.custom_id[4:], modifier=True)
        elif pattern_week.search(ctx.custom_id):
            await self.tool.get_week_bt(ctx, ctx.custom_id[5:], True)
        else:
            await ctx.send("Bouton cliqué mais aucune action définie")
            raise ValueError("Bouton cliqué mais aucune action définie")
        # except BaseException as error:
        # await send_error("on_component",error, event.ctx, bouton = event.ctx.custom_id)

    @listen(MemberUpdate)
    async def on_member_update(self, event: MemberUpdate):
        user_base = get_user_base()
        user = event.after
        if not user_base.has_user(user.id):
            user_base.add_user(user.id, self.tool.get_groupes_as_list(user), self.tool.get_filiere_as_filiere(user))
        else:
            user_base.update_user_groups(user.id, self.tool.get_groupes_as_list(user))