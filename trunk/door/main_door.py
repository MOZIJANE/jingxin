import sys, os
import bottle
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import log
import webutility
import scadaUtility
import door.switchMgr as switchMgr


@scadaUtility.get('/api/switch/on')
def urlRelayopen():
	id= webutility.get_param("id")
	switchInfo= switchMgr.getDoor(id)
	switchInfo.open()
	return {}


@scadaUtility.get('/api/switch/off')
def urlRelayclose():
	id= webutility.get_param("id")
	switchInfo = switchMgr.getDoor(id)
	switchInfo.close()
	return {}


@scadaUtility.get('/api/switch/islock')
def urlRelayislock():
	id= webutility.get_param("id")
	switchInfo = switchMgr.getDoor(id)
	return switchInfo.islock()


#for uwsgi 
app = application = bottle.default_app()

if __name__ == '__main__':
	webutility.run()
else:
	pass