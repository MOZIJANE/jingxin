#coding=utf-8
# ycat			2017-11-01	  create
# AGV的控制Mock 
import sys,os
import time
import threading 
import json
import uuid
import queue
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import utility
import enhance	
import lock
g_lock = threading.RLock()

alarmEvent = enhance.event()		#agvId,eventId,eventDesc 
locationEvent = enhance.event() #agvId,locationId(需要调用getSysLoc反向取位置)
g_locOccupy = {}
g_agvs = {}

#finishCallback参数： finishCallback(obj)
#obj会自动带上下面三个参数 
#obj["agv"] = agvId
#obj["result"] = 0
#obj["resultDesc"] = "success"
@lock.lock(g_lock)
def init(count=3):
	global g_agvs,g_locOccupy
	g_locOccupy = {}
	g_agvs = {}
	for i in range(count):
		g_agvs["agv_mockAgv"+str(i+1)] = ""
	
def wait():
	global g_threads,g_error
	for t in g_threads:
		t.join() 
	if g_error:
		raise g_error
	g_threads.clear()
	
def fini():
	wait()
	
def getAgvLoc(locId):
		return "agv_"+locId
	
def getSysLoc(locId):
	assert locId.find("agv_") != -1
	return locId[4:]

#系统的agvId转成第三方AgvId
def getAgvId(sysAgvId):
	return getAgvLoc(sysAgvId)

#第三方agvId转成系统的AgvId	
def getSysAgvId(agvId):
	return getSysLoc(agvId)
	 
g_threads =[]
g_resultQueue = queue.Queue()
g_timeout = 1

def setTimeout(timeout):
	global g_timeout
	g_timeout = timeout

def setFailed(result,resultDesc):
	global g_resultQueue
	g_resultQueue.put((result,resultDesc))

def getResult():
	global g_resultQueue
	if g_resultQueue.empty():
		return 0,"success"
	else:
		return g_resultQueue.get_nowait()
	
g_error = None
def _run(func,*param):
	def threadFunc():
		try:
			func(*param)
			locationEvent.emit("agv1",1.0,2.0,3.0,4.0)	
		except Exception as e:
			global g_error
			g_error = e
	t = threading.Thread(target=threadFunc)
	global g_threads
	t.start()
	g_threads.append(t)
	
def getAgv():
	global g_agvs
	for a in g_agvs:
		if g_agvs[a] == "":
			g_agvs[a] = "occupy"
			return a
	return None

@lock.lock(g_lock)
def isOccupy(loc):
	global g_locOccupy
	if loc not in g_locOccupy:
		return False
	if g_locOccupy[loc] != "":
		print(loc,"is occuied by ",g_locOccupy[loc])
	return g_locOccupy[loc] != ""
	
@lock.lock(g_lock)
def getLoc(loc):
	global g_locOccupy
	if loc not in g_locOccupy:
		return None
	return g_locOccupy[loc]

@lock.lock(g_lock)	
def apply(locId):
	return getAgv()
	
@lock.lock(g_lock)
def call(agvId,locId,finishCallback,obj):
	global g_locOccupy
	locId = getAgvLoc(locId)
	
	@enhance.catch
	def callFunc(obj,a): 
		ll = getLoc(locId)
		if ll:
			assert ll.find("agv") == -1
		global g_timeout
		time.sleep(g_timeout)
		#obj["agvTaskId"] = uuid.uuid1()
		obj["agv"] = getSysAgvId(a)
		result = getResult()
		obj["result"] = result[0]
		obj["resultDesc"] = result[1]
		if result[0] == 0:
			g_locOccupy[locId] = a
		if finishCallback:
			finishCallback(obj)
	_run(callFunc,obj,agvId)
	return getSysAgvId(agvId)

#带货架运输 
@lock.lock(g_lock)
def moveCart(agvId,cartId,locId1,locId2,finishCallback,obj):	
	global g_locOccupy
	locId = getAgvLoc(locId2)
	agvId2 = getAgvId(agvId)
	
	@enhance.catch
	def moveFunc(agvId2,obj):
		for l in g_locOccupy:
			if g_locOccupy[l] == agvId or g_locOccupy[l] == cartId:
				g_locOccupy[l] = ""
		global g_timeout
		time.sleep(g_timeout)
#		assert not isOccupy(locId)
		g_locOccupy[locId] = cartId
		freeAgv(getSysAgvId(agvId2))
		#obj["agvTaskId"] = uuid.uuid1()
		obj["agv"] = getSysAgvId(agvId2)
		result = getResult()
		obj["result"] = result[0]
		obj["resultDesc"] = result[1]
		if finishCallback:
			finishCallback(obj)
	_run(moveFunc,agvId2,obj)
	
#不带货架运输 
@lock.lock(g_lock)
def move(agvId,locId,finishCallback,obj):	
	global g_locOccupy
	locId = getAgvLoc(locId)
	agvId = getAgvId(agvId)
	
	@enhance.catch
	def moveFunc(agvId,obj):
		for l in g_locOccupy:
			if g_locOccupy[l] == agvId:
				g_locOccupy[l] = ""
		global g_timeout
		time.sleep(g_timeout)
		assert not isOccupy(locId)
		g_locOccupy[locId] = agvId
		#obj["agvTaskId"] = uuid.uuid1()
		obj["agv"] = getSysAgvId(agvId)
		result = getResult()
		obj["result"] = result[0]
		obj["resultDesc"] = result[1]
		if finishCallback:
			finishCallback(obj)
	_run(moveFunc,agvId,obj)
	
@lock.lock(g_lock)
def freeLoc(loc):
	global g_locOccupy
	print("free",getAgvLoc(loc))
	g_locOccupy[getAgvLoc(loc)] = ""
	
#释放对agv的占用 
@lock.lock(g_lock)
def freeAgv(agvId):
	agvId = getAgvId(agvId)
	for l in g_locOccupy:
		if g_locOccupy[l] == agvId:
			g_locOccupy[l] = ""
			print("free ",agvId)
	if agvId not in g_agvs:
		enhance.showTrace() 
	assert g_agvs[agvId]
	g_agvs[agvId] = ""
	
def cancelPutCart(agvId,loc1,finishCallback,obj):
	freeAgv(agvId)
	obj["agv"] = agvId 
	obj["result"] = 0
	obj["resultDesc"] = ""
	if finishCallback:
		finishCallback(obj)
	
@lock.lock(g_lock)
def findAgv(agvId):
	global g_locOccupy
	for l in g_locOccupy:
		if g_locOccupy[l] == agvId:
			return l
	return None
	
@lock.lock(g_lock)
def findCart(cartId):
	global g_locOccupy
	for l in g_locOccupy:
		if g_locOccupy[l] == cartId:
			return l
	return None
	
@lock.lock(g_lock)
def clear():
	global g_locOccupy
	g_locOccupy = {}
	
@lock.lock(g_lock)
def printLoc():
	global g_locOccupy
	if len(g_locOccupy) ==0:
		print("[Empty]")
		return
	s = "["
	for l in g_locOccupy:
		if g_locOccupy[l] != "":
			s += (l+" = "+g_locOccupy[l]+", ")
	s += "]\n"
	print(s)
	
################# unit test #################
def te1stThread():
	global g_locOccupy
	tt = []
	for i in range(20):
		def threadFunc1():
			global g_locOccupy
			while 100:
				g_locOccupy = []
				time.sleep(0.01)
			
		def threadFunc2():
			while 100:
				global g_locOccupy
				for i in range(1000):
					g_locOccupy["test"+str(i)] = i
				time.sleep(0.01)
		t = threading.Thread(target=threadFunc1)
		t.start()
		tt.append(t)
		t = threading.Thread(target=threadFunc2)
		t.start()
		tt.append(t)
	for t in tt:
		t.join()
	g_locOccupy.clear()
	
def testAgvMap():
	init()
	assert getSysAgvId("agv_mockAgv1") == "mockAgv1"
	assert getSysAgvId("agv_mockAgv2") == "mockAgv2"
	assert getSysAgvId("agv_mockAgv3") == "mockAgv3"
	
	assert getAgvId("mockAgv1") == "agv_mockAgv1"
	assert getAgvId("mockAgv2") == "agv_mockAgv2"
	assert getAgvId("mockAgv3") == "agv_mockAgv3"
	a1 = getAgv()
	a2 = getAgv()
	a3 = getAgv() 
	freeAgv(getSysAgvId(a1))
	freeAgv(getSysAgvId(a2))
	freeAgv(getSysAgvId(a3))
	fini() 

def testLoc(): 
	assert getSysLoc("agv_loc1") == "loc1"
	assert getSysLoc("agv_loc2") == "loc2"
	assert getAgvLoc("loc1") == "agv_loc1"
	assert getAgvLoc("loc2") == "agv_loc2"
	
temp = None

def testcall():
	init()
	def finish(obj):  
		global temp
		temp = getAgvId(obj["agv"])  
		
	call("loc1",finish,obj={})
	fini() 
	printLoc() 
	assert findAgv(temp) == getAgvLoc("loc1")
	
def testmoveCart():
	global g_locOccupy
	init()
	def finish(obj):  
		global temp 
		assert findAgv(getAgvId(obj["agv"])) == getAgvLoc("loc1")
		moveCart(obj["agv"],"cart4","loc2",finish2,obj={})

	def finish2(obj): 
		global temp
		temp = obj["agv"]
		print("in finish2")
	call("loc1",finish,obj={})	
	
	fini() 
	printLoc() 
	assert findAgv(temp) is None
	assert g_locOccupy[getAgvLoc("loc2")] == "cart4"
	
def testmove():
	global g_locOccupy
	init()
	def finish(obj):  
		global temp 
		assert findAgv(getAgvId(obj["agv"])) == getAgvLoc("loc1")
		move(obj["agv"],"loc2",finish2,{})
		temp = getAgvId(obj["agv"])
 
	def finish2(obj):  
		global temp
		temp = getAgvId(obj["agv"])
		print("in finish2")
	
	call("loc1",finish,{})	
	
	fini() 
	printLoc()  
	assert findAgv(temp) == getAgvLoc("loc2")
	assert g_locOccupy[getAgvLoc("loc2")] == temp
	
if __name__ == '__main__':
	setTimeout(0.1)
	utility.run_tests()


