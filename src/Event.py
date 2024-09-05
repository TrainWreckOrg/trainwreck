from datetime import datetime
from pytz import timezone
import sentry_sdk

from Enums import Group, GroupL2, GroupL3, Annee, subjects_table
from src.Calendar import Calendar


class Event:
    """Classe utilisée pour gérer les objets événements"""
    def __init__(self, start:datetime, end:datetime, subject:str, group:Group, location:str, teacher:str, annee:Annee, uid:str, isEXAM:bool=False) -> None:
        self.start_timestamp = start
        self.end_timestamp = end
        self.location = location
        self.teacher = teacher
        self.annee = annee
        self.subject = subject
        self.group = group
        self.uid = uid
        self.isEXAM = isEXAM

        self.duree = self.end_timestamp - self.start_timestamp 

    def __eq__(self, other: object) -> bool:
        """Permet de vérifier l'égalité avec un autre objet."""
        if isinstance(other, Event):
            return (self.uid == other.uid and self.start_timestamp == other.start_timestamp and
                    self.end_timestamp == other.end_timestamp and self.location == other.location and
                    self.teacher == other.teacher and self.subject == other.subject and self.group == other.group and
                    self.annee == other.annee and self.isEXAM == other.isEXAM and
                    self.duree == other.duree)
        return False

    def __hash__(self) -> int:
        """Permet d'avoir un hash de l'Event."""
        return hash(self.uid + str(self.start_timestamp) + str(self.end_timestamp) + self.location + self.teacher + self.subject + str(self.group) + str(self.annee) + str(self.isEXAM) + str(self.duree))

    def __str__(self) -> str:
        """Permet d'avoir une str pour représenter l'Event."""
        if self.isEXAM:
            return ":warning: " + (f"{self.start_timestamp.strftime("%Hh%M")}-{self.end_timestamp.strftime("%Hh%M")} : {self.subject} - {self.location} - {self.teacher}".upper()) + " :warning:"
        else:
            return f"{self.start_timestamp.strftime("%Hh%M")}-{self.end_timestamp.strftime("%Hh%M")} : {self.group.value} - {self.subject} - {self.location} - {self.teacher}"

    def str_day(self, autre: 'Event' = None) -> str:
        """Permet de comparer deux Event et de renvoyer une str de l'événement self avec les éléments qui changent en gars."""

        if autre is None:
            if self.isEXAM:
                return ":warning: " + (f"{self.start_timestamp.strftime("%d-%m-%Y")} {self.start_timestamp.strftime("%Hh%M")}-{self.end_timestamp.strftime("%Hh%M")} : {self.subject} - {self.location} - {self.teacher}".upper()) + " :warning:"
            else:
                return f"{self.start_timestamp.strftime("%d-%m-%Y")} {self.start_timestamp.strftime("%Hh%M")}-{self.end_timestamp.strftime("%Hh%M")} : {self.group.value} - {self.subject} - {self.location} - {self.teacher}"

        texte = ""

        if(self.start_timestamp.strftime("%d-%m-%Y")) != (autre.start_timestamp.strftime("%d-%m-%Y")):
            texte += f"**{self.start_timestamp.strftime("%d-%m-%Y")}** "
        else:
            texte += f"{self.start_timestamp.strftime("%d-%m-%Y")} "

        if (self.start_timestamp.strftime("%Hh%M")) != (autre.start_timestamp.strftime("%Hh%M")):
            texte += f"**{self.start_timestamp.strftime("%Hh%M")}-{self.end_timestamp.strftime("%Hh%M")}**"
        else:
            texte += f"{self.start_timestamp.strftime("%Hh%M")}-{self.end_timestamp.strftime("%Hh%M")}"

        texte += " : "

        self_groupe = f"{self.group.value}"
        autre_groupe = f"{autre.group.value}"
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

        if self.isEXAM:
            return ":warning: " + (texte.upper()) + " :warning:"
        else:
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
        ics += f"DESCRIPTION:Groupe : {self.group.value}\\nDurée : {str(self.duree).split(":")[0]}h{str(self.duree).split(":")[1]}\\nEnseignant : {self.teacher}\\nExporté le {datetime.now().strftime("%d/%m/%Y à %Hh%M")}, via EDT Bot\n"
        ics += "UID:" + self.uid + "\n"
        ics += "CREATED:19700101T000000Z" + "\n"
        ics += "LAST-MODIFIED:" + stamp + "\n"
        ics += "SEQUENCE:" + str(datetime.now(tz=timezone("UTC")).timestamp())[:10] + "\n"
        ics += "END:VEVENT" + "\n"
        return ics

class EventL3(Event):
    """Classe utilisée pour gérer les objets événements"""
    def __init__(self, start: datetime, end: datetime, subject: str, group: Group, location: str, teacher: str,
                 isINGE: bool, isMIAGE: bool, uid: str, isEXAM: bool = False, annee: Annee = Annee.L3) -> None:

        # Note : isMIAGE and isINGE are NOT mutually exclusive
        super().__init__(start, end, subject, group, location, teacher, annee, uid, isEXAM)
        self.isMIAGE = isMIAGE
        self.isINGE  = isINGE

    def __eq__(self, other: object) -> bool:
        """Permet de vérifier l'égalité avec un autre objet."""
        if isinstance(other, Event):
            other : EventL3
            return (Calendar.__eq__(self, other) and self.isMIAGE == other.isMIAGE and self.isINGE == other.isINGE)
        return False

    def __hash__(self) -> int:
        """Permet d'avoir un hash de l'Event."""
        return hash(self.uid + str(self.start_timestamp) + str(self.end_timestamp) + self.location + self.teacher + self.subject + str(self.group) + str(self.isMIAGE) + str(self.isINGE) + str(self.isEXAM) + str(self.duree) + str(self.annee))

    def __str__(self) -> str:
        """Permet d'avoir une str pour représenter l'Event."""
        if self.isEXAM:
            return ":warning: " + (f"{self.start_timestamp.strftime("%Hh%M")}-{self.end_timestamp.strftime("%Hh%M")} : {self.subject} - {f" {"INGE" if self.isINGE else ""}{"-" if self.isINGE and self.isMIAGE else ""}{"MIAGE" if self.isMIAGE else ""}" if self.group.value == "CM" else ""} - {self.location} - {self.teacher}".upper()) + " :warning:"
        else:
            return f"{self.start_timestamp.strftime("%Hh%M")}-{self.end_timestamp.strftime("%Hh%M")} : {self.group.value}{f" {"INGE" if self.isINGE else ""}{"-" if self.isINGE and self.isMIAGE else ""}{"MIAGE" if self.isMIAGE else ""}" if self.group.value == "CM" else ""} - {self.subject} - {self.location} - {self.teacher}"

    def str_day(self, autre: 'Event' = None) -> str:
        """Permet de comparer deux Event et de renvoyer une str de l'événement self avec les éléments qui changent en gars."""

        if autre is None:
            if self.isEXAM:
                return ":warning: " + (f"{self.start_timestamp.strftime("%d-%m-%Y")} {self.start_timestamp.strftime("%Hh%M")}-{self.end_timestamp.strftime("%Hh%M")} : {self.subject} - {f" {"INGE" if self.isINGE else ""}{"-" if self.isINGE and self.isMIAGE else ""}{"MIAGE" if self.isMIAGE else ""}" if self.group.value == "CM" else ""} - {self.location} - {self.teacher}".upper()) + " :warning:"
            else:
                return f"{self.start_timestamp.strftime("%d-%m-%Y")} {self.start_timestamp.strftime("%Hh%M")}-{self.end_timestamp.strftime("%Hh%M")} : {self.group.value}{f" {"INGE" if self.isINGE else ""}{"-" if self.isINGE and self.isMIAGE else ""}{"MIAGE" if self.isMIAGE else ""}" if self.group.value == "CM" else ""} - {self.subject} - {self.location} - {self.teacher}"

        texte = ""

        if(self.start_timestamp.strftime("%d-%m-%Y")) != (autre.start_timestamp.strftime("%d-%m-%Y")):
            texte += f"**{self.start_timestamp.strftime("%d-%m-%Y")}** "
        else:
            texte += f"{self.start_timestamp.strftime("%d-%m-%Y")} "

        if (self.start_timestamp.strftime("%Hh%M")) != (autre.start_timestamp.strftime("%Hh%M")):
            texte += f"**{self.start_timestamp.strftime("%Hh%M")}-{self.end_timestamp.strftime("%Hh%M")}**"
        else:
            texte += f"{self.start_timestamp.strftime("%Hh%M")}-{self.end_timestamp.strftime("%Hh%M")}"

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

        if self.isEXAM:
            return ":warning: " + (texte.upper()) + " :warning:"
        else:
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




class EventL2(Event):
    """Classe utilisée pour gérer les objets événements"""
    def __init__(self, start: datetime, end: datetime, subject: str, group: Group, location: str, teacher: str, uid: str, isEXAM: bool = False, annee: Annee = Annee.L2) -> None:
        super().__init__(start, end, subject, group, location, teacher, annee, uid, isEXAM)

def get_event_from_data(start:datetime, end:datetime, sum:str, loc:str, desc:str, uid:str) -> Event:
    if "L3" in sum:
        return get_event_L3_from_data(start, end, sum, loc, desc, uid)
    elif "L2" in sum:
        return get_event_L3_from_data(start, end, sum, loc, desc, uid)

def get_event_L3_from_data(start:datetime, end:datetime, sum:str, loc:str, desc:str, uid:str) -> EventL3:
    """Permet d'extraire les informations des données parsées."""
    # Événements spéciaux.
    if sum == "Réunion rentrée - L3 INGENIERIE INFORMATIQUE":
        return EventL3(start, end, sum, Group.CM, loc, "Équipe Enseignante", True, False,"ADE60323032342d323032352d31323639382d302d30")
    elif sum == "HAPPY CAMPUS DAY":
        return EventL3(start, end, sum, Group.CM, "Campus", "Équipe Enseignante", True, True,"ADE60323032342d323032352d32323835332d302d30")
    elif sum == "Réunion rentrée - L3 MIAGE":
        return EventL3(start, end, sum, Group.CM, loc, "Équipe Enseignante", False, True,"ADE60323032342d323032352d31333132352d302d30")

    # Descsplit contient les informations correspondant à la description de l'événement, séparé par lignes.
    # Ex : ['', '', 'Gr TPC', 'Con. Ana. Algo', 'Con. Ana. Algo', 'L3 INFO - INGENIERIE', 'L3 INFORMAT-UPEX MINERVE', 'LIEDLOFF', '(Exporté le : 27/07/2024 20:20)', '\n\n']
    descsplit = desc.split("\\n")

    # Si la Matière (4eme element) est une abbrev connu dans la subjects_table, remplacer par le nom complet.
    subject = subjects_table[descsplit[3]] if descsplit[3] in subjects_table.keys() else descsplit[3]
    if "L3 INFORMATIQUE" in subject:
        subject = descsplit[2]

    # Nettoie le nom du professeur (antépénultième élément), et inclus un fallback si le nom n'est pas renseigné.
    teacher = descsplit[-3].replace("\n", "").removeprefix(" ") if descsplit[-3] != "L3 INFORMAT-UPEX MINERVE" else "Enseignant ?"
    location = loc if not loc == "" else "Salle ?"

    # Valeur par défaut.
    isMIAGE = False
    isINGE  = False
    group   = Group.CM

    if subject == "Anglais":
        if "MIAGE" in sum :
            # ex : Anglais - TD3 MIAGE
            isMIAGE = True
            match sum[12]:
                case "1":
                    group = GroupL3.TDA1M
                case "2":
                    group = GroupL3.TDA2M
                case "3":
                    group = GroupL3.TDA3M
                case _:
                    # Ce cas ne devrait pas arriver et devrait être fix rapidement.
                    group = Group.UKNW
                    try:
                        raise ValueError("Groupe inconnue anglais Miage dans get_event_from_data")
                    except BaseException as exception:
                        print(exception)
                        sentry_sdk.capture_exception(exception)

        else:
            # ex : Anglais - TD 1
            isINGE = True
            match sum[13]:
                case "1":
                    group = GroupL3.TDA1I
                case "2":
                    group = GroupL3.TDA2I
                case "3":
                    group = GroupL3.TDA3I
                case "4":
                    group = GroupL3.TDA4I
                case _:
                    # Ce cas ne devrait pas arriver et devrait être fix rapidement.
                    group = Group.UKNW
                    try:
                        raise ValueError("Groupe inconnue anglais ingé dans get_event_from_data")
                    except BaseException as exception:
                        print(exception)
                        sentry_sdk.capture_exception(exception)

    else:
        if "L3 INFO - INGENIERIE" in descsplit and "MIAGE" not in sum:
            isINGE = True
        if "L3 INFORMATIQUE - MIAGE" in descsplit or "MIAGE" in sum:
            isMIAGE = True
        # descsplit[2] contient le numéro de groupe ou le nom de la matière si CM.
        if descsplit[2].startswith("Gr"):
            if isINGE:
                isMIAGE = False
                match descsplit[2][3:]:
                    case "TD1":
                        group = GroupL3.TD1I
                    case "TD2":
                        group = GroupL3.TD2I
                    case "TPA":
                        group = GroupL3.TPAI
                    case "TPB":
                        group = GroupL3.TPBI
                    case "TPC":
                        group = GroupL3.TPCI
                    case "TPD":
                        group = GroupL3.TPDI
                    case _:
                        # Ce cas ne devrait pas arriver et devrait être fix rapidement.
                        group = Group.UKNW
                        try:
                            raise ValueError("Groupe inconnue cours ingé dans get_event_from_data")
                        except BaseException as exception:
                            print(exception)
                            sentry_sdk.capture_exception(exception)

            else:
                match descsplit[2][3:]:
                    case "TD1":
                        group = GroupL3.TD1M
                    case "TD2":
                        group = GroupL3.TD2M
                    case "TP1":
                        group = GroupL3.TP1M
                    case "TP2":
                        group = GroupL3.TP2M
                    case "TP3":
                        group = GroupL3.TP3M
                    case _:
                        # Ce cas ne devrait pas arriver et devrait être fix rapidement.
                        group = Group.UKNW
                        try:
                            raise ValueError("Groupe inconnue cours Miage dans get_event_from_data")
                        except BaseException as exception:
                            print(exception)
                            sentry_sdk.capture_exception(exception)

    # Crée un nouvel Objet Event à partir des infos calculées.
    return EventL3(start, end, subject, group, location, teacher, isINGE, isMIAGE, uid)

def get_event_L2_from_data(start:datetime, end:datetime, sum:str, loc:str, desc:str, uid:str) -> EventL2:
    """Permet d'extraire les informations des données parsées."""
    # Événements spéciaux.
    if sum == "HAPPY CAMPUS DAY":
        return EventL2(start, end, sum, Group.CM, "Campus", "Équipe Enseignante", "ADE60323032342d323032352d32323835332d302d30")

    # Descsplit contient les informations correspondant à la description de l'événement, séparé par lignes.
    # Ex : ["","","Gr TPA","Syst. Mono Tâche","Syst. Mono Tâche","L2 INFORMAT- UPEX MINERVE","L2 INFO - INGENIERIE INFO","COUVREUR","(Exporté le:05/09/202 4 11:24)"\n]
    descsplit = desc.split("\\n")
    sumsplit = sum.split(" - ")

    # Si la Matière (4eme element) est une abbrev connu dans la subjects_table, remplacer par le nom complet.
    subject = subjects_table[sumsplit[0]] if sumsplit[0] in subjects_table.keys() else sumsplit[0]

    # Nettoie le nom du professeur (antépénultième élément), et inclus un fallback si le nom n'est pas renseigné.
    teacher = descsplit[-3].replace("\n", "").removeprefix(" ") if descsplit[-3] != "L3 INFORMAT-UPEX MINERVE" else "Enseignant ?"
    location = loc if not loc == "" else "Salle ?"

    # Valeur par défaut.
    group   = Group.CM

    match sumsplit[1]:
        case 'TD1':
            group = GroupL2.TD1
        case 'TD2':
            group = GroupL2.TD2
        case 'TD3':
            group = GroupL2.TD3

        case 'TP1':
            group = GroupL2.TP1
        case 'TP2':
            group = GroupL2.TP2
        case 'TP3':
            group = GroupL2.TP3
        case 'TP4':
            group = GroupL2.TP4
        case 'TP5':
            group = GroupL2.TP5
        case 'TP6':
            group = GroupL2.TP6
        

    # Crée un nouvel Objet Event à partir des infos calculées.
    return EventL2(start, end, subject, group, location, teacher, uid)