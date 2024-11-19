from datetime import datetime, timedelta, date
from urllib.error import URLError
from urllib.request import urlretrieve
from pytz import timezone

from Filter import Filter, TimeFilter, filter_events
from Enums import url, Timing
from Event import *
from sender import send_error_non_async

import os

class Calendar:
    """Classe utilisée pour stocker une liste d'objet Event."""
    def __init__(self, update : bool, argument) -> None:
        """ Update : Si l'on doit télécharger les fichiers ics."""
        # Dictionnaire qui stock les Event associé à l'UID.
        self.events_dict : dict[str:Event]
        self.events_list : list[Event]
        self.exams_dict : dict[str:Event] = {}
        self.exams_list : list[Event]


        self.update_events(update, argument)

    def fetch_calendar(self, url:str, filename:str) -> None:
        """Télécharge le fichier .ics.
        Url : L'URL du fichier à télécharger.
        Filename : Chemin de la destination du fichier.
        """
        try:
            urlretrieve(url, filename)
        except URLError as exception:
            send_error_non_async(exception)

    def convert_timestamp(self, input: str) -> datetime:
        """Permet de convertir les timestamp en ISO-8601, et les passer en UTC+2.
        Input : Une str contenant une date."""
        # 20241105T143000Z -> 2024-11-05T14:30:00Z
        iso_date = f"{input[0:4]}-{input[4:6]}-{input[6:11]}:{input[11:13]}:{input[13:]}"
        return datetime.fromisoformat(iso_date).astimezone(timezone("Europe/Paris"))

    def update_events(self, update: bool, argument) -> None:
        """Met à jour la liste d'événements en mêlant les événements issus des deux .ics.
        Update : Si l'on doit télécharger les fichiers ics.
        """
        output = {}
        filenameINGE = "data/INGE.ics"
        filenameMIAGE = "data/MIAGE.ics"
        
        if not (os.path.exists(filenameINGE) and os.path.exists(filenameMIAGE)):
            update = True

        if update:
            self.fetch_calendar(url["INGE"], filenameINGE)
            self.fetch_calendar(url["MIAGE"], filenameMIAGE)

        # | sert à concaténer deux dictionnaires.
        output = self.parse_calendar(filenameINGE, argument) | self.parse_calendar(filenameMIAGE, argument)


        self.events_dict = output
        # Tri les événements par ordre croissant en fonction de leur date.
        self.events_list = sorted(list(self.events_dict.values()),key=lambda event: event.start_timestamp)
        self.exams_list = sorted(list(self.exams_dict.values()),key=lambda event: event.start_timestamp)

    def parse_calendar(self, filename:str, argument) -> dict[str:Event]:
        """Extrait les données du fichier .ics passé dans filename.
        Filename : Chemin du fichier."""
        # On lit tout le fichiers ICS
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Le dictionnaire qui stock les évents.
        events = {}
        # Dictionnaire pour stocker temporairement les infos d'un événement avant sa création.
        event = {}
        # Liste des exam
        exams = {}

        for line in lines:
            # Balise Ouvrante, crée un nouveau dictionnaire vide.
            if line.startswith("BEGIN:VEVENT"):
                event = {"DTSTART":"", "DTEND":"", "SUMMARY":"", "LOCATION":"", "DESCRIPTION":"", "UID":""}
            # Balise Fermante, envoie les informations récoltées (Timestamps début et fin, le summary (titre), la salle et la description) et on obtient l'Event.
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

            # La description est sur plusieurs lignes et commence par un espace.
            elif line.startswith(" "):
                event["DESCRIPTION"] += line.removeprefix(" ").removesuffix("\n")
            else:
                for prefix in ("DTSTART:", "DTEND:", "SUMMARY:", "LOCATION:", "DESCRIPTION:", "UID:") :
                    if line.startswith(prefix):
                        event[prefix.removesuffix(":")] = line.removeprefix(prefix).removesuffix("\n")
                        break

        events, exams = self.apply_argument(events,exams,argument)

        self.exams_dict |= exams

        events |= exams
        return events


    def apply_argument(self, events:dict[str,Event], exams:dict[str,Event],argument):
        events, exams = self.exam_event_arguement(events, exams, argument)
        events, exams = self.special_event_arguement(events, exams, argument)
        events, exams = self.add_description_event_arguement(events, exams, argument)
        events, exams = self.add_event_arguement(events, exams, argument)
        events, exams = self.override_event_arguement(events, exams, argument)
        events, exams = self.delete_event_arguement(events, exams, argument)
        return events, exams

    def exam_event_arguement(self, events:dict[str,Event], exams:dict[str,Event],argument):
        exams_argument : dict[str:str] = argument.get("exam_list")
        for exam_uid in list(exams_argument.keys()):
            exam  = events.get(exam_uid)
            if exam is not None:
                exam.isEXAM = True
                exam.description_personnel = exams_argument.get(exam_uid)["description"]
                if exams_argument.get(exam_uid)["text"] != "":
                    exam.description = exams_argument.get(exam_uid)["text"]
                exams[exam.uid] = exam
        return events,exams

    def special_event_arguement(self, events:dict[str,Event], exams:dict[str,Event],argument):
        special_argument : dict[str:str] = argument.get("special_event")
        for special_uid in list(special_argument.keys()):
            event  = events.get(special_uid)
            if event is not None:
                event.isSpecial = True
                if special_argument.get(special_uid)["text"] != "":
                    event.description = special_argument.get(special_uid)["text"]
        return events,exams


    def add_description_event_arguement(self, events:dict[str,Event], exams:dict[str,Event],argument):
        description_argument : dict[str:str] = argument.get("add_description")
        for description_uid in list(description_argument.keys()):
            event  = events.get(description_uid)
            if event is not None:
                if description_argument.get(description_uid)["text"] != "":
                    event.description = description_argument.get(description_uid)["text"]
        return events,exams


    def add_event_arguement(self,events:dict[str,Event], exams:dict[str,Event],argument):
        for new_event in argument.get("add_event").values():
            group = Group.UKNW
            for g in Group:
                if g.value == new_event["group"]:
                    group = g
            e = Event(
                self.convert_timestamp(new_event["start"]),
                self.convert_timestamp(new_event["end"]),
                new_event["subject"],
                group,
                new_event["location"],
                new_event["teacher"],
                new_event["isINGE"]=="True",
                new_event["isMIAGE"]=="True",
                new_event["uid"],
                isEXAM= (new_event["isEXAM"] == "True" or new_event["uid"] in list(argument.get("exam_list").keys())),
                isSpecial=(new_event["isSPECIAL"] == "True" or new_event["uid"] in list(argument.get("special_event").keys())),
                description=new_event["text"],
                isAdd=True
            )
            if e.isEXAM:
                exams[e.uid] = e
            events[e.uid] = e

        return events,exams


    def override_event_arguement(self,events:dict[str,Event], exams:dict[str,Event], argument):
        for over_description in argument.get("override_event").keys():
            override_event = argument.get("override_event").get(over_description)
            group=Group.UKNW
            for g in Group:
                if g.value == override_event["group"]:
                    group=g
            over_event = Event(
                self.convert_timestamp(override_event["start"]),
                self.convert_timestamp(override_event["end"]),
                override_event["subject"],
                group,
                override_event["location"],
                override_event["teacher"],
                override_event["isINGE"] == "True",
                override_event["isMIAGE"] == "True",
                override_event["uid"],
                isEXAM=(override_event["isEXAM"] == "True"),
                isSpecial=(override_event["isSPECIAL"] == "True"),
                description=override_event["text"],
            )
            base_event : Event
            if override_event["uid"] in events.keys():
                base_event = events.get(override_event["uid"])
                base_event.override = over_event
            if override_event["uid"] in exams.keys():
                base_event = exams.get(override_event["uid"])
                base_event.override = over_event

        return events,exams

    def delete_event_arguement(self, events: dict[str, Event], exams: dict[str, Event], argument):
        delete_arguement : dict[str,dict[str,str]] = argument.get("delete_event")
        for delete_uid in list(delete_arguement.keys()):
            event: Event = events.get(delete_uid)
            if event is not None:
                event.isDelete = True
                if delete_arguement.get(delete_uid)["text"] != "":
                    event.description = delete_arguement.get(delete_uid)["text"]
        return events, exams

    def get_events(self) -> list[Event]:
        """Retourne la liste des événements."""
        return self.events_list

    def get_exams(self) -> list[Event]:
        """Retourne la liste des exams."""
        return self.exams_list



def changed_events(old: Calendar, new: Calendar, filters: list[Filter] = [TimeFilter(date.today(), Timing.AFTER), TimeFilter((date.today() + timedelta(days=14)), Timing.BEFORE)]):
    """Permet de vérifier si des événements ont été supprimer, ajouter ou modifier compris dans les filtres (défaut 14 jour)."""
    global calendar
    calendar = new
    
    old_events : list[Event] = filter_events(old.get_events(), filters)
    new_events : list[Event] = filter_events(new.get_events(), filters)

    old_events_dict = {e.uid:e for e in old_events}
    new_events_dict = {e.uid:e for e in new_events}

    sup :set[Event]         = set()
    add :set[Event]         = set()
    mod :set[(Event,Event)] = set()

    # Recherche des Event supprimé
    for e in old_events:
        if e.uid not in new_events_dict.keys():
            sup.add(e)

    # Recherche des Event ajouté
    for e in new_events:
        if e.uid not in old_events_dict.keys():
            add.add(e)

    # Recherche des Event modifié
    for e in old_events:
        if e.uid in new_events_dict.keys() and e != new_events_dict[e.uid]:
            mod.add((e, new_events_dict[e.uid]))
    
    changed_id : list[tuple[str, str]] = []

    for ne in add.copy():
        for oe in sup.copy():
            if ne.similar(oe):
                changed_id.append((oe.uid, ne.uid))
                if oe in sup:
                    sup.remove(oe)
                if ne in add:
                    add.remove(ne)

    return sup, add, mod, changed_id


def overlap(calendar: Calendar,argument , filters: list[Filter] = [TimeFilter(date.today(), Timing.AFTER), TimeFilter((date.today() + timedelta(days=14)), Timing.BEFORE)]):
    overlap_list = []

    list_event = filter_events(calendar.get_events(), filters)
    disable_raw : dict[str:str] = argument.get("disable_overlap")
    disable_tab : list[tuple[str:str]] = []
    for disable in disable_raw.values():
        disable:str
        uid1, uid2 = disable.split("|")
        disable_tab.append((uid1,uid2))

    for event1 in list_event:
        for event2 in list_event:
            if event1 == event2 or (event2,event1) in overlap_list:
                continue
            if (event1.uid,event2.uid) in disable_tab or (event2.uid,event1.uid) in disable_tab:
                continue
            if (event1.start_timestamp < event2.start_timestamp and event2.start_timestamp < event1.end_timestamp):
                if check_compatibilite_group(event1,event2):
                    overlap_list.append((event1,event2))
                    continue
            if (event1.start_timestamp < event2.end_timestamp and event2.end_timestamp < event1.end_timestamp):
                if check_compatibilite_group(event1,event2):
                    overlap_list.append((event1,event2))
                    continue
            if (event1.start_timestamp >= event2.start_timestamp and event1.end_timestamp <= event2.end_timestamp):
                if check_compatibilite_group(event1,event2):
                    overlap_list.append((event1,event2))
                    continue

    return overlap_list


def check_compatibilite_group(event1:Event,event2:Event):
    group1 = event1.group
    group2 = event2.group

    if event1.isINGE == event2.isINGE :
        if group1 == Group.CM:
            return group2 in [Group.CM,Group.TD1I,Group.TD2I,Group.TPAI, Group.TPBI, Group.TPCI, Group.TPDI, Group.TDA1I, Group.TDA2I, Group.TDA3I, Group.TDA4I]
        if group1 == Group.TD1I:
            return group2 in [Group.CM,Group.TD1I,Group.TPAI,Group.TPBI,Group.TDA1I,Group.TDA2I]
        if group1 == Group.TD2I:
            return group2 in [Group.CM,Group.TD2I,Group.TPCI,Group.TPDI,Group.TDA3I,Group.TDA4I]
        if group1 in [Group.TPAI,Group.TDA1I]:
            return group2 in [Group.CM,Group.TD1I,Group.TPAI,Group.TDA1I]
        if group1 in [Group.TPBI,Group.TDA2I]:
            return group2 in [Group.CM,Group.TD1I,Group.TPBI,Group.TDA2I]
        if group1 in [Group.TPCI,Group.TDA3I]:
            return group2 in [Group.CM,Group.TD2I,Group.TPCI,Group.TDA3I]
        if group1 in [Group.TPDI,Group.TDA4I]:
            return group2 in [Group.CM,Group.TD2I,Group.TPDI,Group.TDA4I]
    if event1.isMIAGE == event2.isMIAGE :
        if group1 == Group.CM:
            return group2 in [Group.CM,Group.TD1M,Group.TD2M,Group.TP1M, Group.TP2M, Group.TP3M, Group.TDA1M, Group.TDA2M, Group.TDA3M]
        if group1 == Group.TD1M:
            return group2 in [Group.CM,Group.TD1M,Group.TP1M,Group.TP3M,Group.TDA1M,Group.TDA3M]
        if group1 == Group.TD2M:
            return group2 in [Group.CM,Group.TD2M,Group.TP2M,Group.TP3M,Group.TDA2M,Group.TDA3M]
        if group1 in [Group.TP1M,Group.TDA1M]:
            return group2 in [Group.CM,Group.TD1M,Group.TP1M,Group.TDA1M]
        if group1 in [Group.TP2M,Group.TDA2M]:
            return group2 in [Group.CM,Group.TD2M,Group.TP2M,Group.TDA2M]
        if group1 in [Group.TP3M,Group.TDA3M]:
            return group2 in [Group.CM,Group.TD1M,Group.TD2M,Group.TP3M,Group.TDA3M]



calendar: Calendar | None = None

def get_calendar() -> Calendar:
    """Permet d'obtenir l'objet Calendar."""
    global calendar
    return calendar

def set_calendar(calendar_old : Calendar) -> None:
    """Permet d'obtenir l'objet Calendar."""
    global calendar
    calendar = calendar_old