#coding=utf-8
# ycat			2018-8-2	  create
# 对外提供AGV的业务  
import sys,os 
import setup
import time
import threading

if __name__ == '__main__':
	setup.setCurPath(__file__)
import log
import utility
if utility.is_run_all():
	import main_agv
import webutility 
import json_codec as json
import local
import lock as lockImp
#import mapMgr

url = 'http://127.0.0.1:'+str(webutility.readPort()) 
g_current_app = None

class taskInfo:
	def __init__(self):
		pass

#相同的appName会释放之前的锁 
def init(appName=None):
	global g_current_app
	if not appName:
		appName = utility.app_name()
	if g_current_app == appName:
		return
	g_current_app = appName
	param = {}
	param['appName'] = g_current_app  
	while True:
		try:
			_http_get(url + '/api/agv/init', param)
			break
		except Exception as e:
			log.exception("agvApi.init",e)
		time.sleep(1)
	_init()
	
g_threadCheck = None
def _init():
	global g_threadCheck
	if g_threadCheck is None:
		g_threadCheck = threading.Thread(target=_checkFinish)
		g_threadCheck.start()
	
	

def _http_get(url,param):
	global g_current_app
	if g_current_app is None:
		raise Exception("agvApi is not inited") #需要先调用init 
	param['appName'] = g_current_app  
	r = webutility.http_get(url, param, timeout=45,writelog=False)
	result = json.load(r)
	if result["errorno"] != 0: 
		raise Exception(result["errormsg"])
	return result
		
def getMapList():
	param ={}
	param['appName'] = g_current_app  
	r = webutility.http_get(url + '/api/map/floor', param)
	return json.load(r)
		
def getTaskStatus(taskId):
	return _http_get(url + '/api/agv/taskStatus',{"taskId": taskId})["taskList"]
	

#请求AGV，返回agvId
#在调用release之前，别人都无法请求这台AGV 
#filterFunc接收agvId，可以实现自定义过滤，返回True|False 
def apply(taskId, mapId, loc,filterFunc=None,payload=None,timeout=15):
	exclude = []
	while True:
		param = {}
		param['loc'] = loc.strip()
		param['exclude'] = ",".join(exclude)
		param['autoLock'] = False
		param['mapId'] = mapId
		param['taskId'] = taskId
		param['timeout'] = timeout
		result = _http_get(url + '/api/agv/apply', param)
		assert 'agvId' in result
		agvId = result['agvId']
		if filterFunc and not filterFunc(agvId, mapId, loc, payload):
			exclude.append(agvId)
			continue
		_http_get(url + '/api/agv/lock', {"agv":agvId, "taskId":taskId}) 
		return agvId
	
def lock(agvId,taskId):
	_http_get(url + '/api/agv/lock', {"agv":agvId, "taskId":taskId}) 
	

def isAvailable(agvId):
	param = {}
	param['agv'] = agvId
	return _http_get(url + '/api/agv/isAvailable', param)["value"]
	
def startCharge():
	return _http_get(url + '/api/agv/startCharge', {})
	
#释放AGV 
def release(agvId,taskId,force=False):
	param = {}
	param['agv'] = agvId
	param['taskId'] = taskId
	param["force"] = force
	_http_get(url + '/api/agv/release', param)

global g_taskIdList
g_taskIdList = {} #taskId和callback函数的对应关系 
g_lock = lockImp.create("agvApi.g_lock")

#让AGV返航到待命点	
def goHome(agvId,force=False,timeout=30*60):
	param = {}
	param['agv'] = agvId 
	param["force"] = force
	param["timeout"] = timeout
	_http_get(url + '/api/agv/goHome', param)

def checkLineIdle(agvId,start,end):
	param = {}
	param['agv'] = agvId 
	param["start"] = start
	param["end"] = end
	return _http_get(url + '/api/agv/checkLineIdle', param)

#移动AGV到某个点 
#finishCallback是完成回调函数，包括失败或成功的完成，格式为 finishCallback(paramObj)
#stepCallback是每一步移动的回调函数，因为查询时差问题，step有可能会跳跃，格式为 stepCallback(paramObj,status),status为getTaskStatus()返回的值 
#paramObj是字典 
#paramObj输入时,要带上taskId
#paramObj输入时,可以带timeoutSec参数
#paramObj返回时会自动带上下面参数 
#paramObj["agv"] = agvId
#paramObj["loc"] = loc
#paramObj["taskId"] = taskId
#paramObj["result"] = 0
#paramObj["resultDesc"] = "success" 
#paramObj["seer_jackup"] = ""  顶升类型 JackLoad JackUnload
#paramObj["recognize"] = ""  是否识别货架
def move(agvId,loc,finishCallback,paramObj,stepCallback=None):
	assert "taskId" in paramObj
	paramObj['agv'] = agvId
	paramObj['loc'] = loc.strip()
	if "timeoutSec" not in paramObj:
		paramObj["timeoutSec"] = 10*60
	global g_taskIdList,g_lock
	lockImp.acquire(g_lock)
	t = taskInfo()
	t.taskId = paramObj['taskId']
	t.finishCallback = finishCallback
	t.params = paramObj
	t.ticks = utility.ticks()
	t.step = 0
	t.stepCallback = stepCallback
	g_taskIdList[t.taskId] = t
	lockImp.release(g_lock)
	try: 
		_http_get(url + '/api/agv/move', paramObj)
	except:
		lockImp.acquire(g_lock)
		del g_taskIdList[paramObj['taskId']]
		lockImp.release(g_lock)
		raise
		
def moveJackup(agvId,loc,finishCallback,paramObj,stepCallback=None,use_pgv=False,pgv_type =1,recognize=False):
	paramObj["seer_jackup"] = "JackLoad"
	paramObj["recognize"] = recognize
	paramObj["use_pgv"] = use_pgv
	paramObj["pgv_type"] = pgv_type
	return move(agvId,loc,finishCallback,paramObj,stepCallback)
	
	
def moveJackdown(agvId,loc,finishCallback,paramObj,stepCallback=None):
	paramObj["seer_jackup"] = "JackUnload"
	paramObj["recognize"] = False
	return move(agvId,loc,finishCallback,paramObj,stepCallback)
	
def cancelTask(agvId):
	param = {"agv": agvId}
	return _http_get(url + "/api/agv/cancel",param)
	
def getAgvStatusList(mapId):
	param = {}
	param['mapId'] = mapId
	return _http_get(url + '/api/agv/agvStatusList', param)
	
def getAgvStatus(agvId):
	param = {}
	param['agv'] = agvId
	return _http_get(url + '/api/agv/status', param)

def setChargeState(agvId,value):
	param = {}
	param['agv'] = agvId
	param['value'] = value
	return _http_get(url + '/api/agv/setChargeState', param)
	
def getChargeState(agvId):
	param = {}
	param['agv'] = agvId
	return _http_get(url + '/api/agv/getChargeState', param)
	
	
def isLocked(agvId,taskId=None):
	param = {}
	param['agv'] = agvId
	if taskId:
		param['taskId'] = taskId
	return _http_get(url + '/api/agv/isLocked', param)
	
	
def _checkFinish():
	global g_taskIdList,g_lock
	timeout = local.getfloat("ctrl","apiTimeoutSec",600.0)*1000
	while not utility.is_exited():
		try:
			if g_taskIdList == {}:
				continue
			rr = []  
			steps = []
			ids = ",".join(g_taskIdList.keys())
			status = getTaskStatus(ids)
			lockImp.acquire(g_lock)		
			for taskId in status.keys():
				if taskId not in g_taskIdList:
					continue
				t = g_taskIdList[taskId] 
				if utility.ticks() - t.ticks > timeout:
					log.warning("run taskId",taskId,"timeout,",timeout/1000.," seconds")
					t.params["result"] = False
					t.params["resultDesc"] = "taskId %s timeout"%taskId 
					rr.append(t)
					continue
				s = status[taskId]
				if s is None:
					continue
				t.status = s
				if s["status"] == "finish": 
					t.params["result"] = s["success"]
					t.params["resultDesc"] = s["exception"] 
					rr.append(t)
				elif t.stepCallback is not None and s["step"] != t.step:
					t.step = s["step"]
					steps.append(t)
			lockImp.release(g_lock)
			
			for t in steps: 
				try:
					t.stepCallback(t.params,t.status)
				except Exception as e:
					log.exception("agvApi step callback",e)
			
			for t in rr: 
				try:
					t.finishCallback(t.params)
				except Exception as e:
					log.exception("agvApi finish callback",e)
					
			lockImp.acquire(g_lock)
			for t in rr:
				if t.taskId in g_taskIdList:
					del g_taskIdList[t.taskId] 
			lockImp.release(g_lock)
			time.sleep(0.5)
		except Exception as ee:
			log.exception("checkFinish",ee)
			time.sleep(0.5)
	
########## 外围设备相关 ##########
#返回读输入IO列表 [True,False,....]
def readIO(agvId):
	param = {}
	param['agv'] = agvId
	result = _http_get(url + '/api/agv/readIO', param) 
	return result["data"]

#清除输出IO 
def clearIO(agvId):
	param = {}
	param['agv'] = agvId
	_http_get(url + '/api/agv/clearIO', param)
		
		
#设置写IO 
#id		:	number DO的id号, 从0开始 
#status	: 	boolean true为高电平,false为低电
def writeIO(agvId,id,status):
	pparam = {}
	param['agv'] = agvId
	param['id'] = id
	param['status'] = status
	_http_get(url + '/api/agv/writeIO', param)

################## unit test ##################
def test():
	taskId = "ycattest111111"
	init("ycat_test")
	agvId = apply(taskId=taskId, mapId="shuqin",loc="LM1")
	pp = {"t":1}
	pp["taskId"] = taskId
	print("apply",agvId)
	def stepCallback(param,status):
		print("step",param,status)
		
	def finishCallback(param):
		print("finishCallback",param)
	 
	move(agvId,loc="LM6",finishCallback=finishCallback,paramObj=pp,stepCallback=stepCallback)
	import time
	time.sleep(100)

if __name__ == '__main__':
	test()
	

