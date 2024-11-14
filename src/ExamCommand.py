import json
import os
from datetime import datetime

from interactions import Client, slash_command, SlashContext, OptionType, slash_option, SlashCommandChoice, Permissions, \
    Embed, EmbedFooter, User, contexts, Extension, Button, ButtonStyle, ActionRow, ContextType, AutocompleteContext, Role
from Enums import subjects_table, Group, Filiere, Timing
from sender import send, get_error_log_chan, get_arguement_chan

from Calendar import get_calendar
from Filter import filter_events, GroupFilter, Filter, FiliereFilter, TimeFilter
from Tool import get_tool


class ExamCommand(Extension):
    def __init__(self, bot: Client):
        self.bot = bot
        self.tool = get_tool(bot)



    @slash_command(name="add_exam", description="Permet d'ajouter un exam")
    @slash_option(
        name="cours",
        description="Quel cours",
        required=True,
        opt_type=OptionType.STRING,
        choices=[SlashCommandChoice(name=cle, value=valeur) for (cle, valeur) in subjects_table.items()]
    )
    @slash_option(
        name="role",
        description="Quel Groupe ?",
        required=True,
        opt_type=OptionType.ROLE
    )
    @slash_option(
        name="jour",
        description="Quel jour ? (DD-MM-YYYY)",
        required=True,
        autocomplete=True,
        opt_type=OptionType.STRING
    )
    @slash_option(
        name="heure",
        description="Quel heure ? (HH-MM)",
        required=True,
        autocomplete=True,
        opt_type=OptionType.STRING
    )
    @slash_option(
        name="description",
        description="Quel est cette exam ?",
        required=True,
        opt_type=OptionType.STRING
    )
    @slash_option(
        name="texte",
        description="Quel texte voulez vous ajouter à l'exam ?",
        required=False,
        opt_type=OptionType.STRING
    )
    async def add_exam(self, ctx: SlashContext, cours : str, role : Role, jour: str, heure: str, description: str, texte: str = "") -> None:
        """Fonction qui permet d'obtenir l'EDT d'une journée spécifique, ou d'un autre utilisateur s'il est spécifié."""
        role = ctx.args[1]
        rolediscord = self.bot.guilds[0].get_role(role)
        filter: list[Filter] = []

        for filiere in Filiere:
            if rolediscord.name == filiere.value:
                filter.append(FiliereFilter(filiere))
                break

        for gr in Group:
            if rolediscord.name == gr.value:
                filter.append(GroupFilter([gr]))
                break
        try:
            date = datetime.strptime(ctx.args[2], "%d-%m-%Y").date()
        except:
            await ctx.send(choices=[])
            return

        filter += [TimeFilter(date, Timing.AFTER), TimeFilter(date, Timing.BEFORE)]

        liste_cours = filter_events(get_calendar().get_events(), filter)
        uid = ""
        for cours in liste_cours:
            if cours.start_timestamp.strftime("%d-%m-%Y %H:%M") == f"{jour} {heure}":
                uid = cours.uid

        argument  = await self.tool.get_arguement()
        exam_card = {
            "description": description,
            "uid": uid,
            "text": texte,
            "source": ctx.author.display_name
        }

        argument.get("exam_list")[uid] = exam_card

        with open("argument.json", 'w', encoding='utf-8') as file:
            json.dump(argument, file, ensure_ascii=False, indent=4)

        await send(get_arguement_chan(), f"Le cours est : {cours}, le groupe est {role.name}, le jour est {jour}, l'heure est {heure}, \n {exam_card}", ephemeral=False, auto_ephemeral=False, files=["argument.json"])
        await send(ctx, "C'est ajouté.")
        os.remove("argument.json")




    @add_exam.autocomplete("jour")
    async def jour(self, ctx: AutocompleteContext):
        role = ctx.args[1]
        rolediscord = self.bot.guilds[0].get_role(role)
        role_process : list[Filter] = []

        for filiere in Filiere:
            if rolediscord.name == filiere.value:
                role_process.append(FiliereFilter(filiere))
                break

        for gr in Group:
            if rolediscord.name == gr.value:
                role_process.append(GroupFilter([gr]))
                break


        liste_cours = filter_events(get_calendar().get_events(), role_process)

        choices = []
        for cours in liste_cours:
            if cours.subject == ctx.args[0]:
                date = cours.start_timestamp.strftime("%d-%m-%Y")
                dico = {
                        "name": date,
                        "value": date,
                }
                choices.append(dico)
        await ctx.send(choices=choices)
        return



    @add_exam.autocomplete("heure")
    async def heure(self, ctx: AutocompleteContext):
        role = ctx.args[1]
        rolediscord = self.bot.guilds[0].get_role(role)
        filter: list[Filter] = []

        for filiere in Filiere:
            if rolediscord.name == filiere.value:
                filter.append(FiliereFilter(filiere))
                break

        for gr in Group:
            if rolediscord.name == gr.value:
                filter.append(GroupFilter([gr]))
                break
        try:
            date = datetime.strptime(ctx.args[2], "%d-%m-%Y").date()
        except:
            await ctx.send(choices=[])
            return

        filter+=[TimeFilter(date, Timing.AFTER), TimeFilter(date, Timing.BEFORE)]

        liste_cours = filter_events(get_calendar().get_events(), filter)

        choices = []
        for cours in liste_cours:
            if cours.subject == ctx.args[0]:
                heure = cours.start_timestamp.strftime("%H:%M")
                dico = {
                    "name": heure,
                    "value": heure,
                }
                choices.append(dico)
        await ctx.send(choices=choices)
        return