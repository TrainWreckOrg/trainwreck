from datetime import *
from turtle import rt
from pytz import *
from urllib.request import urlretrieve
from pathlib import Path
from enum import Enum
from interactions import Embed

# TODO : add filters
# TODO : cleanup Event object
# TODO : cleanup code

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
    "Con. Orien. Obj " : "Conception Orientée Objet",
    "Pro. Imp. Pro. Ori. Obj" : "Programmation Impérative et Orientée Objet",
    "Con. Ana. Algo" : "Conception et Analyse d'Algorithmes",
    "Log. Lam. Cal" : "Logique et Lambda Calcul",
    "Fram.Web 1" : "Frameworks Web 1"
}

class Filiere(Enum):
    INGE = "Ingé"
    MIAGE = "Miage"

class Group(Enum):
    TPAI = "TP A Inge"
    TPBI = "TP B Inge"
    TPCI = "TP C Inge"
    TPDI = "TP D Inge"
    TPAM = "TP A Miage"
    TPBM = "TP B Miage"
    TPCM = "TP C Miage"
    TPDM = "TP D Miage"
    TD1I = "TD 1 Inge"
    TD2I = "TD 2 Inge"
    TD1M = "TD 1 Miage"
    TD2M = "TD 2 Miage"
    TDA1I = "TD 1 Inge Anglais"
    TDA2I = "TD 2 Inge Anglais"
    TDA3I = "TD 3 Inge Anglais"
    TDA1M = "TD 1 Miage Anglais"
    TDA2M = "TD 2 Miage Anglais"
    TDA3M = "TD 3 Miage Anglais"


class Event:
    """Classe utilisée pour gerer les objets evenements"""
    def __init__(self, start : datetime, end :datetime, subject : str, group :str, location:str, teacher:str, isINGE:bool, isMIAGE:bool) -> None:
        self.start_timestamp = start
        self.end_timestamp = end
        self.location = location
        self.teacher = teacher
        self.subject = subject
        self.group = group
        # Note : isMIAGE and isINGE are not mutually exclusive
        self.isMIAGE = isMIAGE
        self.isINGE  = isINGE
    
    def __str__(self) -> str:
        return f"{self.start_timestamp.strftime("%Hh%M")}-{self.end_timestamp.strftime("%Hh%M")} : {"MIAGE" if (self.isMIAGE) else ""}{" - " if (self.isINGE and self.isMIAGE) else ""}{"INGE" if (self.isINGE) else ""} {self.group} - {self.subject} - {self.location} - {self.teacher}"

class Filter:
    def filter(self, e:Event) -> bool:
        """Prend en argument un evenement `e` et retourne `True` si `e` passe le filtre défini par la sous classe"""
        return True

class TimeFilter(Filter):
    def __init__(self, date:date, before:bool) -> None:
        self.date   = date
        self.before = before

    def filter(self, e: Event) -> bool:
        if self.before :
            return e.end_timestamp.date() < self.date
        else:
            return e.start_timestamp.date() > self.date

class FiliereFilter(Filter):
    def __init__(self, filiere:Filiere) -> None:
        self.filiere = filiere
    
    def filter(self, e: Event) -> bool:
        if self.filiere == Filiere.INGE:
            return e.isINGE
        else:
            return e.isMIAGE

class TPFilter(Filter):
    def __init__(self, tp) -> None:
        self.tp = tp
    
    def filter(self, e: Event) -> bool:
        return True

def fetch_calendar(url:str, filename:str):
    """Récupere le fichier .ics correspondant a une filiere donnée"""
    urlretrieve(url, filename)


def convert_timestamp(input : str) -> datetime :
    """Permet de convertir les timestamp en ISO-8601, et les passer en UTC+2"""
    iso_date = f"{input[0:4]}-{input[4:6]}-{input[6:11]}:{input[11:13]}:{input[13:]}"
    return datetime.fromisoformat(iso_date).astimezone(timezone("Europe/Paris"))


def build_event_from_data(start : datetime, end :datetime, sum : str, loc :str, desc :str) -> Event:
    """Permet d'extraire les informations des données parsées"""
    descsplit = desc.split("\\n")
    subject = subjects_table[descsplit[3]] if descsplit[3] in subjects_table.keys() else descsplit[3]
    teacher = descsplit[-3].replace("\n", "").removeprefix(" ")
    location = loc if not loc == "" else "Ndf"

    isMIAGE = False
    isINGE  = False
    
    if subject == "Anglais":
        if "MIAGE" in sum :
            group = f"{sum[10:13]}"
            isMIAGE = True
        else :
            group = f"TD{sum[13]}"
            isINGE = True
    else:
        if "L3 INFO - INGENIERIE" in descsplit and "Pro. Pro. Per." not in sum:
            isINGE = True
        if "L3 INFORMATIQUE - MIAGE" in descsplit:
            isMIAGE = True
        if descsplit[2].startswith("Gr"):
            group = descsplit[2][3:]
        else :
            group = "CM"
    
    return Event(start, end, subject, group, location, teacher, isINGE, isMIAGE)


def parse_calendar(filiere:str="INGE") -> list[Event]:
    """Extrait les données du fichier .ics et le telecharge si il est manquant"""
    filename = f"input/{filiere}.ics"
    p = Path(filename)
    if not p.exists() :
        fetch_calendar(url[filiere], filename)

    with open(filename, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    events = []
    event = {}
    for line in lines:
        if line.startswith("BEGIN:VEVENT"):
            event = {}
        elif line.startswith("END:VEVENT"):
            # print(event)
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
    return sorted(events, key=lambda event: event.start_timestamp)


def filter_events(events:list[Event], before:date=None, after:date=None, filiere:str="") -> list[Event]:
    output = []

    for event in events:
        if before != None:
            if event.end_timestamp.date() > before :
                continue
        if after != None:
            if event.start_timestamp.date() < after :
                continue
        if (filiere == "MIAGE" and not event.isMIAGE) or (filiere=="INGE" and not event.isINGE) :
            continue
        
        output.append(event)
    return output


def display(events:list[Event]) -> None:
    """affiche une liste d'évenements"""
    current_weekday = 7

    for event in events:
        if event.start_timestamp.weekday() != current_weekday:
            current_weekday = event.end_timestamp.weekday()
            print(f"**{weekday[current_weekday]} {event.start_timestamp.day} {month[event.start_timestamp.month -1]}:**")
        print(event)



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

events = parse_calendar("INGE")

for event in events:
    print(event.group)

# display(events)

filtered_events = filter_events(events, before=date(2024,10,1), filiere="INGE")

# if __name__ == "__main__":
#     display(filtered_events):