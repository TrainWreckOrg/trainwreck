from interactions import Client, Intents
from dotenv import load_dotenv
import os
import re

print("avant : ", os.getcwd())

pattern = r"^(.*\\trainwreck)\\.*$"
match = re.match(pattern, os.getcwd())
if match:
    path = match.group(1)
    os.chdir(path)

print("après : ", os.getcwd())


load_dotenv("cle.env")
token_bot=os.getenv("TOKEN_BOT_DISCORD")
# Si une commande ne veut pas partir / est dupliqué dans la liste des commandes sur discord ajouter
# `delete_unused_application_cmds=True` pour supprimer les commandes en cache

bot = Client(token=token_bot, intents=Intents.ALL, sync_interactions=True)   # TODO : enlevé ALL

bot.load_extension("MyListen")

bot.start()