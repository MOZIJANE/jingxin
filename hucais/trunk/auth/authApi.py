#coding=utf-8
# ycat			2017-10-20	  create
# session管理 
import sys,os
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import bottle
import mongodb as db
import scadaUtility
import rlog
import utility
import webutility
import datetime
import json
import meta as m
import log

#是否为系统管理员 
def isSysAdmin():
	return userId() == "root"

g_domain = None

def getDomain():
	global g_domain
	if g_domain is not None:
		return g_domain
	return data()["domain"]
	
def _getMetaDomain():
	if isSysAdmin():
		return ""
	else:
		return getDomain()
		
def _getOp(url):
	return "-".join(url.split("/")[2:])
	
def checkPermission():
	if "Location" not in bottle.request.headers:
		raise scadaUtility.AuthException("找不到Location参数")
	url = bottle.request.headers["Location"]
	p = _getOp(url)
	if not checkOp(p+".view"):
		raise scadaUtility.AuthException("异常权限访问")
	return checkOp(p+".edit")
	
def writeLog(object,desc):
	log.info(desc)
	d = data()
	rlog.write(userId=d["userId"],userName=d["name"],object=object,desc=desc,domain=d["domain"])
	return
	
m.getDomainFunc = _getMetaDomain
m.checkPermissionFunc = checkPermission
m.writeLogFunc = writeLog
g_sessionData = None
g_sessionId = None

def data():
	global g_sessionData,g_sessionId
	if g_sessionId != sessionId():
		g_sessionId = None
		g_sessionData = None
	if g_sessionData is None:
		data = json.loads(webutility.http_get("http://127.0.0.1:"+str(webutility.readPort())+"/api/auth/user",{"session":sessionId()}))
		if data["errorno"] == -1000:
			raise scadaUtility.AuthException(data["errormsg"])
		if data["errorno"] != 0:
			raise Exception(data["errormsg"])
		g_sessionData = data["session"]
		g_sessionId = sessionId()
	return g_sessionData

g_testSessionId = None

def sessionId():
	global g_testSessionId
	if g_testSessionId is not None:
		return g_testSessionId
	if "Session" not in bottle.request.headers:
		raise scadaUtility.AuthException("找不到Session参数")
	id = bottle.request.headers["Session"]
	if len(id) != 24:
		raise scadaUtility.AuthException("Session格式异常：",id)
	return id
	 
def checkOp(operation):
	if operation not in getOpertions():
		return True
	dd = data()
	if dd["isAdmin"]:
		return True
	for r in dd["role"]:
		if operation in r["operation"]:
			return True
	return False
	 
#写系统日志 
def writeLog(object,desc):
	rlog.write(userId(),userName(),object,desc,data()["domain"])
	
def userId(): 
	global g_userId
	if g_userId is not None:
		return g_userId
	return data()["userId"]
	
def userName(): 
	global g_userName
	if g_userName is not None:
		return g_userName
	return data()["name"]

g_userId = None
g_userName = None
g_opertions = {}
def getOpertions():
	global g_opertions
	if not len(g_opertions):
		g_opertions = db.find("c_operation").dict()
	return g_opertions

def setTest(sessionId,userId,userName=""):
	global g_userId,g_testSessionId,g_userName
	g_userId = userId
	g_testSessionId = sessionId
	if userName == "":
		g_userName = userId
	else:
		g_userName = userName

def unsetTest():
	setTest(None,None, None)	
	
########## unit test ##########
def testop():
	assert _getOp("/comba/mould/mouldInfo") == "mould-mouldInfo"
	assert _getOp("/comba/account/role") == "account-role"
	
#需要先运行main_auth.py
def testLogin():	
	setTest("5b0e51e6df46cb49b4e88d81","xxx","xxxxxxxx")
	try:
		data()
	except Exception as e:
		assert str(e).find("找不到Session=") != -1
	unsetTest()
	import authMgr
	d = authMgr.login("root","17518@Comba","Comba")
	s = d["session"] 
	setTest(s,"xxx","xxxxxxxx")
	dd = data()
	assert d["name"] == "超级管理员"
	assert d["userId"] == "root"
	assert d["role"] == []
	assert d["isAdmin"] 
	assert d["domain"] == "Comba"
	
	authMgr.logout(s)
	try:
		data()
	except Exception as e:
		assert str(e).find("找不到Session=") != -1
		
if __name__ == '__main__':
	utility.run_tests()
	#testLogin()
	
	
	
