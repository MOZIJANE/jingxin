#coding=utf-8
# ycat			2019-12-24	  create
# 管理配置的路径 
import sys,os 
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import log,local
import utility
import webutility 
import json_codec 

#class blockInfo:
#	def __init__(self): 
#		self.blockLines = []	#需要同时block的路径，advancedCurve列表
#		self.paths = [] 		#运行这些路径，需要block，advancedCurve列表
#		 
		
class blocks:
	def __init__(self):
		self.mapId = ""
		self.groups = [] #路径列表 
		self.posGroups = [] #位置列表
			
	def load(self,map): 
		proName = local.get("project","name")
#TODO		if utility.is_test():
#TODO			proName = "test" 
		pp = os.path.abspath(os.path.dirname(__file__)) + "/projects/" + proName + "/block.json"
		if not os.path.exists(pp):
			return False
		self.mapId = map.mapId
		bb = json_codec.load_file(pp)
		for b in bb: 
			if b["map"] != map.mapId:
				continue
			if b["enable"].lower() != "true":
				continue
			path = b["loc"]
			if len(path) == 0:
				continue
		 
			lines = self.getLines(map,path)
			if lines:
				self.groups.append(lines) 
				self.posGroups.append(path)
		return len(self.groups) != 0
		 
	def getLines(self,map,paths):
		ret = []
		for p1 in paths:
			for p2 in paths:
				if p1 == p2:
					continue
				line = map.getLine(p1,p2)
				if line:
					ret.append(line)
				line = map.getLine(p2,p1)
				if line:
					ret.append(line)
		for l in ret:
			l.isOneway = True
			l.isDeadend= True
		return ret 
		
	def getGroup(self,line):
		ret = []
		for g in self.groups:
			if line in g:
				ret += g
		return ret
		
	#取经过的点 
	def getGroupByPos(self,line):
		ret = []
		for i,g in enumerate(self.posGroups):
			if line.startPosName in g:
				ret += self.groups[i]
			if line.endPosName in g:
				ret += self.groups[i]
		return list(set(ret))
	
		

############# unit test #############
def testload(): 
	import mapMgr 
	m = mapMgr.mapInfo.load("big") 
	b = blocks()
	assert b.load(m)
	assert b.mapId == "big" 
	assert [str(s) for s in b.groups[0]] == ['LM59->LM60', 'LM60->LM59', 'LM59->LM58', 'LM58->LM59', 'LM60->LM59', 'LM59->LM60', 'LM58->LM59', 'LM59->LM58']
	g = b.getGroup(m.getLine("LM60","LM59"))
	assert g == b.groups[0][:]
	g = b.getGroup(m.getLine("AP819","LM59"))
	assert len(g) == 0

if __name__ == '__main__':
	import utility 
	utility.run_tests()

