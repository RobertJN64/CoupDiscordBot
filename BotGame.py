import datetime
import random

gameStates = ["Start", "Turn", "Reveal"]

#region GameFunctions
#region Global Functions
def Income(gameState, player):
    player.coins += 1
    return True, "Player now has " + str(player.coins) + " coins!"

def Aid(gameState, player):
    player.coins += 2
    return True, "Player now has " + str(player.coins) + " coins!"

def Coup(gameState, player):
    if player.coins < 7:
        return False, "Not enough coins to coup"
    recPlayer = gameState.getPlayer(gameState.moveTarget)
    if recPlayer is None:
        return False, "That player isn't in the game."
    if recPlayer.coins < 2:
        return False, "That player only has " + str(recPlayer.coins) + " coins."
    player.coins -= 7
    gameState.gamePos = 2 #Reveal
    return True, ""

#endregion
#region CharacterFunctions
def Tax(gameState, player):
    player.coins += 3
    return True, "Player now has " + str(player.coins) + " coins!"

def Steal(gameState, player):
    recPlayer = gameState.getPlayer(gameState.moveTarget)
    if recPlayer is None:
        return False, "That player isn't in the game."
    if recPlayer.coins < 2:
        return False, "That player only has " + str(recPlayer.coins) + " coins."
    if player.id == recPlayer.id:
        return False, "You can't steal from yourself."
    recPlayer.coins -= 2
    player.coins += 2
    return True, "Player now has " + str(player.coins) + " coins!"

def Assassinate(gameState, player):
    print("TODO - Assassinate")
    return True, ""

def Exchange(gameState, player):
    print("TODO - Exchange")
    return True, ""
#endregion
#endregion
#region Classes
class Card:
    def __init__(self, name):
        self.name = name

class Move:
    def __init__(self, name, function, blocklist):
        self.name = name
        self.function = function
        self.blocklist = blocklist

    def run(self, gameState, player):
        return self.function(gameState, player)

class Character:
    def __init__(self, name, movelist):
        self.name = name
        self.moveList = []
        for move in movelist:
            self.moveList.append(moves[move])

#endregion
#region Game Structure


moves = {"Income": Move("Income", Income, []),
         "Aid": Move("Aid", Aid, ["Duke"]),
         "Tax": Move("Tax", Tax, []),
         "Steal": Move("Steal", Steal, ["Captain, Ambassador"]),
         "Assassinate": Move("Assassinate", Assassinate, ["Contessa"]),
         "Exchange": Move("Exchange", Exchange, []),
         "Coup": Move("Coup", Coup, [])}

characters = {"Duke": Character("Duke", ["Tax"]),
              "Captain": Character("Captain", ["Steal"]),
              "Assasin": Character("Assassin", ["Assassinate"]),
              "Contessa": Character("Contessa", []),
              "Ambassador": Character("Ambassador", ["Exchange"])}

cards = {"Duke": Card("Duke"),
         "Captain": Card("Captain"),
         "Assassin": Card("Assassin"),
         "Contessa": Card("Contessa"),
         "Ambassador": Card("Ambassador")}
#endregion

#region deck management
deck = []
for card in cards:
    deck.append(cards[card])


def draw():
    carda = deck.pop(random.randint(0, len(deck)-1))
    cardb = deck.pop(random.randint(0, len(deck)-1))
    return [carda, cardb]
#endregion

class Player:
    def __init__(self, name):
        self.id = name
        self.cards = draw()
        self.revealedCards = []
        self.coins = 2 #you start with 2 coins

    def debug(self, unsafe=False):
        outstr = ""
        outstr += "PLayer id: " + str(self.id) + '\n'
        if unsafe:
            outstr += "Player cards: " + self.cardString() + '\n'
        outstr += "Player face up cards: " + self.revealCardString() + '\n'
        outstr += "Player has " + str(self.coins) + " coins."
        return outstr

    def cardString(self):
        outstr = ""
        for cardid in self.cards:
            outstr += cardid.name + " "
        return outstr

    def revealCardString(self):
        outstr = ""
        for cardid in self.revealedCards:
            outstr += cardid.name + " "
        return outstr

class GameState:
    def __init__(self):
        print("Creating new game...")
        self.createtime = datetime.datetime.now().strftime("%I:%M %p")
        self.moveTarget = None
        self.movePlayer = None
        self.playerList = []
        self.gamePos = 0

    def registerPlayer(self, name):
        self.playerList.append(Player(name))

    def getPlayer(self, name):
        for player in self.playerList:
            if player.id == name:
                return player
        return None

    def debug(self, unsafe=False):
        print("Debug called. Dumping state")
        outstr = "------" + '\n'
        outstr += str(self) + '\n'
        outstr += "Create time: " + str(self.createtime) + '\n'
        outstr += "Game state: " + gameStates[self.gamePos] + '\n'
        outstr += "Last move creator: " + str(self.movePlayer) + '\n'
        outstr += "Last move target: " + str(self.moveTarget) + '\n'
        outstr += "Player data: " + '\n'
        for player in self.playerList:
            outstr += "++++++" + '\n'
            outstr += player.debug(unsafe=unsafe) + '\n'
            outstr += "++++++" + '\n'
        outstr += "-----"
        print(outstr)
        return outstr

    def move(self, ctx, moveID, sender, move_target):
        self.movePlayer = sender
        self.moveTarget = move_target

        if moveID not in moves and (moveID not in characters or len(characters[moveID].moveList) == 0 or len(characters[moveID].moveList) > 1):
            return "Move not found or character has no moves. Try again."

        if moveID in characters:
            moveID = characters[moveID].moveList[0]
        else:
            moveID = moves[moveID]

        player = self.getPlayer(self.movePlayer)
        if player is None:
            return "Looks like you aren't in the game."
        if player.coins > 10 and moveID.name != "Coup":
            return "You have more than 10 coins, you need to coup!"

        success, message = moveID.run(self, player)
        if not success:
            return message

        out = "Move {" + moveID.name + "} executed successfully!"
        if message != '':
            out += "\n" + message

        return out

    def getCards(self, name):
        player = self.getPlayer(name)
        if player is None:
            return "Error. You are not in the current game."
        return player.cardString()

    def revealCard(self, name, cardID):
        player = self.getPlayer(name)
        if player is None:
            return "Error. You are not in the current game."

        if cardID in player.cardString():
            loc = 0
            for loc in range(0, len(player.cards)):
                if player.cards[loc].name == cardID:
                    break
            player.revealedCards.append(player.cards[loc])
            player.cards.pop(loc)

        else:
            return "Error."

        self.gamePos = 1
        return "Player reveals a " + str(cardID)



