from atools import *
from aactions import *
from controller import *

########## Get Requests ##########

def detail():
	game = getGame(request.args)

	#Make sure the requested game is valid
	if game is None:
		redirect(getUrl('overview'))

	#Modules
	userInfo  = getUserInfo(game, auth.user)
	polaroid  = getGamePolaroid(game, userInfo, auth.user)
	btn       = getGameBtns(game, userInfo)
	players   = getPlayers(game)
	gameStats = getGameStats(game)

	return dict(game=game, players=players, btn=btn, polaroid=polaroid, gameStats=gameStats, userInfo=userInfo)

def overview():
	#Modules
	games = getCurrentPolaroid(auth.user)

	return dict(games=games)

@auth.requires_login()
def edit():
	#Make sure the requested game is valid
	game = getGame(request.args)
	if game is None:
		redirect(getUrl('overview'))

	#The current user should be the host of the game.
	if auth.user.id != game.host_id:
		redirect(getUrl('detail', request.args(0)))

	#Page information
	polaroid   = getEditgamePolaroid(game)
	players    = getPlayers(game)
	gameStats  = getGameStats(game)
	updateForm = getEditgameUpdateForm(game)

	return dict(game_id=game.id, polaroid=polaroid, players=players, gameStats=gameStats, updateForm=updateForm)

########## Post Requests ##########

def startgamepost():
	"""
	Receives a post request and starts a game.
	"""

	postdata = request.post_vars
	startGameCheck(postdata['game_id'], auth.user)
	return

def joingamepost():
	"""
	Receives a post request and joins a game.
	"""

	postdata = request.post_vars
	addPlayerCheck(postdata['game_id'], auth.user)
	return

def leavegamepost():
	"""
	Receives a post request and leaves a game.
	"""

	postdata = request.post_vars
	removePlayerCheck(postdata['player_id'], auth.user)
	return

def suicidepost():
	"""
	Receives a post request and leaves a game.
	"""

	postdata = request.post_vars
	killPlayerCheck(postdata['player_id'], auth.user)
	return

def killplayerpost():
	"""
	Receives a post request and kills a player.  Then refreshed the page.
	"""

	postdata = request.post_vars
	killPlayerCheck(postdata['player_id'], auth.user)
	return

def kickplayerpost():
	"""
	Receives a post request and kicks a player.  Then refreshed the page.
	"""

	postdata = request.post_vars
	removePlayerCheck(postdata['player_id'], auth.user)
	return

def deletegamepost():
	"""
	receives a post request and deletes a game.  Then refreshed the page.
	"""

	postdata = request.post_vars
	deleteGameCheck(postdata['game_id'], auth.user)

	return

########## Page Helpers ##########

def getCurrentPolaroid (user):
	"""
	Gets the information to be shown on the polaroids for the current games page.

	Keyword Arguments:
	user     -- row representing the current user

	Return Values:
	out -- list containing dictionary for each game the user is participating in.
	    -- 'image'  file path of the image to show
	    -- 'text1'  string of the name of the game
	"""

	from gluon import current
	db = current.db

	if user is None:
		return []

	#Get a join of all the games associated with a user_id
	games = db((db.player.user_id==user.id) & (db.player.game_id==db.game.id)).select()

	#The list that is being returned.
	out = []

	#Add an entry to the list for each game
	for game in games:

		userInfo = getUserInfo(game.game, user)

		row = {'game_id':'', 'image':'', 'text1':'', 'text2':'', 'accessory':'none'}

		row['game_id'] = game.game.id
		row['text2']   = game.game.name

		if game.game.game_status == 'NOT_STARTED':
			row['image'] = getImage(game.game.image)

		elif game.game.game_status == 'STARTED' and game.player.status == 'DEAD':
			row['image']  = getImage(user.image)
			row['text1']  = 'You are dead.'
			row['accessory'] = 'DEAD'

		elif game.game.game_status == 'STARTED' and userInfo['status'] != 'DEAD':
			player = db((db.player.user_id == user.id) & (db.player.game_id == game.game.id)).select()[0]
			targetPlayer = db.player(player.target_player_id)
			targetUser = db.auth_user(targetPlayer.user_id)
			row['image'] = getImage(targetUser.image)
			row['text1'] = targetUser.first_name + ' ' + targetUser.last_name
			row['accessory'] = 'TARGET'

		elif game.game.game_status == 'FINISHED':
			row['image'] = getImage(game.game.image)
			row['text1'] = 'Game Over!'

		#Add the row to the list
		out.append(row)
	#End for game in games:

	#Sort the games by alphabetical order of game name
	out.sort(key = lambda n: n['text2'] )

	return out

def getEditgamePolaroid (game):
	"""
	Gets the information to be shown on the polaroid for the edit game page.

	Keyword Arguments:
	game     -- row representing the current game

	Return Values:
	polaroid -- dictionary containing game related information about the user
	         -- 'image'  file path of the image to show
	         -- 'text1'  string of the name of the game
	"""

	polaroid = {'image':'', 'text1':'', 'text2':'', 'status':'status'}

	polaroid['image'] = getImage(game.image)
	polaroid['text2'] = game.name

	return polaroid

def getEditgameUpdateForm (game):
	"""
	Gets an update for the edit game page.

	Keyword Arguments:
	game -- row representing the current game

	Return Values:
	formUpdate -- web2py form
	"""

	from gluon import current, redirect, URL, SQLFORM
	db = current.db

	#Hide some fields of the form
	hideFields (db.game, ['id', 'rules', 'host_id', 'game_status', 'password', 'winner_id'])

	formUpdate = SQLFORM(db.game, game.id)
	formUpdate.add_class('assassins-form')

	if formUpdate.process().accepted:
		resizeImage(db.game, game.id)
		redirect(getUrl('edit', game.id))

	return formUpdate

def getGamePolaroid (game, userInfo, user):
	"""
	Gets the information to be shown on the polaroid for the game page.

	Keyword Arguments:
	game     -- row representing the current game
	userInfo -- dictionary representing game related information about the current user
	user     -- row representing the current user

	Return Values:
	polaroid -- dictionary containing game related information about the user
	         -- 'name'   the current user's full name
	         -- 'host'   if the user is the host of the game
	         -- 'status' the status of the user as it appears in the database
	         -- 'joined' weather the user has joined the game

	"""

	from gluon import current
	db = current.db

	polaroid = {'image':'', 'text1':'', 'text2':'', 'accessory':'none'}

	polaroid['text2'] = game.name

	if game.game_status == 'NOT_STARTED':
		polaroid['image'] = getImage(game.image)

	elif game.game_status == 'STARTED' and not userInfo['joined']:
		polaroid['image'] = getImage(game.image)
		polaroid['text1'] = 'The game has started.'

	elif game.game_status == 'STARTED' and userInfo['status'] == 'DEAD':
		polaroid['image']  = getImage(user.image)
		polaroid['text1']  = 'You are dead.'
		polaroid['accessory'] = 'DEAD'

	elif game.game_status == 'STARTED' and userInfo['status'] != 'DEAD':
		player = db((db.player.user_id == user.id) & (db.player.game_id == game.id)).select()[0]
		targetPlayer = db.player(player.target_player_id)
		targetUser = db.auth_user(targetPlayer.user_id)
		polaroid['image'] = getImage(targetUser.image)
		polaroid['text1'] = targetUser.first_name + ' ' + targetUser.last_name
		polaroid['accessory'] = 'TARGET'

	elif game.game_status == 'FINISHED':
		polaroid['image'] = getImage(game.image)
		polaroid['text1'] = 'Game Over'

	return polaroid

def getGameBtns (game, userInfo):
	"""
	Gets which buttons should be visible on the game page.

	Keyword Arguments:
	game     -- row representing the current game
	userInfo -- dictionary representing game related information about the current user

	Return Values:
	btn -- dictionary containing booleans for buttons
	    -- 'all'       Show the button pad
	    -- 'cantstart' Start Game button if there aren't enough players
	    -- 'start'     Start Game
	    -- 'join'      Join Game
	    -- 'leave'     Leave Game
	    -- 'target'    Target Eliminated
	    -- 'dead'      I have been eliminated
	    -- 'edit'      Edit Game
	"""

	btn = {'all':False, 'cantstart':False, 'start':False, 'join':False, 'leave':False, 'target':False, 'dead':False, 'edit':False}

	if userInfo['name'] == 'name':
		return btn

	if game.game_status == 'NOT_STARTED' and userInfo['host']:
		btn['all'] = True
		gameStats = getGameStats(game)
		if gameStats['players'] > 1:
			btn['start'] = True
		else:
			btn['cantstart'] = True

	if game.game_status == 'NOT_STARTED' and not userInfo['joined']:
		btn['all'] = True
		btn['join'] = True

	if not userInfo['host'] and userInfo['joined']:
		btn['all'] = True
		btn['leave'] = True

	if game.game_status == 'STARTED' and userInfo['joined'] and userInfo['status'] != 'DEAD':
		btn['all'] = True
		btn['target'] = True
		btn['dead'] = True

	if userInfo['host']:
		btn['all'] = True
		btn['edit'] = True

	return btn
