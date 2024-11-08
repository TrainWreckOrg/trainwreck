## EDT Bot
EDT Bot est un bot discord Open Source codé en Python par @Dany & @Nathan et hébergé par @Vincent dont l'objectif est de faciliter l'accès des Étudiants de l'Université d'Orléans a leur Emploi du Temps.

## Avertissement
EDT Bot n'est pas exempt de potentiel bug, si jamais vous rencontrez un problème, n'hésitez pas à le signaler aux @Admin.

## Fonctions & Services
- Avertissement de changements + Détecteur de chevauchement de cours : Si un changement à lieux dans votre EDT pour les 14 jours à venir, vous recevrez un ping dans #changement-edt (On demande l'EDT à 5h55, 7h, 8h, 10h, 12h, 14h, 16h, 18h, 20h).
- Envoi Automatique d'EDT : Si vous vous abonnez à ce service via `/subscribe`,
  - Avec l'abonnement Quotidien, vous recevrez votre EDT du jour tous les matins (du Lundi au Vendredi) à 6h avec la possibilité d'avoir le fichier ics correspondant en option.
  - Avec l'abonnement Hebdomadaire votre EDT de la semaine le Lundi matin à 6h avec la possibilité d'avoir le fichier ics correspondant en option (⚠ : Le calendrier n'est pas mis à jour dynamiquement, mais les changements dans une journée n'arrivent en pratique jamais).
- Utilisation en DM : si vous ne souhaitez pas utiliser les commandes dans le serveur, vous pouvez les utiliser dans vos messages privés avec le bot (cliquez sur le bot, puis "Envoyer un message") ⚠ vous devez quand même sélectionner vos rôles dans le serveur.

## Application :
Pour utiliser les applications, il faut, sur PC, faire un clic droit sur un membre, ensuite dans "Applications" et sur Mobile, appuyer sur l'avatar de la personne, ensuite dans le menu "Application".

- `day_user` : Permet d'obtenir l'EDT d'une journée de la personne en fonction d'une date demandé par un modal.
- `week_user` : Permet d'obtenir l'EDT d'une semaine de la personne en fonction d'une date demandé par un modal.
- `today_user` : Permet d'obtenir l'EDT du jour de la personne.
- `tomorrow_user` : Permet d'obtenir l'EDT du lendemain de la personne.
- `this_week_user` : Permet d'obtenir l'EDT de la semaine de la personne.

## Commandes :
- Clé de lecture :
    - `<>` : arguments obligatoires.
        - `<date>` : sont à donner au format `JJ-MM-AAAA` (ou `J-M-AAAA`).
    - `[]` : arguments facultatifs.

- `/get_day <date> [personne]` : Envoie votre EDT pour un jour donné. Si une personne est donnée, donne l'EDT de cette personne
- `/get_week <date> [personne]` : Envoie votre EDT pour la semaine durant laquelle est la date, si une personne est donnée, donne l'EDT de cette personne
- `/today` : Envoie votre EDT du jour
- `/tomorrow` : Envoie votre EDT du lendemain
- `/week` : Envoie votre EDT de la semaine
- `/next_week` : Envoie votre EDT de la semaine prochaine
- `/ics <date début> <date fin>` : Envoie un fichier ICS (iCalendar) des événements entre les deux dates, importable dans la plupart des applications de calendrier (⚠ : Le calendrier n'est pas mis à jour dynamiquement)
- `/subscribe [service] [ics]` : Vous permet de vous abonner à l'envoi de l'EDT dans vos DM de manière Quotidienne (`DAILY`) ou Hebdomadaire (`WEEKLY`) avec la possibilité d'avoir le fichier ics correspondant en option soit `DAILY`, `WEEKLY`, ou les deux. (⚠ : Les envois se font à 6h du matin, mais uniquement en semaine)
- `/unsubscribe [service] [ics]` : Vous permet de vous désabonner à l'envoi de l'EDT dans vos DM (voir `/subscribe` pour plus de détails)
- `/check_subscription` : Vous permet de consulter à quels services d'envoi d'EDT, vous êtes inscrit (voir `/subscribe` pour plus de détails)
- `/exam [personne]` : Envoie la liste de vos examens 