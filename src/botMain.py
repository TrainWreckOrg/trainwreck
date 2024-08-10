from interactions import Client, Intents
from dotenv import load_dotenv
import os

"""
import sentry_sdk as sentry

sentry.init(
    dsn="https://8d27543d8288c4339447b3017fab34c9@o4507712305233920.ingest.de.sentry.io/4507747372957776",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)
"""
# Charge le fichier env
load_dotenv("cle.env")
load_dotenv("keys.env")


token_bot = os.getenv("TOKEN_BOT_DISCORD")

# Si une commande ne veut pas partir / est dupliqué dans la liste des commandes sur discord ajouter
# `delete_unused_application_cmds=True` pour supprimer les commandes en cache
bot = Client(token=token_bot, intents=Intents.DEFAULT | Intents.GUILD_MEMBERS, send_command_tracebacks=False)

# Extension pour gérer les erreurs avec https://sentry.io/
bot.load_extension('interactions.ext.sentry', dsn=str(os.getenv("SENTRY_DSN")))
bot.load_extension("MyListen")
bot.load_extension("MyContextMenus")
bot.load_extension("MySlashCommand")
bot.load_extension("Onboard")

#sentry.capture_message("Ceci est un message d'information")

bot.start()
