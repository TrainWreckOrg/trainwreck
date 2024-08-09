import os

from interactions import slash_command, SlashContext, OptionType, slash_option, SlashCommandChoice, Permissions, Embed, \
    EmbedFooter, User, contexts, Extension, AutocompleteContext, Button, ButtonStyle, ActionRow, ContextType, \
    component_callback
from Tool import get_tool

from Enums import Subscription
from Calendar import get_calendar
from TrainWreck import get_ics, get_embeds
from UserBase import get_user_base
from Filter import *
import re
from datetime import datetime, date, timedelta


class Onboard(Extension):
    def __init__(self, bot):
        self.bot = bot
        self.tool = get_tool(bot)

    @slash_command(name="onboard", description="Permet d'afficher le message d'onboard", default_member_permissions=Permissions.ADMINISTRATOR, contexts=[ContextType.GUILD])
    async def onboard_embed(self, ctx):
        embed = Embed("Bienvenue, ajouter vos rôles.")
        bouton = Button(
            style=ButtonStyle.BLURPLE,
            custom_id="onboard",
            label="Commencer"
        )
        await ctx.send(embed=embed, components=bouton)

    @component_callback(re.compile("onboard"))
    async def onboard_bt(self, ctx):
        await self.onboard(ctx)

    @component_callback(re.compile("inge|miage"))
    async def return_filiere(self, ctx):
        if ctx.custom_id == "inge":
            await ctx.author.add_role(self.tool.get_roles()[Filiere.INGE])

        elif ctx.custom_id == "miage":
            await ctx.author.add_role(self.tool.get_roles()[Filiere.MIAGE])
        await self.onboard(ctx)

    @component_callback(re.compile("^td[1|2][I|M]$"))
    async def return_td(self, ctx):
        if ctx.custom_id == "td1I":
            await ctx.author.add_role(self.tool.get_roles()[Group.TD1I])
        elif ctx.custom_id == "td2I":
            await ctx.author.add_role(self.tool.get_roles()[Group.TD2I])

        elif ctx.custom_id == "td1M":
            await ctx.author.add_role(self.tool.get_roles()[Group.TD1M])
        elif ctx.custom_id == "td2M":
            await ctx.author.add_role(self.tool.get_roles()[Group.TD2M])
        await self.onboard(ctx)

    @component_callback(re.compile("tp"))
    async def return_tp(self, ctx):
        if ctx.custom_id == "tpaI":
            await ctx.author.add_role(self.tool.get_roles()[Group.TPAI])
        elif ctx.custom_id == "tpbI":
            await ctx.author.add_role(self.tool.get_roles()[Group.TPBI])
        elif ctx.custom_id == "tpcI":
            await ctx.author.add_role(self.tool.get_roles()[Group.TPCI])
        elif ctx.custom_id == "tpdI":
            await ctx.author.add_role(self.tool.get_roles()[Group.TPDI])

        elif ctx.custom_id == "tp1M":
            await ctx.author.add_role(self.tool.get_roles()[Group.TP1M])
        elif ctx.custom_id == "tp2M":
            await ctx.author.add_role(self.tool.get_roles()[Group.TP2M])
        elif ctx.custom_id == "tp3M":
            await ctx.author.add_role(self.tool.get_roles()[Group.TP3M])
        await self.onboard(ctx)

    @component_callback(re.compile("^td[1|2|3][I|M]A$"))
    async def return_td_anglais(self, ctx):
        if ctx.custom_id == "td1IA":
            await ctx.author.add_roles([self.tool.get_roles()[Group.TDA1I], self.tool.get_roles()[Group.ONBOARDED]])
        elif ctx.custom_id == "td2IA":
            await ctx.author.add_roles([self.tool.get_roles()[Group.TDA2I], self.tool.get_roles()[Group.ONBOARDED]])
        elif ctx.custom_id == "td3IA":
            await ctx.author.add_roles([self.tool.get_roles()[Group.TDA3I], self.tool.get_roles()[Group.ONBOARDED]])

        elif ctx.custom_id == "td1MA":
            await ctx.author.add_roles([self.tool.get_roles()[Group.TDA1M], self.tool.get_roles()[Group.ONBOARDED]])
        elif ctx.custom_id == "td2MA":
            await ctx.author.add_roles([self.tool.get_roles()[Group.TDA2M], self.tool.get_roles()[Group.ONBOARDED]])
        elif ctx.custom_id == "td3MA":
            await ctx.author.add_roles([self.tool.get_roles()[Group.TDA3M], self.tool.get_roles()[Group.ONBOARDED]])
        await self.onboard(ctx)




    async def onboard(self, ctx):
        filiere = self.tool.get_filiere_as_filiere(ctx.author)
        groupe = self.tool.get_groupes_as_list(ctx.author)
        if filiere == Filiere.UKNW:
            await self.ask_filiere(ctx)
            return
        for group in groupe:
            if group in [Group.TDA1I, Group.TDA2I, Group.TDA3I, Group.TDA1M, Group.TDA2M, Group.TDA3M]:
                await ctx.send("Vous avez déjà tout les rôles nécessaire", ephemeral=True)
                return
        for group in groupe:
            if group in [Group.TPAI, Group.TPBI, Group.TPCI, Group.TPDI, Group.TP1M, Group.TP2M, Group.TP3M]:
                await self.ask_td_anglais(ctx, filiere)
                return
        for group in groupe:
            if group in [Group.TD1I, Group.TD2I, Group.TD1M, Group.TD2M]:
                await self.ask_tp(ctx, filiere)
                return
        await self.ask_td(ctx, filiere)






    async def ask_filiere(self, ctx):
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
        await ctx.send(embed=embed, components=actionRow, ephemeral=True)


    async def ask_td(self, ctx, filiere):
        embed = Embed(title="Quel est votre groupe de TD ?")
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
            await ctx.send(embed = embed, components=actionRow, ephemeral=True)
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
            await ctx.send(embed=embed, components=actionRow, ephemeral=True)
        elif filiere == Filiere.UKNW:
            await self.ask_filiere(ctx)
        else:
            await ctx.send("Une erreur est survenu", ephemeral=True)


    async def ask_tp(self, ctx, filiere):
        embed = Embed(title="Quel est votre groupe de TP ?")
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
            await ctx.send(embed = embed, components=actionRow, ephemeral=True)
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
                custom_id="tp2M",
                label="TP 3"
            )
            actionRow = ActionRow(TP1, TP2, TP3)
            await ctx.send(embed=embed, components=actionRow, ephemeral=True)
        elif filiere == Filiere.UKNW:
            await self.ask_filiere(ctx)
        else:
            await ctx.send("Une erreur est survenu", ephemeral=True)


    async def ask_td_anglais(self, ctx, filiere):
        embed = Embed(title="Quel est votre groupe de TD d'anglais ?", description="Oui, on sais pas pourquoi mais pour l'anglais les groupes sont diffèrent.")
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
            actionRow = ActionRow(TD1, TD2, TD3)
            await ctx.send(embed = embed, components=actionRow, ephemeral=True)
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
            await ctx.send(embed=embed, components=actionRow, ephemeral=True)
        elif filiere == Filiere.UKNW:
            await self.ask_filiere(ctx)
        else:
            await ctx.send("Une erreur est survenu", ephemeral=True)