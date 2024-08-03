from interactions import Client, Intents
from dotenv import load_dotenv
import os


load_dotenv("cle.env")
token_bot=os.getenv("TOKEN_BOT_DISCORD")
# Si une commande ne veut pas partir / est dupliqué dans la liste des commandes sur discord ajouter
# `delete_unused_application_cmds=True` pour supprimer les commandes en cache

bot = Client(token=token_bot, intents=Intents.ALL, sync_interactions=True)   # TODO : enlevé ALL

bot.load_extension("MyListen", package="Bot")

bot.start()