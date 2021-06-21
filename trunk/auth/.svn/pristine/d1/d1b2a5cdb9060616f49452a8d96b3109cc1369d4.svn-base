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
import utility
import datetime 

def add(user):
	cond = {"datetime":{"$lt":utility.now() - datetime.timedelta(hours=12)}}
	db.delete_many("r_session",cond)
	data = {}
	data["datetime"] = utility.now()
	data.update(user)
	return str(db.insert("r_session",data).inserted_id)

def delete(sessionId):
	db.delete_one("r_session",{"_id":sessionId})
	
def load(sessionId):
	data = db.find_one("r_session",{"_id":db.ObjectId(sessionId)})
	if data is None:
		raise scadaUtility.AuthException("找不到Session="+sessionId)
	return data 
	 
if __name__ == '__main__':
	pass
