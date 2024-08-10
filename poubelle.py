def get_date(jour : int, mois : int, annee : int) -> date:
    if jour is None:
        jour = date.today().day
    if mois is None:
        mois = date.today().month
    if annee is None:
        annee_courant = date(day=jour, month=mois, year=date.today().year)
        annee_suivante = date(day=jour, month=mois, year=date.today().year + 1)

        delta_courant = abs(date.today() - annee_courant)
        delta_suivante = abs(date.today() - annee_suivante)

        if delta_courant < delta_suivante:
            annee = date.today().year
        else:
            annee = date.today().year + 1

    return date(year=annee, month=mois, day=jour)



async def get_day_bt(ctx, modifier: bool, jour : int, mois : int, annee : int, personne: User):
    """Fonction qui permet d'obtenir l'EDT d'une journée spécifique"""
    try:
        date_formater = get_date(jour,mois,annee)
        events = filter_events(get_calendar().get_events(),
                               [TimeFilter(date_formater, Timing.DURING), get_filiere(ctx.author),
                                get_groupes(ctx.author)])
        embeds = get_embeds(events, date_formater)

        precedent = Button(
            style=ButtonStyle.PRIMARY,
            custom_id="day-" + (date_formater - timedelta(days=1)).strftime("%d-%m-%Y"),
            label="Jour précédent"
        )

        suivant = Button(
            style=ButtonStyle.PRIMARY,
            custom_id="day-" + (date_formater + timedelta(days=1)).strftime("%d-%m-%Y"),
            label="Jour suivant"
        )

        action_row = ActionRow(precedent, suivant)
        if modifier:
            await ctx.edit_origin(embeds=embeds, components=[action_row])
        else:
            await ctx.send(embeds=embeds, components=[action_row])

    except ValueError:
        await ctx.send(embeds=[create_error_embed(f"La valeur `{jour}` ne correspond pas à une date")], )
    # except BaseException as error:
    # await send_error("get_day_bt",error, ctx, jour=jour)


@slash_command(name="get_day", description="Permet d'avoir l'emploi du temps pour une journée")
@slash_option(
    name="jour",
    description="Quel jour ?",
    required=False,
    opt_type=OptionType.INTEGER
)
@slash_option(
    name="mois",
    description="Quel mois ?",
    required=False,
    opt_type=OptionType.INTEGER
)
@slash_option(
    name="annee",
    description="Quel année ?",
    required=False,
    opt_type=OptionType.INTEGER
)
@slash_option(
    name="personne",
    description="Quel jour ? (DD-MM-YYYY)",
    required=False,
    opt_type=OptionType.USER
)
async def get_day(ctx: SlashContext, jour : int = None, mois : int = None, annee : int = None, personne: User = None):
    """Fonction qui permet d'obtenir l'EDT d'une journée spécifique"""
    #try:
    await get_day_bt(ctx, False, jour, mois, annee, personne)
    #except BaseException as error:
    #    await send_error("get_day",error, ctx, jour=jour)


@slash_command(name="test", description="Test command")
async def test(ctx :SlashContext):
    await ctx.send(ctx.author.avatar_url)


@slash_command(name="dm", description="tries to dm the user")
async def dm(ctx :SlashContext):
    """tries to dm the user"""
    #try:
    user = bot.get_user(ctx.author.id)
    await user.send("👀 est ce que ça a marché ?")
    await ctx.send("done :)")
    #except BaseException as error:
       #await send_error("dm",error, ctx)


async def changement_event(embeds : list[Embed]):
    global channel
    if not channel:
        channel = bot.get_channel(os.getenv("CHANNEL_ID"))
    await channel.send(embeds=embeds)


    if not is_guild_chan(ctx.author):
        await ctx.send("nuh uh\nC'est une commande Administrator-only qui sert a rafraichir la base de donnée, t'es pas vraiment sensé voir ça mais discord refuse de te la cacher, si tu envoie un screenshot à @Kaawan ou @Dany, tu gagne un rôle spécial :)\nhttps://tenor.com/view/nuh-uh-nuh-uh-scout-tf2-gif-12750436057634665505")
        return
    


""" print("avant : ", os.getcwd())

pattern = r"^(.*\\trainwreck)\\.*$"
match = re.match(pattern, os.getcwd())
if match:
    path = match.group(1)
    os.chdir(path)

print("après : ", os.getcwd())
"""


@slash_command(name="test", description="Test command")
    async def test(self, ctx: SlashContext):
        await ctx.send(
            f"{self.tool.ping_liste(Event(datetime.now(), datetime.now(), "Cours", Group.TD1I, "Ta mère", "Ton père", True, False, "007"))}, you got poked by {ctx.author.mention}!")

@slash_command(name="info", description="Envoie des infos sur vos groupes, et filière. Si une personne est donnée, donne ses informations")
    @slash_option(
        name="personne",
        description="Quel utilisateur ?",
        required=False,
        opt_type=OptionType.USER
    )
    async def info(self, ctx: SlashContext, personne: User = None):
        """Fonction qui permet d'afficher le nom, la filière et les groupes de la personne"""
        author = ctx.author if (personne is None) else personne
        you_are = personne is None
        str_role = ""
        for groupe in self.tool.get_groupes_as_list(author):
            str_role += groupe.value + ", "
        str_role = str_role.removesuffix(", ")
        await ctx.send(
            f"{"Vous êtes" if you_are else "Informations sur"} {author.display_name}!\n{"Votre" if you_are else "Sa"} filière est {self.tool.get_filiere_as_filiere(ctx.author).value} et {"vos" if you_are else "ses"} groupes {"sont" if len(self.tool.get_groupes_as_list(ctx.author)) > 1 else "est"} {str_role}.")


async def send_error(self, channel_name, error, ctx, semaine=None, jour=None, bouton=None):
    message_erreur = f"ERREUR dans : {channel_name} - {datetime.now()}\nErreur de type : {type(error)}\nArgument de l'erreur : {error.args}\nDescription de l'erreur : {error}\nLes paramètres de la fonction étais : \n - auteur : {ctx.author}\n - serveur :  {ctx.guild}\n - message :  {ctx.message}\n - channel :  {ctx.channel}\n - role member :  {ctx.member.roles}"
    if semaine:
        message_erreur += f"\n - semaine : {semaine}"
    if jour:
        message_erreur += f"\n - jour : {jour}"
    if bouton:
        message_erreur += f"\n - id_bouton : {bouton}"
    with open("output/error.log", "a") as f:
        f.write(message_erreur)
    await self.bot.get_channel(os.getenv("CHANNEL_ID")).send(f"<@&{os.getenv("ADMIN_ID")}> " + message_erreur)
    await ctx.send(embeds=[self.create_error_embed(
        "Une erreur est survenue, veuillez réessayer ultérieurement, l'équipe de modération est avertie du problème")])