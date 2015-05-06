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
				self.handler.playerID = 1
				self.handler.startScreen1()
			if(data == 3):
				self.handler.check = 1
				self.handler.startScreen2()
			if(data == 4):
				self.handler.check = 1
				self.handler.startScreen2()
				self.handler.connection.transport.write("Ready")
		else:
			data = json.loads(data)
			self.handler.gameData = data
			if(self.handler.started == 0):
				self.handler.startGame()
				self.handler.started = 1

#Protocol for command connection
class Player2ConnectionProtocol(Protocol):

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
				self.handler.playerID = 2
				self.handler.startScreen1()
			if(data == 3):
				self.handler.check = 1
				self.handler.startScreen2()
			if(data == 4):
				self.handler.check = 1
				self.handler.startScreen2()
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
		if self.handler.end:
			reactor.stop()
			self.handler.end = 0

	def dataReceived(self, data):
		data = int(data[0])
		if(data == 1):
			reactor.connectTCP('cushing52.helios.nd.edu', 32001, Player1ConnectionFactory(self.handler))
			self.handler.playerID = 1
			self.handler.startScreen1()
		if(data == 2):
			reactor.connectTCP('cushing52.helios.nd.edu', 32002, Player2ConnectionFactory(self.handler))
			self.handler.playerID = 2
			self.handler.startScreen1()
		if(data == 3):
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

		self.connection = ''
		self.tempconnection = ''
		self.started = 0
		self.playerID = ''
		self.gameData = {}
		self.gs = ""
		self.check = 1
		self.end = 1
		
	def reset(self):
		self.started = 0
		self.playerID = ''
		self.gameData = {}
		self.gs = ""

	def startScreen1(self):
		self.gs = GameSpace(self)
		self.gs.startScreen(self,1)

	def startScreen2(self):
		self.gs.startScreen(self,2)
	
	def startGame(self):
		self.gs.main(self)

#Instantiate handler and pass to command factory
gameHandler = GameHandler()										
initialConnectionFactory = InitialConnectionFactory(gameHandler)	

#Create command connection to home									
reactor.connectTCP('cushing52.helios.nd.edu', 32000, initialConnectionFactory)
	
#Start event loop									
reactor.run()
