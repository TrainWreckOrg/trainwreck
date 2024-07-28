from datetime import datetime, date
from pytz import timezone
from urllib.request import urlretrieve
from pathlib import Path
from enum import Enum
from interactions import Embed

import time

print(
"""
\u001b[2;35m  ______           _       _       __               __   
\u001b[0m\u001b[2;31m /_  __/________ _(_)___  | |     / /_______  _____/ /__ 
\u001b[0m\u001b[2;33m  / / / ___/ __ `/ / __ \\ | | /| / / ___/ _ \\/ ___/ //_/ 
\u001b[0m\u001b[2;36m / / / /  / /_/ / / / / / | |/ |/ / /  /  __/ /__/ ,<    
\u001b[0m\u001b[2;34m/_/ /_/   \\__,_/_/_/ /_/  |__/|__/_/   \\___/\\___/_/|_|(_)\u001b[0m
"""
)

# URL utilisée pour fetch les EDT de chaque filiere
url = {
    "INGE" : "https://aderead.univ-orleans.fr/jsp/custom/modules/plannings/anonymous_cal.jsp?data=e476946ed5447b1050d7a6c48ccf4bad4592592d3b282f749c9a606b710f264f6250ba3fea2e12caebbcd166cfe88476f6893987a472171c27978e76da251b877c79900682576cf2be48a3169e635e57166c54e36382c1aa3eb0ff5cb8980cdb,1",
    "MIAGE" : "https://aderead.univ-orleans.fr/jsp/custom/modules/plannings/anonymous_cal.jsp?data=047ece9af44e28b7aebedd6848891aa04592592d3b282f749c9a606b710f264f6250ba3fea2e12caebbcd166cfe88476574604eff8c5d3443632e6f8ddd25c327c79900682576cf2be48a3169e635e57166c54e36382c1aa3eb0ff5cb8980cdb,1",
}

weekday = [
    "Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"
]

month = [
    "Janvier","Février","Mars","Avril","Mai","Juin","Juillet","Août","Septembre","Octobre","Novembre","Décembre"
]

subjects_table = {
    "Con. Orien. Obj" : "Conception Orientée Objet",
    "Pro. Imp. Pro. Ori. Obj" : "Programmation Impérative & Orientée Objet",
    "Con. Ana. Algo" : "Conception et Analyse d'Algorithmes",
    "Log. Lam. Cal" : "Logique & Lambda Calcul",
    "Fram.Web 1" : "Frameworks Web 1",
    "Pro. Pro. Per." : "Projet Personnel & Professionnel"
}

class Timing(Enum):
    BEFORE  = "Before"
    DURING = "During"
    AFTER   = "After"

class Filiere(Enum):
    INGE    = "Ingé"
    MIAGE   = "Miage"

class Group(Enum):
    TPAI    = "TP A Inge"
    TPBI    = "TP B Inge"
    TPCI    = "TP C Inge"
    TPDI    = "TP D Inge"
    TP1M    = "TP 1 Miage"
    TP2M    = "TP 2 Miage"
    TP3M    = "TP 3 Miage"
    TD1I    = "TD 1 Inge"
    TD2I    = "TD 2 Inge"
    TD1M    = "TD 1 Miage"
    TD2M    = "TD 2 Miage"
    TDA1I   = "TD 1 Inge Anglais"
    TDA2I   = "TD 2 Inge Anglais"
    TDA3I   = "TD 3 Inge Anglais"
    TDA1M   = "TD 1 Miage Anglais"
    TDA2M   = "TD 2 Miage Anglais"
    TDA3M   = "TD 3 Miage Anglais"
    CM      = "CM"
    UKNW    = "UKNW"

# ----- CLASSES -----
class Event:
    """Classe utilisée pour gerer les objets evenements"""
    def __init__(self, start:datetime, end:datetime, subject:str, group:Group, location:str, teacher:str, isINGE:bool, isMIAGE:bool) -> None:
        self.start_timestamp = start
        self.end_timestamp = end
        self.location = location
        self.teacher = teacher
        self.subject = subject
        self.group = group
        # Note : isMIAGE and isINGE are not mutually exclusive
        self.isMIAGE = isMIAGE
        self.isINGE  = isINGE
    
    def __eq__(self, value: object) -> bool:
        return (self.start_timestamp == value.start_timestamp) and (self.location == value.location)

    def __hash__(self) -> int:
        return hash(f"{self.start_timestamp.ctime()}{self.end_timestamp.ctime()}{self.location}{self.subject}")
    
    def __str__(self) -> str:
        return f"{self.start_timestamp.strftime("%Hh%M")}-{self.end_timestamp.strftime("%Hh%M")} : {self.group.value}{f" {"INGE" if self.isINGE else ""}{"-" if self.isINGE and self.isMIAGE else ""}{"MIAGE" if self.isMIAGE else ""}" if self.group.value == "CM" else ""} - {self.subject} - {self.location} - {self.teacher}"

class Filter:
    """Classe de Base pour les filtres"""
    def filter(self, e:Event) -> bool:
        """Prend en argument un evenement `e` et retourne `True` si `e` passe le filtre défini par la sous classe"""
        return True

class TimeFilter(Filter):
    def __init__(self, date:date, timing:Timing) -> None:
        self.date   = date
        self.tming = timing

    def filter(self, e: Event) -> bool:
        match self.timing:
            case Timing.BEFORE:
                return e.end_timestamp.date() <= self.date
            case Timing.AFTER:
                return e.start_timestamp.date() >= self.date
            case Timing.DURING:
                return e.start_timestamp.date() == self.date
            case _:
                # This case should NOT happen and should be fixed asap 
                print("ERROR----------------------------------")
                return False

class FiliereFilter(Filter):
    def __init__(self, filiere:Filiere) -> None:
        self.filiere = filiere
    
    def filter(self, e: Event) -> bool:
        if self.filiere == Filiere.INGE:
            return e.isINGE
        else:
            return e.isMIAGE

class GroupFilter(Filter):
    def __init__(self, groups:list[Group]) -> None:
        self.groups = groups
    
    def filter(self, e: Event) -> bool:
        return (e.group in self.groups)


# ----- HElPER  -----
def need_updating(events:list[Event]) -> bool:
    """Verifie si la liste d'évenement doit être mise a jour, c'est a dire si elle est trop vieille ou vide"""
    filenameINGE = "input/INGE.ics"
    filenameMIAGE = "input/MIAGE.ics"
    pINGE = Path(filenameINGE)
    pMIAGE = Path(filenameMIAGE)

    return get_file_age(pINGE) > 120 or get_file_age(pMIAGE) > 120 or events == []

def update_events() -> list[Event]:
    """Retourne une nouvelle liste d'evenements melant les evenements issus des deux .ics et trié"""
    output = []
    filenameINGE = "input/INGE.ics"
    filenameMIAGE = "input/MIAGE.ics"

    fetch_calendar(url["INGE"], filenameINGE)
    fetch_calendar(url["MIAGE"], filenameMIAGE)
    
    output.extend(parse_calendar(filenameINGE))
    output.extend(parse_calendar(filenameMIAGE))

    return sorted(list(set(output)),key=lambda event: event.start_timestamp) 

def fetch_calendar(url:str, filename:str):
    """Récupere le fichier .ics correspondant a une filiere donnée"""
    urlretrieve(url, filename)

def get_file_age(p:Path) -> int:
    """Retourne l'age d'un fichier en minutes"""
    return int(time.time() - p.stat().st_mtime) // 60 if p.exists() else 666 # file does not exist

def convert_timestamp(input : str) -> datetime :
    """Permet de convertir les timestamp en ISO-8601, et les passer en UTC+2"""
    iso_date = f"{input[0:4]}-{input[4:6]}-{input[6:11]}:{input[11:13]}:{input[13:]}"
    return datetime.fromisoformat(iso_date).astimezone(timezone("Europe/Paris"))


# ----- PARSING -----
def build_event_from_data(start:datetime, end:datetime, sum:str, loc:str, desc:str) -> Event:
    """Permet d'extraire les informations des données parsées"""
    # Evenements spéciaux
    if sum == "Réunion rentrée - L3 INGENIERIE INFORMATIQUE":
        return Event(start, end, sum, Group.CM, loc, "Équipe Enseignante", True, False)
    elif sum == "HAPPY CAMPUS DAY":
        return Event(start, end, sum, Group.CM, "Campus", "Équipe Enseignante", True, True)
    elif sum == "Réunion rentrée - L3 MIAGE":
        return Event(start, end, sum, Group.CM, loc, "Équipe Enseignante", False, True)

    # Descsplit contient les informations correspondant à la description de l'evenement, séparé par lignes
    # ex : ['', '', 'Gr TPC', 'Con. Ana. Algo', 'Con. Ana. Algo', 'L3 INFO - INGENIERIE', 'L3 INFORMAT-UPEX MINERVE', 'LIEDLOFF', '(Exporté le:27/07/2024 20:20)', '\n\n']
    descsplit = desc.split("\\n")
    
    # Si la Matiere (4eme element) est une abbrev connu dans la subjects_table, remplacer par le nom complet
    subject = subjects_table[descsplit[3]] if descsplit[3] in subjects_table.keys() else descsplit[3]

    # Nettoie le nom du professeur (antépénultième élément), et inclu un fallback si le nom n'est pas renseigné
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
                        
    # Crée un nouvel Objet Event a partir des infos calculées
    return Event(start, end, subject, group, location, teacher, isINGE, isMIAGE)

def parse_calendar(filename:str) -> list[Event]:
    """Extrait les données du fichier .ics passé dans filename"""
    with open(filename, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    events = []
    event = {}
    for line in lines:
        # Balise Ouvrante, crée un nouveau dictionnaire vide
        if line.startswith("BEGIN:VEVENT"):
            event = {"DTSTART":"", "DTEND":"", "SUMMARY":"", "LOCATION":"", "DESCRIPTION":""}
        # Balise Fermante, envoie les informations récoltées (Timestamps début et fin, le summary (titre), la salle et la description)
        elif line.startswith("END:VEVENT"):
            e = build_event_from_data(
                convert_timestamp(event["DTSTART"]),
                convert_timestamp(event["DTEND"]),
                event["SUMMARY"],
                event["LOCATION"],
                event["DESCRIPTION"]
            )
            events.append(e)

        elif line.startswith(" "):
            event["DESCRIPTION"] += line.removeprefix(" ")
        else:
            for prefix in ("DTSTART:", "DTEND:", "SUMMARY:", "LOCATION:", "DESCRIPTION:") :
                if line.startswith(prefix):
                    event[prefix.removesuffix(":")] = line.removeprefix(prefix).removesuffix("\n")
                    break
    return events

# ----- EXPORTING -----
def filter_events(events:list[Event], filters:list[Filter]) -> list[Event]:
    """Applique une liste de filtres à la liste d'evenenements passé en parametre et retourne une nouvelle liste"""
    output = events.copy()
    for e in events:
        for f in filters:
            if not f.filter(e):
                output.remove(e)
                break
    return output

def display(events:list[Event]) -> None:
    """affiche une liste d'évenements"""
    current_weekday = 7

    for event in events:
        if event.start_timestamp.weekday() != current_weekday:
            current_weekday = event.end_timestamp.weekday()
            print(f"**{weekday[current_weekday]} {event.start_timestamp.day} {month[event.start_timestamp.month -1]}:**")
        print(event)

def export(events:list[Event], filename:str="output/log.txt") -> None:
    """Exporte une liste d'évenements dans un fichier spécifié"""
    current_weekday = 7
    with open(filename, "w") as f:
        for event in events:
            if event.start_timestamp.weekday() != current_weekday:
                current_weekday = event.end_timestamp.weekday()
                print(f"**{weekday[current_weekday]} {event.start_timestamp.day} {month[event.start_timestamp.month -1]}:**", file=f)
            print(event, file=f)

def getCalendar() -> list[Embed]:
    current_weekday = 7
    calendar = []
    embed = Embed()
    string = ""
    for event in events:
        if event.start_timestamp.weekday() != current_weekday:
            current_weekday = event.end_timestamp.weekday()
            if embed != Embed():
                embed.description = string
                calendar.append(embed)
                string = ""
                embed = Embed()
            embed.title = "**"+ weekday[current_weekday] + " " + str(event.start_timestamp.day) + " " + month[event.start_timestamp.month -1] + " :**"
        else:
            string +="\n"
        string += str(event)
    calendar.pop(0)
    return calendar


# Utilisée pour stocker les evenements
events:list[Event] = []

events = update_events()

filtered_events = filter_events(events, [TimeFilter(date(2024, 10,9), Timing.AFTER), TimeFilter(date(2024,10,11), Timing.BEFORE), FiliereFilter(Filiere.MIAGE), GroupFilter([Group.TD2M, Group.CM])])

(filtered_events)
