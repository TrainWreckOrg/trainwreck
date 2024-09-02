# Time review

Pour le démarrage, 
- Création du client, chargement des extension : 0:00:00.138524
- on_ready : 0:00:01.491459
    - Démarrage des Task : 0:00:00.357667
    - update_calendar() : 0:00:00.931276
        - Total : 0:00:00.918026
        - Génération des deux calendrier : 0:00:00.727576
            - Sans DL : 0:00:00.045572
            - Avec DL : 0:00:00.714655
                - DL : 0:00:00.695629
        - Recherche des changement : 0:00:00.003502




- `/get_day 10-10-2024` : l'envoie du message prend 0:00:00.452770 sur 0:00:00.454770
- `/get_day 10-10-2024 @EDT Bot`,  `/today`, `/tomorrow`, `day_user`, `today_user`, `tomorrow_user` appelle la meme fonction avec different paramètre, juste pour `day_user` l'envoi et le retour du modal


- `/get_week 10-10-2024` : l'envoie prend 0:00:00.404633 sur 0:00:00.407639
- `/get_week 10-10-2024 @EDT Bot`, `/week`, `week_user`, `this_week_user` appelle la meme fonction avec different paramètre, juste pour `week_user` l'envoi et le retour du modal


- `/ics 1-9-2024 1-7-2025` : same 0:00:00.608902 sur 0:00:00.615936

- `/help` : 0:00:00.399590 sur 0:00:00.400090
- `/exam` : 0:00:00.460290 sur 0:00:00.460290 (aucun exam dans la BD)

Pour cette partie, le "sans envoi" comprend une vérification de possession de rôle et ajout/suppression de role donc tjr l'api discord lente


- `/subscribe Daily` : total 0:00:00.836308 sans envoi 0:00:00.302203
- `/subscribe Weekly` : total 0:00:00.580131 sans envoi 0:00:00.217919
- `/subscribe Both` : total 0:00:00.960981 sans envoi 0:00:00.502945
- `/subscribe Daily_ics` : total 0:00:00.846208 sans envoi 0:00:00.479949
- `/subscribe Weekly_ics` : total 0:00:00.917551 sans envoi 0:00:00.507569
- `/subscribe Both_ics` : total 0:00:01.321294 sans envoi 0:00:00.848461
- `/unsubscribe Daily` : total 0:00:00.580758 sans envoi 0:00:00.204222
- `/unsubscribe Weekly` : total 0:00:00.746377 sans envoi 0:00:00.275580
- `/unsubscribe Both` sans ics : total 0:00:02.040971 sans envoi 0:00:00.457067
- `/unsubscribe Both` avec ics : total 0:00:01.256358 sans envoi 0:00:00.816624
- `/unsubscribe Daily_ics` : total 0:00:00.771794 sans envoi 0:00:00.228744
- `/unsubscribe Weekly_ics` : total 0:00:00.705378 sans envoi 0:00:00.215295
- `/unsubscribe Both_ics` : total 0:00:00.880962 sans envoi 0:00:00.414098
- `/check_subscription` : 0:00:00.427887 sur 0:00:00.428388 (l'envoie comprend l’interrogation de la BD vue que c'est dans la meme ligne)






Pour les boutons globalement c'est la meme chose que les commandes

on_member_update : 0:00:00.000500


envoie automatique : 

daily_morning_update week 0:00:01.343478
daily_morning_update day 0:00:01.013144
daily_morning_update total 0:00:02.614343


send_daily_update sans ics : 0:00:00.436330 sur 0:00:00.436330
send_daily_update avec ics : 0:00:00.576814 sur 0:00:00.576814


send_weekly_update sans ics : 0:00:00.771357 sur 0:00:00.771357
send_weekly_update avec ics : 0:00:00.572121 sur 0:00:00.572121

Fait avec 2 personne dans la BD un avec ics et l'autre sans



# Conclusion : 

Pour le démarrage c'est le dl des ics qui prend le plus de temps

Au niveau des commandes sauf subscribe, unsubscribe : c'est l'envoie des message qui prend le plus de temps, donc on ne peut rien y faire

Pour subscribe, unsubscribe : l'envoie prendre du temps mais j'ai pas calculer le temps de  vérification de possession de rôle et ajout/suppression de role qui doit être la principale source de temps

Pour l'envoi automatique, le meme problème que les commande c'est l'envoie qui prend tout le temps, le reste de la fonction est instantanée

(info : les temps d'envoie sont aléatoire des fois c'est rapide et d'autre lent)