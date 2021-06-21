#coding=utf-8
# ycat			2019-9-24	  create
# 提供agv电子门的管理 
import sys,os
import threading 
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import log
import local
import utility
import webutility 
import json_codec as json
import matplotlib.pyplot as plt
import matplotlib.path as mpath  
import matplotlib.patches as mpatches
import ui.pltUtil
import PyQt5
import PyQt5.QtGui
import log
import door.switchMgr as switchMgr
import door.switchApi as switchApi
import threading
import time
import alarm.aliveApi

class doorInfo:
	def __init__(self):
		self.id = ""
		self.x1 = 0.
		self.y1 = 0.
		self.x2 = 0.
		self.y2 = 0.
		self.mapId = ""
		self.ip = ""
		self.on = False
		self._boundPath = None
		self.lines = []
		self.drawObj = None
		self.textObj = None
		self.hold = False
		self.alarmObj = None
		
	def __str__(self):
		return f"door:{self.ip} line:" +".".join([str(s) for s in self.lines])
		
	def draw(self): 
		if self.on:
			color = "green" 
		else:
			color = "red" 
		if self.drawObj is not None:
			self.drawObj.remove()
		plt.figure(self.mapId)
		self.drawObj = ui.pltUtil.addPath(self.boundPath,inverse=False, edgecolor="gray",facecolor=color,alpha=0.8)
		if self.textObj is None:
			self.textObj = plt.gca().text(self.x1,self.y1,self.id,color="blue")
		
	@property
	def r(self):
		return math.atans((self.y1-self.y2),(self.x1-self.x2))
		
	#外围多边型 
	@property
	def boundPath(self):  
		if self._boundPath:
			return self._boundPath
		p = PyQt5.QtGui.QPainterPath()
		p.moveTo(PyQt5.QtCore.QPointF(self.x1,self.y1))
		p.lineTo(PyQt5.QtCore.QPointF(self.x2,self.y2))
		s = PyQt5.QtGui.QPainterPathStroker() 
		s.setWidth(0.2) 
		self._boundPath = s.createStroke(p)
		return self._boundPath
	
	def checkOpen(self,lines): 
		if self.on:
			return True
		for l in self.lines:
			if l not in lines:
				continue
			self.hold = True
			log.info("try open door",self.id) 
			return False
		return True
		
	def checkClose(self,lines):
		if not self.on:
			return True
		find = False
		for l in self.lines:
			if l in lines:
				find = True
		if not find:
			self.hold = False
			log.info("try close door",self.id) 
			return False
		return find 
	
	def open(self): 
		log.info("open door",self.id)
		try:
			if not switchApi.switchOpen(self.id):
				return False
			if self.id == "DOOR06" and local.get("project","name") == "fastprint":
				time.sleep(3)
			time.sleep(1)
			self.on = True
			self.hold = True
			return True
		except Exception as e:
			log.exception("open door "+str(self.id),e)
			return False
		
	def close(self):
		#要有延时关门功能 
		log.info("close door",self.id)
		try: 
			switchApi.switchClose(self.id)
			self.on = False	
			self.hold = False
		except Exception as e:
			log.exception("close door"+str(self.id),e)
			return False
		
		
class doors:
	def __init__(self,mapId):
		self.doors = {} 
		self.mapId = mapId 
		self._load()  
		self._thread = threading.Thread(target=self.run,name="door."+mapId)
		self._thread.start()
		self._checkThread = threading.Thread(target=self.check,name="door."+mapId+".ping")
		self._checkThread.start()
	
	def __str__(self):
		return "\n".join([str(s) for s in self.doors])
	
	def _load(self): 
		d = switchMgr.getDoorByMapId(self.mapId)
		for id in d:
			self.doors[id] = doorInfo()
			self.doors[id].id = id
			self.doors[id].x1 = d[id].point1[0]
			self.doors[id].y1 = d[id].point1[1]
			self.doors[id].x2 = d[id].point2[0]
			self.doors[id].y2 = d[id].point2[1]
			self.doors[id].mapId = d[id].map
			self.doors[id].ip = d[id].ip
			self.doors[id].alarmObj = alarm.aliveApi.aliveObj(moid=id, typeId=39998, desc="门控离线异常", timeoutSecond=60,domain="agv")
		
	def draw(self):
		for d in self.doors:
			d = self.doors[d] 
			d.draw()
			
	#更新哪些门和线有交集 
	def update(self,lines):
		for d in self.doors.values():
			for l in lines:
				if l.path.intersects(d.boundPath):
					d.lines.append(l)

	
	def checkOpen(self,lines):
		for d in self.doors.values():
			if not d.checkOpen(lines):
				return False
		return True
		
		
	def checkClose(self,lines):
		for d in self.doors.values():
			d.checkClose(lines) 
		
	def run(self):
		while not utility.is_exited():
			for d in self.doors.values():
				if d.hold != d.on:
					if d.hold:
						d.open() 
					else:
						d.close() 
			time.sleep(1)
	
	def check(self):
		import shell
		while not utility.is_exited():
			for id in self.doors:
				door = self.doors[id]
				if shell.ping(door.ip,showLog=False):
					door.alarmObj.check()
			time.sleep(5)
			

############# unit test #############
def testdoor(): 
	import mapMgr 
	m = mapMgr.mapInfo.load("408.smap") 
	d = doorInfo()
	d.id = "0"
	d.x1 = 7.75
	d.y1 = 2.09
	d.x2 = 7.898
	d.y2 = 1.517
	d.mapId = "408"
	d.on = False
	m.doors.doors["0"] = d 
	
	d2 = doorInfo()
	d2.id = "1"
	d2.x1 = 0.5811
	d2.y1 = 1.1646
	d2.x2 = 1.3913 
	d2.y2 = 0.3311
	d2.mapId = "408"
	d2.on = False
	m.doors.doors["1"] = d2
	
	m.doors.update(m.curves)
	assert 2 == len(d.lines)
	assert m.getLine("LM23","LM22") in d.lines
	assert m.getLine("LM22","LM23") in d.lines
	assert 6 == len(d2.lines)
	assert m.getLine("LM15","AP7") in d2.lines
	assert m.getLine("AP7","LM15") in d2.lines
	assert m.getLine("LM17","LM15") in d2.lines
	assert m.getLine("LM15","LM17") in d2.lines
	assert m.getLine("LM24","LM15") in d2.lines
	assert m.getLine("LM15","LM24") in d2.lines 


if __name__ == '__main__':
	import utility
	utility.run_tests()

