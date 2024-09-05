# 🚉 EDT Bot

EDT Bot est un bot discord Open Source codé en Python par @Dany & @Kaawan et hébérgé par @VincentGonnet dont l'objectif est de faciliter l'accés des Etudiants de l'Université d'Orléans a leur Emploi du Temps

Modules utilisés (voir requirements.txt) (il y a déjà l'environnement virtuel python dans le dossier env) :
- `Pytz` : Gestion des Time Zones
- `Interactions.py` : Interaction avec l'API Discord (https://interactions-py.github.io/interactions.py/) (`pip install discord-py-interactions --upgrade`)
- `sentry_sdk` : Gestion des erreurs à distance
- `dotenv` : Permet d'obtenir des éléments stockés dans le fichier keys.env
- `pickle` : Pour la base de données.

Pour une éventuelle adaptation, il faudrait :
- Changer les Enums : subjects_table, Filiere, Group, RoleEnum
- Changer les données dans le fichier env
- Modifier Calendar.update_events selon le nombre de filière / d'ics
- Refaire un Calendar.parse_calendar en fonction des ics fournis
- Refaire un Event.get_event_from_data en fonction des ics fournis
- Event à adapter en fonction du nombre de filière
- Modifier FiliereFilter dans Filter
- Refaire entièrement le Fichier Onboard ou attribuer les rôles avec reaction role par exemple
- Dans Tool refaire / adapter
  - get_filiere_as_filiere
  - get_filiere
  - ping_liste
- Modifier DBUser en fonction des besoins de filière
- Corriger les éventuels problèmes crée

Roles discord nécessaire dans cette version :
- Admin
- Perma
- Ingé
- TD 1 Inge
- TD 2 Inge
- TP A Inge
- TP B Inge
- TP C Inge
- TP D Inge
- TD 1 Inge Anglais
- TD 2 Inge Anglais
- TD 3 Inge Anglais
- TD 4 Inge Anglais
- Miage
- TD 1 Miage
- TD 2 Miage
- TP 1 Miage
- TP 2 Miage
- TP 3 Miage
- TD 1 Miage Anglais
- TD 2 Miage Anglais
- TD 3 Miage Anglais
- onboarded
- DAILY
- WEEKLY
- DAILY_ICS
- WEEKLY_ICS


Pour le fichier env, il faut :
- Le token du bot discord `TOKEN_BOT_DISCORD`
- Le token sentry pour recevoir les erreurs `SENTRY_DSN`
- En fonction du nombre de filières
- Le lien vers le fichier ics `INGEICS`
- Le lien vers le fichier ics `MIAGEICS`
- L'identifiant d'un salon discord où le bot pourra afficher certaine erreur (pas toute) et les logs `ERROR_CHANNEL_ID`
- L'identifiant d'un salon discord où le bot pourra envoyer des embeds pour prévenir des changements d'emploi du temps `PING_CHANGE_CHANNEL_ID`
- L'identifiant du serveur discord `SERVEUR_ID`