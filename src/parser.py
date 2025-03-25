from datetime import datetime

from Event import Event, get_event_from_data
from Enums import subjects_table, Group
from sender import send_error_non_async
from pytz import timezone


def entry_point(start:datetime, end:datetime, sum:str, loc:str, desc:str, uid:str, arguement) -> Event|bool:
    try:
        debug = get_debug(start, end, sum, loc, desc, uid, arguement)
        hide = get_hide(uid, arguement)
        if hide:
            return True
        if debug is not None:
            return debug

        tmp = datetime(2025, 1, 12, 0, 0, tzinfo=timezone("Europe/Paris"))
        if start < tmp:
            return get_event_from_data(start, end, sum, loc, desc, uid)
        else:
             return nouveau_parseur(start, end, sum, loc, desc, uid)
    except BaseException as exception:
        send_error_non_async(exception)

def convert_timestamp(input: str) -> datetime:
    """Permet de convertir les timestamp en ISO-8601, et les passer en UTC+2.
    Input : Une str contenant une date."""
    # 20241105T143000Z -> 2024-11-05T14:30:00Z
    iso_date = f"{input[0:4]}-{input[4:6]}-{input[6:11]}:{input[11:13]}:{input[13:]}"
    return datetime.fromisoformat(iso_date).astimezone(timezone("Europe/Paris"))

def get_debug(start:datetime, end:datetime, sum:str, loc:str, desc:str, uid:str, arguement:dict[str:dict[str:str]]):
    debug_list : dict[str:str] = arguement["debug_list"]
    for sum_debug in list(debug_list.keys()):
        if sum_debug == sum or uid == debug_list[sum_debug]["uid"]:
            debug :dict[str:str]= debug_list[sum_debug]
            new_start : datetime = start
            new_end : datetime = end
            new_subject : str = sum
            new_group : Group = Group.UKNW
            new_location : str = loc
            new_teacher : str = "Équipe Enseignante"
            new_isINGE : bool = debug["isINGE"] == "True"
            new_isMIAGE :bool = debug["isMIAGE"] == "True"
            new_uid : str = uid


            if debug["start"] != "":
                new_start = convert_timestamp(debug["start"])
            if debug["end"] != "":
                new_end = convert_timestamp(debug["end"])
            if debug["subject"] != "":
                new_subject = debug["subject"]
            if debug["group"] != "":
                new_group = Group.UKNW
                for g in Group:
                    if g.value == debug["group"]:
                        new_group = g
            if debug["location"] != "":
                new_location = debug["location"]
            if debug["teacher"] != "":
                new_teacher = debug["teacher"]
            if debug["uid"] != "":
                new_uid = debug["uid"]

            return Event(new_start, new_end, new_subject, new_group, new_location, new_teacher, new_isINGE, new_isMIAGE,new_uid)
    return None

def get_hide(uid,arguement) -> bool:
    hide :dict[str:dict[str:str]] = arguement['hidden_event']
    return uid in hide

def nouveau_parseur(start:datetime, end:datetime, sum:str, loc:str, desc:str, uid:str) -> Event:
    # Descsplit contient les informations correspondant à la description de l'événement, séparé par lignes.
    # Ex : ['', '', 'Gr TPC', 'Con. Ana. Algo', 'Con. Ana. Algo', 'L3 INFO - INGENIERIE', 'L3 INFORMAT-UPEX MINERVE', 'LIEDLOFF', '(Exporté le : 27/07/2024 20:20)', '\n\n']
    descsplit = desc.split("\\n")

    # Si la Matière (4eme element) est une abbrev connu dans la subjects_table, remplacer par le nom complet.
    # subject_split = descsplit[3].split(" GR")
    # subject = subjects_table[subject_split[0]] if subject_split[0] in subjects_table.keys() else descsplit[3]
    subject_split = sum.split(" - ")
    group_brut : str = ""
    if len(subject_split) == 3:
        group_brut = subject_split[2].removeprefix("GR").replace(" ","")
    else:
        group_brut = subject_split[1].replace(" ","")

    subject = subjects_table[subject_split[0]] if subject_split[0] in subjects_table.keys() else sum
    if "L3 INFORMATIQUE" in subject:
        subject = descsplit[2]

    # Nettoie le nom du professeur (antépénultième élément), et inclus un fallback si le nom n'est pas renseigné.
    teacher = descsplit[-3].replace("\n", "").removeprefix(" ") if descsplit[-3] != "L3 INFORMAT-UPEX MINERVE" else "Enseignant ?"
    location = loc if not loc == "" else "Salle ?"

    isMIAGE = False
    isINGE  = False
    group   = Group.CM

    if (subject == "Anglais"):
        group, isINGE, isMIAGE = nouveau_parseur_anglais(group_brut)
    elif(subject in ["Framework Web 2", "Programmation N-Tiers", "Réseaux 2"]):
        group, isINGE, isMIAGE = nouveau_parseur_commun(subject, group_brut, sum)
    elif(subject in ["Programmation Logique pour l'IA", "Fondements du calcul", "Techniques de comm", "Recherche en info"]):
        isINGE = True
        isMIAGE = False
        group = get_Inge(group_brut)
    elif(subject in ["Algorithmique avancée", "Droit", "Environnement Économique", "Projet Web"]):
        isINGE = False
        isMIAGE = True
        group = get_Miage(group_brut)
    else:
        try:
            raise ValueError("Cours inconnue dans nouveau_parseur")
        except BaseException as exception:
            send_error_non_async(exception)

    if "CC" in sum:
        teacher = "équipe enseignante"

    # Crée un nouvel Objet Event à partir des infos calculées.
    return Event(start, end, subject, group, location, teacher, isINGE, isMIAGE, uid)

def nouveau_parseur_anglais(group_brut : str):
    isINGE = False
    isMIAGE = False
    if group_brut[3:] =="Info":
        # ex : Anglais - TD 1 Info
        isINGE = True
        group = get_TDA_Inge(group_brut[2:3])
    else:
        # ex : Anglais - TD3
        isMIAGE = True
        group = get_TDA_Miage(group_brut[2:3])

    return group, isINGE, isMIAGE


def nouveau_parseur_commun(subject : str, group_brut : str, sum : str):
    if subject in ["Framework Web 2", "Programmation N-Tiers"]:
        return nouveau_parseur_FW_PNT(group_brut[:3], sum)
    elif subject == "Réseaux 2":
        return nouveau_parseur_REZO(group_brut[:3], sum)
    else:
        try:
            raise ValueError("Cours inconnue dans nouveau_parseur_commun")
        except BaseException as exception:
            send_error_non_async(exception)

def nouveau_parseur_FW_PNT(group_brut : str, sum : str):
    isINGE = False
    isMIAGE = False
    if ("CM" in sum or "CC" in sum):
        group = Group.CM
        isINGE = True
        isMIAGE = True
    elif ("INGE" in sum):
        group = get_Inge(group_brut[:3])
        isINGE = True
    else:
        group = get_Miage(group_brut[:3])
        isMIAGE = True
    return group, isINGE, isMIAGE




def nouveau_parseur_REZO(group_brut : str, sum : str):
    isINGE = False
    isMIAGE = False
    group = Group.UKNW
    if ("CM" in sum or "CC" in sum):
        group = Group.CM
        isINGE = True
        isMIAGE = True
    else:
        if ("Info" in sum):
            isINGE = True
            group = get_Inge(group_brut[:3])
        else:
            isMIAGE = True
            group = get_Miage(group_brut[:3])

    return group, isINGE, isMIAGE


def get_Inge(group_brut : str) -> Group:
    group = Group.UKNW
    match group_brut:
        case "CM":
            group = Group.CM
        case "TD1":
            group = Group.TD1I
        case "TD2":
            group = Group.TD2I
        case "TPA":
            group = Group.TPAI
        case "TPB":
            group = Group.TPBI
        case "TPC":
            group = Group.TPCI
        case "TPD":
            group = Group.TPDI
        case "TP1":
            group = Group.TPAI
        case "TP2":
            group = Group.TPBI
        case "TP3":
            group = Group.TPCI
        case "TP4":
            group = Group.TPDI
        case _:
            # Ce cas ne devrait pas arriver et devrait être fix rapidement.
            group = Group.UKNW
            try:
                raise ValueError("Groupe inconnue cours ingé dans get_Inge")
            except BaseException as exception:
                send_error_non_async(exception)
    return group


def get_Miage(group_brut : str) -> Group:
    group = Group.UKNW
    match group_brut:
        case "CM":
            group = Group.CM
        case "TD1":
            group = Group.TD1M
        case "TD2":
            group = Group.TD2M
        case "TP1":
            group = Group.TP1M
        case "TP2":
            group = Group.TP2M
        case "TP3":
            group = Group.TP3M
        case "TPA":
            group = Group.TP1M
        case "TPB":
            group = Group.TP2M
        case "TPC":
            group = Group.TP3M
        case _:
            # Ce cas ne devrait pas arriver et devrait être fix rapidement.
            group = Group.UKNW
            try:
                raise ValueError("Groupe inconnue cours Miage dans get_Miage")
            except BaseException as exception:
                send_error_non_async(exception)
    return group



def get_TDA_Inge(group_brut : str) -> Group:
    match group_brut:
        case "1":
            group = Group.TDA1I
        case "2":
            group = Group.TDA2I
        case "3":
            group = Group.TDA3I
        case "4":
            group = Group.TDA4I
        case _:
            # Ce cas ne devrait pas arriver et devrait être fix rapidement.
            group = Group.UKNW
            try:
                raise ValueError("Groupe inconnue anglais ingé dans get_event_from_data")
            except BaseException as exception:
                send_error_non_async(exception)
    return group



def get_TDA_Miage(group_brut : str) -> Group:
    match group_brut:
        case "1":
            group = Group.TDA1M
        case "2":
            group = Group.TDA2M
        case "3":
            group = Group.TDA3M
        case _:
            # Ce cas ne devrait pas arriver et devrait être fix rapidement.
            group = Group.UKNW
            try:
                raise ValueError("Groupe inconnue anglais Miage dans get_event_from_data")
            except BaseException as exception:
                send_error_non_async(exception)
    return group