#coding=utf-8 
# ycat			 2015/12/29      create
import sys,os
import datetime
import utility
import mongodb  
import log

def write(userId,userName,object,desc,domain=""):
	ds = {}
	ds["starttime"] = utility.now()
	ds["userId"] = userId
	ds["userName"] = userName
	ds["object"] = object
	ds["desc"] = desc
	ds["domain"] = domain
	mongodb.insert("r_log",ds) 
	log.info(userId,desc,object)

#include代表是否只判断包含关系 
def check_desc(desc,include,index=0): 
	ds = mongodb.find("r_log")
	assert ds
	ds = ds.sort("_id",mongodb.DESCENDING).limit(index+1).skip(index)
	assert ds.next()
	if include:
		assert ds["desc"].find(desc)  != -1
	else:
		assert ds["desc"] == desc

#用于单元测试
def check_log(userId,userName,object,desc,index=0): 
	ds = mongodb.find("r_log")
	assert ds
	ds = ds.sort("_id",mongodb.DESCENDING).limit(index+1).skip(index)
	assert ds.next() 
	assert ds["desc"] == desc
	assert ds["userId"] == userId
	assert ds["userName"] == userName 
	assert ds["object"] == object
		
def clear_log():
	mongodb.drop_table("r_log")
	
#############################	unit test	###########################	
def test_write_log():
	import re
	mongodb.delete_many("r_log",{"userId":re.compile("^test")})
	write("test_user","姚舜","仪表xxx","this is a test log")
	assert 1 == mongodb.find("r_log").count
	write("test_user","姚舜","仪表xxx","this is a test log2")
	assert 2 == mongodb.find("r_log").count
	
	check_log("test_user","姚舜","仪表xxx","this is a test log",1)
	check_log("test_user","姚舜","仪表xxx","this is a test log2")
	
	check_desc("this is a test log",False,1)
	check_desc("log2",True) 
	mongodb.delete_many("r_log",{"userId":re.compile("^test")})
	
if __name__ == '__main__':
	utility.run_tests()
		