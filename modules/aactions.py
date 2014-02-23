"""
Functions with side effects.
"""

from atools import *

########## Actions Generally Invoked by the User ##########

def killPlayerCheck (player_id, user):
	"""
	Checks if the player is valid and that the user has permission to kill that player.  Performs the kill if everything is valid.

	Keyword Arguments:
	player_id  -- id of the player to be killed
	user       -- the user who is performing this action

	Return Values:
	True  -- The action was performed. 
	False -- The action was not performed.
	"""

	from gluon import current
	db = current.db

	#The user should exist
	if user is None:
		return False

	#The player should exist
	player = db.player(player_id)
	if player is None:
		return False

	#The game should exist
	#TODO: This is enforced at a database level?
	game = db.game(player.game_id)
	#if game is None:
	#	return False

	#the host has permission to edit the player
	if db((db.player.id==player.id)&(db.player.game_id==db.game.id)&(db.game.host_id==user.id)).count() > 0:
		pass
	#the player has permission to edit the player
	elif db.player(player.id).user_id == user.id:
		pass
	#no one else should be able to edit the player
	else:
		return False

	#reassign targets if necessary
	if game.game_status == 'STARTED':
		reassignTarget(player)
		updateGame(game)

	killPlayer(player)

	return True

def killPlayer (player):
	"""
	Sets a row from db.players to DEAD.  This eliminates or zombifies a player.

	Keyword Arguments:
	player -- the player to be killed
	"""

	#kill the player
	player.update_record(status = "DEAD")

	#Update the game
	#updateGame(player.game_id, player)

	return

def removePlayerCheck (player_id, user):
	"""
	Check if the player is valid and that the user has permission to remove that player.  Removes the player if everything is valid.

	Keyword Arguments:
	player_id -- id of the row in db.players
	user      -- row representing the current user who is performing this action

	Return Values:
	True  -- The action was performed. 
	False -- The action was not performed.
	"""

	from gluon import current
	db = current.db

	#The user should exist
	if user is None:
		return False

	#The player should exist
	player = db.player(player_id)
	if player is None:
		return False

	#The game should exist
	#TODO: This is enforced at a database level?
	game = db.game(player.game_id)
	#if game is None:
	#	return False

	#the host may not be kicked
	if game.host_id == player.user_id:
		return False
	#the host has permission to edit the player
	elif db((db.player.id==player.id)&(db.player.game_id==db.game.id)&(db.game.host_id==user.id)).count() > 0:
		pass
	#the player has permission to edit the player
	elif db.player(player.id).user_id == user.id:
		pass
	#no one else should be able to edit the player
	else:
		return False

	#reassign targets if necessary
	if game.game_status == 'STARTED':
		reassignTarget(player)
		updateGame()

	#kick the player
	removePlayer(player)

	return

def removePlayer (player):
	"""
	Deletes a row from db.player.  This removes the player from a game.

	Keyword Arguments:
	player -- the row representing the player that needs to be deleted
	"""

	from gluon import current
	db = current.db

	#update the game
	#updateGame(player.game_id, player)

	#kick the player
	db(db.player.id==player.id).delete()
	#player.delete()

	#TODO: Send the player an informational message.
	#You have been kicked from GAME_NAME.

	return

def deleteGameCheck (game_id, user):
	"""
	Checks if the game is valid and that the user has permission to delete that game.  Performs the delete if everything is valid.

	Keyword Arguments:
	game_id -- id of the row in db.game that needs to be deleted
	user    -- the user who is performing this action

	Return Values:
	True  -- The action was performed. 
	False -- The action was not performed.
	"""

	from gluon import current
	db = current.db

	#The user should exist
	if user is None:
		return False

	#The game should exist
	game = db.game[game_id]
	if game is None:
		return False

	#the host has permission to delete the game
	if db.game[game_id].host_id == user.id:
		pass
	#no one else should be able to delete the game
	else:
		return False

	#Perform the delete
	deleteGame(game)

	return True

def deleteGame (game):
	"""
	Deletes a row from db.game.  This deletes the game.

	Keyword Arguments:
	game -- the row representing the game that needs to be deleted
	"""

	from gluon import current
	db = current.db

	#Send each player in the game a message so they don't get confused about a game suddenly disappearing.
	#GAME_NAME was deleted by its host.

	db(db.game.id==game.id).delete()

	return

def startGameCheck (game_id, user):
	"""
	Checks if the game is valid and that the user has permission to start this game.  Performs the start if everything is valid.

	Keyword Arguments:
	game_id -- id of the row in db.game that needs to be started
	user    -- the user who is performing this action

	Return Values:
	True  -- The action was performed. 
	False -- The action was not performed.
	"""

	from gluon import current
	db = current.db

	#The game should exist
	game = db.game(game_id)
	if game is None:
		return False

	#Only the host has permission to start a game
	if game.host_id != user.id:
		return False

	#You can only start a game that has not started
	if game.game_status != 'NOT_STARTED':
		return False

	#The game needs at least 2 players
	gameStats = getGameStats(game)
	if gameStats['players'] < 2:
		return False

	startGame(game)

	return True

def startGame (game):
	"""
	Starts a game.

	Keyword Arguments:
	game_id  -- id of the game that needs to be started
	"""

	from random import shuffle
	from gluon import current
	db = current.db

	#Get the players of a game
	players = getPlayers(game)

	#Randomize the targets
	shuffle(players)

	#Update targets in database
	#The last player in the list targets the first player in the list
	targetPlayerId = players[0]['player_id']
	player = db.player(players[len(players)-1]['player_id'])
	player.update_record(target_player_id = targetPlayerId, status='ALIVE')

	#Each player targets the next player in the list
	for i in range (0, len(players)-1):
		targetPlayerId = players[i+1]['player_id']
		player = db.player(players[i]['player_id'])
		player.update_record(target_player_id = targetPlayerId, status='ALIVE')
	#End for i in range (0, len(players)-1):

	#Set the game as having started
	game.update_record(game_status = "STARTED")
	return

def addPlayerCheck (game_id, user):
	"""
	Checks if a player is able to join a game.  Performs the join if the game is valid.

	Keyword Arguments:
	game_id -- id of the row in db.game
	user    -- the user who is joining the game

	Return Values:
	True  -- The action was performed. 
	False -- The action was not performed.
	"""

	from gluon import current
	db = current.db

	#The user should exist
	if user is None:
		return False

	#The game should exist
	game = db.game[game_id]
	if game is None:
		return False

	#The user should not already be joined
	#Some action

	addPlayer(game, user)

	return True

def addPlayer (game, user):
	"""
	Adds a row to db.players.  This causes a player to join a game.

	Keyword Arguments:
	game_id -- id of the row in db.game
	user    -- the user who is joining the game
	"""

	from gluon import current
	db = current.db

	db.player.insert(game_id=game.id, user_id=user.id, status="ALIVE")

	#updateGame(game, player)

	return True

########## Actions to be performed as a result of game state changes ##########

def reassignTarget (player):
	"""
	Assigns player's target to whomever is targetting player.

	Keyword Arguments:
	player -- the player that is being removed form the chain
	"""

	from gluon import current
	db = current.db

	player2 = db(db.player.target_player_id == player.id).select()[0]
	player2.update_record(target_player_id = player.target_player_id)

	return

def updateGame (game):
	"""
	Checks if a game has reached it's finish conditon.  Finishes the game if so.

	Keyword Arguments:
	game -- row representing a game
	"""

	from gluon import current
	db = current.db

	#Only a started game can be finished
	if game.game_status != 'STARTED':
		return
	#The game is over only when there is one player left alive
	if db((db.player.game_id == game.id)&(db.player.status == 'ALVIVE')).count() > 1:
		return

	game.update_record(game_status = "FINISHED")
	return
