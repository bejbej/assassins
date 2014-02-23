from atools import *
from aactions import *
from controller import *

@auth.requires_login()
def settings():
	#Set the text and picture for the polaroid
	image = getImage(auth.user.image)

	hideFields (db.auth_user, ['id'])

	form=SQLFORM(db.auth_user, auth.user.id)
	form.add_class('assassins-form')

	if form.process().accepted:
		resizeImage(db.auth_user, form.vars.id)
		
		#update the session cache
		auth.user.first_name = form.vars.first_name
		auth.user.last_name = form.vars.last_name
		auth.user.image = form.vars.image
		redirect(getUrl('settings'))

	return dict(form=form, image=image)