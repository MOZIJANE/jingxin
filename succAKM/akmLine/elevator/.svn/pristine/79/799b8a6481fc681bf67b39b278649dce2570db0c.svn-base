import sys, os
import setup 
if __name__ == '__main__':
	setup.setCurPath(__file__) 
import time 
import utility
import queue
import threading
import log
g_elevators = {}

class mock:
	def __init__(self,name,floorNum=10):
		self.name = name
		self.isOpening = 0 
		self.isClosing = 0
		self.isFinishOpen = 0
		self.floorId = 1
		self.isRunning = 0
		self.floorNum = floorNum
		self.isUpward = 0
		self.isDownward = 0
		self.tasks = queue.Queue()
		self.thread = threading.Thread(target=self.threadFunc)
		self.thread.start()
		
	def status(self):
		ret = {}
		ret["isOpening"] = self.isOpening
		ret["isClosing"] = self.isClosing
		ret["isFinishOpen"] = self.isFinishOpen
		ret["isRunning"]= self.isRunning
		ret["isUpward"] = self.isUpward
		ret["isDownward"] = self.isDownward
		ret["inFloor"] = self.floorId	
		ret["isMaintain"] = "normal"
		return ret
		
	def threadFunc(self):
		while True:
			task = self.tasks.get()
			self.runTask(task)
			
	def addTask(self,task):
		self.tasks.put(task) 
		
	def runTask(self,task): 
		if task["cmd"] == "goFloor":  
			f = task["floor"] 
			if self.floorId == f:
				self.isRunning = 0
				self.isUpward = 0
				self.isDownward = 0
				return
			log.info(self.name,"go floor from",self.floorId,"to",f)
			self.isRunning = 1
			if self.floorId > f:
				self.isDownward = 1
				self.isUpward = 0
				f2 = self.floorId
				for i in range(f2-1,f-1,-1): 
					time.sleep(5)
					self.floorId = i
					log.info(self.name,"on floor",self.floorId)
			else:
				self.isDownward = 0
				self.isUpward = 1
				f2 = self.floorId
				for i in range(f2+1,f+1): 
					time.sleep(5) 
					self.floorId = i
					log.info(self.name,"on floor",self.floorId)
			self.isRunning = 0
			self.isUpward = 0
			self.isDownward = 0
		elif task["cmd"] == "hold":
			if self.isFinishOpen == 1:
				log.info(self.name,"hold door at floor",self.floorId)
			else:
				log.info(self.name,"opening door at floor",self.floorId)
				self.isFinishOpen = 0
				self.isOpening = 1
				time.sleep(5) 
				self.isOpening = 0
				self.isFinishOpen = 1
				log.info(self.name,"opened door at floor",self.floorId)
		elif task["cmd"] == "unhold":
			if self.isFinishOpen == 0 and self.isClosing == 0 and self.isOpening == 0:
				log.info(self.name,"repeat close door at floor",self.floorId)
			else:
				log.info(self.name,"closing door at floor",self.floorId)
				self.isFinishOpen = 0
				self.isClosing = 1
				time.sleep(5) 
				self.isClosing = 0
				self.isFinishOpen = 0
				log.info(self.name,"closed door at floor",self.floorId)

def _get(elevatorId):
	global g_elevators
	if elevatorId not in g_elevators:
		g_elevators[elevatorId] = mock(name=elevatorId)
	return g_elevators[elevatorId]
	
	
def hold(elevatorId): 
	t = {"cmd":"hold"}
	_get(elevatorId).addTask(t)
	

def unhold(elevatorId):
	t = {"cmd":"unhold"}
	_get(elevatorId).addTask(t)


def goFloor(elevatorId,floorId):
	t = {"cmd":"goFloor","floor":floorId}
	_get(elevatorId).addTask(t)
	

def status(elevatorId):
	return _get(elevatorId).status()


# test

def test_elevator():
	elevatorId='ELEVATOR01'
	while True:
		span = 0.5
		time.sleep(span)
		goFloor(elevatorId,2)
		time.sleep(span)
		goFloor(elevatorId,5)
		time.sleep(20)
		goFloor(elevatorId,1)
		time.sleep(span)
		goFloor(elevatorId,3)


if __name__ == '__main__':
	test_elevator()

