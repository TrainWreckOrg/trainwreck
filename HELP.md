## TrainWreck
TrainWreck.py est un bot discord Open Source codé en Python par @Dany & @Nathan et hébérgé par @Vincent dont l'objectif est de faciliter l'accés des Etudiants de l'Université d'Orléans a leur Emploi du Temps

## Fonctions & Services
- Avertissement de changements : Si un changement a lieux dans votre EDT pour les 14 jours a venir, vous recevrez un ping dans #annonce-bot
- Envoi Automatique d'EDT : Si vous vous abonnez à ce service via `/subscribe`, Avec l'abonnement Quotidien, vous recevrez votre EDT du jour tout les matins (du Lundi au Vendredi) a 6h, et avec l'abonnement Hebdomadaire votre EDT de la semaine le Lundi matin (⚠ : Le calendrier n'est pas mis a jour dynamiquement, mais les changements dans une journée n'arrivent en pratique jamais)
- Utilisation en DM : si vous ne souhaitez pas utiliser les commandes dans le serveur, vous pouvez les utiliser dans vos messages privés avec le bot (cliquez sur le bot, puis "Envoyer un message") ⚠ vous devez quand même selectionner vos rôles dans le serveur

## Commandes :
- Clé de lecture :
    - `<>` : arguments obligatoires.
        - `<date>` : sont a donner au format `DD-MM-YYYY` (ou `D-M-YYYY`).
    - `[]` : arguments facultatifs.

- `/get_day <date> [personne]` : Envoie votre EDT pour un jour donné. Si une personne est donnée, donne l'EDT de cette personne
- `/get_week <date> [personne]` : Envoie votre EDT pour la semaine durant laquelle est la date, si une personne est donnée, donne l'EDT de cette personne
- `/today` : Envoie votre EDT du jour
- `/tomorrow` : Envoie votre EDT du lendemain
- `/week` : Envoie votre EDT de la semaine

- `/ics <date début> <date fin>` : Envoie un fichier ICS (iCalendar) des événements entre les deux dates, importable dans la plupart des applications de calendrier (⚠ : Le calendrier n'est pas mis a jour dynamiquement)

- `/info [personne]` : Envoie des infos sur vos groupes, et filière. Si une personne est donnée, donne les informations de cette personne

- `/subscribe <service>` : Vous permet de vous abonner à l'envoi de l'EDT dans vos DM de maniere Quotidienne (`DAILY`) ou Hebdomadaire (`WEEKLY`). (⚠ : Les envoi se font à 6h du matin, mais uniquement en semaine)
- `/unsubscribe <service>` : Vous permet de vous desabonner à l'envoi de l'EDT dans vos DM (voir `/subscribe` pour plus de détails)
- `/check_subscription` : Vous permet de consulter à quels service d'envoi d'EDT vous êtes inscrit (voir `/subscribe` pour plus de détails)