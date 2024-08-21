from interactions import Client, slash_command, Permissions, Embed, Extension, Button, ButtonStyle, ActionRow, \
    ContextType, component_callback, SlashContext, ComponentContext
import re

from Enums import RoleEnum
from Tool import get_tool
from Filter import *


class Onboard(Extension):
    """Classe contenant le processus d'attribution des rôles."""
    def __init__(self, bot: Client):
        self.bot = bot
        self.tool = get_tool(bot)

    @slash_command(name="onboard", description="Permet d'afficher le message d'onboard.", default_member_permissions=Permissions.ADMINISTRATOR, contexts=[ContextType.GUILD])
    async def onboard_embed(self, ctx: SlashContext) -> None:
        """Permet d'afficher le message d'onboard."""
        embed = Embed("Bienvenue, ajouter vos rôles.")
        bouton = Button(
            style=ButtonStyle.BLURPLE,
            custom_id="onboard",
            label="Commencer"
        )
        await ctx.send(embed=embed, components=bouton)

    @component_callback(re.compile("onboard"))
    async def onboard_bt(self, ctx:ComponentContext) -> None:
        """Permet de faire réagir le bouton d'onboard."""
        await self.onboard(ctx, edit=False)

    @component_callback(re.compile("inge|miage"))
    async def return_filiere(self, ctx:ComponentContext) -> None:
        """Permet d'ajouter un rôle de filière en fonction du bouton cliqué."""
        # Si la personne à déjà une filière.
        if self.tool.get_filiere_as_filiere(ctx.author) != Filiere.UKNW:
            await ctx.edit_origin(embed=Embed(title="Vous ne pouvez pas avoir plusieurs rôles de la même catégorie."), components=ActionRow(Button(style=ButtonStyle.RED, label="Pas autorisée", disabled=True)))
            return

        if ctx.custom_id == "inge":
            await ctx.author.add_role(self.tool.get_roles(ctx.guild)[Filiere.INGE])

        elif ctx.custom_id == "miage":
            await ctx.author.add_role(self.tool.get_roles(ctx.guild)[Filiere.MIAGE])
        await self.onboard(ctx, edit=True)

    @component_callback(re.compile("^td[1|2][I|M]$"))
    async def return_td(self, ctx:ComponentContext) -> None:
        """Permet d'ajouter un rôle de TD en fonction du bouton cliqué."""
        # Si la personne à déjà un groupe de TD.
        for group in self.tool.get_groupes_as_list(ctx.author):
            if group in [Group.TD1I, Group.TD2I, Group.TD1M, Group.TD2M]:
                await ctx.edit_origin(embed=Embed(title="Vous ne pouvez pas avoir plusieurs rôles de la même catégorie."), components=ActionRow(Button(style=ButtonStyle.RED, label="Pas autorisée", disabled=True)))
                return

        if ctx.custom_id == "td1I":
            await ctx.author.add_role(self.tool.get_roles(ctx.guild)[Group.TD1I])
        elif ctx.custom_id == "td2I":
            await ctx.author.add_role(self.tool.get_roles(ctx.guild)[Group.TD2I])

        elif ctx.custom_id == "td1M":
            await ctx.author.add_role(self.tool.get_roles(ctx.guild)[Group.TD1M])
        elif ctx.custom_id == "td2M":
            await ctx.author.add_role(self.tool.get_roles(ctx.guild)[Group.TD2M])
        await self.onboard(ctx, edit=True)

    @component_callback(re.compile("tp"))
    async def return_tp(self, ctx:ComponentContext) -> None:
        """Permet d'ajouter un rôle de TP en fonction du bouton cliqué."""
        # Si la personne à déjà un groupe de TP.
        for group in self.tool.get_groupes_as_list(ctx.author):
            if group in [Group.TPAI, Group.TPBI, Group.TPCI, Group.TPDI, Group.TP1M, Group.TP2M, Group.TP3M]:
                await ctx.edit_origin(embed=Embed(title="Vous ne pouvez pas avoir plusieurs rôles de la même catégorie."), components=ActionRow(Button(style=ButtonStyle.RED, label="Pas autorisée", disabled=True)))
                return

        if ctx.custom_id == "tpaI":
            await ctx.author.add_role(self.tool.get_roles(ctx.guild)[Group.TPAI])
        elif ctx.custom_id == "tpbI":
            await ctx.author.add_role(self.tool.get_roles(ctx.guild)[Group.TPBI])
        elif ctx.custom_id == "tpcI":
            await ctx.author.add_role(self.tool.get_roles(ctx.guild)[Group.TPCI])
        elif ctx.custom_id == "tpdI":
            await ctx.author.add_role(self.tool.get_roles(ctx.guild)[Group.TPDI])

        elif ctx.custom_id == "tp1M":
            await ctx.author.add_role(self.tool.get_roles(ctx.guild)[Group.TP1M])
        elif ctx.custom_id == "tp2M":
            await ctx.author.add_role(self.tool.get_roles(ctx.guild)[Group.TP2M])
        elif ctx.custom_id == "tp3M":
            await ctx.author.add_role(self.tool.get_roles(ctx.guild)[Group.TP3M])
        await self.onboard(ctx, edit=True)

    @component_callback(re.compile("^td[1|2|3|4][I|M]A$"))
    async def return_td_anglais(self, ctx:ComponentContext) -> None:
        """Permet d'ajouter un rôle de TD Anglais en fonction du bouton cliqué."""
        # Si la personne à déjà un groupe de TD d'Anglais.
        for group in self.tool.get_groupes_as_list(ctx.author):
            if group in [Group.TDA1I, Group.TDA2I, Group.TDA3I, Group.TDA4I, Group.TDA1M, Group.TDA2M, Group.TDA3M]:
                await ctx.edit_origin(embed=Embed(title="Vous ne pouvez pas avoir plusieurs rôles de la même catégorie."), components=ActionRow(Button(style=ButtonStyle.RED, label="Pas autorisée", disabled=True)))
                return
        if ctx.custom_id == "td1IA":
            await ctx.author.add_roles([self.tool.get_roles(ctx.guild)[Group.TDA1I], self.tool.get_roles(ctx.guild)[RoleEnum.ONBOARDED]])
        elif ctx.custom_id == "td2IA":
            await ctx.author.add_roles([self.tool.get_roles(ctx.guild)[Group.TDA2I], self.tool.get_roles(ctx.guild)[RoleEnum.ONBOARDED]])
        elif ctx.custom_id == "td3IA":
            await ctx.author.add_roles([self.tool.get_roles(ctx.guild)[Group.TDA3I], self.tool.get_roles(ctx.guild)[RoleEnum.ONBOARDED]])
        elif ctx.custom_id == "td4IA":
            await ctx.author.add_roles([self.tool.get_roles(ctx.guild)[Group.TDA4I], self.tool.get_roles(ctx.guild)[RoleEnum.ONBOARDED]])

        elif ctx.custom_id == "td1MA":
            await ctx.author.add_roles([self.tool.get_roles(ctx.guild)[Group.TDA1M], self.tool.get_roles(ctx.guild)[RoleEnum.ONBOARDED]])
        elif ctx.custom_id == "td2MA":
            await ctx.author.add_roles([self.tool.get_roles(ctx.guild)[Group.TDA2M], self.tool.get_roles(ctx.guild)[RoleEnum.ONBOARDED]])
        elif ctx.custom_id == "td3MA":
            await ctx.author.add_roles([self.tool.get_roles(ctx.guild)[Group.TDA3M], self.tool.get_roles(ctx.guild)[RoleEnum.ONBOARDED]])
        await self.onboard(ctx, edit=True)

    async def onboard(self, ctx: SlashContext | ComponentContext, edit: bool = False) -> None:
        """Permet de demander la bonne chose en fonction des rôles déjà attribuée."""
        filiere = self.tool.get_filiere_as_filiere(ctx.author)
        groupe = self.tool.get_groupes_as_list(ctx.author)
        # Est-ce que la personne a déjà une filière.
        if filiere == Filiere.UKNW:
            await self.ask_filiere(ctx, edit=edit)
            return
        # Est-ce que la personne a déjà un groupe de TD d'Anglais.
        for group in groupe:
            if group in [Group.TDA1I, Group.TDA2I, Group.TDA3I, Group.TDA4I, Group.TDA1M, Group.TDA2M, Group.TDA3M]:
                if edit:
                    await ctx.edit_origin(embed=Embed(title="Vous avez déjà tout les rôles nécessaire"), components=ActionRow(Button(style=ButtonStyle.RED, label="Pas autorisée", disabled=True)))
                else:
                    await ctx.send(embed=Embed(title="Vous avez déjà tout les rôles nécessaire"), ephemeral=True)
                return
        # Est-ce que la personne a déjà un groupe de TP.
        for group in groupe:
            if group in [Group.TPAI, Group.TPBI, Group.TPCI, Group.TPDI, Group.TP1M, Group.TP2M, Group.TP3M]:
                await self.ask_td_anglais(ctx, filiere, edit=edit)
                return
        # Est-ce que la personne a déjà un groupe de TD.
        for group in groupe:
            if group in [Group.TD1I, Group.TD2I, Group.TD1M, Group.TD2M]:
                await self.ask_tp(ctx, filiere, edit=edit)
                return
        await self.ask_td(ctx, filiere, edit=edit)

    async def ask_filiere(self, ctx: SlashContext | ComponentContext, edit: bool = False) -> None:
        """Permet de demander la filière."""
        embed = Embed(title="Quel est votre filière ?")
        inge = Button(
            style=ButtonStyle.BLURPLE,
            custom_id="inge",
            label="Ingénieur"
        )
        miage = Button(
            style=ButtonStyle.BLURPLE,
            custom_id="miage",
            label="MIAGE"
        )
        actionRow = ActionRow(inge, miage)
        if edit:
            await ctx.edit_origin(embed=embed, components=actionRow)
        else:
            await ctx.send(embed=embed, components=actionRow, ephemeral=True)

    async def ask_td(self, ctx: SlashContext | ComponentContext, filiere: Filiere, edit: bool = False) -> None:
        """Permet de demander le groupe de TD."""
        embed = Embed(title="Quel est votre groupe de TD ?")
        actionRow = ActionRow()
        if filiere == Filiere.INGE:
            TD1 = Button(
                style=ButtonStyle.BLURPLE,
                custom_id="td1I",
                label="TD 1"
            )
            TD2 = Button(
                style=ButtonStyle.BLURPLE,
                custom_id="td2I",
                label="TD 2"
            )
            actionRow = ActionRow(TD1, TD2)
        elif filiere == Filiere.MIAGE:
            TD1 = Button(
                style=ButtonStyle.BLURPLE,
                custom_id="td1M",
                label="TD 1"
            )
            TD2 = Button(
                style=ButtonStyle.BLURPLE,
                custom_id="td2M",
                label="TD 2"
            )
            actionRow = ActionRow(TD1, TD2)
        elif filiere == Filiere.UKNW:
            await self.ask_filiere(ctx)
        else:
            await ctx.send("Une erreur est survenu", ephemeral=True)
            try:
                raise ValueError("Onboard Filière inconnue dans ask_td")
            except BaseException as exception:
                await self.tool.send_error(exception)

        if edit:
            await ctx.edit_origin(embed=embed, components=actionRow)
        else:
            await ctx.send(embed=embed, components=actionRow, ephemeral=True)

    async def ask_tp(self, ctx: SlashContext | ComponentContext, filiere: Filiere, edit: bool = False) -> None:
        """Permet de demander le groupe de TP."""
        embed = Embed(title="Quel est votre groupe de TP ?")
        actionRow = ActionRow()
        if filiere == Filiere.INGE:
            TPA = Button(
                style=ButtonStyle.BLURPLE,
                custom_id="tpaI",
                label="TP A"
            )
            TPB = Button(
                style=ButtonStyle.BLURPLE,
                custom_id="tpbI",
                label="TP B"
            )
            TPC = Button(
                style=ButtonStyle.BLURPLE,
                custom_id="tpcI",
                label="TP C"
            )
            TPD = Button(
                style=ButtonStyle.BLURPLE,
                custom_id="tpdI",
                label="TP D"
            )
            actionRow = ActionRow(TPA, TPB, TPC, TPD)
        elif filiere == Filiere.MIAGE:
            TP1 = Button(
                style=ButtonStyle.BLURPLE,
                custom_id="tp1M",
                label="TP 1"
            )
            TP2 = Button(
                style=ButtonStyle.BLURPLE,
                custom_id="tp2M",
                label="TP 2"
            )
            TP3 = Button(
                style=ButtonStyle.BLURPLE,
                custom_id="tp3M",
                label="TP 3"
            )
            actionRow = ActionRow(TP1, TP2, TP3)
        elif filiere == Filiere.UKNW:
            await self.ask_filiere(ctx)
        else:
            await ctx.send("Une erreur est survenu", ephemeral=True)
            try:
                raise ValueError("Onboard Filière inconnue dans ask_tp")
            except BaseException as exception:
                await self.tool.send_error(exception)

        if edit:
            await ctx.edit_origin(embed=embed, components=actionRow)
        else:
            await ctx.send(embed=embed, components=actionRow, ephemeral=True)

    async def ask_td_anglais(self, ctx: SlashContext | ComponentContext, filiere: Filiere, edit: bool = False) -> None:
        """Permet de demander le groupe de TD d'Anglais."""
        embed = Embed(title="Quel est votre groupe de TD d'anglais ?", description="Oui, on sais pas pourquoi mais pour l'anglais les groupes sont diffèrent.")
        actionRow = ActionRow()
        if filiere == Filiere.INGE:
            TD1 = Button(
                style=ButtonStyle.BLURPLE,
                custom_id="td1IA",
                label="TD 1 Anglais"
            )
            TD2 = Button(
                style=ButtonStyle.BLURPLE,
                custom_id="td2IA",
                label="TD 2 Anglais"
            )
            TD3 = Button(
                style=ButtonStyle.BLURPLE,
                custom_id="td3IA",
                label="TD 3 Anglais"
            )
            TD4 = Button(
                style=ButtonStyle.BLURPLE,
                custom_id="td4IA",
                label="TD 4 Anglais"
            )
            actionRow = ActionRow(TD1, TD2, TD3, TD4)
        elif filiere == Filiere.MIAGE:
            TD1 = Button(
                style=ButtonStyle.BLURPLE,
                custom_id="td1MA",
                label="TD 1 Anglais"
            )
            TD2 = Button(
                style=ButtonStyle.BLURPLE,
                custom_id="td2MA",
                label="TD 2 Anglais"
            )
            TD3 = Button(
                style=ButtonStyle.BLURPLE,
                custom_id="td3MA",
                label="TD 3 Anglais"
            )
            actionRow = ActionRow(TD1, TD2, TD3)
        elif filiere == Filiere.UKNW:
            await self.ask_filiere(ctx)
        else:
            await ctx.send("Une erreur est survenu", ephemeral=True)
            try:
                raise ValueError("Onboard Filière inconnue dans ask_td_anglais")
            except BaseException as exception:
                await self.tool.send_error(exception)

        if edit:
            await ctx.edit_origin(embed=embed, components=actionRow)
        else:
            await ctx.send(embed=embed, components=actionRow, ephemeral=True)
