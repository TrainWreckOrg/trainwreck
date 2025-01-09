from datetime import datetime
from pytz import timezone
import sentry_sdk

from Enums import Group, subjects_table, weekday
from sender import send_error_non_async


class Event:
    """Classe utilisée pour gérer les objets événements"""
    def __init__(self, start:datetime, end:datetime, subject:str, group:Group, location:str, teacher:str, isINGE:bool, isMIAGE:bool, uid:str, isEXAM:bool=False, isAdd:bool=False, isDelete:bool=False, old_event = None, isSpecial : bool = False, description : str= "") -> None:
        self.start_timestamp = start
        self.end_timestamp = end
        self.location = location
        self.teacher = teacher
        self.subject = subject
        self.group = group
        # Note : isMIAGE and isINGE are NOT mutually exclusive
        self.isMIAGE = isMIAGE
        self.isINGE  = isINGE
        self.uid = uid

        self.isEXAM = isEXAM
        self.isSpecial = isSpecial
        self.isAdd = isAdd
        self.isDelete = isDelete
        self.old_event = old_event
        self.description = description
        self.description_personnel = ""

        self.duree = self.end_timestamp - self.start_timestamp 

    def similar(self, other: object) -> bool:
        """Permet de vérifier l'égalité du contenu avec un autre objet. (ne prend pas en compte l'uid)"""
        if isinstance(other, Event):
            return (self.start_timestamp == other.start_timestamp and
                    self.end_timestamp == other.end_timestamp and self.location == other.location and
                    self.teacher == other.teacher and self.subject == other.subject and self.group == other.group and
                    self.isMIAGE == other.isMIAGE and self.isINGE == other.isINGE and self.isEXAM == other.isEXAM and
                    self.duree == other.duree)
        return False

    def __eq__(self, other: object) -> bool:
        """Permet de vérifier l'égalité avec un autre objet."""
        if isinstance(other, Event):
            return (self.uid == other.uid and self.start_timestamp == other.start_timestamp and
                    self.end_timestamp == other.end_timestamp and self.location == other.location and
                    self.teacher == other.teacher and self.subject == other.subject and self.group == other.group and
                    self.isMIAGE == other.isMIAGE and self.isINGE == other.isINGE and self.isEXAM == other.isEXAM and
                    self.duree == other.duree)
        return False

    def __hash__(self) -> int:
        """Permet d'avoir un hash de l'Event."""
        return hash(self.uid + str(self.start_timestamp) + str(self.end_timestamp) + self.location + self.teacher + self.subject + str(self.group) + str(self.isMIAGE) + str(self.isINGE) + str(self.isEXAM) + str(self.duree))

    def __str__(self) -> str:
        """Permet d'avoir une str pour représenter l'Event."""
        event = f"{self.start_timestamp.strftime("%Hh%M")}-{self.end_timestamp.strftime("%Hh%M")} : {self.group.value}{f" {"INGE" if self.isINGE else ""}{"-" if self.isINGE and self.isMIAGE else ""}{"MIAGE" if self.isMIAGE else ""}" if self.group.value == "CM" else ""} - {self.subject} - {self.location} - {self.teacher}"
        if self.description != "":
            event += f" - :information_source: ||{self.description}||"

        if self.isEXAM:
            event = f":warning: {(event.upper())} :warning:"
        if self.isSpecial:
            event = f":sparkles: {event} :sparkles:"
        if self.isAdd:
            event = f":white_check_mark: Cette Event à été ajouter manuellement {event}"
        if self.isDelete:
            event = f":x: Cette Event à été supprimer manuellement {event}"
        if self.old_event is not None:
            event = f":pencil2: {event} Cette event remplace {self.old_event.__str__()}"
        event = event.replace(":INFORMATION_SOURCE:",":information_source:")
        return event

    def str_day(self, autre: 'Event' = None) -> str:
        """Permet de comparer deux Event et de renvoyer une str de l'événement self avec les éléments qui changent en gars."""

        if autre is None:
            return f"{weekday[self.start_timestamp.weekday()]} {self.start_timestamp.strftime("%d-%m-%Y")} {self.__str__()}"

        texte = ""

        day=f"{weekday[self.start_timestamp.weekday()]} {self.start_timestamp.strftime("%d-%m-%Y")}"

        if(self.start_timestamp.strftime("%d-%m-%Y")) != (autre.start_timestamp.strftime("%d-%m-%Y")):
            texte += f"**{day}** "
        else:
            texte += f"{day} "

        time=f"{self.start_timestamp.strftime("%Hh%M")}-{self.end_timestamp.strftime("%Hh%M")}"
        time_autre=f"{autre.start_timestamp.strftime("%Hh%M")}-{autre.end_timestamp.strftime("%Hh%M")}"

        if time != time_autre:
            texte += f"**{time}**"
        else:
            texte += time

        texte += " : "

        self_groupe = f"{self.group.value}{f" {"INGE" if self.isINGE else ""}{"-" if self.isINGE and self.isMIAGE else ""}{"MIAGE" if self.isMIAGE else ""}" if self.group.value == "CM" else ""}"
        autre_groupe = f"{autre.group.value}{f" {"INGE" if autre.isINGE else ""}{"-" if autre.isINGE and autre.isMIAGE else ""}{"MIAGE" if autre.isMIAGE else ""}" if autre.group.value == "CM" else ""}"
        if (self_groupe) != (autre_groupe):
            texte += f"**{self_groupe}**"
        else:
            texte += self_groupe

        texte += " - "

        if (self.subject) != (autre.subject):
            texte += f"**{self.subject}**"
        else:
            texte += self.subject

        texte += " - "

        if (self.location) != (autre.location):
            texte += f"**{self.location}**"
        else:
            texte += self.location

        texte += " - "

        if (self.teacher) != (autre.teacher):
            texte += f"**{self.teacher}**"
        else:
            texte += self.teacher

        if self.description != "":
            texte += f" - ||{self.description}||"

        if self.isEXAM:
            texte = f":warning: {(texte.upper())} :warning:"
        if self.isSpecial:
            texte = f":sparkles: {texte} :sparkles:"
        if self.isAdd:
            texte = f":white_check_mark: Cette Event à été ajouter manuellement {texte}"
        if self.isDelete:
            texte = f":x: Cette Event à été supprimer manuellement {texte}"
        if self.old_event is not None:
            texte = f":pencil2: {texte} Cette event remplace {self.old_event.__str__()}"

        texte = texte.replace(":INFORMATION_SOURCE:",":information_source:")
        return texte

    def ics(self) -> str:
        """Permet d'avoir l'Event au format ICS."""
        ics = "BEGIN:VEVENT\n"
        stamp = str(datetime.now().replace(microsecond=0).astimezone(timezone("UTC")).isoformat()).replace("-", "").replace(":", "").replace("+0000","Z")
        ics += "DTSTAMP:" + stamp + "\n"
        start = str(self.start_timestamp.astimezone(timezone("UTC")).isoformat()).replace("-", "").replace(":", "").replace("+0000","Z")
        ics += "DTSTART:" + start + "\n"
        end = str(self.end_timestamp.astimezone(timezone("UTC")).isoformat()).replace("-", "").replace(":", "").replace("+0000","Z")
        ics += "DTEND:" + end + "\n"
        ics += "SUMMARY:" + self.subject + "\n"
        ics += "LOCATION:" + self.location + "\n"
        ics += f"DESCRIPTION:Groupe : {self.group.value}{f" {"INGE" if self.isINGE else ""}{"-" if self.isINGE and self.isMIAGE else ""}{"MIAGE" if self.isMIAGE else ""}" if self.group == Group.CM else ""}\\nDurée : {str(self.duree).split(":")[0]}h{str(self.duree).split(":")[1]}\\nEnseignant : {self.teacher}\\nExporté le {datetime.now().strftime("%d/%m/%Y à %Hh%M")}, via EDT Bot\n"
        ics += "UID:" + self.uid + "\n"
        ics += "CREATED:19700101T000000Z" + "\n"
        ics += "LAST-MODIFIED:" + stamp + "\n"
        ics += "SEQUENCE:" + str(datetime.now(tz=timezone("UTC")).timestamp())[:10] + "\n"
        ics += "END:VEVENT" + "\n"
        return ics


def ancien_parseur(start:datetime, end:datetime, sum:str, loc:str, desc:str, uid:str) -> Event:
    """Permet d'extraire les informations des données parsées."""


    # Descsplit contient les informations correspondant à la description de l'événement, séparé par lignes.
    # Ex : ['', '', 'Gr TPC', 'Con. Ana. Algo', 'Con. Ana. Algo', 'L3 INFO - INGENIERIE', 'L3 INFORMAT-UPEX MINERVE', 'LIEDLOFF', '(Exporté le : 27/07/2024 20:20)', '\n\n']
    descsplit = desc.split("\\n")

    # Si la Matière (4eme element) est une abbrev connu dans la subjects_table, remplacer par le nom complet.
    # subject_split = descsplit[3].split(" GR")
    # subject = subjects_table[subject_split[0]] if subject_split[0] in subjects_table.keys() else descsplit[3]
    subject_split = sum.split(" - ")
    group_brut : str = ""
    if len(subject_split) == 3:
        group_brut = subject_split[2].removeprefix("GR").replace(" ","")
    else:
        group_brut = subject_split[1].replace(" ","")

    subject = subjects_table[subject_split[0]] if subject_split[0] in subjects_table.keys() else sum
    if "L3 INFORMATIQUE" in subject:
        subject = descsplit[2]

    # Nettoie le nom du professeur (antépénultième élément), et inclus un fallback si le nom n'est pas renseigné.
    teacher = descsplit[-3].replace("\n", "").removeprefix(" ") if descsplit[-3] != "L3 INFORMAT-UPEX MINERVE" else "Enseignant ?"
    location = loc if not loc == "" else "Salle ?"


    # Valeur par défaut.
    isMIAGE = False
    isINGE  = False
    group   = Group.CM
    if group_brut in ["CM","HM", "CC-"]:
        group = Group.CM
        if "L3 INFO - INGENIERIE" in descsplit and "MIAGE" not in sum:
            isINGE = True
        if "L3 INFORMATIQUE - MIAGE" in descsplit or "MIAGE" in sum:
            isMIAGE = True
    elif subject == "Anglais":
        if "MIAGE" in sum :
            # ex : Anglais - TD3 MIAGE
            isMIAGE = True
            match group_brut[2]: #sum[12]
                case "1":
                    group = Group.TDA1M
                case "2":
                    group = Group.TDA2M
                case "3":
                    group = Group.TDA3M
                case _:
                    # Ce cas ne devrait pas arriver et devrait être fix rapidement.
                    group = Group.UKNW
                    try:
                        raise ValueError("Groupe inconnue anglais Miage dans get_event_from_data")
                    except BaseException as exception:
                        send_error_non_async(exception)

        else:
            # ex : Anglais - TD 1
            isINGE = True
            match group_brut[2]: #sum[13]
                case "1":
                    group = Group.TDA1I
                case "2":
                    group = Group.TDA2I
                case "3":
                    group = Group.TDA3I
                case "4":
                    group = Group.TDA4I
                case _:
                    # Ce cas ne devrait pas arriver et devrait être fix rapidement.
                    group = Group.UKNW
                    try:
                        raise ValueError("Groupe inconnue anglais ingé dans get_event_from_data")
                    except BaseException as exception:
                        send_error_non_async(exception)

    else:
        if "L3 INFO - INGENIERIE" in descsplit and "MIAGE" not in sum:
            isINGE = True
        if "L3 INFORMATIQUE - MIAGE" in descsplit or "MIAGE" in sum:
            isMIAGE = True
        # descsplit[2] contient le numéro de groupe ou le nom de la matière si CM.
        #if descsplit[2].startswith("Gr"):
        if isINGE:
            isMIAGE = False
            match group_brut[:3]: # subject_split[0]
                case "TD1":
                    group = Group.TD1I
                case "TD2":
                    group = Group.TD2I
                case "TPA":
                    group = Group.TPAI
                case "TPB":
                    group = Group.TPBI
                case "TPC":
                    group = Group.TPCI
                case "TPD":
                    group = Group.TPDI
                case "TP1":
                    group = Group.TPAI
                case "TP2":
                    group = Group.TPBI
                case "TP3":
                    group = Group.TPCI
                case "TP4":
                    group = Group.TPDI
                case _:
                    # Ce cas ne devrait pas arriver et devrait être fix rapidement.
                    group = Group.UKNW
                    try:
                        print(end)
                        raise ValueError("Groupe inconnue cours ingé dans get_event_from_data")
                    except BaseException as exception:
                        send_error_non_async(exception)

        else:
            match group_brut[:3] :  #descsplit[2][3:]:
                case "TD1":
                    group = Group.TD1M
                case "TD2":
                    group = Group.TD2M
                case "TP1":
                    group = Group.TP1M
                case "TP2":
                    group = Group.TP2M
                case "TP3":
                    group = Group.TP3M
                case "TPA":
                    group = Group.TP1M
                case "TPB":
                    group = Group.TP2M
                case "TPC":
                    group = Group.TP3M
                case _:
                    # Ce cas ne devrait pas arriver et devrait être fix rapidement.
                    group = Group.UKNW
                    try:
                        raise ValueError("Groupe inconnue cours Miage dans get_event_from_data")
                    except BaseException as exception:
                        send_error_non_async(exception)

    if "CC" in sum:
        teacher = "équipe enseignante"

    # Crée un nouvel Objet Event à partir des infos calculées.
    return Event(start, end, subject, group, location, teacher, isINGE, isMIAGE, uid)
