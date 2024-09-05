from datetime import date
import sentry_sdk

from Enums import Timing, Filiere, Group
from Event import Event
from src.Event import EventL3


class Filter:
    """Classe de Base pour les filtres."""
    def filter(self, e:Event) -> bool:
        """Prend en argument un événement `e` et retourne `True` si `e` passe le filtre défini par la sous classe."""
        return True


class TimeFilter(Filter):
    """Classe pour les filtres temporelle."""
    def __init__(self, date:date, timing:Timing) -> None:
        self.date   = date
        self.timing = timing

    def filter(self, e: Event) -> bool:
        """Permet de savoir si l'Event passe le filtre."""
        match self.timing:
            case Timing.BEFORE:
                return e.end_timestamp.date() <= self.date
            case Timing.AFTER:
                return e.start_timestamp.date() >= self.date
            case Timing.DURING:
                return e.start_timestamp.date() == self.date
            case _:
                # Ce cas ne devrait pas arriver et devrait être fix rapidement.
                try:
                    raise ValueError("Timing inconnue dans la classe TimeFilter")
                except BaseException as exception:
                    print(exception)
                    sentry_sdk.capture_exception(exception)
                return False


class FiliereFilter(Filter):
    """Classe pour les filtres de filière."""
    def __init__(self, filiere:Filiere) -> None:
        self.filiere = filiere

    def filter(self, e: Event) -> bool:
        """Permet de savoir si l'Event passe le filtre."""
        if self.filiere == Filiere.INGE:
            e : EventL3
            return e.isINGE
        elif self.filiere == Filiere.MIAGE:
            e : EventL3
            return e.isMIAGE
        else:
            return True


class GroupFilter(Filter):
    """Classe pour les filtres de groupe."""
    def __init__(self, groups:list[Group]) -> None:
        self.groups = groups

    def filter(self, e: Event) -> bool:
        """Permet de savoir si l'Event passe le filtre."""
        return e.group in self.groups


def filter_events(events:list[Event], filters:list[Filter]) -> list[Event]:
    """Applique une liste de filtres à la liste d'événements passée en paramètre et retourne une nouvelle liste filtrée."""
    output = events.copy()
    for e in events:
        for f in filters:
            if not f.filter(e):
                output.remove(e)
                break
    return output
