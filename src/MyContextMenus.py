from datetime import date, timedelta

from interactions import Extension, ContextMenuContext, Message, message_context_menu, user_context_menu, Member
from Tool import get_tool

class MyContextMenus(Extension):
    def __init__(self, bot):
        self.bot = bot
        self.tool = get_tool(bot)


    @user_context_menu(name="today_user")
    async def today_user(self, ctx: ContextMenuContext):
        await self.tool.get_day_bt(ctx, date.today().strftime("%d-%m-%Y"), False,personne=ctx.target, ephemeral=True)


    @user_context_menu(name="tomorrow_user")
    async def tomorrow_user(self, ctx: ContextMenuContext):
        await self.tool.get_day_bt(ctx, (date.today()+timedelta(days=1)).strftime("%d-%m-%Y"), False, personne=ctx.target, ephemeral=True)


    @user_context_menu(name="week_user")
    async def week_user(self, ctx: ContextMenuContext):
        await self.tool.get_week_bt(ctx, date.today().strftime("%d-%m-%Y"), False, personne=ctx.target, ephemeral=True)