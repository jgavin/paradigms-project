#Jacob Gavin & James Harkins
#game_client.py
#Twisted Primer Assignment

from twisted.internet.protocol import Factory
from twisted.internet.protocol import ClientFactory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
from twisted.internet.defer import DeferredQueue
from twisted.internet.defer import Deferred
from game import *
import cPickle as pickle
import json

import sys
import os

#Helper function that checks if a string is an int
def isInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

#Protocol for command connection
class Player1ConnectionProtocol(Protocol):

	def __init__(self, handler):
		self.handler = handler

	def connectionMade(self):
		self.handler.connection = self

	def connectionLost(self,reason):
			#stop the reactor on connection lost, if it hasn't been lost yet
			if self.handler.end: #Check if connection has been lost
				reactor.stop() #Stop the connection
				self.handler.end = 0 #Set the connection lost yet

	def dataReceived(self, data):
		if isInt(data[0]): #Use helper function to see if data is an int
			data = int(data[0])
			if(data == 1): #We are player 1
				if self.handler.check: #Perform a reset only if we havent reset already
					self.handler.reset() #Perform the reset
					self.handler.check = 0 #Set the reset check
				self.handler.playerID = 1 #Set your player ID
				self.handler.startScreen1() #Display start screen
			if(data == 3): #Means the user has clicked the start game 
				self.handler.check = 1 #Set our reset check
				self.handler.startScreen2() #Display "waiting for other player" screen
			if(data == 4): #Means both players have clicked the start game
				self.handler.check = 1 #Set reset check
				self.handler.connection.transport.write("Ready") #Tell server both clients are ready
		else:
			data = json.loads(data)
			self.handler.gameData = data #set the data in our game file to the incoming data
			if(self.handler.started == 0): #if we havent started yet
				self.handler.startGame() #start the game
				self.handler.started = 1 #set start check to 1

#Protocol for command connection
class Player2ConnectionProtocol(Protocol):
	#Basically the same code as Player2ConnectionProtocol
	def __init__(self, handler):
		self.handler = handler

	def connectionMade(self):
		self.handler.connection = self

	def connectionLost(self, reason):
		if self.handler.end:
			reactor.stop()
			self.handler.end = 0

	def dataReceived(self, data):
		if isInt(data[0]):
			data = int(data[0])
			if(data == 1):
				if self.handler.check:
					self.handler.reset()
					self.handler.check = 0
				self.handler.playerID = 2 #Only difference is we set playerID to 2
				self.handler.startScreen1()
			if(data == 3):
				self.handler.check = 1
				self.handler.startScreen2()
			if(data == 4):
				self.handler.check = 1
				self.handler.connection.transport.write("Ready")
		else:
			data = json.loads(data)
			self.handler.gameData = data
			if(self.handler.started == 0):
				self.handler.startGame()
				self.handler.started = 1


#Protocol for command connection
class InitialConnectionProtocol(Protocol):

	def __init__(self, handler):
		self.handler = handler

	def connectionMade(self):
		self.handler.connection  = self

	def connectionLost(self, reason):
		#stop the reactor on connection lost, if it hasn't been lost yet
		if self.handler.end: #Check if connection has been lost
			reactor.stop() #Stop the connection
			self.handler.end = 0 #Set the connection lost yet

	def dataReceived(self, data):
		data = int(data[0])
		if(data == 1): #If data = 1 we are player1, connect to player 1s port
			reactor.connectTCP('student00.cse.nd.edu', 9301, Player1ConnectionFactory(self.handler))
			self.handler.playerID = 1 #Player ID set to 1
			self.handler.startScreen1() #Display start screen
		if(data == 2): #If data = 2 we are player2, connect to player 2s port
			reactor.connectTCP('student00.cse.nd.edu', 9302, Player2ConnectionFactory(self.handler))
			self.handler.playerID = 2 #Player ID set to 2
			self.handler.startScreen1() #Display start screen
		if(data == 3): #User has clicked, display waiting for other player screen
			self.handler.startScreen2()
		
		

#Factory for initial connection factory
class InitialConnectionFactory(ClientFactory):

	def __init__(self, handler):
		self.handler = handler

	def buildProtocol(self, addr):
		
		return InitialConnectionProtocol(self.handler)

#Factory for player1 connection factory
class Player1ConnectionFactory(ClientFactory):

	def __init__(self, handler):
		self.handler = handler

	def buildProtocol(self, addr):
		
		return Player1ConnectionProtocol(self.handler)

#Factory for player2 connection factory
class Player2ConnectionFactory(ClientFactory):

	def __init__(self, handler):
		self.handler = handler

	def buildProtocol(self, addr):
		
		return Player2ConnectionProtocol(self.handler)

#Handler which stores copies of all connections and handles all interactions between connections
class GameHandler:

	#Initialize connections to empty string and construct deferred queue
	def __init__(self):

		self.connection = '' #Stores our connection to server
		self.tempconnection = '' #Stores our intial connection to server
		self.started = 0 #Check to see if we have started the game
		self.playerID = '' #Our player ID
		self.gameData = {} #Stores game data we send to game.py
		self.gs = "" #Stores our GameSpace class
		self.check = 1 #Checks for reset
		self.end = 1 #Check for endgame
		
	#Reset all our values
	def reset(self):
		self.started = 0
		self.playerID = ''
		self.gameData = {}
		self.gs = ""

	#Display the start game screen
	def startScreen1(self):
		self.gs = GameSpace(self)
		self.gs.startScreen(self,1)

	#Display the "waiting for other player" screen
	def startScreen2(self):
		self.gs.startScreen(self,2)
	
	#Begin the game
	def startGame(self):
		self.gs.main(self)

#Instantiate handler and pass to command factory
gameHandler = GameHandler()										
initialConnectionFactory = InitialConnectionFactory(gameHandler)	

#Create command connection to home									
reactor.connectTCP('student00.cse.nd.edu', 9300, initialConnectionFactory)
	
#Start event loop									
reactor.run()
