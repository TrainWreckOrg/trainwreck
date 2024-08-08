# Time review

Pour le démarrage, c'est le dl des ics qui prend le plus de temps (0:00:00.692964 sur 0:00:01.082672)

(info : les temps d'envoie sont aléatoire des fois c'est rapide et d'autre lent)

- `/get_day 10-10-2024` : l'envoie du message prend 0:00:00.418701 sur 0:00:00.420710, le filtage des events est instantanté (oui je blague pas)
- `/get_day 10-10-2024 @EDT Bot` : same 0:00:00.462861 sur 0:00:00.465361
- `/today` : same 0:00:00.486170 sur 0:00:00.488173
- `/tomorrow` : same 0:00:00.546130 sur 0:00:00.547630


- `/get_week 10-10-2024` : l'envoie prend 0:00:00.389264 sur 0:00:00.391764
- `/get_week 10-10-2024 @EDT Bot` : same 0:00:00.509967 sur 0:00:00.512966
- `/week` : same 0:00:00.619714 sur 0:00:00.621713


- `/ics 1-9-2024 1-7-2025` : same 0:00:00.603995 sur 0:00:00.611004

- `/info` : 0:00:00.600034 sur 0:00:00.600034, oui notre code est instantané
- `/info @EDT Bot` : same 0:00:00.477238 sur 0:00:00.477238



- `/subscribe Daily` : 0:00:00.566725 sur 0:00:00.567225
- `/subscribe Weekly` : 0:00:00.543406 sur 0:00:00.543910
- `/subscribe Both` : 0:00:00.567656 sur 0:00:00.568660
- `/unsubscribe Daily` : 0:00:00.410642 sur 0:00:00.411143
- `/unsubscribe Weekly` : 0:00:00.494638 sur 0:00:00.495643
- `/unsubscribe Both` : 0:00:00.655501 sur 0:00:00.656505
- `/check_subscription` : 0:00:00.611170 sur 0:00:00.611170
- `/userscan` : 0:00:00.572916 sur 0:00:00.573918 (sans avoir nuke la bd ni changement)
- `/userscan` : 0:00:00.394545 sur 0:00:00.395548 (db nuke)
- `/help` : 0:00:00.390152 sur 0:00:00.390654
- `/test` : 0:00:00.701985 sur 0:00:00.701985
- `/exam` : 0:00:00.496289 sur 0:00:00.496289


Pour les ContextMenu globalement c'est la meme chose que les commandes


Pour les boutons globalement c'est la meme chose que les commandes

on_member_update : 0:00:00.000500


envoie automatique : 

daily_morning_update : 0:00:01.038891 dont 0:00:00.664610 d'envoie pour week et 0:00:00.372282 d'envoie pour day

send_daily_update : 0:00:00.453641 sur 0:00:00.454641
send_weekly_update : 0:00:00.736888 sur 0:00:00.737887