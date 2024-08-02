from Event import *
from datetime import datetime, timedelta, date
from pytz import timezone
from urllib.request import urlretrieve
from Enums import url, Timing
from Filter import Filter, TimeFilter, filter_events

class Calendar:
    """Classe utilisée pour stocker une liste d'objet evenements"""
    def __init__(self, update : bool) -> None:
        self.events_dict : dict[str:Event]
        self.events_list : list[Event]

        self.update_events(update)


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

calendar :Calendar = None

def changed_events(old : Calendar, new : Calendar, filters :list[Filter] = [TimeFilter(date.today(), Timing.AFTER), TimeFilter((date.today() + timedelta(days=14)), Timing.BEFORE)]):
    global calendar
    calendar = new
    
    old_events : list[Event] = filter_events(old.get_events(), filters)
    new_events : list[Event] = filter_events(new.get_events(), filters)

    old_events_dict = {e.uid:e for e in old_events}
    new_events_dict = {e.uid:e for e in new_events}

    sup :set[Event]         = set()
    add :set[Event]         = set()
    mod :set[(Event,Event)] = set()

    for e in old_events:
        if e.uid not in new_events_dict.keys():
            sup.add(e)
    
    for e in new_events:
        if e.uid not in old_events_dict.keys():
            add.add(e)
    
    for e in old_events:
        if e.uid in new_events_dict.keys() and e != new_events_dict[e.uid]:
            mod.add((e, new_events_dict[e.uid]))
    
    return sup, add, mod


def get_calendar() -> Calendar:
    global calendar
    return calendar