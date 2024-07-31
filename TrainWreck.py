from datetime import datetime, date, timedelta
from pytz import timezone
from urllib.request import urlretrieve
from pathlib import Path
from enum import Enum
from interactions import Embed, Member
from dotenv import load_dotenv

import time, os, pickle

print(
"""
\u001b[2;35m  ______           _       _       __               __   
\u001b[0m\u001b[2;31m /_  __/________ _(_)___  | |     / /_______  _____/ /__ 
\u001b[0m\u001b[2;33m  / / / ___/ __ `/ / __ \\ | | /| / / ___/ _ \\/ ___/ //_/ 
\u001b[0m\u001b[2;36m / / / /  / /_/ / / / / / | |/ |/ / /  /  __/ /__/ ,<    
\u001b[0m\u001b[2;34m/_/ /_/   \\__,_/_/_/ /_/  |__/|__/_/   \\___/\\___/_/|_|(_)\u001b[0m
"""
)

ascii = """
```ansi
[2;35m  ______           _       _       __               __   
[0m[2;31m /_  __/________ _(_)___  | |     / /_______  _____/ /__ 
[0m[2;33m  / / / ___/ __ `/ / __ \\ | | /| / / ___/ _ \\/ ___/ //_/ 
[0m[2;36m / / / /  / /_/ / / / / / | |/ |/ / /  /  __/ /__/ ,<    
[0m[2;34m/_/ /_/   \\__,_/_/_/ /_/  |__/|__/_/   \\___/\\___/_/|_|(_)[0m
```
"""

load_dotenv("cle.env")

# URL utilisée pour fetch les EDT de chaque filière
url = {
    "INGE" : os.getenv("INGEICS"),
    "MIAGE" : os.getenv("MIAGEICS"),
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

colors = [0xc62139,0xe16136,0xd8a74c,0x4a668c,0x304d7a, 0x213150, 0xf3f5f7]

class Timing(Enum):
    BEFORE  = "Before"
    DURING = "During"
    AFTER   = "After"

class Filiere(Enum):
    INGE    = "Ingé"
    MIAGE   = "Miage"
    UKNW    = "UKNW"

    def __str__(self):
        return self.value

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

    def __str__(self):
        return self.value

class Subscription(Enum):
    DAILY   = "DAILY"
    WEEKLY  = "WEEKLY"
    BOTH    = "BOTH"
    NONE    = "NONE"

    def __str__(self):
        return self.value

# ----- CLASSES -----
class Event:
    """Classe utilisée pour gérer les objets événements"""
    def __init__(self, start:datetime, end:datetime, subject:str, group:Group, location:str, teacher:str, isINGE:bool, isMIAGE:bool, uid:str) -> None:
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
        ics += "DESCRIPTION:\\n\\n" + self.group.value + "\\n" + self.subject + self.subject + "\\nL3 INFO - INGENIERIE\\nL3 INFORMAT-UPEX MINERVE\\n" + self.teacher + "\\n(Exporté le:" + str(datetime.now()) + ")\\n" + "\n"
        ics += "UID:" + self.uid + "\n"
        ics += "CREATED:19700101T000000Z" + "\n"
        ics += "LAST-MODIFIED:" + stamp + "\n"
        ics += "SEQUENCE:2141354890" + "\n"
        ics += "END:VEVENT" + "\n"
        return ics

class Filter:
    """Classe de Base pour les filtres"""
    def filter(self, e:Event) -> bool:
        """Prend en argument un événement `e` et retourne `True` si `e` passe le filtre défini par la sous classe"""
        return True

class Calendar:
    """Classe utilisée pour stocker une liste d'objet evenements"""
    def __init__(self, events_dict : dict[str:Event] = {}) -> None:
        self.events_dict = events_dict
        self.events_list = sorted(list(self.events_dict.values()),key=lambda event: event.start_timestamp)


    def fetch_calendar(self, url:str, filename:str) -> None:
        """Récupère le fichier .ics correspondant à une filière donnée"""
        urlretrieve(url, filename)

    def convert_timestamp(self, input : str) -> datetime :
        """Permet de convertir les timestamp en ISO-8601, et les passer en UTC+2"""
        # 20241105T143000Z -> 2024-11-05T14:30:00Z
        iso_date = f"{input[0:4]}-{input[4:6]}-{input[6:11]}:{input[11:13]}:{input[13:]}"
        return datetime.fromisoformat(iso_date).astimezone(timezone("Europe/Paris"))

    def update_events(self, update: bool):
        """met a jour la liste d'événements en mêlant les événements issus des deux .ics"""
        output = {}
        filenameINGE = "data/INGE.ics"
        filenameMIAGE = "data/MIAGE.ics"

        if update:
            self.fetch_calendar(url["INGE"], filenameINGE)
            self.fetch_calendar(url["MIAGE"], filenameMIAGE)

        # | sert a concaténer deux dictionnaires
        output = self.parse_calendar(filenameINGE) | self.parse_calendar(filenameMIAGE)

        self.events_dict = output
        self.events_list = sorted(list(self.events_dict.values()),key=lambda event: event.start_timestamp)
   
    
    def parse_calendar(self, filename:str) -> dict[str:Event]:
        """Extrait les données du fichier .ics passé dans filename"""
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()

        events = {}
        event = {}
        for line in lines:
            # Balise Ouvrante, crée un nouveau dictionnaire vide
            if line.startswith("BEGIN:VEVENT"):
                event = {"DTSTART":"", "DTEND":"", "SUMMARY":"", "LOCATION":"", "DESCRIPTION":"", "UID":""}
            # Balise Fermante, envoie les informations récoltées (Timestamps début et fin, le summary (titre), la salle et la description)
            elif line.startswith("END:VEVENT"):
                e = get_event_from_data(
                    self.convert_timestamp(event["DTSTART"]),
                    self.convert_timestamp(event["DTEND"]),
                    event["SUMMARY"],
                    event["LOCATION"],
                    event["DESCRIPTION"],
                    event["UID"]
                )
                events[e.uid] = e

            elif line.startswith(" "):
                event["DESCRIPTION"] += line.removeprefix(" ")
            else:
                for prefix in ("DTSTART:", "DTEND:", "SUMMARY:", "LOCATION:", "DESCRIPTION:", "UID:") :
                    if line.startswith(prefix):
                        event[prefix.removesuffix(":")] = line.removeprefix(prefix).removesuffix("\n")
                        break
        return events

    def get_events(self) -> list[Event]:
        return self.events_list

    def get_events_dict(self) -> dict[str:Event]:
        return self.events_dict

    # def get_events_dict() -> dict[str:Event]:
    #     global events_dict
    #     if need_updating(events_dict):
    #         events_old : dict[str:Event] = {}
    #         if events_dict == {}:
    #             events_old = update_events(False)
    #         else:
    #             events_old = events_dict
    #         events_dict = update_events(True)
    #         change(events_old, events_dict)
    #     return events_dict



class TimeFilter(Filter):
    def __init__(self, date:date, timing:Timing) -> None:
        self.date   = date
        self.timing = timing

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

class User:
    def __init__(self, id:int, groups:list[Group], filiere:Filiere) -> None:
        self.id         = id
        self.groups     = groups
        self.filiere    = filiere

    def __hash__(self) -> int:
        return self.id

    def __str__(self) -> str:
        return f"<{self.id}, {self.groups}, {self.filiere.value}>"

class UserBase:
    def __init__(self, users:dict[int:User], daily_subscribed_users:set, weekly_subscribed_users:set) -> None:
        self.users                      = users
        self.daily_subscribed_users     = daily_subscribed_users
        self.weekly_subscribed_users    = weekly_subscribed_users

    def __str__(self) -> str:
        return f"<users:{[str(x) for x in self.users.values()]}, daily:{self.daily_subscribed_users}, weekly:{self.weekly_subscribed_users}>"

    def has_user(self, id:int) -> bool:
        """Vérifie si l'utilisateur est déjà enregistré"""
        return id in self.users.keys()

    def is_user_subscribed(self, id:int, subscription:Subscription) -> bool:
        if self.has_user(id):
            is_daily = id in self.daily_subscribed_users
            is_weekly = id in self.weekly_subscribed_users
            match subscription:
                case Subscription.DAILY:
                    return is_daily
                case Subscription.WEEKLY:
                    return is_weekly
                case Subscription.BOTH:
                    return is_daily and is_weekly
                case Subscription.NONE:
                    return (not is_daily) and (not is_weekly)

    def add_user(self, id:int, groups:list[Group], filiere:Filiere) -> None:
        """Enregistre l'utilisateur s'il n'est pas déjà enregistré, sinon ne fait rien"""
        if not self.has_user(id):
            self.users[id] = User(id, groups, filiere)
            dump_user_base(self)

    def update_user_groups(self, id:int, new_groups:list[Group]) -> None:
        """Remplace les groupes de l'utilisateur par une ceux de `new_groups`"""
        if self.has_user(id):
            self.users[id].groups = new_groups
            dump_user_base(self)


    def user_subscribe(self, id:int, subscription:Subscription):
        """Abonne un utilisateur à une ou plusieurs des listes"""
        if self.has_user(id):
            match subscription:
                case Subscription.DAILY:
                    self.daily_subscribed_users.add(id)
                case Subscription.WEEKLY:
                    self.weekly_subscribed_users.add(id)
                case Subscription.BOTH:
                    self.daily_subscribed_users.add(id)
                    self.weekly_subscribed_users.add(id)
            dump_user_base(self)


    def user_unsubscribe(self, id:int, subscription:Subscription):
        """Désabonne un utilisateur à une ou plusieurs des listes"""
        if self.has_user(id):
            match subscription:
                case Subscription.DAILY if self.is_user_subscribed(id, subscription):
                    self.daily_subscribed_users.remove(id)
                case Subscription.WEEKLY if self.is_user_subscribed(id, subscription):
                    self.weekly_subscribed_users.remove(id)
                case Subscription.BOTH if self.is_user_subscribed(id, subscription):
                    self.daily_subscribed_users.remove(id)
                    self.weekly_subscribed_users.remove(id)
            dump_user_base(self)
    

    def get_user(self, id:int) -> User:
        """Retourne un Objet utilisateur s'il est présent dans la base de donnée, None sinon"""
        if self.has_user(id):
            return self.users[id]
        else:
            return None



def load_user_base():
    """Récupère la base d'utilisateur depuis le fichier UserBase.pkl"""
    with open("data/UserBase.pkl", "rb") as f:
        return pickle.load(f)

def dump_user_base(user_base:UserBase):
    """Charge la base d'utilisateur dans le fichier UserBase.pkl"""
    with open("data/UserBase.pkl", "wb") as f:
        pickle.dump(user_base, f, pickle.HIGHEST_PROTOCOL)




# ----- HElPER  -----
def filter_events(events:list[Event], filters:list[Filter]) -> list[Event]:
    """Applique une liste de filtres à la liste d'événements passée en paramètre et retourne une nouvelle liste"""
    output = events.copy()
    for e in events:
        for f in filters:
            if not f.filter(e):
                output.remove(e)
                break
    return output

# ----- PARSING -----
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


# ----- DISPLAYING -----
def display(events:list[Event]) -> None:
    """Affiche une liste d'événements"""
    current_weekday = 7

    for event in events:
        if event.start_timestamp.weekday() != current_weekday:
            current_weekday = event.end_timestamp.weekday()
            print(f"**{weekday[current_weekday]} {event.start_timestamp.day} {month[event.start_timestamp.month -1]}:**")
        print(event)

def export(events:list[Event], filename:str="output/log.txt") -> None:
    """Exporte une liste d'événements dans un fichier spécifié"""
    current_weekday = 7
    with open(filename, "w") as f:
        for event in events:
            if event.start_timestamp.weekday() != current_weekday:
                current_weekday = event.end_timestamp.weekday()
                print(f"**{weekday[current_weekday]} {event.start_timestamp.day} {month[event.start_timestamp.month -1]}:**", file=f)
            print(event, file=f)

def get_embeds(events:list[Event]) -> list[Embed]:
    if len(events) == 0:
        return [Embed(title="Aucun Cours")]
    current_weekday = 7
    embeds : list[Embed] = []
    for event in events:
        if event.start_timestamp.weekday() != current_weekday:
            current_weekday = event.start_timestamp.weekday()
            embed = Embed(f"{weekday[current_weekday]} {event.start_timestamp.day} {month[event.start_timestamp.month -1]}:", "", colors[current_weekday])
            embeds.append(embed)
        embeds[-1].description += "- " + str(event) + "\n"
    embeds[-1].set_footer("Les emploi du temps sont fournis a titre informatif uniquement,\n -> Veuillez vous référer à votre page personnelle sur l'ENT")
    return embeds


calendar  :Calendar = Calendar({})
user_base :UserBase = load_user_base()
calendar.update_events(False)

new_calendar = Calendar({})
new_calendar.update_events(True)


def get_user_base() -> UserBase:
    global user_base
    user_base = load_user_base()
    return user_base

def get_calendar() -> Calendar:
    global calendar
    return calendar


def get_ics(events:list[Event]):
    ics = ("BEGIN:VCALENDAR\n"
           "METHOD:REQUEST\n"
           "PRODID:-//ADE/version 6.0\n"
           "VERSION:2.0\n"
           "CALSCALE:GREGORIAN\n")

    for event in events:
        ics += event.ics()

    ics += "END:VCALENDAR"
    with open("output/calendar.ics", "w", encoding="UTF-8") as f:
        f.write(ics)
    return True

def changed_events(old : Calendar, new : Calendar, filters :list[Filter]= [TimeFilter(date.today(), Timing.AFTER), TimeFilter((date.today() + timedelta(days=14)), Timing.BEFORE)]):
    old_events = filter_events(old.get_events(), filters)
    new_events = filter_events(new.get_events(), filters)

    


    # changement : list[Embed] = []
    # changement_events : list[Event] = []
    # for new_uid in new.get_events_dict():
    #     new_event = new.get_events_dict().get(new_uid)
    #     old_event = old.get_events_dict().get(new_uid)
    #     if old_event != new_event:
    #         embed = Embed(title="Changement sur cette événement", description=f"**Ancien événement :**\n{old_event}\n**Nouvelle événement :**\n{new_event}")
    #         changement.append(embed)
    #         changement_events.append(new_event)
    # if len(changement) != 0:
    #     return embed, (len(filter_events(changement_events, )) > 0)
    #     #changement_event(changement)


changed_events(calendar, new_calendar, [TimeFilter(date.today(), Timing.AFTER), TimeFilter((date.today() + timedelta(days=14)), Timing.BEFORE)])
