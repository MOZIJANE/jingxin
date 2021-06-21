# coding=utf-8
# ycat			2018-8-2	  create
# Mock函数 
import sys, os
import datetime
import setup
import time
import json
import threading
import random
import PyQt5.QtGui
import math
if __name__ == '__main__':
	setup.setCurPath(__file__) 
import utility
import log
log.warning("use mockAgvCtrl")

SPEED = 0.05

TASK_STATUS_NONE=0
TASK_STATUS_WAITING=1
TASK_STATUS_RUNNING=2
TASK_STATUS_SUSPENDED=3
TASK_STATUS_COMPLETED=4
TASK_STATUS_FAILED=5
TASK_STATUS_CANCELED=6
 
g_agvs = dict()
g_disableBattery = True

def disableBattery():
	global g_disableBattery
	g_disableBattery = True

def addAgv(agvId,map,startPos,width,height):
	global g_agvs 
	g_agvs[agvId] = mockAgv(agvId,map,startPos)
	g_agvs[agvId].width = width
	g_agvs[agvId].height = height 
	return g_agvs[agvId] 
	
g_crush_list = set()

def normAngle(angle):
	while angle > 2*math.pi:
		angle -= 2.0 * math.pi 
	while angle < -2*math.pi:
		angle += 2.0 * math.pi 
	return angle
	
def checkLink(agvId):
	return True
 
	
class mockAgv:
	def __init__(self,agvId,map,startPos):
		self.map = map
		self.agvId = agvId
		self.jackDownStatus = 1
		
		self.startChargeTime = utility.ticks()					#开始充电或不充电的的时间  
		self.currentBatteryLevel = min(1.0,random.random()+0.5)	#开始的电量 
		
		self._startTick = utility.ticks()
		self.status = {}
		self.status["blocked"] = False
		self.status["emergency"] = False
		
		self.status["mode"] = 1
		self.status["time"] = 0
		self.status["total_time"] = 0
		self.status["x"] = 0
		self.status["y"] = 0
		self.status["vx"] = 0
		self.status["vy"] = 0
		self.status["w"] = 0
		self.status["area_ids"] = []
		
		self.status["DI"] = [False] * 16
		self.status["DO"] = [False] * 16
		self.status["DI_valid"] = ["True"] * 16
		self.status["fatals"] = []
		self.status["errors"] = []
		self.status["warnings"] = []
		self.status["ret_code"] = 0
		self.status["err_msg"] = "" 
		self.status["odo"] = 0
		self.status["confidence"] = 1
		self.status["loadmap_status"] = 1
		self.status["slam_status"] = 0
		self.status["reloc_status"] = 1 #TODO：跳过reloc流程 
		self.status["charging"] = False 
		
		self.status["task_type"] = 0
		self.status["task_status"] = 0
		self.status['angle'] = 0
		self.status["battery_level"] = 1
		self.setPos(startPos) 
		self.oldPos = None
		self.thread = None
		self.targetList = []
		self.unitId = None
		self.units = {}
		
	@property
	def mapId(self):
		return self.map.mapId
		
		
	def switchMap(self,mapId):
		import mapMgr
		assert self.map.mapId != mapId
		self.map = mapMgr.getMap(mapId)
		
	def getCurrentMap(self):
		return self.map.mapId
		
	#撞车判断 
	def _checkCrash(self):
		global g_crush_list
		if self.map.hasAgv(self.agvId):
			return False
			
		if self.agvId in g_crush_list:
			while True:
				log.error(self.agvId,"crush")
				time.sleep(2)
		
		if not self.map.getAgv(self.agvId):
			return
		my = self.map.getAgv(self.agvId).boundPath
		for a in self.map.agvs:
			if a.agvId == self.agvId:
				continue
			if a.boundPath.intersects(my):
				while True:
					log.error(self.agvId,"crush with",a.agvId)
					if a.agvId not in g_crush_list:
						g_crush_list.add(a.agvId)
					time.sleep(2)
		doors = self.map.doors
		for d in doors.doors.values():
			if d.on:
				continue
			for a in self.map.agvs: 
				if a.boundPath.intersects(d.boundPath.toFillPolygon(PyQt5.QtGui.QTransform())):
					while True:
						log.error(self.agvId,"crush with door",d.id) 
						time.sleep(2)
		import elevatorMgr
		pos = self.map.getPosByPoint(self.status["x"],self.status["y"])
		if not pos:
			return
		floor = elevatorMgr.getFloor(self.mapId,pos)
		if not floor:
			return 
		s = floor.readStatus()
		if s["isFinishOpen"] != 1:
			while True:
				log.error(self.agvId,"crush with elevator",str(floor)) 
				time.sleep(2)

	
	@property
	def x(self): 
		return self.status['x']

	@property
	def y(self): 
		return self.status['y']
		
	@property
	def angle(self): 
		return self.status['angle']
	
	#是否初始化完成 
	def checkInit(self):
		return 1
		
	def requireControl(self):
		return {"success": True}
		
	def releaseControl(self):
		return {"success": True}
	
	def reloc(self,pos): 
		self.status["reloc_status"] = 3
		if pos:
			self.setPoint(pos[0],pos[1],pos[2])
		#下面这句打开，定时器会冲突 
		#self.setPos(self.home)
	
	def confirmReloc(self):
		self.status["reloc_status"] = 1
		
	#### 机器人模拟操作 #### 
	@property
	def currentPosName(self):
		pos = self.map.getPosByPoint(self.status["x"],self.status["y"])
		if pos:
			return pos.name
		else:
			return ""
		
		
	@property
	def boundPath(self):
		r = PyQt5.QtGui.QTransform().rotateRadians(self.angle)
		t = PyQt5.QtGui.QTransform().translate(self.x,self.y)
		p = PyQt5.QtGui.QPainterPath()
		h = self.agvInfo.height
		w = self.agvInfo.width
		p.addRect(-h/2,-w/2,h,w) 
		return t.map(r.map(p))
		
	@property
	def blockPath(self):
		h = self.agvInfo.height
		w = self.agvInfo.width
		x = h/2
		y = self.y - w/2 - self.blockMargin[0]
		r = PyQt5.QtGui.QTransform().rotateRadians(self.angle)
		t = PyQt5.QtGui.QTransform().translate(self.x,self.y)
		p = PyQt5.QtGui.QPainterPath() 
		p.addRect(x,y,h,w) 
		return t.map(r.map(p))
		
		
	#根据位置名配置点位信息 
	def setPos(self,posName,ignoreDir=False): 
		p = self.map.getPos(posName) 
		r = None
		if not p.ignoreDir and  not ignoreDir:
			r = p.dir 
		self.setPoint(p.x,p.y,r)  
			
	def setPoint(self,x,y,dir):
		if self.status["x"] == 0 and self.status["y"] == 0:
			c = False
		else:
			c = True
		self.status["x"] = x
		self.status["y"] = y
		if dir is not None:	
			#v = dir%(3.14*2)
			#if v < 0:
			#	v += 3.14*2
			self.status["angle"] = normAngle(dir)
		if c:
			self._checkCrash()
		
	
	def turnTo(self,angle,waitTime):   
		r1 = normAngle(self.angle)
		r2 = normAngle(angle)
		#print(math.degrees(r1),"turn to",math.degrees(r2))
		a = r1
		d = math.pi/18. 
		if r2 - r1 < math.pi:
			while abs(normAngle(a - r2)) > d:
				a += d
				self.setPoint(self.x,self.y,a)
				time.sleep(waitTime)
		else: 
			while abs(normAngle(a - r2)) > d:
				a -= d 
				self.setPoint(self.x,self.y,a)
				time.sleep(waitTime) 
		return self.setPoint(self.x,self.y,angle)
	 
	def moveLine(self,startPos,endPos,waitTime):
		step = 0
		line = self.map.getLine(startPos,endPos)
		assert line
		pp = line.ptrList
		d = 0
		if line.backward: 
			d = math.pi
		for p in pp:  
			if step == 0:
				a = self.turnTo(p[2]+d,waitTime)  
			self.setPoint(p[0],p[1],p[2]+d) 
			self.status["odo"] += 0.1
			step+=0.1 
			self._checkCrash()
			time.sleep(waitTime) 
		self.setPos(endPos,True) 
		self._checkCrash()
	
	def moveFunc(self):
		while not utility.is_exited():
			self._checkCrash()
			if len(self.targetList) == 0:
				time.sleep(1)
				continue
			loc = self.targetList.pop(0)
			self.move(loc)
			
	
	@property
	def enableBattery(self):
		global g_disableBattery  
		return not g_disableBattery
	
	def move(self,posName):
		print("mock:",self.agvId,"start ->",posName)
		#assert self.status["task_status"] != 2 #"RUNNING"
		self.status["task_type"] = 3
		self.status["task_status"] = 2 #"RUNNING"
		self.status["target_id"] = posName
		self.status["vx"] = 0.5
		self.status["vy"] = 0.3
		self.status["w"] = 0.2
		if self.batteryLevel == 0 and self.enableBattery:
			log.error(self.agvId,"电量不足",self.batteryLevel)
			return
		
		if self.currentPosName == posName:
			log.error("mock:",self.agvId,"原地移动",self.currentPosName)
			#TODO: self.status["task_status"] = 0
			return
			
		target = self.map.getPos(posName)
		_,paths,_,_ = self.map.getPathSingle(self.currentPosName,posName,None)
		if len(paths) == 0:
			log.error("mock:",self.agvId,"路径不存在",self.currentPosName+"->"+posName)
			return
		waitTime = SPEED
		for i in range(len(paths)-1):
			self.moveLine(paths[i],paths[i+1],waitTime=waitTime)
			 
		old = self.status["charging"]
		if target.className == "ChargePoint":
			self.status["charging"] = True
		else:
			self.status["charging"] = False
		if old != self.status["charging"]:
			self.startChargeTime = utility.ticks()
			self.currentBatteryLevel = self.status["battery_level"] 
		if len(self.targetList) == 0: 
			if not self.map.getPos(posName).ignoreDir:
				self.turnTo(self.map.getPos(posName).dir,waitTime) 
			self.status["task_status"] = 0 #"NONE"
			print("mock:",self.agvId,"finish move to",self.mapId+"."+posName)
		else:
			#if len(self.targetList) != 1:
			#	print("mock",self.targetList)
			#assert 1 == len(self.targetList)
			print("mock: ",self.agvId,"continue move to",self.mapId+"."+self.targetList[0])
		
	def jackUp(self):
		self.jackUpStatus = 1
		self.jackDownStatus = 0
		
	def jackDown(self):
		self.jackUpStatus = 0
		self.jackDownStatus = 1
		
	def rotationLeft(self):
		self.rotationLeftStatus = 1
		self.rotationRightStatus = 0
		self.rotationResetStatus = 0
		self.rotationClearStatus = 0
		
	def rotationRight(self):
		self.rotationLeftStatus = 0
		self.rotationRightStatus = 1
		self.rotationResetStatus = 0
		self.rotationClearStatus = 0
		
	def rotationReset(self):
		self.rotationLeftStatus = 0
		self.rotationRightStatus = 0
		self.rotationResetStatus = 1
		self.rotationClearStatus = 0
		
	def rotationClear(self):
		self.rotationLeftStatus = 0
		self.rotationRightStatus = 0
		self.rotationResetStatus = 0
		self.rotationClearStatus = 1
		
	def rollerLoad(self):
		if self.unitId in self.units:
			self.units[self.unitId]["rollerLoadStatus"] = 1
			self.units[self.unitId]["payload"] = 1
		
	def rollerUnload(self):
		if self.unitId in self.units:
			self.units[self.unitId]["rollerUnloadStatus"] = 1
			self.units[self.unitId]["payload"] = 0

	def rollerSetUnit(self,unitId):
		self.unitId = unitId
		if unitId not in self.units:
			self.units[unitId] = {"payload": 0,"rollerLoadStatus": 0 ,"rollerUnloadStatus": 0}

	def rollerLoadStatus(self,unitId):
		if unitId in self.units:
			return self.units[unitId]["rollerLoadStatus"]

	def rollerUnloadStatus(self,unitId):
		if unitId in self.units:
			return self.units[unitId]["rollerUnloadStatus"]

	def unitStatus(self,unitId):
		if unitId in self.units:
			return self.units[unitId]["payload"]
		return 0

	def rollerStop(self):
		for id in self.units:
			self.units[id]["rollerLoadStatus"] = 0
			self.units[id]["rollerUnloadStatus"] = 0

	def rollerReset(self):
		for id in self.units:
			self.units[id]["rollerLoadStatus"] = 0
			self.units[id]["rollerUnloadStatus"] = 0

	def rollerDeviceInfo(self):
		return {"hasUnloadAlarm": 0, "hasLoadAlarm": 0}

	def playAudio(agvId, name, loop):
		pass

	def resumeAudio(agvId):
		pass

	def stopAudio(agvId):
		pass

	@property
	def batteryLevel(self):
		if not self.enableBattery:
			return self.status["battery_level"]
		t = self.startChargeTime
		if self.status["charging"]:
			self.status["battery_level"] = min(1,(self.currentBatteryLevel+(utility.ticks()-t)/1000*0.1))
		else:
			self.status["battery_level"] = max(0,(self.currentBatteryLevel - (utility.ticks()-t)/1000*0.005)) 
		return self.status["battery_level"]
	
	#任务失败 
	def fail(self):
		self.status["task_type"] = 0
		self.status["task_status"] = 5#"FAILED"
		
	#取消任务 
	def cancel(self):
		self.status["task_type"] = 0
		self.status["task_status"] = 6#"CANCELED"
		
	def reboot(self):
		self._startTick = utility.ticks()
	
	def block(self):
		self.status["blocked"] = True
		
	def unblock(self):
		self.status["blocked"] = False
		
	def emergency(self,value):
		self.status["emergency"] = value
	
	def setDI(self,id,status):
		self.status["DI"][id]=status
	
	def alarm(self,type,code):
		assert type in ["fatals","errors","warnings"]
		if code not in self.status[type]:
			self.status[type].append(code)
		
	def clearAlarm(self,type):
		assert type in ["fatals","errors","warnings"]
		self.status[type] = []
	
	def error(self,errorCode,errorMsg):
		self.status["ret_code"] = errorCode
		self.status["err_msg"] = errorMsg
		
	#IO操作 
	def readIO(self): 
		return self.status["DI"]

	def clearIO(self):
		self.status["DO"] = [False] * 16

	def writeIO(self, id, status):
		self.status["DO"][id] = status
		
	def getStatus(self):  
		self.status["time"] = utility.ticks() - self._startTick
		self.status["total_time"] = utility.ticks() - self._startTick
		t = self.batteryLevel  
		return utility.clone(self.status)
	
	def uploadMap(self, data):
		print('mock:uploadMap to agv already!')

	def downloadMap(self, mapName):
		if mapName.find('.smap') == -1:
				mapName = mapName + '.smap'
		file_map = "projects/fastprint/" + mapName
		file_map = os.path.abspath(os.path.dirname(__file__)) + "/../../agvCtrl/" + file_map
		with open(file_map, 'r') as f:
			m = f.read()
			return m
	
	def clampOpen(self, direction):
		if direction == '1':
			self.units["clampLeft"] = 1

		elif direction == '2':
			self.units["clampRight"] = 1

	def clampClose(self, direction):
		if direction == '1':
			self.units["clampLeft"] = 2

		elif direction == '2':
			self.units["clampRight"] = 2

	def clampStatus(self, direction):
		direction = int(direction)
		if direction == 1:
			return self.units["clampLeft"]
		elif direction == 2:
			return self.units["clampRight"]


	def finishButtonStatus(self):
		return 1
		
def checkInit(agvId):
	if agvId not in g_agvs:
		return False
	return getAgv(agvId).checkInit()

def requireControl(agvId):
	return getAgv(agvId).requireControl()

def releaseControl(agvId):
	return getAgv(agvId).releaseControl()
	
def reloc(agvId,pos=None):
	getAgv(agvId).reloc(pos)

#确认定位正确 
def confirmReloc(agvId):
	getAgv(agvId).confirmReloc()
	
#def _loadAgvList():
#	with open(os.path.abspath(os.path.dirname(__file__)+"/../../agvCtrl/testagv.cfg") , 'r') as f:
#		aa = json.load(f) 
#		agvList = {}
#		for a in aa:
#			if aa[a]["enable"].lower() == "false":
#				continue
#			agvList[a] = aa[a]
#		return agvList

def setXY(agvId,x,y,angle):
	getAgv(agvId).setPoint(x,y,angle)
	return getAgv(agvId)

def setPos(agvId,pos):
	getAgv(agvId).setPos(pos)

 
def getAgv(agvId): 
	global g_agvs
	if agvId not in g_agvs:
		return None
	return g_agvs[agvId]
 
def cancelTask(agvId):
	getAgv(agvId).cancel()
 
	
def move(agvId, loc):
	agv = getAgv(agvId)
	agv.status["task_status"] = 2
	if agv.thread is None:
		agv.thread = threading.Thread(target=agv.moveFunc,name="mock.move")
		agv.thread.start()
		agv.targetList.append(loc)
	else:
		agv.targetList.append(loc)
	 
def goTargetAndDoWork(agvId, loc, operation, recognize=False,use_pgv=False,pgv_adjust_dist=False):
	move(agvId,loc)
	
def jackUp(agvId,speed=5000,distance=99999,loc=None):
	return getAgv(agvId).jackUp()

def jackDown(agvId,speed=5000,distance=99999,loc=None):
	return getAgv(agvId).jackDown()

def jackDownStatus(agvId):
	a = getAgv(agvId)
	if a is None:
		return None
	return {"status": a.jackDownStatus} 

def jackUpStatus(agvId):
	return {"status": getAgv(agvId).jackUpStatus} 


def rotationLeft(agvId,speed=10000,distance=47800):
	return getAgv(agvId).rotationLeft()


def rotationRight(agvId,speed=10000,distance=47800):
	return getAgv(agvId).rotationRight()


def rotationLeftStatus(agvId,target):
	return {"status": getAgv(agvId).rotationLeftStatus} 


def rotationRightStatus(agvId,target):
	return {"status": getAgv(agvId).rotationRightStatus} 

def rotationReset(agvId):
	return getAgv(agvId).rotationReset()
	
def rotationClear(agvId):
	return getAgv(agvId).rotationClear()

def rotationResetStatus(agvId):
	return {"status": getAgv(agvId).rotationResetStatus} 

def rotationClearStatus(agvId):
	return {"status": getAgv(agvId).rotationClearStatus} 
	
def statusPgv(agvId):
	return {"status": 1} 
	
def readIO(agvId): 
	return getAgv(agvId).readIO()


def clearIO(agvId):
	getAgv(agvId).clearIO()


def writeIO(agvId, id, status):
	getAgv(agvId).writeIO(id, status)

def readStatus1(agvId,param=None): 
	return getAgv(agvId).getStatus()

def switchMap(agvId, mapName):
	return getAgv(agvId).switchMap(mapName)

def uploadMap(agvId, data):
	return getAgv(agvId).uploadMap(data)

def downloadMap(agvId, mapName):
	return getAgv(agvId).downloadMap(mapName)
	
def getMapList(agvId):
	data = {}
	data["current_map"] = getAgv(agvId).getCurrentMap()
	data["maps"] = [getAgv(agvId).getCurrentMap(),] 
	return data


def clampStatus(agvId, direction):
	return {"status": getAgv(agvId).clampStatus(direction)}


def clampOpen(agvId, direction):
	return getAgv(agvId).clampOpen(direction)


def clampClose(agvId, direction):
	return getAgv(agvId).clampClose(direction)


def finishButtonStatus(agvId):
	return {"status": getAgv(agvId).finishButtonStatus()}



def rollerSetUnit(agvId, unitId):
	return getAgv(agvId).rollerSetUnit(unitId)


def rollerBackLoad(agvId):
	return getAgv(agvId).rollerLoad()


def rollerBackUnload(agvId):
	return getAgv(agvId).rollerUnload()


def rollerFrontLoad(agvId):
	return getAgv(agvId).rollerLoad()


def rollerFrontUnload(agvId):
	return getAgv(agvId).rollerUnload()


def rollerLoadStatus(agvId, unitId):
	return {"status": getAgv(agvId).rollerLoadStatus(unitId)}


def rollerUnloadStatus(agvId, unitId):
	return {"status": getAgv(agvId).rollerUnloadStatus(unitId)}


def unitStatus(agvId,unitId):
	return {"status": getAgv(agvId).unitStatus(unitId)}

def rollerStop(agvId):
	return getAgv(agvId).rollerStop()

def rollerReset(agvId):
	return getAgv(agvId).rollerReset()

def rollerDeviceInfo(agvId):
	return getAgv(agvId).rollerDeviceInfo()

def playAudio(agvId, name, loop):
	return getAgv(agvId).playAudio(name, loop)


def resumeAudio(agvId):
	return getAgv(agvId).resumeAudio()


def stopAudio(agvId):
	return getAgv(agvId).stopAudio()
	

# 用于单元测试
def setDI(agvId,id,status):
	getAgv(agvId).setDI(id,status)

def setDOs(agvId,id,status):
	return {"ret_code":0}


def getAllDO(agvId):
	return getAgv(agvId).status["DO"]
	
def getDO(agvId, id):
	return getAgv(agvId).status["DO"][id]

def clearDI(agvId):
	getAgv(agvId).status["DI"]=[False] * 16

def rotationDistanceStatus(agvId):
	return None

def readIOs(agvId):
	return {'DO':[{
		"id": 0,
		"source": "normal",
		"status": 1
	}, {
		"id": 1,
		"source": "normal",
		"status": 1
	}, {
		"id": 2,
		"source": "normal",
		"status": 1
	}, {
		"id": 3,
		"source": "normal",
		"status": 1
	}, {
		"id": 4,
		"source": "normal",
		"status": 1
	}, {
		"id": 5,
		"source": "normal",
		"status": 1
	}, {
		"id": 6,
		"source": "normal",
		"status": 1
	},{
		"id": 7,
		"source": "normal",
		"status": 1
	},{
		"id": 8,
		"source": "normal",
		"status": 1
	},{
		"id": 9,
		"source": "normal",
		"status": 1
	},{
		"id": 10,
		"source": "normal",
		"status": 1
	},{
		"id": 11,
		"source": "normal",
		"status": 1
	},{
		"id": 12,
		"source": "normal",
		"status": 1
	},{
		"id": 13,
		"source": "normal",
		"status": 1
	},{
		"id": 14,
		"source": "normal",
		"status": 1
	},{
		"id": 15,
		"source": "normal",
		"status": 1
	},{
		"id": 16,
		"source": "normal",
		"status": 1
	},{
		"id": 17,
		"source": "normal",
		"status": 1
	},{
		"id": 18,
		"source": "normal",
		"status": 1
	},{
		"id": 19,
		"source": "normal",
		"status": 1
	},{
		"id": 20,
		"source": "normal",
		"status": 1
	},{
		"id": 21,
		"source": "normal",
		"status": 1
	},{
		"id": 22,
		"source": "normal",
		"status": 1
	},{
		"id": 23,
		"source": "normal",
		"status": 1
	},{
		"id": 24,
		"source": "normal",
		"status": 1
	},{
		"id": 25,
		"source": "normal",
		"status": 1
	},{
		"id": 26,
		"source": "normal",
		"status": 1
	},{
		"id": 27,
		"source": "normal",
		"status": 1
	},{
		"id": 28,
		"source": "normal",
		"status": 1
	},{
		"id": 29,
		"source": "normal",
		"status": 1
	},{
		"id": 30,
		"source": "normal",
		"status": 1
	},{
		"id": 31,
		"source": "normal",
		"status": 1
	},{
		"id": 32,
		"source": "normal",
		"status": 1
	},{
		"id": 33,
		"source": "normal",
		"status": 1
	},{
		"id": 34,
		"source": "normal",
		"status": 1
	},{
		"id": 35,
		"source": "normal",
		"status": 1
	},{
		"id": 36,
		"source": "normal",
		"status": 1
	},{
		"id": 37,
		"source": "normal",
		"status": 1
	}],"DI":[{
		"id": 0,
		"source": "normal",
		"status": True,
		"valid": True
	}, {
		"id": 1,
		"source": "normal",
		"status": True,
		"valid": True
	}, {
		"id": 2,
		"source": "normal",
		"status": True,
		"valid": True
	}, {
		"id": 3,
		"source": "normal",
		"status": True,
		"valid": True
	}, {
		"id": 4,
		"source": "normal",
		"status": True,
		"valid": True
	}, {
		"id": 5,
		"source": "normal",
		"status": True,
		"valid": True
	}, {
		"id": 6,
		"source": "normal",
		"status": True,
		"valid": True
	}, {
		"id": 7,
		"source": "normal",
		"status": True,
		"valid": True
	}, {
		"id": 8,
		"source": "normal",
		"status": True,
		"valid": True
	}, {
		"id": 9,
		"source": "virtual",
		"status": True,
		"valid": True
	}]}

@utility.fini()
def fini():
	global g_agvs 
	for a in g_agvs.values():
		if a.thread:
			a.thread.join()
			
			
