#coding = utf-8
#lizhenwei		2017-08-30		create
#手柄按键配置
import os,sys
import json

import setup
currentPath = os.path.dirname(__file__)
if __name__ == '__main__':
	setup.setCurPath(__file__)

def _initKeyPosMap():
	keyPosMap = {}
	for i in range(6):
		key = i+1
		r,c = divmod(i,3)
		keyPosMap[key] = "%d%d"%(r,c)
	for i in range(24) :
		r,c = divmod(i,4)
		r += 2
		key = 7 + i
		keyPosMap[key] = "%d%d"%(r,c)
	keyPosMap[41] = "81"
	keyPosMap[42] = "82"
	return keyPosMap
	
def _initKeyNameMap():
	keyNameMap = {}
	keyNameMap["00"] = "test"			#轨迹
	keyNameMap["01"] = "stop"				#停止
	keyNameMap["02"] = "reset"				#复位
	keyNameMap["10"] = None
	keyNameMap["11"] = None
	keyNameMap["12"] = None
	keyNameMap["20"] = "pageUp"				#选择上10行
	keyNameMap["21"] = "itemUp"				#选择上1行
	keyNameMap["22"] = "itemDown"			#选择下1行
	keyNameMap["23"] = "pageDown"			#选择下10行
	keyNameMap["30"] = "locate"				#定位
	keyNameMap["31"] = "stepUp"				#到上一步
	keyNameMap["32"] = "stepDown"	 		#到下一步
	keyNameMap["33"] = "updateCoord"		#更新坐标
	keyNameMap["40"] = "rForward"			#r轴正运动
	keyNameMap["41"] = "yForward"			#y轴正运动
	keyNameMap["42"] = "zUp"				#z轴抬起
	keyNameMap["43"] = "wireBack"			#退锡
	keyNameMap["50"] = "xBack"				#x轴负运动
	keyNameMap["51"] = None
	keyNameMap["52"] = "xForward"			#x轴正运动
	keyNameMap["53"] = "wireForward"		#送锡	
	keyNameMap["60"] = "rBack"				#r轴负运动
	keyNameMap["61"] = "yBack"				#y轴负运动
	keyNameMap["62"] = "zDown"				#z轴下降
	keyNameMap["63"] = 	"tempUp"			#升温
	keyNameMap["70"] = "speedMicro"			#r速度1级
	keyNameMap["71"] = "speedLow"			#r速度2级
	keyNameMap["72"] = "speedHigh"			#r速度3级
	keyNameMap["73"] = "tempDown"			#降温
	keyNameMap["81"] = "airBlow"			#吹气
	keyNameMap["82"] = "ironAir"			#烙铁的气缸
	return keyNameMap

def saveKeyCfg(keyName):
	f = open(currentPath + '/stickKeyCfg.cfg','w')
	json.dump(keyName, f, indent = 4, sort_keys=True,)
	f.close()
	
def loadKeyCfg():
	try:
		f = open(currentPath + '/stickKeyCfg.cfg','r')
		keyName = json.load(f)
		f.close()
	except:
		keyNameMap = _initKeyNameMap()
		saveKeyCfg(keyName)
	return keyName
	
def getCommandName():
	r = []
	for k, v in keyNameMap().items():
		if v:
			r.append(v)
	return r
	
g_keyPosMap = None
g_keyNameMap = None
g_pressDelayMs = 500

def keyPosMap():
	global g_keyPosMap
	if not g_keyPosMap:
		g_keyPosMap = _initKeyPosMap()
	return g_keyPosMap
	
def keyNameMap():
	global g_keyNameMap
	if not g_keyNameMap:
		g_keyNameMap = loadKeyCfg()
	return g_keyNameMap
	

if __name__ == "__main__":
	g_keyNameMap = _initKeyNameMap()
	saveKeyCfg()
	loadKeyCfg()
	assert getCommandName()
	