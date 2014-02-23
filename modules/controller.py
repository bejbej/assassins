"""
Keeps track of which controller is responsible for each page.
"""

from gluon import URL

def getUrl (page, arg1=''):

	table = {
		'edit'          :'game',
		'overview'      :'game',
		'detail'        :'game',
		'startgamepost' :'game',
		'joingamepost'  :'game',
		'leavegamepost' :'game',
		'suicidepost'   :'game',
		'killplayerpost':'game',
		'kickplayerpost':'game',
		'deletegamepost':'game',
		'join'          :'default',
		'create'        :'default',
		'settings'      :'user',
		'about'         :'help',
		'howtoplay'     :'help',
		'victory'       :'help',
		'login'         :'auth',
		'logout'        :'auth',
		'register'      :'auth',
		'password_reset':'auth'
	}

	if arg1 == '':
		return URL(table[page], page)
	return URL(table[page], page, args=arg1)
