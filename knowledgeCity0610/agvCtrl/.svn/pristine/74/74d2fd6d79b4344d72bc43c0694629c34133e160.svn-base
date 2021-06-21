#coding=utf-8
# ycat			2019-9-24	  create
# 提供agv电子门的管理 
import sys,os 
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import log
import utility
import webutility 
import json_codec as json
import matplotlib.pyplot as plt 
import ui.pltUtil
import PyQt5
import PyQt5.QtGui
import log 
import threading
import time
if utility.is_test():
	import elevator.elevatorApiMock as elevatorApi
else:
	import elevator.elevatorApi as elevatorApi
import lock as lockImp
import local
import alarm.aliveApi
g_lock = lockImp.create("elevatorMgr.lock")

class floorInfo: 
	def __init__(self,elevator,name,loc):
		self.id = name  
		self.elevator = elevator 
		index = loc.find(".")
		assert index != -1
		self.map = None
		self.mapId = loc[0:index]
		self.loc = loc[index+1:]		#对应LM点
		self.x = None						#LM点中心
		self.y = None			
		self.width = 0
		self.height = 0
		self.holded = False 
		self.drawObj = None
		self.textObj = None
		
	@property
	def agvId(self):
		if not self.map:
			return None
		return self.map.getPos(self.loc).agvId
		
	@property
	def elevatorName(self):
		return self.elevator.name
	
	def draw(self):  
		if self.x is None:
			return 
		s = self.status()
		if s is None:
			return
		lw = 4		
		if str(s["inFloor"]) == str(self.id):
			fcolor = "lightgreen"
			color = "red" 
			if s["isFinishOpen"] == 1: 
				color = "None" 
		else:
			color = "red"  
			fcolor = "lightgray"		
		if self.isBlocked and color != "None":
			color = "yellow"
		
		if s["isMaintain"] != "normal":
			color = "red"  
			fcolor = "red"
		
		if self.drawObj:
			self.drawObj.remove() 
		if self.textObj:
			self.textObj.remove()

		p = PyQt5.QtGui.QPainterPath() 
		p.addRect(-self.width/2.,-self.height/2.,self.width,self.height)   
		t = PyQt5.QtGui.QTransform().translate(self.x,self.y)
		p = t.map(p)
		fig = plt.figure(self.mapId)
		self.drawObj = ui.pltUtil.addPath(p,edgecolor=color,facecolor=fcolor,alpha=0.6,lw=lw) 
		t = "unblock\n"
		if self.isBlocked:
			t = "block by " + self.elevator.blockAgv + "\n" 
		t += "floor:" + str(s["inFloor"]) + "\n" 
		t += self.elevatorName + ("[holded]" if self.holded else "[unhold]")  
		self.textObj = fig.gca().text(self.x-self.width/2.+0.1,self.y-self.height/2.+0.3,t,color="g")

	
	@property
	def isBlocked(self):
		return self.elevator.isBlocked
		
	#协议要求：如果需要电梯开门，则需要一直发送电梯开门，目前定义时间为 500ms 发一次，具体时间根据测试情况， 需要关门则，不发开门指令即可，电梯开门不会强迫关门。 
	def checkOpen(self,force):  
		if force:
			#强制刷到最新状态 
			s = self.elevator.readStatus()
		else:
			s = self.elevator.getStatus() 
		if s is None:
			return False
		if s["isMaintain"] != "normal":
			log.warning(self.elevatorName,"status",s["isMaintain"])
			return False
		if str(s["inFloor"]) != str(self.id):
			self.holded = False
			#这里会产生很多次调用 
			self.elevator.goFloor(self.id)
			return False 
		self.holded = True
		for f in self.elevator.floors:
			if f.id != self.id:
				f.holded = False
		self.elevator.hold()
		if s["isRunning"] == 1:
			return False
		if s["isOpening"] == 1:
			return False
		return s["isFinishOpen"] == 1

	def checkClose(self): 
		self.holded = False 
		s = self.elevator.getStatus() 
		if s is None:
			return False
		if s["isMaintain"] != "normal":
			log.warning(self.elevatorName,"status",s["isMaintain"])
			return False
		if s["isOpening"] == 1:
			return False
		if s["isClosing"] == 1:
			return False
		if s["isFinishOpen"] == 1:
			self.elevator.unhold()
			return False
		#if s["isRunning"] == 1:
		#	return False
		return True 

	def status(self): 
		return self.elevator._status

	def __str__(self):
		return str(self.id) + "[" + self.mapId + "." + self.loc + "]"
		
	def _keepOpen(self):
		if not self.holded:
			return
		s = self.elevator.getStatus() 
		if s is not None:
			if str(s["inFloor"]) != str(self.id):
				self.elevator.goFloor(self.id)
				return
		self.elevator.hold()
	
		
class elevator:
	def __init__(self,name,cfg):
		self.name = name
		self.floors = []
		self.blockFloorId = None
		self.blockAgv = None
		self._status = None
		self._load(cfg) 
		self._alarmObj = alarm.aliveApi.aliveObj(moid=name, typeId=39999, desc="电梯离线异常", timeoutSecond=30,domain="agv")
	
	@property
	def agvId(self):
		for f in self.floors:
			a = f.agvId
			if a:
				return a
		return None
	
	#当前电梯在第几层 
	@property
	def floor(self):
		return self._floor
		
	@property
	def isBlocked(self):
		return self.blockAgv is not None
			
	def _load(self,cfg): 
		self.floors = []
		self._floor = None 
		if cfg["enable"].lower() != "true":
			return 
		for c in cfg["floor"]:  
			assert 1 == len(c)
			for k in c:
				f = floorInfo(self,int(k),c[k]) 
				f.width = cfg["width"]
				f.height = cfg["height"]
				assert self.findFloor(f.mapId) is None	#两个电梯门不能同一层楼  
				self.floors.append(f)
	
	def findFloor(self,mapId,loc=None):
		for f in self.floors:
			if mapId == f.mapId:
				if loc is None or loc == f.loc:
					return f
		return None
				
	def isLink(self,mapId1,mapId2):
		if self.findFloor(mapId1) and self.findFloor(mapId2):
			return True
		return False
		
		
	def draw(self,mapId):
		for f in self.floors:
			if mapId is not None and f.mapId != mapId:
				continue 
			f.draw()
		
	def get(self,mapId,loc):
		for f in self.floors:
			if f.mapId != mapId:
				continue
			if f.loc == loc:
				return f
		return None

	def __str__(self):
		ret = self.name + "\n"
		for f in self.floors:
			ret += "\t" + str(f) + "\n"
		return ret
		
	def updateMap(self,map):	 
		for f in self.floors:
			if f.mapId != map.mapId:
				continue
			f.map = map
			p = map.getPos(f.loc)
			f.x = p.x
			f.y = p.y
			
	def tryBlock(self,agvId,mapId,loc):
		f = self.findFloor(mapId,loc)
		assert f	
		for f in self.floors:
			if f.agvId is not None and f.agvId != agvId:
				return [f.agvId,]
				
		if self.blockAgv is None or self.blockAgv == agvId:
			return [] 
		return [self.blockAgv,]
		
	def block(self,agvId,mapId,loc):   
		if len(tryBlock(agvId,mapId,loc)):
			log.warning(agvId,"try to block",self.name,"failed, block by",self.blockAgv)
			return False  
		self.blockAgv = agvId
		self.blockFloorId = self.findFloor(mapId,loc)
		log.info(agvId,"block",self.name)
		return True
	
	def unblockForce(self,agvId):
		if self.blockFloorId:
			self.blockFloorId.holded = False
			self.blockAgv = None 
		else:
			#只会关闭一次，因为有时候会超时 
			self.unhold()
		self.blockFloorId = None
		log.info(agvId,"unblock elevator",self.name) 
	
	def unblock(self,agvId,mapId,loc): 
		if agvId == self.blockAgv:
			f = self.findFloor(mapId,loc)
			if not f:
				return 
			f.holded = False 
			self.unblockForce(agvId)
			#self.blockAgv = None 
			#self.blockFloorId = None
			#self.unhold()
			#log.info("elevator",self.name,"is unblock by",agvId,"at",mapId+"."+loc) 
		
	def keepOpen(self):
		for f in self.floors:
			f._keepOpen()
	
	def getStatus(self):
		return self._status
	
	def readStatus(self): 
		try:
			s = elevatorApi.status(self.name)
			lockImp.acquire(g_lock)
			self._status = s
			lockImp.release(g_lock)
			self._alarmObj.check()
			return s
		except Exception as e:
			log.error('Exception in readStatus of elevator:', e)
			return None
		
	#@lockImp.lock(g_lock)
	@utility.catch
	def unhold(self):
		return elevatorApi.unhold(self.name)
		
	#@lockImp.lock(g_lock)
	def goFloor(self,floorId):
		log.info(self.name,"go floor",self.blockAgv,self.blockFloorId) 
		try:
			return elevatorApi.goFloor(self.name,floorId)
		except Exception as e:
			log.error('Exception in goFloor of elevator:', e)

	#@lockImp.lock(g_lock)
	def hold(self):
		log.info(self.name,"hold door",self.blockAgv,self.blockFloorId) 
		elevatorApi.hold(self.name)
		
g_floors = None
g_elevators = None
g_thread = None
 
def _load():	
	global g_elevators,g_floors
	if g_elevators is not None:
		return
	g_elevators = {}
	g_floors = {}
	
	proName = local.get("project","name")
	if utility.is_test():
		proName = "test"
	
	file = os.path.abspath(os.path.dirname(__file__)+"/..") + "/agvCtrl/projects/"+proName+"/elevator.json"

	obj = json.load_file(file)
	for e in obj:
		if obj[e]["enable"].lower() != "true":
			continue
		g_elevators[e] = elevator(e,obj[e])
		for f in g_elevators[e].floors:
			g_floors[f.mapId+"."+f.loc] = f	
	g_thread = threading.Thread(target=keepOpenThread,name="elevator.keep")
	g_thread.start()
	
@utility.fini()
def fini():
	global g_thread
	if g_thread is not None:
		g_thread.join()

def updateMap(map): 
	_load()
	global g_elevators 
	for e in g_elevators.values():
		e.updateMap(map) 
			
def desc(): 
	global g_elevators
	_load()
	ret = ""
	for e in g_elevators.values():
		ret += str(e) + "\n"
	return ret
		
def draw(mapId=None):
	global g_elevators
	_load() 
	for e in g_elevators.values():
		e.draw(mapId)
			
#取出两个地图之间是否有电梯相连 
def getElevator(mapId1,mapId2):
	_load() 
	ret = []
	if mapId1 == mapId2:
		return ret
	for e in g_elevators.values():
		if e.isLink(mapId1,mapId2):
			ret.append(e)
	return ret
	
	
def getElevatorByMapId(mapId):
	global g_floors
	_load()	
	r = set()
	for f in g_floors.values():
		if f.mapId == mapId:
			r.add(f.elevator)
	return list(r)
	
#取得和这个mapId相关联的所有地图id 
def getMaps(mapId):
	_load() 
	r = set()
	ee = getElevatorByMapId(mapId)
	for e in ee:
		for f in e.floors:
			if f.mapId != mapId:
				r.add(f.mapId)
	return list(r)
	
	
#尝试取得电梯的占用权
@lockImp.lock(g_lock)
def tryBlock(agvId,mapId,loc):
	f = getFloor(mapId,loc) 
	if not f: 
		return []
	return f.elevator.tryBlock(agvId,mapId,loc)
	
	
#取得电梯的占用权 
@lockImp.lock(g_lock)
def block(agvId,mapId,loc):
	f = getFloor(mapId,loc) 
	if not f:
		return True
	if len(tryBlock(agvId,mapId,loc)) == 0:
		return f.elevator.block(agvId,mapId,loc)
	return False
	
	
#释放电梯控权 
@lockImp.lock(g_lock)
def unblock(agvId,mapId,loc):
	import agvList
	cur = agvList.getAgv(agvId).curTarget
	mapId = agvList.getAgv(agvId).mapId
	for e in g_elevators.values():
		if e.findFloor(mapId,cur) is not None:
			continue
		e.unblock(agvId,mapId,loc)
	
@lockImp.lock(g_lock)
def unblockByAgv(agvId):
	for e in g_elevators.values():
		if e.blockAgv == agvId:
			e.unblockForce(agvId)
			
@lockImp.lock(g_lock)
def isBlocked(agvId):
	for e in g_elevators.values():
		if e.blockAgv == agvId:
			return True
	return False
	
	
def getBlockAgv(mapId,loc):
	f = getFloor(mapId,loc)
	if f:
		return f.elevator.blockAgv
	return None
	
	
#agv在电梯外面，判断电梯已经到本层楼，并且处于开门状态 
#agv在电梯里面，判断电梯已经到目的地，并且处于开门状态 
def checkOpen(agvId,mapId,loc,force=False): 
	f = getFloor(mapId,loc)
	if f:
		if f.elevator.blockAgv and agvId != f.elevator.blockAgv:
			return False
		#要从电梯出来 
		return f.checkOpen(force=force) 
	return True


#agv在电梯外面，判断电梯处于关门状态 	
#agv在电梯里面，判断电梯处于关门状态 	
def checkClose(agvId,mapId,loc):
	f = getFloor(mapId,loc)
	if f:
		if f.elevator.blockAgv and agvId != f.elevator.blockAgv:
			return False
		return f.checkClose()
	return True
 
	
def keepOpenThread():
	log.debug("elevator thread start")
#TODO	time.sleep(10)
	while not utility.is_exited():
		for e in g_elevators.values():	
			try:
				e.readStatus()
				e.keepOpen()
			except Exception as er:
				log.exception("elevator keepOpenThread",er)
		time.sleep(1)
	
	
def getFloor(mapId,loc):
	_load() 
	key = mapId + "." + loc
	if key in g_floors:
		return g_floors[key]
	return None
	
############# unit test #############
def testdoor(): 
	m = _load()
	s = desc()
	print(s)
	r = getElevator("testscada","408")
	assert 2 == len(r)
	r = getElevator("408","testscada")
	assert 2 == len(r)
	r = getElevator("4082","testscada")
	assert 0 == len(r) 
	import mapMgr
	m1 = mapMgr.getMap("408") 
	m1.show()


if __name__ == '__main__':
	import utility
	utility.run_tests()

