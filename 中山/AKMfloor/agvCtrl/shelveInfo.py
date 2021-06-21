#coding=utf-8
#ycat 
#货架的管理 
import os,sys 
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import json_codec as json 
import utility
import local

g_shelves = None

def maxWidth():
	_load()
	return max(v["width"] for v in g_shelves.values())
	
def maxHeight():
	_load()
	return max(v["height"] for v in g_shelves.values())
	
def get(shelveId):
	_load()
	return g_shelves[shelveId]
	
def _load():
	global g_shelves
	if g_shelves is None:
		proName = local.get("project","name")
		if utility.is_test():
			proName = "test" 
		file = os.path.abspath(os.path.dirname(__file__))+ "/projects/"+proName+"/shelve.cfg" 
		if not os.path.exists(file):
			raise Exception("Can't find " +file)
		g_shelves = json.load_file(file)
	assert len(g_shelves) == 1
	for v in g_shelves.values():
		return v
	assert 0
	
	

############# unit test #############
def testload():
	w = width()
	h = height()
	assert w > 0.5
	assert h > 0.5
	assert h < 3
	assert w < 3
	
if __name__ == "__main__":   
	import utility
	utility.run_tests()
	
	
