from interactions import Embed, EmbedFooter, Member, User
from datetime import date

from Enums import weekday, month, colors
from Filter import *
from Event import *


def get_embeds(events: list[Event], user: User | Member, jour: date = date(year=2077, month=7, day=7), jour2: date = None) -> list[Embed]:
    """Permet de générer une liste d'Embed à partir d'une liste d'Event."""
    # Cette fonction est une usine à gaz évité de la modifier !
    icon = user.avatar_url
    if len(events) == 0:
        return [Embed(title=f"{weekday[jour.weekday()]} {jour.day} {month[jour.month - 1]} {jour.year}{f" - {weekday[jour2.weekday()]} {jour2.day} {month[jour2.month - 1]} {jour2.year}" if (jour2 is not None) else ""}:", description="Aucun Cours", footer=EmbedFooter(f"Emploi du Temps de @{user.display_name}\nLes emploi du temps sont fournis a titre informatif uniquement,\n -> Veuillez vous référer à votre page personnelle sur l'ENT", icon))]
    current_day = date(1970, 1, 1)
    embeds : list[Embed] = []
    for event in events:
        if event.start_timestamp.date() != current_day:
            current_day = event.start_timestamp.date()
            embed = Embed(f"{weekday[current_day.weekday()]} {event.start_timestamp.day} {month[event.start_timestamp.month - 1]} {event.start_timestamp.year}:", "", colors[current_day.weekday()])
            embeds.append(embed)
        embeds[-1].description += "- " + str(event) + "\n"
    
    embeds[-1].set_footer(f"Emploi du Temps de @{user.display_name}\nLes emploi du temps sont fournis à titre informatif uniquement,\n -> Veuillez-vous référer à votre page personnelle sur l'ENT", icon)
    return embeds


def get_ics(events: list[Event], filename: str):
    """Permet de régénérer un fichier ics."""
    ics = ("BEGIN:VCALENDAR\n"
           "METHOD:REQUEST\n"
           "PRODID:-//ADE/version 6.0\n"
           "VERSION:2.0\n"
           "CALSCALE:GREGORIAN\n")

    for event in events:
        ics += event.ics()

    ics += "END:VCALENDAR"
    with open(f"{filename}.ics", "w", encoding="UTF-8") as f:
        f.write(ics)
    return True
