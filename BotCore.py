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

    @bot.event
    async def on_ready():
        print(f'{bot.user} has connected to Discord!')

    @bot.command(name="debug", help="Dumps current game state. DO NOT RUN DURING GAME")
    async def debug(ctx, unsafe=False):
        message = game.debug(unsafe=unsafe)
        await ctx.send(message)

    @bot.command(name="move", help="Plays a move. Try Duke/Assasin/Captain/Ambassador or Income/Aid/Tax/Steal/Assassinate/Exchange/Coup")
    async def move(ctx, moveID, move_target=None):
        if game.gamePos == 1:
            sender = '<@!' + str(ctx.message.author.id) + '>'
            message = game.move(ctx, moveID, sender, str(move_target))
            await ctx.send(message)
        else:
            await ctx.send("You can't do that right now.")

    @bot.command(name="gamehelp", help="Gives info about the game and commands.")
    async def gamehelp(ctx):
        message = "Coup is a social deduction game." + '\n'
        message += "Use !move to play on your turn." + '\n'
        message += "Try characters like Duke or Captain" + '\n'
        message += "Or use moves like Income and Aid"
        await ctx.send(message)

    @bot.command(name="join", help="Add yourself to the game!")
    async def join(ctx):
        if game.gamePos == 0:
            game.registerPlayer('<@!' + str(ctx.message.author.id) + '>')
            await ctx.message.author.send(game.getCards('<@!' + str(ctx.message.author.id) + '>'))
            await ctx.send("Player joined!")
        else:
            await ctx.send("Game already started.")

    @bot.command(name="cards", help="Returns cards in your hand")
    async def dm(ctx):
        message = game.getCards('<@!' + str(ctx.message.author.id) + '>')
        await ctx.message.author.send(message)
        await ctx.send("DM sent")

    @bot.command(name="reveal", help="Places that card face up.")
    async def reveal(ctx, card):
        if game.gamePos == 2:
            message = game.revealCard('<@!' + str(ctx.message.author.id) + '>', card)
            await ctx.send(message)
        else:
            await ctx.send("You can't do that right now.")

    @bot.command(name="start", help="Starts a game.")
    async def start(ctx):
        if game.gamePos == 0:
            game.gamePos = 1
            await ctx.send("Started game!")
        else:
            await ctx.send("Game already running.")

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


