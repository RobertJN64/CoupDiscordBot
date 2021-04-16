import BotGame

from discord.ext import commands

help_command = commands.DefaultHelpCommand(
    no_category = 'Game Commands'
)

with open('token.txt') as f:
    TOKEN = f.read()

print(TOKEN)

print("Running Bot Core script to connect Bot")


def newGame():
    return BotGame.GameState()

def instantiate(game):
    bot = commands.Bot(command_prefix='!', help_command=help_command)

    #region Simple Events
    @bot.event
    async def on_ready():
        print(f'{bot.user} has connected to Discord!')

    @bot.command(name="gamehelp", help="Gives info about the game and commands.")
    async def gamehelp(ctx):
        message = "Coup is a social deduction game." + '\n'
        message += "Use !move to play on your turn." + '\n'
        message += "Try characters like Duke or Captain" + '\n'
        message += "Or use moves like Income and Aid"
        await ctx.send(message)
    #endregion

    @bot.command(name="debug", help="Dumps current game state. DO NOT RUN DURING GAME")
    async def debug(ctx, unsafe=False):
        message = game.debug(unsafe=unsafe)
        await ctx.send(message)

    @bot.command(name="state", help="Repeats last state message sent.")
    async def state(ctx):
        message = game.advanceState(False)
        await ctx.send(message)

    @bot.command(name="force", help="Sets an attribute to a new value. DO NOT RUN DURING GAME")
    async def force(ctx, player, attribute, value):
        message = game.force(player, attribute, value)
        await ctx.send(message)

    @bot.command(name="move", help="Plays a move. Try Duke/Assasin/Captain/Ambassador or Income/Aid/Tax/Steal/Assassinate/Exchange/Coup")
    async def move(ctx, moveID, move_target=None):
        sender = '<@!' + str(ctx.message.author.id) + '>'
        valid, info = game.valid("Turn", sender)
        if valid:
            message = game.move(moveID, sender, str(move_target))
            await ctx.send(message.message)
            if message.sendDM:
                await ctx.message.author.send(message.DM)
        else:
            await ctx.send(info)

    @bot.command(name="join", help="Add yourself to the game!")
    async def join(ctx):
        sender = '<@!' + str(ctx.message.author.id) + '>'
        valid, info = game.valid("join", sender)
        if valid:
            game.registerPlayer(sender)
            await ctx.message.author.send("Starting cards: " + game.getCards('<@!' + str(ctx.message.author.id) + '>'))
            await ctx.send("Player joined!")
        else:
            await ctx.send(info)

    @bot.command(name="cards", help="Returns cards in your hand")
    async def dm(ctx):
        message = game.getCards('<@!' + str(ctx.message.author.id) + '>')
        await ctx.message.author.send(message)
        await ctx.send("DM sent")

    @bot.command(name="reveal", help="Places that card face up.")
    async def reveal(ctx, card):
        sender = '<@!' + str(ctx.message.author.id) + '>'
        valid, info = game.valid("Reveal", sender)
        if valid:
            message = game.revealCard(sender, card)
            await ctx.send(message.message)
            if message.sendDM:
                await ctx.message.author.send(message.DM)
        else:
            await ctx.send(info)

    @bot.command(name="discard", help="Discards cards after card exchange. Run in DM.")
    async def discard(ctx, carda, cardb):
        sender = '<@!' + str(ctx.message.author.id) + '>'
        valid, info = game.valid("Waiting", sender)
        if valid:
            game.discard(sender, [carda, cardb])
        else:
            await ctx.send(info)

    @bot.command(name="start", help="Starts a game.")
    async def start(ctx):
        sender = '<@!' + str(ctx.message.author.id) + '>'
        valid, info = game.valid("Start", sender)
        if valid:
            if len(game.playerList) > 0: # TODO - number of players in a game
                game.gamePos = 1
                game.nextPlayer = game.playerList[0].id
                await ctx.send("Started game! Next player: " + str(game.playerList[0].id))
            else:
                await ctx.send("Not enough players.")
        else:
            await ctx.send(info)

    @bot.command(name="block", help="Blocks last move.")
    async def block(ctx):
        if game.gamePos != 0:
            message = game.block()
            await ctx.send(message.message)
            if message.sendDM:
                await ctx.message.author.send(message.DM)

    @bot.command(name="challenge", help="Challenges a player.")
    async def challenge(ctx):
        sender = '<@!' + str(ctx.message.author.id) + '>'
        if game.gamePos != 0:
            message = game.challenge(sender)
            await ctx.send(message.message)
            if message.sendDM:
                await ctx.message.author.send(message.DM)

    @bot.command(name="table", help="Shows the current state in a friendly manner.")
    async def table(ctx):
        message = game.showTable()
        for m in message:
            await ctx.send(m)

    @bot.command(name="hardreset", help="Hard resets the current game state. DO NOT RUN DURING GAME")
    async def hardreset(ctx):
        game.__init__()
        await ctx.send("Game state reset.")

    class Actions(commands.Cog):
        """Alternatives to !move"""

        def __init__(self, Bot):
            self.bot = Bot

        @commands.command(name="Income", help="Income (1 coin)")
        async def income(self, ctx):
            await move(ctx, "Income", None)

        @commands.command(name="Aid", help="Aid (2 coins)")
        async def aid(self, ctx):
            await move(ctx, "Aid", None)

        @commands.command(name="Coup", help="Coup (7 Coins -> Lose influence)")
        async def coup(self, ctx):
            await move(ctx, "Coup", None)

        @commands.command(name="Tax", help="Tax (3 coins)")
        async def tax(self, ctx):
            await move(ctx, "Tax", None)

        @commands.command(name="Duke", help="Tax (3 coins)")
        async def duke(self, ctx):
            await move(ctx, "Duke", None)

        @commands.command(name="Steal", help="Steal (2 coins)")
        async def steal(self, ctx, move_target=None):
            await move(ctx, "Steal", move_target)

        @commands.command(name="Captain", help="Captain (2 coins)")
        async def captain(self, ctx, move_target=None):
            await move(ctx, "Captain", move_target)

        @commands.command(name="Assassinate", help="Steal (3 coins -> Lose influence)")
        async def assassinate(self, ctx, move_target=None):
            await move(ctx, "Assassinate", move_target)

        @commands.command(name="Assassin", help="Assassinate (3 coins -> Lose influence)")
        async def assassin(self, ctx, move_target=None):
            await move(ctx, "Assassin", move_target)

        @commands.command(name="Exchange", help="Swap cards (2 cards)")
        async def exchange(self, ctx, move_target=None):
            await move(ctx, "Exchange", move_target)

        @commands.command(name="Ambassador", help="Swap cards (2 cards)")
        async def ambassador(self, ctx, move_target=None):
            await move(ctx, "Ambassador", move_target)

    bot.add_cog(Actions(bot))
    bot.run(TOKEN)


