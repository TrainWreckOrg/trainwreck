from dotenv import load_dotenv
import os

from enum import Enum

load_dotenv("keys.env")

# URL utilisée pour fetch les EDT de chaque filière.
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

# Pour convertir les abréviations des cours en complet.
subjects_table = {
    "Con. Orien. Obj" : "Conception Orientée Objet",
    "Pro. Imp. Pro. Ori. Obj" : "Programmation Impérative & Orientée Objet",
    "Con. Ana. Algo" : "Conception et Analyse d'Algorithmes",
    "Log. Lam. Cal" : "Logique & Lambda Calcul",
    "Fram.Web 1" : "Frameworks Web 1",
    "Pro. Pro. Per." : "Projet Personnel & Professionnel",
    "Réseaux 1" : "Réseaux 1",
    "Anglais": "Anglais",
    "Programmation Avancée": "Programmation Avancée",
    "Statistique":"Statistique",
    "Gestion comptable":"Gestion comptable",
    "Système d’information" : "Système d’information",
    "Techniques de communicat°" : "Techniques de comm",
    "Framework Web 2" : "Framework Web 2",
    "Programmation N-Tiers" : "Programmation N-Tiers",
    "Programmation Logique IA" : "Programmation Logique pour l'IA",
    "Fondements du calcul" : "Fondements du calcul",
    "Réseaux 2" : "Réseaux 2",
    "Algorithmique avancée" : "Algorithmique avancée",
    "Droit" : "Droit",
    "Environnement Économique" : "Environnement Économique",
    "La recherche en info." : "Recherche en info"
}

# Liste des couleurs pour les embeds.
colors = [0xc62139, 0xe16136, 0xd8a74c, 0x4a668c, 0x304d7a, 0x213150, 0xf3f5f7]


class Timing(Enum):
    """Représent les différents états de timing (BEFORE, DURING, AFTER)."""
    BEFORE = "Before"
    DURING = "During"
    AFTER  = "After"


class Filiere(Enum):
    """Représent les différentes filières (INGE, MIAGE, UKNW)."""
    INGE  = "Ingé"
    MIAGE = "Miage"
    UKNW  = "UKNW"

    def __str__(self):
        return self.value


class Group(Enum):
    """Représent les différents groupes (TD, TP, TD Anglais, CM, UKNW)."""
    TD1I    = "TD 1 Inge"
    TD2I    = "TD 2 Inge"
    TPAI    = "TP A Inge"
    TPBI    = "TP B Inge"
    TPCI    = "TP C Inge"
    TPDI    = "TP D Inge"
    TD1M    = "TD 1 Miage"
    TD2M    = "TD 2 Miage"
    TP1M    = "TP 1 Miage"
    TP2M    = "TP 2 Miage"
    TP3M    = "TP 3 Miage"
    TDA1I   = "TD 1 Inge Anglais"
    TDA2I   = "TD 2 Inge Anglais"
    TDA3I   = "TD 3 Inge Anglais"
    TDA4I   = "TD 4 Inge Anglais"
    TDA1M   = "TD 1 Miage Anglais"
    TDA2M   = "TD 2 Miage Anglais"
    TDA3M   = "TD 3 Miage Anglais"
    CM      = "CM"
    UKNW    = "UKNW"

    def __str__(self):
        return self.value


class RoleEnum(Enum):
    """Représent les différents rôles du discord qui ne sont pas en lien avec l'EDT."""
    ADMIN = "Admin"
    MODO = "Modérateur"
    EDTBOT = "EDT Bot"
    EDTTEST = "EDT TEST"
    PERMA = "Perma"
    ONBOARDED = "onboarded"

    def __str__(self):
        return self.value


class Subscription(Enum):
    """Représent les différents états d'abonnement (DAILY, WEEKLY, BOTH, NONE)."""
    DAILY  = "DAILY"
    WEEKLY = "WEEKLY"
    BOTH   = "BOTH"
    NONE   = "NONE"
    DAILY_ICS = "DAILY_ICS"
    WEEKLY_ICS = "WEEKLY_ICS"
    BOTH_ICS = "BOTH_ICS"
    NONE_ICS = "NONE_ICS"

    def __str__(self):
        return self.value
