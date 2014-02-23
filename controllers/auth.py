from atools import *
from aactions import *
from controller import *

def login():
	form = auth.login()
	form.add_button(T('Lost Password'),getUrl('password_reset'),_class='btn')
	return dict(form=form)

def logout():
	auth.logout()
	redirect(getUrl('about'))
	return dict()

def register():
	hideFields (db.auth_user, ['image'])
	return dict(form=auth.register())

def password_reset():
	form = auth.request_reset_password()
	return dict(form=form);