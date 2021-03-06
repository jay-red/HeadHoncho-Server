import asyncio
import websockets
import os
from random import choice
from json import loads, dumps

#try:
#        await client.send( chr( OP_GAME ) + chr( 0x00 ) )
#except websockets.exceptions.ConnectionClosedOK:
#        print( "closed" )

#await game.send( chr( OP_JOIN ) + chr( nextUID ) + data )

class Player():
	def __init__( self, room, client ):
		self.room = room
		self.client = client
		self.ready = False

class Room():
	def __init__( self ):
		self.p1 = None
		self.p2 = None

rooms = []
rooms.append( Room() )

players = {}

async def hh( client, path ):
	global rooms
	async for msg in client:
		data = loads( msg )
		op = data[ "op" ]
		packet = {}
		if op == "create":
			room = rooms[ 0 ]
			if room.p1 != None:
				try:
					await room.p1.client.close()
				except websockets.exceptions.ConnectionClosedOK:
					print( "closed" )
			if room.p2 != None:
				try:
					await room.p2.client.close()
				except websockets.exceptions.ConnectionClosedOK:
					print( "closed" )
			room.p1 = None
			room.p2 = None
		elif op == "join":
			packet[ "op" ] = "join"
			room = data[ "room" ]
			p =  Player( room, client )
			if room < len( rooms ):
				room = rooms[ room ]
				if room.p1 != None and room.p2 != None:
					packet[ "code" ] = 1
				else:
					packet[ "code" ] = 0
					players[ client ] = p
					if room.p1 == None:
						room.p1 = p
					else:
						room.p2 = p
			else:
				packet[ "code" ] = 2
			await client.send( dumps( packet ) )
		elif op == "ready":
			if client in players:
				p = players[ client ]
				if p.room < len( rooms ):
					room = rooms[ p.room ]
					p.ready = True
					if room.p1.ready and room.p2.ready:
						packet[ "op" ] = "start"
						try:
							await room.p1.client.send( dumps( packet ) )
						except websockets.exceptions.ConnectionClosedOK:
							print( "closed" )
						try:
							await room.p2.client.send( dumps( packet ) )
						except websockets.exceptions.ConnectionClosedOK:
							print( "closed" )
		elif op == "shoot":
			print( "shot" )
			if client in players:
				p = players[ client ]
				if p.room < len( rooms ):
					room = rooms[ p.room ]
					if room.p1 == p:
						try:
							await room.p2.client.send( dumps( data ) )
						except websockets.exceptions.ConnectionClosedOK:
							print( "closed" )
					elif room.p2 == p:
						try:
							await room.p1.client.send( dumps( data ) )
						except websockets.exceptions.ConnectionClosedOK:
							print( "closed" )

if( "PORT" in os.environ ):
	start_server = websockets.serve( hh, "0.0.0.0", os.environ[ "PORT" ] )
else:
	start_server = websockets.serve( hh, "0.0.0.0", 10419 )

asyncio.get_event_loop().run_until_complete( start_server )
asyncio.get_event_loop().run_forever()
