#coding=utf-8
# ycat			2017-12-20	  create
# 华太agv的驱动
import sys,os
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import log
import json
import driver.agv.wsClient as wsClient
import config
import queue
import enhance
import uuid
import threading
import lock
import utility
import json_codec
import time
import datetime
import ralarm
import mytimer
#websocket对象
g_ws = None

#读到的命令回复
g_readBuf = []

#位置事件
locationEvent = enhance.event()


#位置信息
g_loc = None

#小车映射表
g_agvMap = {}

class agvInfo:
	def __init__(self,agvId):
		self.agvId = agvId
		self.x = 0
		self.y = 0
		self.a = 0
		self.w = 0
		self.locked = False
		self.cartLoc = None
		self.updateTime=utility.now()

g_lockObj = threading.RLock()

class agvList:
	def __init__(self):
		self.lockObj = threading.RLock()
		self.agvs = {}

	def get(self,agvId):
		if agvId not in self.agvs:
			self.agvs[agvId] = agvInfo(agvId)
		return self.agvs[agvId]

	@lock.lock(g_lockObj)
	def isLocked(self,agvId):
		return self.get(agvId).locked

	@lock.lock(g_lockObj)
	def setPos(self,agvId,x,y,a,w):
		agv = self.get(agvId)
		agv.x = x
		agv.y = y
		agv.a = a
		agv.w = w
		agv.updateTime=utility.now()
		self.agvs[agvId]=agv

	@lock.lock(g_lockObj)
	def setLocked(self,agvId,status):
		self.get(agvId).locked = status

	@lock.lock(g_lockObj)
	def setCart(self,agvId,loc):
		self.get(agvId).cartLoc = loc

	def getCartLoc(self,agvId):
		return self.get(agvId).cartLoc

	def hasAgv(self):
		for a in self.agvs:
			if not self.agvs[a].locked:
				return True
		return False

#agv当前状态
g_agvList = agvList()

def init():
	global g_ws
	g_ws = wsClient.client()
	g_ws.onOpenCallback = onOpen
	g_ws.open(config.get("agvwebsocket","url"),onRecieve)

def fini():
	global g_ws
	if g_ws:
		g_ws.close()

g_snSeq = 0
g_seqLock = threading.RLock()

def getSn():
	global g_snSeq
	g_snSeq+=1
	return "%06d"%g_snSeq

@lock.lock(g_seqLock)
def send(topic,data):
	global g_ws
	d = data
	sn = getSn()
	d["sn"] = sn
	msg = json_codec.dump({"device":"table","topic":topic,"data":d})
	g_ws.send(msg)
	return sn

@lock.lock(g_lockObj)
def _get(sn):
	global g_readBuf
	now = utility.ticks()
	rr = []
	ret = None
	for i,n in enumerate(g_readBuf):
		if (now - n[0]) > 3600*1000:
			log.warning("delete timeout msg",n[1])
			rr.append(i)
		if "sn" in n[1]["data"] and n[1]["data"]["sn"] == sn:
			ret = n[1]
			del g_readBuf[i]
			return ret
	if len(rr):
		for i in reversed(rr):
			del g_readBuf[i]
	return None

@lock.lock(g_lockObj)
def _add(data):
	global g_readBuf
	g_readBuf.append((utility.ticks(),data))

def read(sn,type,timeoutSec=15,agvId=""):
	global g_readBuf
	start = utility.ticks()
	timeoutMilliSec = timeoutSec * 1000
	log.debug("正在等待命令结果，此命令有效时间为"+ timeoutSec.__str__()+ "小车"+ agvId + " 命令"+type+"，sn="+str(sn))
	while not utility.is_exited() and (utility.ticks() - start) < timeoutMilliSec:
		msg = _get(sn)
		if msg is not None:
			data = msg["data"]
			if type ==  data["type"]:
				currenttime=utility.ticks() - start
				log.debug("已经返回命令结果，此命令耗时"+ currenttime.__str__() + "小车"+ agvId + " 命令"+type+"，sn="+str(sn))

				return data
			else:
				log.warning("want",type,"drop",data)
		time.sleep(0.1)
	if	agvId!="":
		msg = "小车"+ agvId + " 命令超时"+type+"，sn="+str(sn)+",超时时间"+str(timeoutSec)+"秒"
	else:
		msg = "在登陆或请求小车阶段, 命令超时"+type+"，sn="+str(sn)+",超时时间"+str(timeoutSec)+"秒"
	log.warning(msg)

	raise Exception(msg)
 

@mytimer.interval(1000*60)
def checkAlive(expireTime=60):
	global g_agvList
	nowtime=utility.now()
	for agvinfoitem in g_agvList.agvs.values():
		if nowtime - agvinfoitem.updateTime> datetime.timedelta(seconds=expireTime):
			msg = agvinfoitem.agvId + "小车"+str(expireTime)+"秒无响应离线" 
			ralarm.alarm(agvinfoitem.agvId, 4005, msg)
			log.warning(msg)


def onRecieve(msg):
	data = json.loads(msg)
	if "data" in data:
		if isinstance(data["data"],str):
			data["data"] = json_codec.load(data["data"])

	if data["topic"] != "msg_reply":
		if data["topic"] == "pose":
			global g_agvList,locationEvent
			x,y,a,w = data["data"]["x"],data["data"]["y"],data["data"]["a"],data["data"]["w"]
			agvId= getSysAgvId(data["id"])
			g_agvList.setPos(agvId=agvId,x=x,y=y,a=a,w=w)
			agvNewInfo= g_agvList.get(agvId)
			ralarm.clear(agvId,4005)
			locationEvent.emit(agvNewInfo.agvId,x=agvNewInfo.x,y=agvNewInfo.y,a=agvNewInfo.a,w=agvNewInfo.w)
			return
		elif data["topic"] == "yaml":
			#获取地图配置信息
			#地图配置信息是页面登陆成功后服务器立即发送的
			return
		elif data["topic"] == "roadpath":
			#获取路径信息
			return
		elif data["topic"] == "posPositions":
			#位置信息更新
			#updateLoc(data["data"])
			return
		elif data["topic"] == "robotReset":
			#小车重置转盘

			return
		elif data["topic"] == "alarm":
			#小车电量变化，障碍物
			log.error(getSysAgvId(data["id"]),data["data"]["content"])
			return
	else:
		if "data" in data:
			if data["topic"] == "msg_reply" and data["data"]["type"] == "msg_robotbutton":
				#机器人上线通知，文档有错
				log.warning("agv online",data["data"]["uuid"])
				return
			elif data["topic"] == "msg_reply" and data["data"]["type"] == "msg_robotdownline":
				#机器人下线通知，文档有错
				log.error("agv offline",data["data"]["uuid"])
				return
		_add(data)


def getMissionType(type,srcLoc,destLoc):
	global g_loc
	readCfg() #TODO:ycat 稳定后去掉
	assert type == "get" or type == "put"
	for loc in g_loc:
		if destLoc[0:len(loc)] == loc:
			cfg = g_loc[loc]
			l = srcLoc+".A."+type
			if l in cfg:
				return destLoc+".A",cfg[l]
			l = srcLoc+"."+type
			if l in cfg:
				return destLoc,cfg[l]
			return destLoc,cfg[type]

	raise Exception("找不到位置配置%s:%s->%s"%(type,srcLoc,destLoc))


def readCfg():
	global g_loc,g_agvMap
	p = os.path.dirname(__file__)
	pp = "location.cfg"
	if p:
		pp = p+"/"+pp
	fp = open(pp,"r")
	g_loc = json.load(fp)
	fp.close()

	pp = "agv.cfg"
	if p:
		pp = p+"/"+pp
	fp = open(pp,"r")
	g_agvMap = json.load(fp)
	fp.close()

#系统的agvId转成华太AgvId
def getAgvId(sysAgvId):
	global g_agvMap
	return g_agvMap[sysAgvId]

#第三方agvId转成华太AgvId
def getSysAgvId(agvId):
	global g_agvMap
	for a in g_agvMap:
		if g_agvMap[a] == agvId:
			return a
	return None

def isLocked(agvId):
	global g_agvList
	return g_agvList.isLocked(agvId)

###########  华太的命令，如果出现异常，记得释放小车  ###########
def onOpen():
	global g_ws
	if g_ws.isConnected:
		readCfg()
		t = threading.Thread(target=_login)
		t.start()

def _login():
	try:
		sn = send("login",{"psd":2017,"name":"ycat"})
		data = read(sn,"login_reply")
		unlockAll()
	except Exception as e:
		log.exception("login failed",e)

def apply(locId):
	global g_agvList
	if not g_agvList.hasAgv():
		return None
	sn = send("applyRobot",{"nickname":locId,"type":0})
	data = read(sn,"msg_ApplyRobot",timeoutSec=15)
	if "replay" in data and data["replay"] != 1:
		raise Exception("应用小车失败1！"+locId)
	if "reply" in data and data["reply"] != 1:
		raise Exception("应用小车失败2！"+locId)
	agvId = getSysAgvId(data["id"])
	g_agvList.setLocked(agvId,True)
	return agvId


def reset(agvId):
	sn = send("robotReset", {"id": agvId})
	data = read(sn,"msg_robotReset",timeoutSec=20,agvId=agvId)

def unlock(agvId):
	global g_agvList
	loc = g_agvList.getCartLoc(agvId)
	if loc:
		#让小车从货架底下出来
		cancel(agvId,loc)
	agvId2 = getAgvId(agvId)

	g_agvList.setLocked(agvId,False)
	sn = send("reversal", {"id": agvId2})
	data = read(sn,"msg_reversal",agvId= agvId2)

	sn = send("unlock",{"id":agvId2})


	data = read(sn,"msg_unlock",agvId=agvId2)

def cancel(agvId,loc):
	move(agvId, loc + ".3")
def taskFinish(agvId):
	agvId2 = getAgvId(agvId)
	sn = send("reversal",{"id":agvId2})
	data = read(sn,"msg_reversal",agvId=agvId2)

#是否为货架点
def isCartLoc(loc):
	if loc == "begin_2":
		return True
	return loc[-2:] != "_2"

def move(agvId,loc,type=""):
	agvId2 = getAgvId(agvId)
	sn = send("target",{"id":agvId2,"nicktype":"取料","type":type,"nickname":loc,"nk":123})
	read(sn,"msg_RobotReached",timeoutSec=10*60,agvId=agvId2)
	log.info(agvId,"reached",loc)

def stop(agvId):
	agvId2 = getAgvId(agvId)
	sn = send("cancel",{"id":agvId2})
	read(sn,"msg_RobotReached",timeoutSec=1*60,agvId=agvId2)


def unlockAll():
	global g_agvMap
	for a in g_agvMap:
		unlock(a)

def mission(agvId,type):
	agvId2 = getAgvId(agvId)
	sn = send("mission",{ "id": agvId2, "content": "mission"+str(type)})
	data = read(sn,"msg_mission",timeoutSec=120,agvId=agvId2)
	cartId = None
	if type == 1:
		#失败发camera,workFail
		if data["content"] == "camera,big_offset":
			log.info("AGV="+agvId +"执行任务"+str(type)+"失败，货架偏移过大")
			raise Exception("AGV="+agvId +"执行任务"+str(type)+"失败，货架偏移过大")

		elif data["content"] == "camera,workFail":
			log.info("AGV="+agvId +"执行任务"+str(type)+"失败，二维码识别失败")
			raise Exception("AGV="+agvId +"执行任务"+str(type)+"失败，二维码识别失败")

		elif data["content"]=="mission1,workFail":
			log.info("AGV="+agvId +"执行任务"+str(type)+"失败，该位置没有货架?")
			raise Exception("执行任务" + str(type) + "失败，AGV=" + agvId + ", 原因:" + data["content"])
		else:
			cartId = data["content"][7:]
			return cartId
	if data["content"].find("workDone") == -1:
		raise Exception("执行任务"+str(type)+"失败，AGV="+agvId + ", 原因:"+data["content"])
	return cartId


########################
def test0():
	import time
	init()
	unlock("agv1")
	agvId = apply("st_2")
	popDown(agvId,"st_2")
	#moveEx(agvId,"st_2","down")
	#popUp(agvId,"st_2")
	#popDown(agvId,"st_2")
	#move(agvId,"lt_2")
	#popDown(agvId,"lt_2")
	unlock(agvId)
	fini()

def test1():
	import time
	init()
	unlock("agv1")
	loc2 = "st_2"
	loc1 = "lt_2"
	agvId = apply(loc1)
	moveEx(agvId,loc1,"up")

	popUp(agvId,loc1)
	time.sleep(4)

	moveEx(agvId,loc2,"down")
	popDown(agvId,loc2)
	unlock(agvId)
	fini()

def test2():
	import time
	init()
	unlock("agv1")
	loc1 = "st_2"
	agvId = apply(loc1)
	move(agvId,loc1,"up")
	#cancel(agvId,loc1)
	#move(agvId,loc1)

	unlock(agvId)
	fini()

def testisCartLoc():
	assert isCartLoc("seat1_1")
	assert not isCartLoc("seat1_2")
	assert isCartLoc("seat21_1")
	assert not isCartLoc("seat21_2")
	assert isCartLoc("begin_1")
	assert isCartLoc("begin_2")
	assert isCartLoc("begin_3")
	assert isCartLoc("stockA_row1_col2")
	assert isCartLoc("stockE_row1_col2")
	assert isCartLoc("stockB_row1_col0")


def testgetMissionType():
	assert getMissionType("get","","begin_1") == ("begin_1",3)
	assert getMissionType("get","","begin_2") == ("begin_2",4)
	assert getMissionType("put","","begin_1") == ("begin_1",4)
	assert getMissionType("put","","begin_2") == ("begin_2",3)

	assert getMissionType("get","","stockA_row1_col2") == ("stockA_row1_col2",3)
	assert getMissionType("get","","stockA_row1_col2") == ("stockA_row1_col2",3)
	assert getMissionType("get","","stockA_row6_col2") == ("stockA_row6_col2",4)
	assert getMissionType("get","","stockA_row6_col2") == ("stockA_row6_col2",4)

	assert getMissionType("put","begin_1","stockA_row13_col2") == ("stockA_row13_col2",4)
	assert getMissionType("put","begin_2","stockA_row13_col2") == ("stockA_row13_col2",4)
	assert getMissionType("put","begin_3","stockA_row5_col2") == ("stockA_row5_col2",3)
	assert getMissionType("put","begin_2","stockA_row5_col2") == ("stockA_row5_col2",3)

	assert getMissionType("put","begin_1","stockA_row1_col1") == ("stockA_row1_col1.A",3)
	assert getMissionType("put","begin_2","stockA_row9_col2") == ("stockA_row9_col2",3)
	assert getMissionType("put","begin_2","stockA_row7_col1") == ("stockA_row7_col1.A",3)

	assert getMissionType("put","begin_3","stockA_row1_col1") == ("stockA_row1_col1",3)
	assert getMissionType("put","begin_3","stockA_row9_col1") == ("stockA_row9_col1.A",3)

	assert getMissionType("get","stockA_row1_col1","seat1_1") == ("seat1_1",4)
	assert getMissionType("put","stockA_row1_col1","seat1_1") == ("seat1_1",4)
	assert getMissionType("get","stockA_row1_col1","seat16_1") == ("seat16_1",3)
	assert getMissionType("put","stockA_row1_col1","seat16_1") == ("seat16_1",4)

def methodreadtest():
	read("00027","abc",150,"AGV004")

def test_checkAlive():

	agvId='TESTAGV_01'
	g_agvList.setPos(agvId=agvId, x=0.1, y=0.5, a=2, w=5)
	time.sleep(5)
	checkAlive(expireTime=2)
	alarms= ralarm.getAlarm()
	str=agvId+'AGVOFFLINE'
	vv= alarms[str]
	assert vv

if __name__ == '__main__':
	#test2()
	#readCfg()
	#testisCartLoc()
	# testgetMissionType()
	test_checkAlive()


#[DEBUG]2018-01-30 14:11:46,946: ws rec: {"device":"table","topic":"msg_reply","id":"AGV_02","nickname":"","data":{"type":"msg_exceptionInfo","content":"moving_state,has_obstacle","sn":null}}










