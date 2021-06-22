#coding=utf-8
# ycat			2020-5-24	  create
# 管理配置的路径 
import sys,os 
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import log,local
import utility
import webutility 
import json_codec 

g_pos_cfg = None

def _init(): 
	global g_pos_cfg
	if g_pos_cfg is not None:
		return g_pos_cfg
	proName = local.get("project","name")
	if utility.is_test():
		proName = "test" 
	pp = os.path.abspath(os.path.dirname(__file__)) + "/projects/" + proName + "/posCfg.json"
	if not os.path.exists(pp):
		g_pos_cfg = {}
		return g_pos_cfg
	g_pos_cfg = json_codec.load_file(pp)
	return g_pos_cfg

def getPosLen(mapId,loc):
	_init()
	if mapId in g_pos_cfg:
		if loc in g_pos_cfg[mapId]:
			return int(g_pos_cfg[mapId][loc])
	return 0

############## unit test ##############		
def testload():
	assert 100 == getPosLen("desai-all-20191223","AP34")
	assert 100 == getPosLen("desai-all-20191223","AP35")
	assert 0 == getPosLen("desai-all-20191223","AP334")
	assert 0 == getPosLen("desai-all-201912231","AP33")

if __name__ == '__main__':
	import utility 
	utility.run_tests()

