#Jacob Gavin & James Harkins
#game_server.py
#Twisted Primer Assignment

from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
from twisted.internet.defer import DeferredQueue
from twisted.internet.defer import Deferred
import json
import cPickle as pickle
from math import *

#Protocol for temp connection
class TempProtocol(LineReceiver):

	def __init__(self, handler):
		self.handler = handler

    	def connectionMade(self):
		if(self.handler.connectionMade == 0):
			self.handler.connectionMade = 1
			self.sendLine("1")
		else:
			self.sendLine("2")
		return

#Protocol for player1 connection
class Player1Protocol(LineReceiver):

	def __init__(self, handler):
		self.handler = handler

    	def connectionMade(self):
		self.handler.player1Connection = self

	def dataReceived(self, data):
		data = json.loads(data)
		self.handler.processPlayer1Events(data)	
		return

#Protocol for player2 connection
class Player2Protocol(LineReceiver):

	def __init__(self, handler):
		self.handler = handler

    	def connectionMade(self):
		self.handler.player2Connection = self
		self.handler.tellPlayersToStart()
		return

	def dataReceived(self, data):
		data = json.loads(data)
		self.handler.processPlayer2Events(data)		
		return
		

#Factory for client1 connection
class TempFactory(Factory):

	def __init__(self, handler):
		self.handler = handler	

    	def buildProtocol(self, addr):
       		return TempProtocol(self.handler)

#Factory for client1 connection
class Player1Factory(Factory):

	def __init__(self, handler):
		self.handler = handler	

    	def buildProtocol(self, addr):
       		return Player1Protocol(self.handler)

#Factory for client2 connection
class Player2Factory(Factory):

	def __init__(self, handler):
		self.handler = handler	

    	def buildProtocol(self, addr):
       		return Player2Protocol(self.handler)

	
#Handler which holds copies of every connection and handles all interaction between connections
class GameHandler:


	#Initialize to connections to empty string and create deferred queue
	def __init__(self):

		self.connectionMade = 0
		self.player1Connection = ''
		self.player2Connection = ''

		self.player1x = 100
		self.player1y = 100
		self.player2x = 200
		self.player2y = 200

		self.player1GunAngle = 270
		self.player2GunAngle = 270

		self.player1Angle = 90
		self.player2Angle = 90

		

	def tellPlayersToStart(self):
		self.sendGameData(1)
		self.sendGameData(2)

	def processPlayer1Events(self, events):
		mx = events['mx']
		my = events['my']
		if( events["mouseEvent"] == 'Pressed' ):
			self.addBullet(self.player1x, self.player1y, mx, my)

		direction = events["keyPressed"]
		if( direction != '' ):
			self.movePlayer(1, direction)

		self.computeAngle(1, mx, my)

		self.sendGameData(1)
		return

	def processPlayer2Events(self, events):
		mx = events['mx']
		my = events['my']
		if( events["mouseEvent"] == 'Pressed' ):
			self.addBullet(self.player2x, self.player2y, mx, my)

		direction = events["keyPressed"]
		if( direction != '' ):
			self.movePlayer(2, direction)

		self.computeAngle(2, mx, my)

		self.sendGameData(2)
		return

	def addBullet(self, playerx, playery, mx, my):
		
		return

	def movePlayer(self, playerID, direction):
		if(direction == 'Right'):
			if playerID == 1:
				self.player1x = self.player1x + 10
				self.player1Angle = 90
			if playerID == 2:
				self.player2x = self.player2x + 10
				self.player2Angle = 90

		if(direction == 'Left'):
			if playerID == 1:
				self.player1x = self.player1x - 10
				self.player1Angle = 270
			if playerID == 2:
				self.player2x = self.player2x - 10
				self.player2Angle = 270

		if(direction == 'Up'):
			if playerID == 1:
				self.player1y = self.player1y - 10
				self.player1Angle = 180
			if playerID == 2:
				self.player2y = self.player2y - 10
				self.player2Angle = 180

		if(direction == 'Down'):
			if playerID == 1:
				self.player1y = self.player1y + 10
				self.player1Angle = 0
			if playerID == 2:
				self.player2y = self.player2y + 10
				self.player2Angle = 0

		return

	def computeAngle(self, playerID, mx, my):

		if(playerID == 1):
			dx = mx - (self.player1x)
			dy = my - (self.player1y)
			rAngle = atan2(dy, -dx)
			self.player1GunAngle  = degrees(rAngle) + 90

		if(playerID == 2):
			dx = mx - (self.player2x)
			dy = my - (self.player2y)
			rAngle = atan2(dy, -dx)
			self.player2GunAngle  = degrees(rAngle) + 90

	def sendGameData(self, playerID):

		data = {}
		data['player1x'] = self.player1x
		data['player1y'] = self.player1y
		data['player2x'] = self.player2x
		data['player2y'] = self.player2y

		if(playerID == 1):
			data['partnerGunAngle'] = self.player2GunAngle
		if(playerID == 2):
			data['partnerGunAngle'] = self.player1GunAngle

		data['player1Angle'] = self.player1Angle
		data['player2Angle'] = self.player2Angle

		data = json.dumps(data)
		
		if(playerID == 1):
			self.player1Connection.transport.write(data)
		if(playerID == 2):
			self.player2Connection.transport.write(data)
	

#Create connectionHandler and pass it to factories
gameHandler = GameHandler()
tempFactory = TempFactory(gameHandler)
player1Factory = Player1Factory(gameHandler)
player2Factory = Player2Factory(gameHandler)

#Listen For Connections from Work and direct to Command and Client Factories
reactor.listenTCP(32000, tempFactory)
reactor.listenTCP(32001, player1Factory)
reactor.listenTCP(32002, player2Factory)

#Start event loop
reactor.run()

