#/test/appadmin

# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

db = DAL('sqlite://storage.sqlite')
from gluon import current
current.db = db

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate, Recaptcha, Mail
auth = Auth(db)




auth.settings.extra_fields['auth_user']= [
	Field('image', 'upload', requires=IS_EMPTY_OR(IS_IMAGE()), autodelete=True),
	Field('theme', default='corkboard')
	]
auth.settings.captcha = Recaptcha(request,'6LfwzNgSAAAAAMmbmBYTtbCCd0EH39aPcT8QZqle', '6LfwzNgSAAAAANZOk80WPMjllGce5az1KfFa08Hc')
auth.settings.login_captcha = False 
## create a mailer for user verification
mail = auth.settings.mailer
mail.settings.server = 'smtp.gmail.com:587'
mail.settings.sender = 'webmaster.assassins@gmail.com'
mail.settings.login = 'webmasterassassins:uituituit'
## setup auth for email verification/reset
auth.settings.registration_requires_verification = True
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True
auth.messages.verify_email = 'Click on the link http://' + request.env.http_host + URL(r=request,c='default',f='user',args=['verify_email']) + '/%(key)s to verify your email'
auth.messages.reset_password = 'Click on the link http://' + request.env.http_host + URL(r=request,c='default',f='user',args=['reset_password']) + '/%(key)s to reset your password'
auth.settings.register_next = URL('default', 'verify')




## create all tables needed by auth if not custom tables
auth.define_tables()
db.auth_user.theme.requires = IS_IN_SET(('corkboard','hipster', 'other'))




db.define_table('game', 
	Field('name', default='Default Game', requires=IS_NOT_EMPTY()),
	Field('password', 'password'),
	Field('image', 'upload', default='', requires=IS_EMPTY_OR(IS_IMAGE()), autodelete=True),
	Field('location', requires=IS_NOT_EMPTY()),
	Field('expected_start_date', 'date', requires=IS_NOT_EMPTY()),
	Field('description', 'text', default='####Target Elimination\nEliminate your target by hitting his or her torso with a clean sock.\n\n####Safe Zones\nNowhere is safe.  However, be considerate of your surroundings.'),
	Field('host_id', 'reference auth_user'),
	Field('game_status', default='NOT_STARTED'),
	Field('rules', default='Assassins'),
	Field('winner_id', 'reference auth_user'),
	migrate = True
	)
db.game.game_status.requires = IS_IN_SET(('NOT_STARTED','STARTED','FINISHED'))
db.game.rules.requires = IS_IN_SET(('Assassins','Humans v. Zombies'))



#Player Table
#A player is an auth_user who has joined a specific game
db.define_table('player',
	Field('game_id', 'reference game'),
	Field('user_id', 'reference auth_user'),
	Field('target_player_id', 'reference player'),
	Field('status', default='ALIVE'), 
	migrate = True
	)
db.player.status.requires = IS_IN_SET(('ALIVE','DEAD', 'HALF_DEAD'))



db.define_table('event',
	Field('game_id', 'reference game'),
	Field('killer_id', 'reference auth_user'),
	Field('dead_id', 'reference auth_user'),
	Field('event_time', 'datetime', notnull=True), 
	migrate = True
	)
