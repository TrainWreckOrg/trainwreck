from datetime import date, timedelta

from interactions import Extension, ContextMenuContext, Message, message_context_menu, user_context_menu, Member, \
    modal_callback, ModalContext
from interactions import Modal, ParagraphText, ShortText, SlashContext, slash_command

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

    @user_context_menu(name="day_user")
    async def day_user(self, ctx: ContextMenuContext):
        await self.day_user_modal(ctx)

    async def day_user_modal(self, ctx: ContextMenuContext):
        my_modal = Modal(
            ShortText(label="Jour ? (DD-MM-YYYY)", custom_id="date_user"),
            title=f"EDT de {ctx.target} ?",
            custom_id="day_user",

        )
        await ctx.send_modal(modal=my_modal)
        modal_ctx: ModalContext = await ctx.bot.wait_for_modal(my_modal)

        # extract the answers from the responses dictionary
        jour = modal_ctx.responses["date_user"]

        await self.tool.get_day_bt(ctx=modal_ctx, jour=jour, modifier=False, personne=ctx.target, ephemeral=True)

    @user_context_menu(name="week_user")
    async def week_user(self, ctx: ContextMenuContext):
        await self.week_user_modal(ctx)

    async def week_user_modal(self, ctx: ContextMenuContext):
        my_modal = Modal(
            ShortText(label="Semaine ? (DD-MM-YYYY)", custom_id="semaine_user"),
            title=f"EDT de {ctx.target} ?",
            custom_id="week_user",

        )
        await ctx.send_modal(modal=my_modal)
        modal_ctx: ModalContext = await ctx.bot.wait_for_modal(my_modal)

        # extract the answers from the responses dictionary
        semaine = modal_ctx.responses["semaine_user"]

        await self.tool.get_week_bt(ctx=modal_ctx, semaine=semaine, modifier=False, personne=ctx.target, ephemeral=True)
