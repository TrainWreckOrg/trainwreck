from datetime import datetime, timedelta
from Enums import Group, subjects_table
from pytz import timezone

class Event:
    """Classe utilisée pour gérer les objets événements"""
    def __init__(self, start:datetime, end:datetime, subject:str, group:Group, location:str, teacher:str, isINGE:bool, isMIAGE:bool, uid:str, isEXAM:bool=False) -> None:
        self.start_timestamp = start
        self.end_timestamp = end
        self.location = location
        self.teacher = teacher
        self.subject = subject
        self.group = group
        # Note : isMIAGE and isINGE are not mutually exclusive
        self.isMIAGE = isMIAGE
        self.isINGE  = isINGE
        self.uid = uid
        self.isEXAM = isEXAM

        self.duree = self.end_timestamp - self.start_timestamp 


    def __eq__(self, other: object) -> bool:
        if isinstance(other, Event):
            return (self.uid == other.uid and self.start_timestamp == other.start_timestamp and
                    self.end_timestamp == other.end_timestamp and self.location == other.location and
                    self.teacher == other.teacher and self.subject == other.subject and self.group == other.group and
                    self.isMIAGE == other.isMIAGE and self.isINGE == other.isINGE)
        return False

    def __hash__(self) -> int:
        return hash(self.uid + str(self.start_timestamp) + str(self.end_timestamp) + self.location + self.teacher + self.subject + str(self.group) + str(self.isMIAGE) + str(self.isINGE))

    def __str__(self) -> str:
        if self.isEXAM:
            return ":warning: " + (f"{self.start_timestamp.strftime("%Hh%M")}-{self.end_timestamp.strftime("%Hh%M")} : {self.subject} - {f" {"INGE" if self.isINGE else ""}{"-" if self.isINGE and self.isMIAGE else ""}{"MIAGE" if self.isMIAGE else ""}" if self.group.value == "CM" else ""} - {self.location} - {self.teacher}".upper()) + " :warning:"
        else:
            return f"{self.start_timestamp.strftime("%Hh%M")}-{self.end_timestamp.strftime("%Hh%M")} : {self.group.value}{f" {"INGE" if self.isINGE else ""}{"-" if self.isINGE and self.isMIAGE else ""}{"MIAGE" if self.isMIAGE else ""}" if self.group.value == "CM" else ""} - {self.subject} - {self.location} - {self.teacher}"

    def ics(self) -> str:
        ics = "BEGIN:VEVENT\n"
        stamp = str(datetime.now().replace(microsecond=0).astimezone(timezone("UTC")).isoformat()).replace("-", "").replace(":", "").replace("+0000","Z")
        ics += "DTSTAMP:" + stamp + "\n"
        start = str(self.start_timestamp.astimezone(timezone("UTC")).isoformat()).replace("-", "").replace(":", "").replace("+0000","Z")
        ics += "DTSTART:" + start + "\n"
        end = str(self.end_timestamp.astimezone(timezone("UTC")).isoformat()).replace("-", "").replace(":", "").replace("+0000","Z")
        ics += "DTEND:" + end + "\n"
        ics += "SUMMARY:" + self.subject + "\n"
        ics += "LOCATION:" + self.location + "\n"
        
        ics += f"DESCRIPTION:Groupe : {self.group.value}{f" {"INGE" if self.isINGE else ""}{"-" if self.isINGE and self.isMIAGE else ""}{"MIAGE" if self.isMIAGE else ""}" if self.group == Group.CM else ""}\nDurée : {str(self.duree)}\nEnseignant : {self.teacher}\nExporté le : {datetime.now().strftime("%d/%m/%Y à %Hh%M")}, via EDT Bot"

        # ics += "DESCRIPTION:\\n\\n" + self.group.value + "\\n" + self.subject + self.subject + "\\nL3 INFO - INGENIERIE\\nL3 INFORMAT-UPEX MINERVE\\n" + self.teacher + "\\n(Exporté le:" + str(datetime.now()) + ")\\n" + "\n"
        ics += "UID:" + self.uid + "\n"
        ics += "CREATED:19700101T000000Z" + "\n"
        ics += "LAST-MODIFIED:" + stamp + "\n"
        ics += "SEQUENCE:" + str(datetime.now(tz=timezone("UTC")).timestamp())[:10] + "\n"
        ics += "END:VEVENT" + "\n"
        return ics

def get_event_from_data(start:datetime, end:datetime, sum:str, loc:str, desc:str, uid:str) -> Event:
    """Permet d'extraire les informations des données parsées"""
    # Événements spéciaux
    if sum == "Réunion rentrée - L3 INGENIERIE INFORMATIQUE":
        return Event(start, end, sum, Group.CM, loc, "Équipe Enseignante", True, False,"ADE60323032342d323032352d31323639382d302d30")
    elif sum == "HAPPY CAMPUS DAY":
        return Event(start, end, sum, Group.CM, "Campus", "Équipe Enseignante", True, True,"ADE60323032342d323032352d32323835332d302d30")
    elif sum == "Réunion rentrée - L3 MIAGE":
        return Event(start, end, sum, Group.CM, loc, "Équipe Enseignante", False, True,"ADE60323032342d323032352d31333132352d302d30")

    # Descsplit contient les informations correspondant à la description de l'événement, séparé par lignes
    # ex : ['', '', 'Gr TPC', 'Con. Ana. Algo', 'Con. Ana. Algo', 'L3 INFO - INGENIERIE', 'L3 INFORMAT-UPEX MINERVE', 'LIEDLOFF', '(Exporté le : 27/07/2024 20:20)', '\n\n']
    descsplit = desc.split("\\n")

    # Si la Matière (4eme element) est une abbrev connu dans la subjects_table, remplacer par le nom complet
    subject = subjects_table[descsplit[3]] if descsplit[3] in subjects_table.keys() else descsplit[3]
    if "L3 INFORMATIQUE" in subject:
        subject = descsplit[2]

    # Nettoie le nom du professeur (antépénultième élément), et inclus un fallback si le nom n'est pas renseigné
    teacher = descsplit[-3].replace("\n", "").removeprefix(" ") if descsplit[-3] != "L3 INFORMAT-UPEX MINERVE" else "Enseignant ?"
    location = loc if not loc == "" else "Salle ?"

    # Valeur par défaut
    isMIAGE = False
    isINGE  = False
    group   = Group.CM

    if subject == "Anglais":
        if "MIAGE" in sum :
            # ex : Anglais - TD3 MIAGE
            isMIAGE = True
            match sum[12]:
                case "1":
                    group = Group.TDA1M
                case "2":
                    group = Group.TDA2M
                case "3":
                    group = Group.TDA3M
                case _:
                        # This case should NOT happen and should be fixed asap
                        group = Group.UKNW
                        print("ERROR : NO GROUP FOUND (INGE) :", sum , "---------------------")

        else :
            # ex : Anglais - TD 1
            isINGE = True
            match sum[13]:
                case "1":
                    group = Group.TDA1I
                case "2":
                    group = Group.TDA2I
                case "3":
                    group = Group.TDA3I
                case _:
                        # This case should NOT happen and should be fixed asap
                        group = Group.UKNW
                        print("ERROR : NO GROUP FOUND (INGE) :", sum , "---------------------")
    else:
        if "L3 INFO - INGENIERIE" in descsplit and "Pro. Pro. Per." not in sum and "MIAGE" not in sum:
            isINGE = True
        if "L3 INFORMATIQUE - MIAGE" in descsplit or "MIAGE" in sum:
            isMIAGE = True
        # descsplit[2] contient le numéro de groupe ou le nom de la matière si CM
        if descsplit[2].startswith("Gr"):
            if isINGE:
                isMIAGE = False
                match descsplit[2][3:]:
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
                    case _:
                        # This case should NOT happen and should be fixed asap 
                        group = Group.UKNW
                        print("ERROR : NO GROUP FOUND (INGE) :", sum , "---------------------")
            else:
                match descsplit[2][3:]:
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
                    case _:
                        # This case should NOT happen and should be fixed asap 
                        group = Group.UKNW
                        print("ERROR : NO GROUP FOUND (MIAGE) :", sum , "---------------------")

    # Crée un nouvel Objet Event à partir des infos calculées
    return Event(start, end, subject, group, location, teacher, isINGE, isMIAGE, uid)