import json
import os
import re
from datetime import datetime
from lib2to3.fixes.fix_input import context

from interactions import Client, slash_command, SlashContext, OptionType, slash_option, SlashCommandChoice, Permissions, \
    Embed, EmbedFooter, User, contexts, Extension, Button, ButtonStyle, ActionRow, ContextType, AutocompleteContext, \
    Role, StringSelectMenu, component_callback, ComponentContext, StringSelectOption
from Enums import subjects_table, Group, Filiere, Timing
from sender import send, get_error_log_chan, get_arguement_chan

from Calendar import get_calendar
from Filter import filter_events, GroupFilter, Filter, FiliereFilter, TimeFilter
from Tool import get_tool


class ExamCommand(Extension):
    def __init__(self, bot: Client):
        self.bot = bot
        self.tool = get_tool(bot)

    @slash_command(name="add_exam", description="Permet d'ajouter un exam", contexts=[ContextType.GUILD])
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

        exam_card = {
            "description": description,
            "uid": uid,
            "text": texte,
            "source": ctx.author.display_name
        }

        string_exam = f'"{uid}" : ' + str(exam_card).replace("'",'"')

        # await send(get_arguement_chan(), f"Le cours est : {cours}, le groupe est {role.name}, le jour est {jour}, l'heure est {heure}, \n {exam_card}", ephemeral=False, auto_ephemeral=False, files=["argument.json"])
        await send(ctx, f"Le cours est : {cours}, le groupe est {role.name}, le jour est {jour}, l'heure est {heure} va etre ajouter par un admin, \n {string_exam}", ephemeral=False, auto_ephemeral=False)
        # os.remove("argument.json")

    #@slash_command(name="test", description="Permet d'ajouter un exam", contexts=[ContextType.GUILD])
    async def test(self, ctx: SlashContext) -> None:
        """Commande qui permet de bot la création d'exam pour un certaine matière et le cours numéro x"""
        for group in [Group.TPAI, Group.TPBI, Group.TPCI, Group.TPDI, Group.TP1M, Group.TP2M, Group.TP3M]:
            liste_cours = filter_events(get_calendar().get_events(), [GroupFilter([group])])

            list_cours_cible = []
            for cours in liste_cours:
                if cours.subject == "Réseaux 2":
                    list_cours_cible.append(cours)

            list_cours_cible = sorted(list_cours_cible,key=lambda event: event.start_timestamp)
            print(f"Il y a {len(list_cours_cible)} pour le groupe {group.value}")
            export = ""
            compteur = 1
            content = ["Question sur le DM", "Couche transport et application"]
            for num in [3,4]:
                event = list_cours_cible[num]
                exam_card = {
                    "description": f"CC{compteur} Réseaux 2 {group}",
                    "uid": event.uid,
                    "text": content[compteur-1],
                    "source": "Mail prof"
                }
                compteur+=1

                string_exam = f'"{event.uid}" : ' + str(exam_card).replace("'",'"')
                export += "\n" + string_exam

            # Define the file path
            file_path = "export.txt"

            # Write the variable export to the file
            with open(file_path, "a", encoding="utf-8") as file:
                file.write(export)
            await send(ctx, "C'est dans le fichier", ephemeral=True, auto_ephemeral=False)
        # await send(get_arguement_chan(), f"Le cours est : {cours}, le groupe est {role.name}, le jour est {jour}, l'heure est {heure}, \n {exam_card}", ephemeral=False, auto_ephemeral=False, files=["argument.json"])
        # os.remove("argument.json")

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





    @slash_command(name="delete_exam", description="Permet de supprimer un exam", contexts=[ContextType.GUILD])
    async def delete_exam(self,ctx : SlashContext):

        list_exam = get_calendar().get_exams()
        menu_option = []

        for exam in list_exam:
            menu_option.append(
                StringSelectOption(
                    label=exam.subject,
                    value=f"delete_exam:{exam.uid}",
                    description= f"{exam.start_timestamp.strftime("%Hh%M")}-{exam.end_timestamp.strftime("%Hh%M")} : {exam.group.value}{f" {"INGE" if exam.isINGE else ""}{"-" if exam.isINGE and exam.isMIAGE else ""}{"MIAGE" if exam.isMIAGE else ""}" if exam.group.value == "CM" else ""} - {exam.subject} - {exam.location} - {exam.teacher}"[:100]
                )
            )

        list_component = []

        for i in range(0,len(menu_option), 25):
            list_component.append(
                StringSelectMenu(
                    menu_option[:25],
                    placeholder="Quel exam voulez vous supprimer ?",
                    min_values = 1,
                    max_values = 1,
                    custom_id = "delete_exam"
                )
            )
            menu_option = menu_option[25:]

        for component in list_component:
            await ctx.send("Choisir une option", components=component)
        # await send(ctx, content="Choisir une option", components=list_component)

    @component_callback(re.compile("delete_exam"))
    async def responseMenu(self, ctx: ComponentContext) -> None:
        argument = await self.tool.get_arguement()
        exam_delete = argument.get("exam_list").get(ctx.values[0].removeprefix("delete_exam:"))
        await send(ctx, f"Le cours est : {exam_delete} n'est plus un exam", ephemeral=False, auto_ephemeral=False)
        # exam_delete = argument.get("exam_list").pop(ctx.values[0].removeprefix("delete_exam:"))
        #
        # with open("argument.json", 'w', encoding='utf-8') as file:
        #     json.dump(argument, file, ensure_ascii=False, indent=4)
        #
        # await send(get_arguement_chan(),
        #            f"Le cours est : {exam_delete} n'est plus un exam",
        #            ephemeral=False, auto_ephemeral=False, files=["argument.json"])
        # await send(ctx, "C'est supprimer.")
        # os.remove("argument.json")