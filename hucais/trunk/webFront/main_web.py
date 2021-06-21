#coding=utf-8 
# ycat			 2018/07/28      create
import sys,os,bottle  
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)

BASE_PATH = os.path.abspath(os.path.dirname(__file__)+"/../vue/dist") + "/"

@bottle.route('/<domain>/static/<path:path>')	
def get_domain_static_file(domain,path):
	return bottle.static_file(path,root=BASE_PATH+"static/")

@bottle.route('/static/<path:path>')	
def get_static_file(path):
	return bottle.static_file(path,root=BASE_PATH+"static/")
	 
@bottle.route('/<domain>')	
@bottle.route('/<domain>/')	 
@bottle.route('/<domain>/index')	 
def get_index(domain): 
	return bottle.static_file("index.html",root=BASE_PATH)
	
@bottle.route('/')	 
@bottle.route('/index')	 
def get_wrong_addr(): 
	return "<H3>地址不正确，需要带上域名</H3>"

#for uwsgi 
app = application = bottle.default_app()

if __name__ == '__main__':
	import webutility
	webutility.run()
else:
	#run in uwsgi
	pass 
