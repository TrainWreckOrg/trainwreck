from datetime import *
from pytz import *

# TODO : fix Anglais
# TODO : fix subject names
# TODO : add filters
# TODO : cleanup Event object
# TODO : cleanup code
# TODO : separate code better ?
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
    def __init__(self, start : datetime, end :datetime, sum : str, loc :str, desc :str) -> None:
        
        descsplit = desc.split("\\n")

        self.start_timestamp    = start
        self.end_timestamp      = end
        self.location           = loc if not loc == "" else "Ndf"
        self.teacher            = descsplit[-3].replace("\n", "").removeprefix(" ")
        self.subject            = subjects_table[descsplit[3]] if descsplit[3] in subjects_table.keys() else descsplit[3]
        self.group              = ""
        # Note : isMIAGE and isINGE are not mutually exclusive
        self.isMIAGE            = False
        self.isINGE             = False
        
        if self.subject == "Anglais":
            if "MIAGE" in sum :
                self.group = f"{sum[10:13]}"
                self.isMIAGE = True
            else :
                self.group = f"TD{sum[13]}"
                self.isINGE = True
        else:
            if "L3 INFO - INGENIERIE" in descsplit and "Pro. Pro. Per." not in sum:
                self.isINGE = True
            if "L3 INFORMATIQUE - MIAGE" in descsplit:
                self.isMIAGE = True
            if descsplit[2].startswith("Gr"):
                self.group = descsplit[2][3:]
            else :
                self.group = "CM"
    
    def __str__(self) -> str:
        return f"{self.summary} : {self.location}\n{self.description}\n{self.start_timestamp.ctime()} - {self.end_timestamp.ctime()}"

def convert_timestamp(input : str) -> datetime :
    iso_date = f"{input[0:4]}-{input[4:6]}-{input[6:11]}:{input[11:13]}:{input[13:]}"
    return datetime.fromisoformat(iso_date).astimezone(timezone("Europe/Paris"))

def parse_calendar(file : str = "input/ADECal.ics") -> list[Event]:
    with open(file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    events = []
    event = {}
    for line in lines:
        if line.startswith("BEGIN:VEVENT"):
            event = {}
        elif line.startswith("END:VEVENT"):
            # print(event)
            e = Event(
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

events = parse_calendar()
current_weekday = 0
for event in events:
    if event.start_timestamp.weekday() >= current_weekday:
        print(f"**{weekday[current_weekday]} {event.start_timestamp.day}:**")
        current_weekday+=1
    print( f"{event.start_timestamp.strftime("%Hh%M")}-{event.end_timestamp.strftime("%Hh%M")} : {"MIAGE" if event.isMIAGE else ""}{" - " if event.isINGE and event.isMIAGE else ""}{"INGE" if event.isINGE else ""} {event.group} - {event.subject} - {event.location} - {event.teacher}")



