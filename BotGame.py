import datetime
import random
import copy

#CONFIG
config_enforceturns = True

gameStates = ["Start", "Turn", "Reveal", "Waiting", "End"]

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
    player.coins -= 7
    gameState.expectedRevealList = []
    gameState.gamePos = 2 #Reveal
    gameState.nextPlayer = recPlayer.id
    return True, "You were couped."

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
    if player.coins < 3:
        return False, "Not enough coins to assassinate"
    recPlayer = gameState.getPlayer(gameState.moveTarget)
    if recPlayer is None:
        return False, "That player isn't in the game."
    player.coins -= 3
    gameState.expectedRevealList = []
    gameState.gamePos = 2  # Reveal
    gameState.nextPlayer = recPlayer.id
    return True, "You were assassinated."

def Exchange(gameState, player):
    player.cards += gameState.draw(2)
    gameState.nextPlayer = player.id
    gameState.gamePos = 3
    return True, ""
#endregion
#endregion
#region Classes
class Card:
    def __init__(self, name, emojistr):
        self.name = name
        self.emoji = emojistr
        self.junk = False

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
         "Steal": Move("Steal", Steal, ["Captain", "Ambassador"]),
         "Assassinate": Move("Assassinate", Assassinate, ["Contessa"]),
         "Exchange": Move("Exchange", Exchange, []),
         "Coup": Move("Coup", Coup, [])}

characters = {"Duke": Character("Duke", ["Tax"]),
              "Captain": Character("Captain", ["Steal"]),
              "Assassin": Character("Assassin", ["Assassinate"]),
              "Contessa": Character("Contessa", []),
              "Ambassador": Character("Ambassador", ["Exchange"])}

cards = {"Duke": Card("Duke", "<:CoupDuke:832276533388640256>"),
         "Captain": Card("Captain", "<:CoupCaptain:832276532176617493>"),
         "Assassin": Card("Assassin", "<:CoupAssassin:832276533652881448>"),
         "Contessa": Card("Contessa", "<:CoupContessa:832276953415024730>"),
         "Ambassador": Card("Ambassador", "<:CoupAmbassador:832276533179318292>")}
#endregion
#region more classes
class Player:
    def __init__(self, gameState, name, rawname):
        self.id = name
        self.rawname = rawname
        self.cards = gameState.draw(2)
        self.revealedCards = []
        self.coins = 2 #you start with 2 coins
        self.alive = True

    def debug(self, unsafe=False):
        outstr = ""
        outstr += "Player id: " + str(self.id) + '\n'
        if unsafe:
            outstr += "Player cards: " + self.cardString() + '\n'
        outstr += "Player face up cards: " + self.revealCardString() + '\n'
        outstr += "Player has " + str(self.coins) + " coins." + '\n'
        outstr += "Player alive: " + str(self.alive)
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
    
class Response:
    def __init__(self, message, sendDM=False, DM="", MainChat=""):
        self.message = message
        self.sendDM = sendDM
        self.DM = DM
        self.mainChat = MainChat
        
class playerState:
    def __init__(self, deck):
        self.playerList = []
        self.deck = deck

    def addPlayer(self, gameState, name, rawname):
        self.playerList.append(Player(gameState, name, rawname))

    def getPlayer(self, name):
        for player in self.playerList:
            if player.id == name and player.alive:
                return player
        return None
#endregion

lastPlayerState = playerState(deck=[])
class GameState:
    def __init__(self):
        print("Creating new game...")
        self.createtime = datetime.datetime.now().strftime("%I:%M %p") #helps with keeping track of objects
        self.moveTarget = None #reciever of the move (ie assassin, steal)
        self.movePlayer = None #creator of the move
        deck = []
        for cardID in cards:
            deck.append(copy.deepcopy(cards[cardID]))  # 3 of each card
            deck.append(copy.deepcopy(cards[cardID]))
            deck.append(copy.deepcopy(cards[cardID]))
        self.players = playerState(deck) #handles player list + player cards + coins
        self.gamePos = 0 #current state of game
        self.junk = False #param to set by functions that don't need it
        self.lastmove = None #last action done by player ie: tax / block / challenge
        self.turnPos = 0 #keeps track of whose turn it is
        self.nextPlayer = None #next person to complete an action
        self.expectedRevealList = [] #valid cards to reveal
        self.challenger = None #person who intiated a challenge
        self.assassinFlag = 0

    def debug(self, unsafe=False):
        global lastPlayerState
        print("Debug called. Dumping state")
        outstr = "------" + '\n'
        outstr += "Main obj: " + str(self) + '\n'
        outstr += "Player obj: " + str(self.nextPlayer) + '\n'
        outstr += "Last player state obj: " + str(lastPlayerState) + '\n'
        outstr += "Create time: " + str(self.createtime) + '\n'
        outstr += "Game state: " + gameStates[self.gamePos] + '\n'
        outstr += "Last move: " + str(self.lastmove) + '\n'
        outstr += "Last move creator: " + str(self.movePlayer) + '\n'
        outstr += "Last move target: " + str(self.moveTarget) + '\n'
        outstr += "Next player: " + str(self.nextPlayer) + '\n'
        outstr += "Turn Pos: " + str(self.turnPos) + '\n'
        outstr += "Challenger: " + str(self.challenger) + '\n'
        outstr += "Deck length: " + str(len(self.players.deck)) + '\n'
        outstr += "Assassin Flag: " + str(self.assassinFlag) +'\n'
        outstr += "Expected reveal list: "
        for cardID in self.expectedRevealList:
            outstr += cardID.name + ", "
        outstr += '\n'
        outstr += "Player data: " + '\n'
        for player in self.players.playerList:
            outstr += "++++++" + '\n'
            outstr += player.debug(unsafe=unsafe) + '\n'
            outstr += "++++++" + '\n'
        outstr += "-----"
        print(outstr)
        return outstr
    
    def registerPlayer(self, name, rawname):
        self.players.addPlayer(self, name, rawname)

    def getPlayer(self, name):
        return self.players.getPlayer(name)

    def draw(self, count):
        out = []
        for i in range(0, count):
            out.append(self.players.deck.pop(random.randint(0, len(self.players.deck) - 1)))
        return out

    def getCards(self, name):
        player = self.getPlayer(name)
        if player is None:
            return "Error. You are not in the current game."
        return player.cardString()

    def checkWin(self):
        winner = None
        deadplayers = 0
        for player in self.players.playerList:
            if len(player.cards) == 0:
                player.alive = False
                deadplayers += 1
            else:
                winner = player.id

        if deadplayers == len(self.players.playerList) - 1:
            return True, winner
        else:
            return False, None

    def nextTurn(self, nextPlayer = True):
        self.turnPos += 1
        if self.turnPos >= len(self.players.playerList):
           self.turnPos = 0
        if nextPlayer:
            self.nextPlayer = self.players.playerList[self.turnPos].id
        if not self.players.playerList[self.turnPos].alive:
            self.nextTurn()

    def valid(self, action, sender): #gives descriptive error messages
        if action == "join":
            for player in self.players.playerList:
                if player.id == sender:
                    return False, "Already in game." #First we check if a player is already in game
            action = "Start"

        if action == "Start" and self.gamePos != 0: #Are they trying to join and has game started?
            return False, "Game has already started."

        if self.gamePos != 0 and sender != self.nextPlayer and config_enforceturns:
            return False, "Waiting for " + self.nextPlayer + " to play." #It isn't their turn

        if action == gameStates[self.gamePos]: #ok, everything looks good
            return True, ""

        elif self.gamePos == 0:
            return False, "Game has not started." #trying to play but game is has not started

        elif self.gamePos == 1:
            return False, "Waiting for a player to take their turn." #trying to reveal a card during a turn

        elif self.gamePos == 2:
            return False, "Waiting for a player to reveal a card." #trying to complete turn during a reveal card

        elif self.gamePos == 3:
            return False, "A player is in the middle of their turn." #during ambassador exchange

        elif self.gamePos == 4:
            return False, "The game is over."

        else:
            return False, "Invalid action at this time."

    def advanceGameState(self, nextTurn = True):
        win, player =  self.checkWin()
        if not win:
            if self.gamePos == 0:
                return Response("Game has not started, so this event shouldn't have happened.")
            if self.gamePos == 1:
                if self.lastmove == "challenge":
                    return Response("Challenge finished. Next player: " + self.nextPlayer)
                if self.lastmove == "block":
                    return Response("Block successful. Next player: " + self.nextPlayer)
                if nextTurn:
                    self.nextTurn()
                return Response("Move {" + self.lastmove + "} executed successfully! Next player: " + self.nextPlayer)

            if self.gamePos == 2:
                return Response(self.nextPlayer + " reveal a card.")

            if self.gamePos == 3:
                return Response("Move {" + self.lastmove + "} in progress! DM sent with new cards. Discard in DM. Game will resume shortly.",
                    sendDM=True, DM="You drew 2 cards and now have: " + self.getPlayer(self.movePlayer).cardString() + ". Discard 2.")

            if self.gamePos == 4:
                return Response("The game is over.")
        else:
            return Response("Game over! " + player + " won!")

    def move(self, moveID, sender, move_target):
        global lastPlayerState
        self.movePlayer = sender
        self.moveTarget = move_target

        #region verify move
        if moveID not in moves and (moveID not in characters or len(characters[moveID].moveList) == 0 or len(characters[moveID].moveList) > 1):
            return Response("Move not found or character has no moves. Try again.")

        if moveID in characters:
            moveID = characters[moveID].moveList[0]
        else:
            moveID = moves[moveID]

        player = self.getPlayer(self.movePlayer)
        if player is None:
            return Response("Looks like you aren't in the game.")
        if player.coins >= 10 and moveID.name != "Coup":
            return Response("You have more than 10 coins, you need to coup!")

        #endregion

        self.lastmove = moveID.name
        self.assassinFlag = moveID.name == "Assassinate"

        lastPlayerState = copy.deepcopy(self.players)
        success, message = moveID.run(self, player)
        if not success:
            return Response(message)

        response = self.advanceGameState()

        if self.lastmove == "Assassinate":
            self.nextTurn(nextPlayer=False)

        if message != "":
            response.message = message + " " + response.message

        return response

    def revealCard(self, name, cardID):
        global lastPlayerState

        #region Check if card is valid
        player = self.getPlayer(name)
        if player is None:
            return Response("Error. You are not in the current game.")
        if cardID in player.cardString():
            loc = 0
            for loc in range(0, len(player.cards)):
                if player.cards[loc].name == cardID:
                    break
            if cardID in self.expectedRevealList:
                self.players.deck.append(player.cards[loc])
            else:
                player.revealedCards.append(player.cards[loc])
            player.cards.pop(loc)

        else:
            return Response("Error.")
        #endregion

        for cardInfo in self.expectedRevealList:
            if cardInfo.name == cardID:
                tempstate = self.players #save players hand
                self.revertstate()
                if cardID != "Ambassador":
                    self.getPlayer(name).cards = tempstate.getPlayer(name).cards #1 card
                    self.getPlayer(name).cards += self.draw(1)
                self.gamePos = 2
                self.expectedRevealList = []
                self.nextPlayer = self.challenger

                return Response("Player reveals a " + str(cardID) + ". This is valid, so " + self.nextPlayer + " must reveal a card now.",
                                sendDM=True, DM="You drew 1 card and now have: " + self.getPlayer(self.movePlayer).cardString())


        if self.assassinFlag and len(self.players.getPlayer(name).cards) != 0 and name == self.challenger: #we revealed one
            self.assassinFlag = False

        else:
            self.gamePos = 1

        gs = self.advanceGameState(nextTurn= self.lastmove != "block" and self.lastmove != "challenge")
        return gs

    def discard(self, player, cardList):
        player = self.getPlayer(player)
        if player is None:
            return Response("Error. You are not in the current game.")

        minilist = copy.deepcopy(player.cards)
        mlist = []
        for card in minilist:
            mlist.append(card.name)
        for card in cardList:
            if card in mlist:
                mlist.remove(card)
            else:
                message = Response("Error.")
                return message

        for card in cardList:
            if card in player.cardString():
                loc = 0
                for loc in range(0, len(player.cards)):
                    if player.cards[loc].name == card:
                        break
                self.players.deck.append(player.cards.pop(loc))

        self.gamePos = 1
        gs = self.advanceGameState()
        gs.mainChat = gs.message
        gs.message = "Cards Discarded."
        return gs

    def revertstate(self):
        global lastPlayerState
        temp = copy.deepcopy(lastPlayerState)
        lastPlayerState = copy.deepcopy(self.players)
        self.players = copy.deepcopy(temp)

    def block(self, sender):
        if self.movePlayer != sender:
            if self.lastmove is not None and len(moves[self.lastmove].blocklist) > 0:
                bcards = []
                for cardID in moves[self.lastmove].blocklist:
                    bcards.append(cards[cardID])
                self.movePlayer = sender
                self.expectedRevealList = bcards
                self.lastmove = "block"
                self.revertstate()
                if self.gamePos == 2:
                    self.gamePos = 1
                response = self.advanceGameState()
                return response
            else:
                return Response("Move can't be blocked.")
        else:
            return Response("You can't block yourself.")

    def challengeRevert(self, sender, message):
        self.gamePos = 2
        self.lastmove = "challenge"
        self.challenger = sender
        self.nextPlayer = self.movePlayer
        self.revertstate()
        return Response(message)

    def challenge(self, sender):
        global lastPlayerState
        if self.movePlayer != sender:
            if self.lastmove == "block":
                self.nextPlayer = self.movePlayer
                return self.challengeRevert(sender, "Block challenged, " + self.movePlayer + " reveal a card.")
            for character in characters:
                character = characters[character]
                for move in character.moveList:
                    if self.lastmove == move.name:
                        self.expectedRevealList = [character]
                        return self.challengeRevert(sender, "Move challenged, " + self.movePlayer + " reveal a card.")
            return Response("Move can't be challenged.")
        else:
            return Response("You can't challenge yourself!")

    def showTable(self):
        out = []
        nextstr = ""
        for player in self.players.playerList:
            counter = 0
            nextstr += "᲼᲼" + player.rawname
            counter += len(player.rawname)
            for i in range(counter, 18):
                nextstr += " "

        out.append(nextstr)

        nextstr = ""
        for player in self.players.playerList:
            for card in player.cards:
                card.junk = False
                nextstr += "<:CoupCardBack:832410965612953660>"

            for card in player.revealedCards:
                nextstr += card.emoji

            nextstr += "      "

        out.append(nextstr)

        nextstr = ""
        for player in self.players.playerList:
            nextstr += "᲼᲼᲼" + str(player.coins) + " <:CoupCoin:832411528165589003>" + "                "

        out.append(nextstr)
        return out

    def force(self, player, attribute, value):
        if player == "gameState":
            if attribute == "gamePos":
                self.gamePos = int(value)
            elif attribute == "moveTarget":
                self.moveTarget = str(value)
            elif attribute == "movePlayer":
                self.movePlayer = str(value)
            elif attribute == "lastMove":
                self.lastmove = str(value)
            elif attribute == "turnPos":
                self.turnPos = int(value)
            elif attribute == "nextPlayer":
                self.nextPlayer = str(value)
            elif attribute == "challenger":
                self.challenger = str(value)
            else:
                return Response("Error, couldn't find attribute.")
            return Response("Sucess!")
        else:
            player = self.getPlayer(player)
            if player is None:
                return  Response("Error, couldn't find player.")
            else:
                if attribute == "coins":
                    player.coins = int(value)
                elif attribute == "alive":
                    player.alive = bool(value)
                elif attribute == "draw":
                    player.cards += self.draw(int(value))
                else:
                    return Response("Error, couldn't find attribute.")
                return Response("Success!")