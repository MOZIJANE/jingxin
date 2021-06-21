import sys, os
import bottle
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import log
import webutility
import scadaUtility
import utility 
#for uwsgi 
app = application = bottle.default_app()

if __name__ == '__main__': 
	webutility.run()
else:
	pass