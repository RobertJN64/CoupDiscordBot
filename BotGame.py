import datetime
import random
import copy

#CONFIG
config_enforceturns = True


lastGameState = None
gameStates = ["Start", "Turn", "Reveal"]

#region GameFunctions
#region Global Functions
def Income(gameState, player):
    gameState.junk = False
    player.coins += 1
    return True, "Player now has " + str(player.coins) + " coins!"

def Aid(gameState, player):
    gameState.junk = False
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
    gameState.junk = False
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
              "Assassin": Character("Assassin", ["Assassinate"]),
              "Contessa": Character("Contessa", []),
              "Ambassador": Character("Ambassador", ["Exchange"])}

cards = {"Duke": Card("Duke"),
         "Captain": Card("Captain"),
         "Assassin": Card("Assassin"),
         "Contessa": Card("Contessa"),
         "Ambassador": Card("Ambassador")}
#endregion

class Player:
    def __init__(self, gameState, name):
        self.id = name
        self.cards = gameState.draw(2)
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
        self.junk = False
        self.lastmove = None
        self.turnPos = 0
        self.nextPlayer = ""
        self.deck = []
        for cardID in cards:
            self.deck.append(copy.deepcopy(cards[cardID])) #3 of each card
            self.deck.append(copy.deepcopy(cards[cardID]))
            self.deck.append(copy.deepcopy(cards[cardID]))

    def nextTurn(self):
        self.turnPos += 1
        if self.turnPos >= len(self.playerList):
           self.turnPos = 0
        self.nextPlayer = self.playerList[self.turnPos].id

    def registerPlayer(self, name):
        self.playerList.append(Player(self,name))

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
        outstr += "Last move: " + str(self.lastmove) + '\n'
        outstr += "Next player: " + str(self.nextPlayer) + '\n'
        outstr += "Turn Pos: " + str(self.turnPos) + '\n'
        outstr += "Player data: " + '\n'
        for player in self.playerList:
            outstr += "++++++" + '\n'
            outstr += player.debug(unsafe=unsafe) + '\n'
            outstr += "++++++" + '\n'
        outstr += "-----"
        print(outstr)
        return outstr

    def draw(self, count):
        out = []
        for i in range(0, count):
            out.append(self.deck.pop(random.randint(0, len(self.deck) - 1)))
        return out

    def valid(self, action, sender):
        if action == "join":
            for player in self.playerList:
                if player.id == sender:
                    return False, "Already in game."
            action = "Start"
        if action == "Start" and self.gamePos != 0:
            return False, "Game has started."
        if self.gamePos != 0 and sender != self.nextPlayer and config_enforceturns:
            return False, "Waiting for " + self.nextPlayer + " to play."
        if action == gameStates[self.gamePos]:
            return True, ""
        elif self.gamePos == 0:
            return False, "Game has not started."
        elif self.gamePos == 2:
            return False, "Waiting for a player to reveal a card."
        elif self.gamePos == 1:
            return False, "Waiting for a player to take their turn."
        else:
            return False, "Invalid action at this time."

    def move(self, ctx, moveID, sender, move_target):
        global lastGameState
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

        self.lastmove = moveID.name
        lastGameState = copy.deepcopy(self)
        success, message = moveID.run(self, player)
        if not success:
            return message

        out = "Move {" + moveID.name + "} executed successfully! Next player: " + str(self.playerList[0].id)
        if message != '':
            out += "\n" + message

        self.nextTurn()

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

    def block(self):
        global lastGameState
        if self.lastmove is not None and len(moves[self.lastmove].blocklist) > 0:
            temp = copy.deepcopy(lastGameState)
            lastGameState = copy.deepcopy(self)
            return temp, "Move blocked."
        else:
            return self, "Move can't be blocked"

    def showTable(self):
        out = []
        for player in self.playerList:
            out.append(player.id)
            s = ""
            for card in player.cards:
                s += "<:CoupCardBack:832410965612953660>"

            for card in player.revealedCards:
                s += ":coup" + card.name + ": "

            out.append(s)
            out.append("-")
        return out



