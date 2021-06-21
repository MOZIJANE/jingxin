# coding: utf-8
# author: ycat
# date: 2017-11-15 
import sys
import os
import bottle
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import utility
import webutility
import scadaUtility
import json_codec
import bottle
import _session
import authMgr
 
@scadaUtility.post('/api/auth/login')
def urlLogin():  
	user = webutility.get_param("user")
	pwd = webutility.get_param("password")
	domain = webutility.get_param("domain")
	return authMgr.login(user,pwd,domain)
 
	
@scadaUtility.get('/api/auth/logout')
def urlLogout():
	session = bottle.request.headers["session"]
	return authMgr.logout(session)

@scadaUtility.get('/api/auth/user')
def urlGetUser():
	session = webutility.get_param("session")
	if not session:
		if "session" not in bottle.request.headers:
			raise scadaUtility.AuthException("取不到用户登录信息")
		session = bottle.request.headers["session"]
	return {"session":_session.load(session)}

#for uwsgi 
app = application = bottle.default_app()

if __name__ == '__main__':
	if webutility.is_bottle():
		utility.start()
	webutility.run()
else:
	utility.start()
 
