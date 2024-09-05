import os

from interactions import Extension, Client, ContextMenuContext, user_context_menu, ModalContext, Modal, ShortText
from datetime import date, timedelta, datetime

from Tool import get_tool


class MyContextMenus(Extension):
    """Classe contenant les Context Menu."""
    def __init__(self, bot : Client):
        self.bot = bot


    @user_context_menu(name="today_user")
    async def today_user(self, ctx: ContextMenuContext) -> None:
        """Permet de savoir l'EDT d'une personne pour aujourd'hui."""
        await get_tool(self.bot, ctx.guild).get_day_bt(ctx, date.today().strftime("%d-%m-%Y"), False, personne=ctx.target)

    @user_context_menu(name="tomorrow_user")
    async def tomorrow_user(self, ctx: ContextMenuContext) -> None:
        """Permet de savoir l'EDT d'une personne pour demain."""
        await get_tool(self.bot, ctx.guild).get_day_bt(ctx, (date.today()+timedelta(days=1)).strftime("%d-%m-%Y"), False, personne=ctx.target)

    @user_context_menu(name="this_week_user")
    async def this_week_user(self, ctx: ContextMenuContext) -> None:
        """Permet de savoir l'EDT d'une personne pour cette semaine."""
        await get_tool(self.bot, ctx.guild).get_week_bt(ctx, date.today().strftime("%d-%m-%Y"), False, personne=ctx.target)

    @user_context_menu(name="day_user")
    async def day_user(self, ctx: ContextMenuContext) -> None:
        """Permet de savoir l'EDT d'une personne pour une date."""
        await self.day_user_modal(ctx)

    async def day_user_modal(self, ctx: ContextMenuContext) -> None:
        """Permet de demander à une personne une date par un modal et lui envoyer l'EDT d'une autre personne"""
        # Création du modal.
        my_modal = Modal(
            ShortText(label="Jour ? (DD-MM-YYYY)", custom_id="date_user"),
            title=f"EDT de {ctx.target} ?",
            custom_id="day_user",
        )
        # Envoie du modal.
        await ctx.send_modal(modal=my_modal)
        # Attente de la réponse au modal
        modal_ctx: ModalContext = await ctx.bot.wait_for_modal(my_modal)

        jour = modal_ctx.responses["date_user"]
        await self.bot.get_channel(os.getenv("ERROR_CHANNEL_ID")).send(
            f"{ctx.author.display_name} ({ctx.author.id}) à utilise {ctx.command.name} sur {ctx.target} ({ctx.target_id}) pour avoir le jour {jour}, le {datetime.now()}")
        await get_tool(self.bot, ctx.guild).get_day_bt(ctx=modal_ctx, jour=jour, modifier=False, personne=ctx.target)

    @user_context_menu(name="week_user")
    async def week_user(self, ctx: ContextMenuContext) -> None:
        """Permet de savoir l'EDT d'une personne pour une semaine."""
        await self.week_user_modal(ctx)

    async def week_user_modal(self, ctx: ContextMenuContext) -> None:
        """Permet de demander à une personne une semaine par un modal et lui envoyer l'EDT d'une autre personne"""
        # Création du modal.
        my_modal = Modal(
            ShortText(label="Semaine ? (DD-MM-YYYY)", custom_id="semaine_user"),
            title=f"EDT de {ctx.target} ?",
            custom_id="week_user",
        )
        # Envoie du modal.
        await ctx.send_modal(modal=my_modal)
        # Attente de la réponse au modal
        modal_ctx: ModalContext = await ctx.bot.wait_for_modal(my_modal)

        semaine = modal_ctx.responses["semaine_user"]
        await self.bot.get_channel(os.getenv("ERROR_CHANNEL_ID")).send(
            f"{ctx.author.display_name} ({ctx.author.id}) à utilise {ctx.command.name} sur {ctx.target} ({ctx.target_id}) pour avoir la semaine du {semaine}, le {datetime.now()}")
        await get_tool(self.bot, ctx.guild).get_week_bt(ctx=modal_ctx, semaine=semaine, modifier=False, personne=ctx.target)
