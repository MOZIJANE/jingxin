# coding: utf-8
# author: ycat
# date: 2018-05-28
# desc: 用户管理
import sys
import os
import datetime
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import mongodb as db
import utility
import rlog,log
import meta
import _session
import authApi

def getUser(userId, pwd, domain):
	isAdmin = False
	if userId == "root" and meta.password.scramble(pwd) == "729969d6854f8ca9e4cbd8ce11b48b80":		
		data = {}
		data["_id"] = "root"
		data["uname"] = "root"
		data["name"] = "超级管理员"
		data["domain"] = domain
		data["role"] = []
		data["enable"] = True
		data["password"] = ""
		isAdmin = True
	else:
		cond = {"uname": userId,"domain":domain,"$or":[{"password":meta.password.scramble(pwd)},{"password":pwd}]}
		data = db.find_one("u_user",cond)
		if data and len(data["role"]):
			data["role"] = db.find("u_role",{"_id" : {"$in": [ db.ObjectId(x) for x in data["role"]] }}).list()
			for r in data["role"]:
				if r["isAdmin"]:
					isAdmin = True
					break
	if data:
		data["isAdmin"] = isAdmin
		if not data["enable"]:
			raise Exception("用户已被禁用")
	return data

	
def login(userId,pwd,domain):
	ret = getUser(userId,pwd,domain)
	if ret is None:	
		log.error("login error:",userId,pwd,domain)
		raise Exception("用户名或密码错误")
	ret["userId"] = ret["uname"]
	del ret["_id"]
	del ret["uname"]
	del ret["password"]		
	ret["session"] = _session.add(ret)
	rlog.write(userId,ret["name"],"系统","登陆成功",domain)
	return ret

def logout(sessionId):
	data = _session.load(sessionId)
	_session.delete(sessionId)
	rlog.write(data["userId"],data["name"],"系统","退出登陆",data["domain"])

#========================================== unit test ==========================================
def testGetUser():
	import re
	db.delete_many("u_user",{"uname":re.compile("ycattest.*")})  
	db.delete_many("u_role",{"name":"ycattest","domain":"test"})  
	roleId = db.insert("u_role",{"name":"ycattest","isAdmin":False,"domain":"test","operation":["gateway.view"
	,"gateway-gatewaySetUp.edit"]}).inserted_id
	roleId = str(roleId)
	
	db.insert("u_user",{"enable":True,"uname":"ycattest111","name":"测试用户","domain":"test","password":"123456","role":[]})
	db.insert("u_user",{"enable":True,"uname":"ycattest222","name":"测试用户2","domain":"test","password":"04522abf42bb8ad979fe66948402bc0d","role":[roleId]})
	
	db.insert("u_user",{"enable":False,"uname":"ycattest223","name":"测试用户2","domain":"test","password":"04522abf42bb8ad979fe66948402bc0d","role":[roleId]})
	
	assert getUser("root","1751118@Comba1","comba") is None
	r = getUser("root","17518@Comba","comba")
	assert r is not None
	assert r["domain"] == "comba"
	
	assert getUser("ycattest111","123456","test1") is None
	assert getUser("ycattest111","123456","test")  
	assert getUser("ycattest222","123456","test") 
	u = getUser("ycattest222","123456","test") 
	assert 1 == len(u["role"])
	assert str(u["role"][0]["_id"])  == roleId
	assert  u["role"][0]["operation"]   == ["gateway.view","gateway-gatewaySetUp.edit"]
	
	try:
		assert getUser("ycattest223","123456","test")   
	except Exception as e:
		assert str(e).find("用户已被禁用") != -1
	
	data = login("root","17518@Comba","comba")
	
	assert data
	assert _session.load(data["session"])["isAdmin"] 
	id = data["session"]
	data = _session.load(data["session"])
	assert str(data["_id"]) == id
	assert data["userId"] == "root"
	assert data["domain"] == "comba"
	assert data["name"] == "超级管理员"
	
	data = login("ycattest111","123456","test")
	assert data
	  
	assert not _session.load(data["session"])["isAdmin"]
	id = data["session"]
	data = _session.load(data["session"])
	assert str(data["_id"]) == id
	assert data["userId"] == "ycattest111"
	assert data["domain"] == "test"
	assert data["name"] == "测试用户"
	
	data = login("ycattest222","123456","test")
	assert data 
	id = data["session"]
	ss = data["session"]
	data = _session.load(data["session"])
	assert str(data["_id"]) == id
	assert data["userId"] == "ycattest222"
	assert data["domain"] == "test"
	assert data["name"] == "测试用户2"
	assert len(data["role"]) == 1
	assert data["role"][0]["operation"] == ["gateway.view","gateway-gatewaySetUp.edit"]
	
	try:
		login("test222","123451","test")
	except Exception as e:
		assert str(e) == "用户名或密码错误"
		
	try:
		login("test222","123456","test1")
	except Exception as e:
		assert str(e) == "用户名或密码错误"
	
	_session.load(ss)	
	logout(ss)
	try:
		_session.load(ss)
		assert 0
	except Exception as e:
		pass
	db.delete_many("u_role",{"name":"ycattest","domain":"test"})  
	db.delete_many("u_user",{"uname":re.compile("ycattest.*")}) 
	
	 
if __name__ == '__main__':
	utility.run_tests() 
	



