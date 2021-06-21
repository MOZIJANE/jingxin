# coding=utf-8
# ycat			2020-2-21	  create
# AGV类型管理  
import sys, os
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import utility 
import local,log
import json_codec as json

g_data = {}
g_cur_path = __file__

def has(type,key):
	if not g_data:
		_load()
	if type not in g_data:
		return False
	return key in g_data[type]

def get(type,key,default=None):
	try:
		if not g_data:
			_load()
		if key in g_data[type]:
			return g_data[type][key]
			
		if default is not None:
			return default
	except KeyError as e:
		log.error("agvType",type,key)
		raise e
	
def getStr(type,key,default=None):
	return str(get(type,key,default))
	
def getFloat(type,key,default=None):
	return float(get(type,key,default))
	
def getBool(type,key,default=None):
	r = str(get(type,key)).lower()
	if r == "1" or r == "true":
		return True
	if r == "0" or r == "false":
		return False
	if default is not None:
		return default
	raise ValueError(bool,r)
	

def _load():
	global g_data
	g_data.clear()
	proName = local.get("project","name")
	if utility.is_test():
		proName = "test"
	file = "projects/"+proName+"/agvType.cfg" 
	file = os.path.abspath(os.path.dirname(g_cur_path)) + "/" + file
	g_data = json.load_file(file)
	return g_data

############# unit test #############
def test_load():
	assert get("test","float_value") == 0.4
	assert get("test","int_value") == 0.7
	assert get("test","str_value") == "aaaaa"
	assert get("test","bool_value") == "True"
	assert getStr("test","int_value") == "0.7"
	assert getFloat("test","float_value") == 0.4
	assert getFloat("test","int_value") == 0.7
	assert getBool("test","bool_value") == True

if __name__ == '__main__': 	 
	utility.run_tests()
