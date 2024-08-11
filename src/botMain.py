from interactions import Client, Intents
from dotenv import load_dotenv
import sentry_sdk
import os


# Charge le fichier env
load_dotenv("cle.env")
load_dotenv("keys.env")

# Init https://sentry.io/
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    # Set traces_sample_rate to 1.0 to capture 100% of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100% of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)


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

bot.start()
