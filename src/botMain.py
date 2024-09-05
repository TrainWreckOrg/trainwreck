import datetime

from interactions import Client, Intents, SlashContext, ModalContext, ContextMenuContext, ComponentContext
from dotenv import load_dotenv
import sentry_sdk
import os
from Tool import get_tool


# Charge le fichier env
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
bot = Client(token=token_bot, intents=Intents.DEFAULT | Intents.GUILD_MEMBERS | Intents.GUILD_PRESENCES, send_command_tracebacks=False)

# Extension pour gérer les erreurs avec https://sentry.io/
bot.load_extension('interactions.ext.sentry', dsn=str(os.getenv("SENTRY_DSN")))
bot.load_extension("MyListen")
bot.load_extension("MyContextMenus")
bot.load_extension("MySlashCommand")
bot.load_extension("Onboard")


async def log(ctx: SlashContext | ModalContext | ContextMenuContext | ComponentContext, **kwargs):
    """Fonction qui permet de logger toutes les actions."""
    get_tool(bot)
    if isinstance(ctx, ComponentContext):
        ctx_bt : ComponentContext = ctx
        await bot.get_channel(os.getenv("ERROR_CHANNEL_ID")).send(
            f"{ctx.author.display_name} ({ctx.author.id}) à utilise {ctx_bt.custom_id} {kwargs}, le {datetime.datetime.now()}")
    elif isinstance(ctx, ContextMenuContext):
        ctx_menu : ContextMenuContext = ctx
        await bot.get_channel(os.getenv("ERROR_CHANNEL_ID")).send(
            f"{ctx_menu.author.display_name} ({ctx_menu.author.id}) à utilise {ctx_menu.command.name} sur {ctx_menu.target} ({ctx_menu.target_id}) {kwargs}, le {datetime.datetime.now()}")
    else:
        await bot.get_channel(os.getenv("ERROR_CHANNEL_ID")).send(f"{ctx.author.display_name} ({ctx.author.id}) à utilise {ctx.command.name} {kwargs}, le {datetime.datetime.now()}")

# Définition d'une action avant une action
bot.pre_run_callback = log

# Démarrage du bot
bot.start()
