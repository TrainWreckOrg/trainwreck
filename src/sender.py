import sentry_sdk
from interactions import Client, Intents, SlashContext, ModalContext, ContextMenuContext, ComponentContext, \
    AutocompleteContext, Embed, GuildText
import os


bot = None
tool = None

def set_bot(bot_new : Client):
    global bot
    bot = bot_new

def get_bot() -> Client | None:
    global bot
    return bot

def set_tool(tool_new):
    global tool
    tool = tool_new

def get_error_log_chan() -> GuildText:
    return get_bot().get_channel(os.getenv("ERROR_CHANNEL_ID"))


async def send(context: SlashContext | ModalContext | ContextMenuContext | ComponentContext | AutocompleteContext | GuildText,
         content : str = "", embeds: list[Embed] = [], components = [], files: list[str] = [], ephemeral :bool = False, auto_ephemeral:bool=False, nb_try : int = 5):
    # S'il y a plus de 10 embeds à envoyer
    if len(embeds) > 10:
        cut = embeds
        for i in range(0,len(embeds),10):
            await send(context,embeds=cut[:10], components=components, ephemeral=ephemeral)
            cut = cut[10:]
        return

    try:
        if auto_ephemeral:
            ephemeral = False
            if "Member" in str(type(context.author)):
                ephemeral = not context.author.has_role(tool.get_perma_role(get_bot().user.guilds[0]))  # Permanent si la personne à le rôle
        await context.send(content=content, embeds=embeds, components=components, files=files,ephemeral=ephemeral)
    except BaseException as exception:
        if nb_try == 0:
            await send_error(exception)
        await send(context,content,embeds, components, files, ephemeral, auto_ephemeral, nb_try-1)


async def send_error(exception: BaseException) -> None:
    """Permet de faire la gestion des erreurs pour l'ensemble du bot, envoie un message aux admins et prévient l'utilisateur de l'erreur."""
    global tool
    guild = get_bot().user.guilds[0]
    print(exception)
    sentry_sdk.capture_exception(exception)
    await send(get_error_log_chan(),
        f"{tool.get_admin_mention(guild)} {exception}")


def send_error_non_async(exception: BaseException):
    print(exception)
    sentry_sdk.capture_exception(exception)
