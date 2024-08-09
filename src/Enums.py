from enum import Enum
from dotenv import load_dotenv

import os
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
    TDA1M   = "TD 1 Miage Anglais"
    TDA2M   = "TD 2 Miage Anglais"
    TDA3M   = "TD 3 Miage Anglais"
    CM      = "CM"
    UKNW    = "UKNW"
    ONBOARDED = "onboarded"

    def __str__(self):
        return self.value

class Subscription(Enum):
    DAILY   = "DAILY"
    WEEKLY  = "WEEKLY"
    BOTH    = "BOTH"
    NONE    = "NONE"

    def __str__(self):
        return self.value

ascii_logo = """
```ansi
[2;35m  ______           _       _       __               __   
[0m[2;31m /_  __/________ _(_)___  | |     / /_______  _____/ /__ 
[0m[2;33m  / / / ___/ __ `/ / __ \\ | | /| / / ___/ _ \\/ ___/ //_/ 
[0m[2;36m / / / /  / /_/ / / / / / | |/ |/ / /  /  __/ /__/ ,<    
[0m[2;34m/_/ /_/   \\__,_/_/_/ /_/  |__/|__/_/   \\___/\\___/_/|_|(_)[0m
```
"""