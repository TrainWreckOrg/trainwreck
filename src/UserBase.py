import pickle

from Enums import Group, Filiere, Subscription, Annee


class DBUser:
    """Classe représentant un utilisateur dans la BD."""
    def __init__(self, id: int, annee : Annee, filiere: Filiere, groups: list[Group]) -> None:
        self.id         = id
        self.annee      = annee
        self.filiere    = filiere
        self.groups     = groups


    def __hash__(self) -> int:
        return self.id

    def __str__(self) -> str:
        return f"<{self.id}, {self.groups}, {self.filiere.value}>"


class UserBase:
    """Classe représentant la BD."""
    def __init__(self, users: dict[int:DBUser], daily_subscribed_users: set, weekly_subscribed_users: set, daily_subscribed_users_ics: set, weekly_subscribed_users_ics: set) -> None:
        self.users                      = users
        self.daily_subscribed_users     = daily_subscribed_users
        self.weekly_subscribed_users    = weekly_subscribed_users
        self.daily_subscribed_users_ics     = daily_subscribed_users_ics
        self.weekly_subscribed_users_ics    = weekly_subscribed_users_ics


    def __str__(self) -> str:
        return f"<users:{[str(x) for x in self.users.values()]}, daily:{self.daily_subscribed_users}, weekly:{self.weekly_subscribed_users}>"

    def has_user(self, id: int) -> bool:
        """Vérifie si l'utilisateur est déjà enregistré."""
        return id in self.users.keys()

    def is_user_subscribed(self, id: int, subscription: Subscription) -> bool:
        """Permet de savoir si un utilisateur est abonée à une certaine subscription."""
        if self.has_user(id):
            is_daily = id in self.daily_subscribed_users
            is_weekly = id in self.weekly_subscribed_users
            match subscription:
                case Subscription.DAILY:
                    return is_daily
                case Subscription.WEEKLY:
                    return is_weekly
                case Subscription.BOTH:
                    return is_daily and is_weekly
                case Subscription.NONE:
                    return (not is_daily) and (not is_weekly)

    def is_user_subscribed_ics(self, id: int, subscription: Subscription) -> bool:
        """Permet de savoir si un utilisateur est abonée aux ics d'une certaine subscription."""
        if self.has_user(id):
            is_daily = id in self.daily_subscribed_users_ics
            is_weekly = id in self.weekly_subscribed_users_ics
            match subscription:
                case Subscription.DAILY_ICS:
                    return is_daily
                case Subscription.WEEKLY_ICS:
                    return is_weekly
                case Subscription.BOTH_ICS:
                    return is_daily and is_weekly
                case Subscription.NONE_ICS:
                    return (not is_daily) and (not is_weekly)

    def add_user(self, id: int, groups: list[Group], filiere: Filiere, annee : Annee = Annee.UKNW) -> None:
        """Enregistre l'utilisateur s'il n'est pas déjà enregistré, sinon ne fait rien."""
        if not self.has_user(id):
            self.users[id] = DBUser(id, annee, filiere, groups)
            dump_user_base(self)

    def update_user(self, id: int ,new_groups: list[Group], new_filiere: Filiere = Filiere.UKNW, new_annee: Annee = Annee.UKNW) -> None:
        """Remplace les groupes de l'utilisateur par une ceux de `new_groups`."""
        if self.has_user(id):
            self.users[id].annee = new_annee
            self.users[id].filiere = new_filiere
            self.users[id].groups = new_groups
            dump_user_base(self)

    def user_subscribe(self, id: int, subscription: Subscription) -> None:
        """Abonne un utilisateur à une ou plusieurs des listes."""
        if self.has_user(id):
            match subscription:
                case Subscription.DAILY:
                    self.daily_subscribed_users.add(id)
                case Subscription.WEEKLY:
                    self.weekly_subscribed_users.add(id)
                case Subscription.BOTH:
                    self.daily_subscribed_users.add(id)
                    self.weekly_subscribed_users.add(id)
            dump_user_base(self)

    def user_unsubscribe(self, id: int, subscription: Subscription) -> None:
        """Désabonne un utilisateur à une ou plusieurs des listes
        (si l'utilisateur est abonnée à l'ICS, il est aussi désactivée)."""
        if self.has_user(id):
            match subscription:
                case Subscription.DAILY if self.is_user_subscribed(id, subscription):
                    self.daily_subscribed_users.remove(id)
                    self.user_unsubscribe_ics(id, Subscription.DAILY_ICS)
                case Subscription.WEEKLY if self.is_user_subscribed(id, subscription):
                    self.weekly_subscribed_users.remove(id)
                    self.user_unsubscribe_ics(id, Subscription.WEEKLY_ICS)
                case Subscription.BOTH:
                    self.user_unsubscribe_ics(id, Subscription.BOTH_ICS)
                    if self.is_user_subscribed(id, Subscription.DAILY):
                        self.daily_subscribed_users.remove(id)
                    if self.is_user_subscribed(id, Subscription.WEEKLY):
                        self.weekly_subscribed_users.remove(id)
            dump_user_base(self)

    def user_subscribe_ics(self, id: int, subscription: Subscription) -> None:
        """Abonne un utilisateur à une ou plusieurs des listes d'ICS
        (si l'utilisateur n'est pas abonnée à l'envoyer classique, il est aussi activée)."""
        if self.has_user(id):
            match subscription:
                case Subscription.DAILY_ICS:
                    self.user_subscribe(id, Subscription.DAILY)
                    self.daily_subscribed_users_ics.add(id)
                case Subscription.WEEKLY_ICS:
                    self.user_subscribe(id, Subscription.WEEKLY)
                    self.weekly_subscribed_users_ics.add(id)
                case Subscription.BOTH_ICS:
                    self.user_subscribe(id, Subscription.BOTH)
                    self.daily_subscribed_users_ics.add(id)
                    self.weekly_subscribed_users_ics.add(id)
            dump_user_base(self)

    def user_unsubscribe_ics(self, id: int, subscription: Subscription) -> None:
        """Désabonne un utilisateur à une ou plusieurs des listes d'ICS."""
        if self.has_user(id):
            match subscription:
                case Subscription.DAILY_ICS if self.is_user_subscribed_ics(id, subscription):
                    self.daily_subscribed_users_ics.remove(id)
                case Subscription.WEEKLY_ICS if self.is_user_subscribed_ics(id, subscription):
                    self.weekly_subscribed_users_ics.remove(id)
                case Subscription.BOTH_ICS:
                    if self.is_user_subscribed_ics(id, Subscription.DAILY_ICS):
                        self.daily_subscribed_users_ics.remove(id)
                    if self.is_user_subscribed_ics(id, Subscription.WEEKLY_ICS):
                        self.weekly_subscribed_users_ics.remove(id)
            dump_user_base(self)

    def get_user(self, id: int) -> DBUser | None:
        """Retourne un Objet utilisateur s'il est présent dans la base de donnée, None sinon."""
        if self.has_user(id):
            return self.users[id]
        else:
            return None


def load_user_base():
    """Récupère la base d'utilisateur depuis le fichier UserBase.pkl."""
    with open("data/UserBase.pkl", "rb") as f:
        return pickle.load(f)


def dump_user_base(user_base: UserBase):
    """Charge la base d'utilisateur dans le fichier UserBase.pkl."""
    with open("data/UserBase.pkl", "wb") as f:
        pickle.dump(user_base, f, pickle.HIGHEST_PROTOCOL)


def get_user_base() -> UserBase:
    """Permet d'obtenir la BD."""
    global user_base
    user_base = load_user_base()
    return user_base

def nuke():
    """Permet d'effacer la BD."""
    global user_base
    user_base = UserBase({}, set(), set(), set(), set())
    dump_user_base(user_base)
