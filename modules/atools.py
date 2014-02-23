"""
General purpose getters and tools.
"""

def getImage (image):
	"""
	Gets an image or gets a default image if the image does not exist.

	Keyword Arguments:
	image -- file path of the image to get

	Return Values:
	out -- file path of the image
	    -- file path of a default image if the image does not exist
	"""

	from gluon import URL

	out = URL('static', 'images/default.png')
	if image is not None and image is not '':
		out = URL('default', 'download', args=image)

	return out

def getGame (args):
	"""
	Takes an argument and tries to get a row from db.game with it.

	Keyword Arguments:
	args -- url argument that corresponds to an id of a game

	Return Values:
	out -- row corresponding to the game
	    -- none if a game could not be retrieved or the argument is invalid
	"""

	from gluon import current
	db = current.db

	#There needs to be at least 1 argument
	if len(args) == 0:
		return None

	#The argument should be an integer
	if not args(0).isdigit():
		return None

	#Get the current game information referenced by the argument
	game_id = int(args(0))
	out = db.game(game_id)

	return out

def getGameStats (game):
	"""
	Gets statistics about the game.

	Keyword Arguments:
	game    -- row representing the current game

	Return Values:
	out -- dictionary containing game statistics
	    -- 'id'      id of the game
	    -- 'rules'   string representing the type of the game (Assassins or Humans v. Zombies)
	    -- 'players' total number of players
	    -- 'alive'   number of players alive
	    -- 'dead'    number of players dead
	"""

	from gluon import current
	db = current.db

	players = db(db.player.game_id==game.id).select()

	out = {'id':0, 'players':0, 'alive':0}

	out['id']      = game.id
	out['players'] = len(players)

	dead    = 0
	notDead = 0

	for player in players:
		if player.status == 'DEAD':
			dead = dead+1
		else:
			notDead = notDead+1
	#End for player in players:

	out['alive'] = notDead
	out['dead']  = dead

	return out

def getUserInfo (game, user):
	"""
	Gets game related information about the current user.

	Keyword Arguments:
	game    -- row representing the current game
	user    -- row representing the current user

	Return Values:
	out -- dictionary containing game related information about the user
	    -- 'name'        current user's full name
	    -- 'host'        if the user is the host of the game
	    -- 'status'      status of the user as it appears in the database
	    -- 'joined'      weather the user has joined the game
	    -- 'player_id'   id of the player representing the user in this game
	    -- 'can_start'   the user can join the game
	    -- 'can_join'    the user can join the game
	    -- 'can_leave'   the user can join the game
	    -- 'can_suicide' the user can suicide
	"""

	from gluon import current
	db = current.db

	out = {'name':'name', 'host':False, 'status':'status', 'joined':False, 'player_id':-1}

	if user is None:
		return out

	#get the user's full name
	out['name'] = user.first_name + ' ' + user.last_name

	#check if the user is the host of this game
	if user.id == game.host_id:
		out['host'] = True

	#get the player representing the user in this game
	player = db((db.player.user_id==user.id) & (db.player.game_id==game.id)).select()

	#check if the user has joined this game 
	if len(player) > 0:
		out['joined'] = True
		out['status'] = player[0].status
		out['player_id'] = player[0].id

	return out

def getPlayers (game):
	"""
	Gets a sorted list of players for a game.

	Keyword Arguments:
	game_id -- id of the game to get the players from

	Return Values:
	out -- list of dictionaries representing players
	    -- 'name'      the full name of the player
	    -- 'status'    the status of the player
	    -- 'player_id' the id of the player
	    -- 'user_id'   the auth_user id of the player
	    -- 'host'      True if the player is the host of the game
	"""

	from gluon import current
	db = current.db

	#Rows for the current player's list
	players = db( (db.player.user_id==db.auth_user.id) & (db.player.game_id==game.id) ).select(db.player.id, db.player.status, db.auth_user.id, db.auth_user.first_name, db.auth_user.last_name)

	out = []
	for player in players:
		row = {'name':'name', 'status':'ALIVE', 'player_id':'0', 'user_id':'0', 'host':False}

		row['name'] = player.auth_user.first_name + ' ' + player.auth_user.last_name
		row['status'] = player.player.status
		row['player_id'] = player.player.id
		row['user_id'] = player.auth_user.id

		#Check if the player is the host
		if db((db.game.host_id == player.auth_user.id) & (db.game.id == game.id)).count() > 0:
			row['host'] = True

		out.append(row)
	#End for player in players:

	#Sort players by status, then by name
	out.sort(key = lambda n: (n['status'], n['name']))

	return out

def hideFields (table, fields):
	"""
	Hides fields in a form.

	Keyword Arguments:
	table  -- the table in a database
	fields -- list of strings that represent fields within the database
	       -- ['field1', 'field2', 'etc...']
	"""

	#How does this even work?  Does this change some sort of global variable?

	for field in fields:
		field = table[field]
		field.readable = field.writable = False
	#End for field in fields:

	return

def resizeImage(table, id):
	"""
	Resizes an image to 200x200 pixels

	Keyword Arguments:
	table -- the table in a database
	id    -- if of a row within the database
	"""

	from gluon import current
	db = current.db
	request = current.request

	#HURRRR just put 'try' around everything
	try:
		#Get the image from the database
		thisImage=db(table.id==id).select()[0]

		import os, uuid
		from PIL import Image

		#Load the image from the uploads folder.
		im=Image.open(request.folder + '/uploads/' + thisImage.image)

		#Get the image dimenions
		width = im.size[0]
		height = im.size[1]

		#The image id taller than it is wide
		if width < height:
			top    = int((height-width)/2)
			bottom = int(height-((height-width)/2))
			im = im.crop((0,top,width,bottom))
		
		#The image is wider than it is tall
		elif height < width:
			left  = int((width-height)/2)
			right = int(width-((width-height)/2))
			im = im.crop((left,0,right,height))

		#Scale the image down to 200x200
		size = (200, 200)
		im.thumbnail(size, Image.ANTIALIAS)

		#Save the image
		im.save(request.folder + '/uploads/' + thisImage.image)
	except:
		return
	return

def generatePolaroid(attr):

	return
