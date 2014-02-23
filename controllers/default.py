# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################
from atools import *
from controller import *

########## Get Requests ##########

def user():
	redirect(getUrl('login'))

def index():
	redirect(getUrl('about'))
	return dict()

def login():
	redirect(getUrl('login'))
	return

def download():
	"""
	allows downloading of uploaded files
	http://..../[app]/default/download/[filename]
	"""
	return response.download(request,db)

def call():
	"""
	exposes services. for example:
	http://..../[app]/default/call/jsonrpc
	decorate with @services.jsonrpc the functions to expose
	supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
	"""
	return service()

def data():
	"""
	http://..../[app]/default/data/tables
	http://..../[app]/default/data/create/[table]
	http://..../[app]/default/data/read/[table]/[id]
	http://..../[app]/default/data/update/[table]/[id]
	http://..../[app]/default/data/delete/[table]/[id]
	http://..../[app]/default/data/select/[table]
	http://..../[app]/default/data/search/[table]
	but URLs must be signed, i.e. linked with
		A('table',_href=URL('data/tables',user_signature=True))
	or with the signed load operator
		LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
	"""
	return dict(form=crud())

def error():
	"""response.flash = T("Welcome to Assassins!")"""
	return dict(message=T('Hello World'))

def join():
	#Select all games as a list
	items = db(db.game.id > 0).select()

	return dict(items=items)

@auth.requires_login()
def create():
	from gluon.tools import Crud

	#Hide the fields that should not be accessable by the user
	hideFields (db.game, ['host_id', 'game_status', 'password', 'winner_id', 'rules'])

	#Run the form
	#form = SQLFORM(db.game)
	#form.add_class('assassins-form')
	#form.vars.host_id=auth.user.id

	#Create the form
	crud = Crud(db)
	crud.messages.submit_button = 'Create Game'
	form = crud.create(db.game)
	form.add_class('assassins-form')
	form.vars.host_id=auth.user.id

	#When the form is submitted, add the creator as a player and go to new game
	if form.process().accepted:
		addPlayer(form.vars.id, auth.user)
		resizeImage(db.game, form.vars.id)
		redirect(URL('game', 'detail', args=form.vars.id))

	return dict(form=form)
	
def verify():
	return dict()
