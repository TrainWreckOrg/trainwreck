from datetime import *
from pytz import *
from urllib.request import urlretrieve
from pathlib import Path


# TODO : add filters
# TODO : cleanup Event object
# TODO : cleanup code
# TODO : add RSS compat ?

weekday = [
    "Lundi",
    "Mardi",
    "Mercredi",
    "Jeudi",
    "Vendredi",
    "Samedi",
    "Dimanche"
]

subjects_table = {
    "Con. Orien. Obj " : "Conception Orientée Objet",
    "Pro. Imp. Pro. Ori. Obj" : "Programmation Impérative et Orientée Objet",
    "Con. Ana. Algo" : "Conception et Analyse d'Algorithmes",
    "Log. Lam. Cal" : "Logique et Lambda Calcul",
    "Fram.Web 1" : "Frameworks Web 1"
}

class Event:
    """Class used to manage event objects"""
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
        return f"{self.summary} : {self.location}\n{self.description}\n{self.start_timestamp.ctime()} - {self.end_timestamp.ctime()}"

def build_event_from_data(start : datetime, end :datetime, sum : str, loc :str, desc :str) -> Event:
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

def convert_timestamp(input : str) -> datetime :
    iso_date = f"{input[0:4]}-{input[4:6]}-{input[6:11]}:{input[11:13]}:{input[13:]}"
    return datetime.fromisoformat(iso_date).astimezone(timezone("Europe/Paris"))

def parse_calendar(filename: str = "input/ADECal.ics") -> list[Event]:
    p = Path(filename)
    if not p.exists() :
        fetch_calendar(filename)

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

def display(events : list[Event]):
    current_weekday = -1
    for event in events:
        if event.start_timestamp.weekday() != current_weekday:
            print(f"**{weekday[current_weekday]} {event.start_timestamp.day}:**")
            current_weekday = event.end_timestamp.weekday()
        print( f"{event.start_timestamp.strftime("%Hh%M")}-{event.end_timestamp.strftime("%Hh%M")} : {"MIAGE" if (event.isMIAGE) else ""}{" - " if (event.isINGE and event.isMIAGE) else ""}{"INGE" if (event.isINGE) else ""} {event.group} - {event.subject} - {event.location} - {event.teacher}")


def fetch_calendar(filename:str = "input/ADECal.ics"):
    url = ("https://aderead.univ-orleans.fr/jsp/custom/modules/plannings/anonymous_cal.jsp?data=e476946ed5447b1050d7a6c48ccf4bad4592592d3b282f749c9a606b710f264f6250ba3fea2e12caebbcd166cfe88476f6893987a472171c27978e76da251b877c79900682576cf2be48a3169e635e57166c54e36382c1aa3eb0ff5cb8980cdb,1")
    urlretrieve(url, filename)

display(parse_calendar())

