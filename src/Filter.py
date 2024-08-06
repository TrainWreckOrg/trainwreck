from Event import Event
from datetime import date
from Enums import Timing, Filiere, Group

class Filter:
    """Classe de Base pour les filtres"""
    def filter(self, e:Event) -> bool:
        """Prend en argument un événement `e` et retourne `True` si `e` passe le filtre défini par la sous classe"""
        return True

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

def filter_events(events:list[Event], filters:list[Filter]) -> list[Event]:
    """Applique une liste de filtres à la liste d'événements passée en paramètre et retourne une nouvelle liste"""
    output = events.copy()
    for e in events:
        for f in filters:
            if not f.filter(e):
                output.remove(e)
                break
    return output