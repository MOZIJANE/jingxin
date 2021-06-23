#coding=utf-8
#地图的管理 
import os,sys
import glob
import math
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import json_codec as json
import utility
import PyQt5.QtGui 
import PyQt5.QtCore  
import numpy as np
import log 
import local
import bezierPath
import shelveInfo
import ui.pltUtil
import elevatorMgr
import posCfg
from matplotlib import pyplot as plt

def normAngle(angle):
	while angle > math.pi:
		angle -= 2.0 * math.pi 
	while angle < -math.pi:
		angle += 2.0 * math.pi 
	return angle
 
BLOCK_NONE = 0				#没有占用 
BLOCK_SHARE = 1				#可以和别车共享，相交线段变成EXCLUDE 
BLOCK_EXCLUDE = 2			#不可以和别车共享，仅可以在BLOCK_NONE上进行BLOCK_EXCLUDE 操作 
BLOCK_EXCLUDE_CFG = 3		#效果和BLOCK_EXCLUDE一样，但是由人工配置的

#可以在在BLOCK_SHARE|BLOCK_NONE上进行BLOCK_SHARE操作，但EXCLUDE不行
#同时SHARE线段相交的线段，其它线段变成EXCLUDE 
 

def printPaths(paths):
	print(strPaths(paths))
	
printLines = printPaths
	
def strPaths(paths):
	if paths is None:
		return "[None]"
	return ",".join([str(x) for x in paths])
	 

def drawArrow(plt,x,y,angle,width,color="g",head_width=0.3, head_length=0.3):
	#angle = angle/3.1415 *180 
	return plt.gca().arrow(x,y,math.cos(angle)*width,math.sin(angle)*width,head_width=head_width, head_length=head_length,color=color)
	
def remove(obj):
	try:
		if isinstance(obj,list):
			for o in obj:
				o.remove()
		else:
			obj.remove()
	except Exception as e:
		log.warning("remove",obj,str(e))
		
#带x,y的为point，有名字的叫posoition或者location 
#地图上的一个点，通常是边界点 
class point:
	def __init__(self):
		self.x = 0.0
		self.y = 0.0
		self.z = 0.0
	
	def __str__(self):
		return "x=%f,y=%f"%(self.x,self.y)
		
		
class agvPoint:
	def __init__(self,agvId): 
		self.agvId = agvId
		self.agvInfo = None	
		self.clear()
		self.pathObj = None
		self.pathObj2 = None
		self.textObj = None
		self.blockObj = None
		self.targetListObj = None
		self.targetPosObj = None
		self.targetPosTextObj = None
		self.targetPosObj2 = None
		self.targetPosTextObj2 = None
	
	def clear(self):
		self.targetList = None
		self.isDeadlock = False #是否死锁 
		self.nextTargetPosName = None	   #下一个目的位置信息,想到到达的，实际未到达的 
		self.checkFailed = False 	#检查是否通过 
		self.checkFailedTick = 0	#上次check fail的时间 
		self.isBlocked = False		#是否block失败
		self.blockAgvs = []			#当前小车被阻挡的AGV列表，用于计算死锁的  
		self.blockFailLines = []	#block失败的路径列表名，用于计算死锁的  
		self.checkFailLines = []	#check失败的路径列表名，用于计算死锁的  
		self.failPos = ""			#pos位置失败的列表，用于计算死锁的 
		self.selected = False		#界面选择状态
		elevatorMgr.unblockByAgv(self.agvId)
	
	def getFailLines(self):
		ret = []
		if self.failPos:
			pos = self.map.getPos(self.failPos)
			for l in pos.nextLines:
				ret.append(str(l))
			for l in pos.preLines:
				ret.append(str(l))
		ret += self.blockFailLines
		ret += self.checkFailLines 
		#TODO 这里有问题，对向的也要加进来~~~~
		return ret
	
	def setTargetList(self,targets): 
		self.targetList = targets
	
	def _getNextPath(self,mapId):
		if not self.agvInfo:
			return []
		if not self.agvInfo.params:
			return []
		pp = self.agvInfo.params
		if "pathsList" not in pp:
			return []
		if "pathIndex" not in pp:
			return []
		ret = []
		index = pp["pathIndex"]
		pp = pp["pathsList"]
		for p in pp[index:]:
			if p == pp[index]:
				#第一条路，前面已经取过了 
				if self.mapId == mapId:
					continue
			if p[0] == mapId:
				ret.append(p)
		return ret
		
	def getTargetListAll(self):
		if not self.map:
			return []
		if not self.targetList:
			return []
		ret = self.targetList[:]
		pp = self._getNextPath(self.mapId)
		for p in pp:
			if p[0] == self.mapId:
				ret += p[1]
		return ret
	
	#分段返回，因为第一段和第二段的级别不一样 
	def getTargetLines(self,map):
		if not self.map:	
			return []
		if not self.targetList:	
			return []
		ret = []
		if self.mapId == map.mapId:
			curPos = self.currentPosName
			# curPos = None
			ret.append(self.map.getStartLines(curPos,self.targetList))
		pp = self._getNextPath(map.mapId)
		for p in pp:
			if p[0] == map.mapId:
				ll = map.getStartLines(p[1][0],p[1])
				ret.append(ll)
		return ret
			 
	@property
	def targetPosName(self):
		if not self.targetList:
			return None
		pos = self.targetList[-1]
		if not self.map:
			return pos
		pp = self._getNextPath(self.mapId)
		for p in pp:
			if self.mapId == p[0]:
				pos = p[1][-1]
			else:
				break
		return pos
			
	@property
	def currentPosName(self):
		return self.agvInfo.curTarget
	
	@property
	def currentPos(self):
		cur = self.currentPosName
		if not cur:
			return None
		m = self.map
		if not map:
			return None
		try:
			return m.getPos(cur)
		except Exception as e:
			log.error(self.agvId,"currentPos",e)
			return None
	
	def inElevator(self):
		cur = self.currentPos
		if not cur:
			return False
		return cur.inElevator()
	
	@property
	def x(self): 
		return self.agvInfo.x
		
	@property
	def y(self): 
		return self.agvInfo.y
		
	@property
	def angle(self):
		return self.agvInfo.angle
	
	@property
	def r(self):
		return normAngle(self.angle)
	
	@property
	def width(self):
		if self.agvInfo.hasShelve:
			return float(self.agvInfo.shelf["width"])
		return self.agvInfo.width
		
	@property
	def height(self):
		if self.agvInfo.hasShelve:
			return float(self.agvInfo.shelf["height"])
		return self.agvInfo.height
	
	@property
	def map(self):
		if self.agvInfo.mapId is None:
			return None
		return self.agvInfo.map
		
	@property
	def mapId(self):
		if self.agvInfo.mapId is None:
			return None
		return self.map.mapId
		
	@property
	def figure(self):
		return plt.figure(self.mapId)
	
	#判断agv路径上是否有相关的路线 
	#def hasLine(self,line):
	#	if not self.targetList:
	#		return False
	#	for i,p in enumerate(self.targetList):
	#		if p == line.startPosName and i < len(self.targetList) + 1:
	#			return self.targetList[i+1] == line.endPosName
	#	return False
		
	
	def draw(self,fig):  
		import matplotlib.path as mpath  
		import matplotlib.patches as mpatches
		if self.agvInfo.status is None:
			return 
		# if self.agvInfo.isAvailable() == 'disconnect':
			# if self.pathObj is not None:
				# remove(self.pathObj)
			# if self.textObj is not None:
				# remove(self.textObj)
			# if self.blockObj is not None:
				# remove(self.blockObj)
			# if self.targetListObj is not None:
				# remove(self.targetListObj)
			# if self.targetPosObj is not None:
				# remove(self.targetPosObj)
			# if self.targetPosTextObj is not None:
				# remove(self.targetPosTextObj)
			# if self.targetPosObj2 is not None:
				# remove(self.targetPosObj2)
			# if self.targetPosTextObj2 is not None:
				# remove(self.targetPosTextObj2)
			# return
		if self.pathObj is not None:# and fig == self.pathObj.figure:
			remove(self.pathObj)
			self.pathObj = None
			#remove(self.pathObj2)
			#self.pathObj2 = None
			
		if self.pathObj is None:
			#画小车本体
			if self.isBlocked:
				color = "orange" 
			elif self.checkFailed:
				color = "yellow" 
			elif self.agvInfo.batteryLevel < 0.2:
				color = "DarkGray"
			elif self.agvInfo.isMoving():
				color = "lime"    
			else:
				color = "green"
			self.pathObj = fig.gca().add_patch(mpatches.PathPatch(ui.pltUtil.qt2path(self.boundPath,inverse=False), edgecolor="black",facecolor=color,alpha=0.8,zorder=20000))
			#self.pathObj2 = fig.gca().add_patch(mpatches.PathPatch(ui.pltUtil.qt2path(self.blockRectPath,inverse=False), edgecolor="black",facecolor="green",alpha=0.1))
		#画小车ID 
		if self.textObj is not None:# and fig == self.textObj.figure:
			remove(self.textObj)
		self.textObj = fig.gca().text(self.x+0.1,self.y+0.1,str(self.agvId),color="black",zorder=20000)  
		
		#画阻挡区域 
		if self.blockObj is not None:# and fig == self.blockObj.figure:
			remove(self.blockObj)
			self.blockObj = None
		
		pp = self.blockPath 
		if pp and not pp.isEmpty():  
			if not self.checkFailed:
				c = "blue"
				a = 0.3
			else:
				c = "red"
				a = 0.5
			box = PyQt5.QtGui.QPainterPath() 
			box.setFillRule(1) #加上这个才能叠加 	https://doc.qt.io/qt-5/qt.html#FillRule-enum 
			#box.addPolygon(pp)
			box.addPath(pp)
			self.blockObj = fig.gca().add_patch(mpatches.PathPatch(ui.pltUtil.qt2path(box,inverse=False),edgecolor="none", facecolor=c,alpha=a,zorder=-100))	
		else:
			self.blockObj = None
		
		#画要走的路径
		if self.targetListObj:# and fig == self.targetListObj.figure:
			r = self.targetListObj
			self.targetListObj = None
			remove(r)
		if self.targetList: 
			path_data = []
			for t in self.getTargetListAll():
				if  path_data or t == self.currentPosName:
					path_data.append((self.map.getPos(t).x,self.map.getPos(t).y))
			if path_data:
				xx, yy = zip(*path_data)
				color = "g"
				alpha = 0.3
				if self.selected:
					color = "yellow"
					alpha = 1
				self.targetListObj, = fig.gca().plot(xx, yy, 'go-',linewidth=12,color=color,alpha=alpha,zorder=-100) 
		else:
			self.targetListObj = None 
		
		#画终点
		if self.targetPosObj:# and fig == self.targetPosObj.figure:
			remove(self.targetPosObj)
		if self.targetPosTextObj:# and fig == self.targetPosTextObj.figure:
			remove(self.targetPosTextObj)
		if self.targetPosObj2:# and fig == self.targetPosObj2.figure:
			remove(self.targetPosObj2)
		if self.targetPosTextObj2:# and fig == self.targetPosTextObj2.figure:
			remove(self.targetPosTextObj2)
			
		if self.targetList:
			pos = self.map.getPos(self.targetList[-1])
			n = self.targetPosName
			if pos.name != n:
				self.targetPosObj2 = fig.gca().plot(pos.x,pos.y, '*',color="blue",zorder=1000, markersize=12)
				self.targetPosTextObj2 = fig.gca().text(pos.x,pos.y+0.2,self.agvId,color="black")
				pos = self.map.getPos(n)
			else:
				self.targetPosObj2 = None
				self.targetPosTextObj2 = None
			self.targetPosObj, = fig.gca().plot(pos.x,pos.y, 'r*',zorder=1000, markersize=12)
			self.targetPosTextObj = fig.gca().text(pos.x,pos.y+0.2,self.agvId,color="g")
		else:
			self.targetPosObj = None
			self.targetPosTextObj = None
		
	
	#小车外围多边型 
	@property
	def boundPath(self): 
		return self.getBoundPath(self.x,self.y,self.r,self.width,self.height)#.toFillPolygon(PyQt5.QtGui.QTransform()) 
		
	
	def getBoundPath(self,x,y,r,w,h):
		rr = PyQt5.QtGui.QTransform().rotateRadians(r)
		t = PyQt5.QtGui.QTransform().translate(x,y)
		p = PyQt5.QtGui.QPainterPath() 
		p.addRect(-h/2,-w/2,h,w)  
		return t.map(rr.map(p))
	
	@property
	def currentPos(self):
		return self.map.getPos(self.currentPosName)
	 
	def setPos(self,posName): 
		import driver.seerAgv.mockAgvCtrl as agvCtrl 
		assert utility.is_test()
		self.agvInfo.setPos(posName)
		agvCtrl.setPos(self.agvId, posName)  
	
	def getCheckLines(self):
		if self.nextTargetPosName is None:
			return []
		if self.currentPosName is None:
			return []
		if self.targetList is None:
			return [] 
		if self.agvInfo.agvId is None:
			return [] 
		lastPos = None
		ret = []
		for p in self.targetList:
			if p == self.currentPosName:
				lastPos = p
				continue 
			elif lastPos:
				line = self.map.getLine(lastPos,p)
				lastPos = p 
				if line:
					ret.append(line)
			if p == self.nextTargetPosName:
				return ret 
		return []
	 
	
	#当前小车阻挡的区域，根据点线和占用空间来判断 
	@property
	def blockPath(self):   
		lines = self.getCheckLines()
		pp = []
		#增加block区域 
		for p in lines:
			g = self.map.blockCfg.getGroupByPos(p)
			if g:
				pp += g
		lines += pp
		lines = list(set(lines))
		
		box = None
		scale = local.getfloat("ctrl","enlargeValue")
		w = self.width*scale
		h = self.height*scale 
		for i in range(len(lines)):
			#print("add line",str(lines[i]))
			line = lines[i]  
			if box is None:
				box = line.blockPath(x=self.x,y=self.y,w=w,h=h)
				box.setFillRule(1)
				#开始点会带旋转
				if line.startPos.contains(self.x,self.y):
					p = bezierPath.rotate(self.x,self.y,self.r,line.r,w,h)
					box.addPath(p)
			else:	
				p = line.blockPath(x=None,y=None,w=w,h=h)
				box.addPath(p)
				
			if i != len(lines)-1:
				next = lines[i+1]
				#当前线段结束转到下一线段
				p = bezierPath.rotate(line.endPos.x,line.endPos.y,line.end_r,next.r,w,h)
				box.addPath(p) 
				
		if lines:
			line = lines[-1]
			if line.endPos.rotation:
				p = bezierPath.rotate(line.endPos.x,line.endPos.y,0,math.pi,w,h)
				box.addPath(p)
		if box is None:
			return box
		return box#.simplified()#.toFillPolygon(PyQt5.QtGui.QTransform())
		
	def isLastTargetPos(self,loc):
		if not self.targetList:
			return False
		return self.targetList[-1] == loc
	
	def tryCheck(self, agvs):
		myBlock = self.blockPath
		if myBlock is None: 
			myBlock = self.boundPath
		
		for other in agvs:
			if other.agvId == self.agvId: 
				continue
				
			#两台车的nextTargetPosName不能重合 
			if other.agvInfo.isMoving():
				if other.agvInfo.nextTarget == self.nextTargetPosName:
					log.warning(self.agvId,"has same next target with",other.agvId,"at",other.agvInfo.nextTarget)
					return other.agvId
				
			#另一台车被block了，只计算小车自己占的位置 
			o = other.blockPath
			if o is None:
				o = other.boundPath
			elif other.isBlocked and not other.agvInfo.isMoving():
				o = other.boundPath	
			elif other.checkFailed: 
				if not other.agvInfo.isMoving():
					#因为状态更新需要时间，所以超过一个点位的，可能小车的当前位置不准 
					if utility.ticks() - other.checkFailedTick > 1000: #已经checkfail一段时间了，状态已经稳定 
						o = other.boundPath	
			if myBlock.intersects(o):
				return other.agvId
		return None
	
	
	# 判断小车是否能通行，通过当前小车到终点位置有没有小车区域相关的判断方法
	# 注意这里同线是可以通行的，通过防碰撞传感器停止 
	# 如果被阻挡，则返回AGVID 
	#判断将要走的路径，是否有交集
	def check(self, agvs):
		otherId = self.tryCheck(agvs)
		if otherId:
			if not self.checkFailed:
				self.checkFailedTick = utility.ticks()
			self.checkFailed = True 
			self.blockAgvs = [otherId,] 
			pp = self.getCheckLines()
			self.checkFailLines = [str(p) for p in pp]
			return False
		
		lines = self.getCheckLines() 
		if not self.map.doors.checkOpen(lines):
			return False  
		self.checkFailed = False
		self.checkFailedTick = 0
		if not self.isBlocked:
			self.blockAgvs = []
		self.checkFailLines = []
		self.failPos = ""
		return True
		
	def checkElevator(self,lines):
		if not lines:
			return True
		if not elevatorMgr.checkOpen(self.agvId,self.mapId,lines[0].startPosName,force=True):
			return False 
		if self.isLastTargetPos(lines[-1].endPosName) and not elevatorMgr.checkOpen(self.agvId,self.mapId,lines[-1].endPosName,force=True):	
			return False 
		return True
	 
	def unblock(self):
		blockLines = []
		for c in self.map.curves:
			if self.agvId not in c.blockAgvId:
				continue 
			blockLines.append(c)

		uu = self.getUnfinishLine()   
		for c in blockLines:
			if c in uu:
				continue
			if c.isDeadend and c.oposite in uu:
				continue 
			c.unblock(self.agvId)
		
		
	#取出未完成的路线 
	def getUnfinishLine(self):
		if self.currentPosName is None:
			return []
		if self.targetList is None:
			return [] 
		lastPos = None
		ret = []
		for p in self.targetList:
			if p == self.currentPosName:
				lastPos = p
				continue 
			elif lastPos:
				line = self.map.getLine(lastPos,p)
				lastPos = p 
				if line is None:
					raise Exception("路径不存在2" + str(lastPos)+"->"+str(p))
				ret.append(line)
		return ret
		
	def getUnfinishPos(self):
		if self.currentPosName is None:
			return []
		if self.targetList is None:
			return [] 
		lastPos = None
		ret = []
		for p in self.targetList:
			if p == self.currentPosName:
				lastPos = p
				continue 
			elif lastPos: 
				ret.append(p)
		return ret 
		
		
@json.rename("_startPos","startPos")
@json.rename("_endPos","endPos")
@json.rename("name","instanceName")
@json.rename("ctrlPoint1","controlPos1")
@json.rename("ctrlPoint2","controlPos2")
@json.rename("_p","property")
@json.list_type("pos",point())
@json.list_type("controlPos1",point())
@json.list_type("controlPos2",point())
class advancedCurve:
	def __init__(self):
		self.className = ""		#高级曲线类型
		self.name = ""			#曲线唯一标识名
		self._startPos = {}		#贝塞尔曲线起始点,一定是地图中出现过的某个高级点
		self._endPos = {}		#贝塞尔曲线终止点曲线起始点,一定是地图中出现过的某个高级点 
		self.ctrlPoint1 = None	#贝塞尔曲线控制点1 
		self.ctrlPoint2 = None	#贝塞尔曲线控制点2  
		self._p = []			#读属性的字段  
		self.property = {}		#属性字典 
		self.devices = []		#设备模型相关 
		self._positions = {}	#高级点字典 
		self._bezierPath = None
		
		self.lineObj = None		#画图对象 
		self.arrowObj = None	
		self._blockType = BLOCK_NONE	#是否上锁 
		self.blockAgvId = set()  						#上锁的AGVID列表
		self.isOneway = False						#是否为独木桥,整体路径为独木桥，则会变成断头路
		self.isDeadend = False						#是否为断头路 
		self._opositeLine = None					#A->B的逆向路为B->A 
		self._blockGroup = []						#上锁的组，即连通deadend和oneway的列表  
		self._map = None
		
		self._ptrList = None							#组成曲线的(x,y,r)列表
		self._lineBound = None							#0.5米宽的线段，用于判断agv是否在线段上 
		self._lastBound = {"w":0,"h":0,"bound":None}	#缓存最后一次车子的路径 
		
		
	def __str__(self):
		return "%s->%s"%(self.startPos.name,self.endPos.name) 
	
	def equal(self,startPosName,endPosName):
		if startPosName != self.startPos.name:
			return False
		return endPosName == self.endPos.name
	
	@property
	def mapId(self):
		return self._map.mapId
		
	@property
	def ptrList(self):
		if self._ptrList is None:
			pp = [(self.startPos.x, self.startPos.y), (self.ctrlPoint1.x, self.ctrlPoint1.y),(self.ctrlPoint2.x, self.ctrlPoint2.y), (self.endPos.x,self.endPos.y)]
			self._ptrList = bezierPath.bezier(*pp)
			self._lineBound = bezierPath.strock(self._ptrList,width=0.5,height=0.5)#.toFillPolygon(PyQt5.QtGui.QTransform()) 
		return self._ptrList
		
		
	#是否为倒退
	@property
	def backward(self):
		if "direction" not in self.property:
			return False
		return self.property["direction"] == 1
	
	@property
	def agvId(self):	 
		for agv in self._map.agvs: 
			if self.contains(agv.x,agv.y):
				return agv.agvId
			if self.endPos.contains(agv.x,agv.y):
				return agv.agvId
			if self.startPos.contains(agv.x,agv.y):
				return agv.agvId
		return None
		
	@property
	def agvs(self):	
		ret = []
		for agv in self._map.agvs: 
			if self.contains(agv.x,agv.y):
				ret.append(agv.agvId)
			elif self.endPos.contains(agv.x,agv.y):
				ret.append(agv.agvId)
			elif self.startPos.contains(agv.x,agv.y):
				ret.append(agv.agvId)
		return ret
	
	@property
	def blockType(self):
		return self._blockType
	
	@blockType.setter
	def blockType(self,t): 
		self._blockType = t
		try:
			self.draw(self.figure)
		except Exception as e:
			log.exception("blockType",e)
	
	@property
	def oposite(self):
		return self._opositeLine
	 
	@property
	def figure(self):
		return plt.figure(self._map.mapId)
	
	def tryBlock(self,agvId,paths,type=None):
		def _tryBlock(This,agvId): 
			if This.isDeadend:
				blockType = BLOCK_EXCLUDE
			else:
				blockType = BLOCK_SHARE 
			if type is not None:
				blockType = type
				
			if agvId in This.blockAgvId:
				return []
				
			if blockType == BLOCK_EXCLUDE or blockType == BLOCK_EXCLUDE_CFG: 
				if This.blockType != BLOCK_NONE:
					return list(This.blockAgvId)
				if This.oposite and This.oposite.isBlocked:	
					if agvId not in This.oposite.blockAgvId:
						return list(This.oposite.blockAgvId)
				#判断当前路径上是否有另一台AGV存在 
				a = This.agvId
				if a is not None:
					if a != agvId:
						return [a,]
				return []
			else:
				#shareBlock   
				if This.blockType == BLOCK_EXCLUDE or blockType == BLOCK_EXCLUDE_CFG:	
					return list(This.blockAgvId) 
				if This.oposite and This.oposite.isBlocked:
					if len(This.oposite.blockAgvId) > 1:
						#多台agv在对向，不可以调整方向 
						return list(This.oposite.blockAgvId)
					if agvId not in This.oposite.blockAgvId: 
						return list(This.oposite.blockAgvId) 
					#TODO: 在oneway上调头，这时要把对向的agv unlock掉，不过try中unlock不好，这时会导致这条路变独占的 
				return []
		pp = self._getBlockPath(paths)
		for c in pp:  
			ret = _tryBlock(c,agvId)
			if len(ret) != 0:
				return ret 
			ret = elevatorMgr.tryBlock(agvId,c.mapId,c.startPosName)
			if len(ret) != 0:
				return ret
			ret = elevatorMgr.tryBlock(agvId,c.mapId,c.endPosName)
			if len(ret) != 0:
				return ret	
		return [] 
		
	def block(self,agvId,paths,type=None):
		def _block(This,agvId): 
			if This.isDeadend: 
				blockType = BLOCK_EXCLUDE
			else:
				blockType = BLOCK_SHARE 
			if type is not None:
				blockType = type
			This.blockType = blockType
			if agvId not in This.blockAgvId:
				This.blockAgvId.add(agvId)  
			elevatorMgr.block(agvId,This.mapId,This.startPosName)
			elevatorMgr.block(agvId,This.mapId,This.endPosName)
			#log.success(agvId,"block",str(This))
			return True
		pp = self._getBlockPath(paths) 
		for c in pp:  
			if not _block(c,agvId):
				return False   
		return True 
		
	def unblock(self,agvId):
		def _unblock(This,agvId):
			if agvId in This.blockAgvId:
				This.blockAgvId.remove(agvId)
			if not This.blockAgvId:
				This.blockType = BLOCK_NONE
			elevatorMgr.unblock(agvId,This.mapId,This.startPosName)
			elevatorMgr.unblock(agvId,This.mapId,This.endPosName) 
		_unblock(self,agvId)
		if self.oposite:
			if agvId in self.oposite.blockAgvId:
				_unblock(self.oposite,agvId)
	
	def _getBlockPath(self,paths):
		pp = []
		for c in paths:
			assert isinstance(c,advancedCurve)  
		for c in paths:   
			if c in self._blockGroup:  
				if c.isDeadend: 
					if c.oposite:  
						pp.append(c.oposite)
				pp.append(c)
			elif len(pp) > 1:
				break
		pp2 = pp[:]
		for p in pp:
			g = self._map.blockCfg.getGroup(p)
			if g:
				pp2 += g
		return pp2
		
	@property
	def isBlocked(self):
		return self.blockType != BLOCK_NONE
	
	@property
	def startPos(self):
		return self._positions[self._startPos["instanceName"]]
		
	@property
	def endPos(self):
		return self._positions[self._endPos["instanceName"]]
		
	@property
	def startPosName(self):
		return self.startPos.name
		
	@property
	def endPosName(self):
		return self.endPos.name
	
	@property
	def length(self): 
		p = self.path
		r = self._length
		r += posCfg.getPosLen(self.mapId,self.endPosName)
		return r
		 
	
	@property
	def path(self):
		if self._bezierPath is None:
			p = PyQt5.QtGui.QPainterPath()
			p.moveTo(self.startPos.x, self.startPos.y)
			p.cubicTo(self.ctrlPoint1.x, self.ctrlPoint1.y,
								 self.ctrlPoint2.x, self.ctrlPoint2.y,
								 self.endPos.x, self.endPos.y)
			self._bezierPath = p
			self._length = p.length() 
		return self._bezierPath
	
	
	#外围多边型 
	def boundPath(self,w,h):
		if w == self._lastBound["w"] and h == self._lastBound["h"]:
			return self._lastBound["bound"]
		p = bezierPath.strock(self._ptrList,width=w,height=h)
		self._lastBound["w"] = {"w":w,"h":h,"bound":p}
		return p
		
	
	def contains(self,x,y):
		if self._lineBound is None:
			pp = self.ptrList
		return self._lineBound.contains(PyQt5.QtCore.QPointF(x,y))
		#return self._lineBound.containsPoint(PyQt5.QtCore.QPointF(x,y),1)
		 
	
	@property
	def r(self):
		if self.backward:
			return self.ptrList[0][2]+math.pi
		else:
			return self.ptrList[0][2]
			
	@property
	def end_r(self):
		if self.backward:
			return self.ptrList[-1][2]+math.pi
		else:
			return self.ptrList[-1][2]
	
	def angleAtPoint(self,x,y):
		i = bezierPath.getIndex(x,y,self.ptrList)
		return self._ptrList[int(i)][2]
		
	def percentAtPoint(self,x,y):
		if not self.ptrList:
			return 0
		i = self.indexAtPoint(x,y)
		return i/len(self.ptrList)
		
	def indexAtPoint(self,x,y):
		return bezierPath.getIndex(x,y,self.ptrList)
		
	#取出线段的点 
	def pointAtPercent(self,percent):
		return self.path.pointAtPercent(percent)
		
	#取出当前位置到终点位置的外围多边型
	#用于判断两车是否有相交，不相交，小车才可以通行 
	def blockPath(self,x,y,w,h):
		if x is None or not self.contains(x,y):  
			return self.boundPath(w,h)  
		return bezierPath.strock(self._ptrList, width = w,height=h,x=x,y=y)
		
		
	def draw(self,fig):
		import matplotlib.path as mpath  
		import matplotlib.patches as mpatches
		if self.blockType == BLOCK_EXCLUDE: 
			lw = 6
		if self.blockType == BLOCK_EXCLUDE_CFG: 
			lw = 6
		elif self.blockType == BLOCK_SHARE: 
			lw = 6
		else: 
			lw = 1
		
		if self.isDeadend or self.blockType == BLOCK_EXCLUDE:
			color = "red"
		elif self.isOneway:
			color = "orange"
		else:
			color = "green"
		if self.blockType == BLOCK_EXCLUDE_CFG:
			color = "purple"
			
		if self.lineObj:
			remove(self.lineObj)
		linePath = mpatches.PathPatch(
			mpath.Path([(self.startPos.x, self.startPos.y), (self.ctrlPoint1.x, self.ctrlPoint1.y), 
			(self.ctrlPoint2.x, self.ctrlPoint2.y), (self.endPos.x,self.endPos.y)],
			[mpath.Path.MOVETO, mpath.Path.CURVE4, mpath.Path.CURVE4, mpath.Path.CURVE4 ]),
			fc="none",edgecolor=color,linewidth=lw)  
		self.lineObj = fig.gca().add_patch(linePath)   
		
		#p = self.pointAtPercent(0.3)  
		#写名字
		#t = self.name
		#if self.isDeadend:
		#	t += "[D]"
		#elif self.isOneway:
		#	t += "[X]"
		#	
		#fig.gca().text(p.x(),p.y()+0.2,t,color=color)
		
		#画箭头 
		percent = 0.1
		p = self.pointAtPercent(percent) 
		if self.isBlocked:
			color = "black" 
		if self.arrowObj:# and fig == self.arrowObj.figure:
			remove(self.arrowObj)
		
		#if not self.backward:
		self.arrowObj = drawArrow(fig,p.x(),p.y(),self.r,width=0.25,color=color,head_width=0.12, head_length=0.12)    
				
				
	#更新block组 
	def _updateBlockGroup(self,map=None): 
		assert 0 == len(self._blockGroup) #only invoke once 
		def getLine(lines,visited,findList,dir):
			for l in lines:
				if (l.startPos.name,l.endPos.name) in visited:
					continue
				#把对向的oneway回程排除
				if l.isOneway and not l.isDeadend:
					if (l.endPos.name,l.startPos.name) in visited: 
						continue 
				if l.isOneway or l.isDeadend:  
					findList.append(l)
					visited.add((l.startPos.name,l.endPos.name)) 
					if dir == "next":
						getLine(l.endPos.nextLines,visited,findList,dir)
					else:
						getLine(l.startPos.preLines,visited,findList,dir)
		ret = [self,]
		visited = set()
		visited.add((self.startPos.name,self.endPos.name))
		if self.isOneway or self.isDeadend:  
			getLine(self.endPos.nextLines,visited,ret,dir="next") 
			getLine(self.startPos.preLines,visited,ret,dir="pre")
		
		if map:
			g = map.blockCfg.getGroup(self)
			if g:
				ret += g
		self._blockGroup = ret  
		return ret	
	
	
	
@json.rename("name","instanceName")
@json.list_type("pos",point())
@json.rename("_p","property")
class advancedPoint:
	def __init__(self):
		#高级点类型
		#LandMark(普通站点),ChargePoint(充电点),ReturnPoint(返航点)
		#GyroCaliPoint(陀螺仪标定点),RobotHome(出生点) 
		self.className = ""
		self.name = ""			#高级点唯一标识名
		self.pos = None
		self.ignoreDir = False	#是否忽略方向
		self.dir = 0.0			#方向 
		self._p = []
		self.property = {}		#属性数组 
		self.attribute = {}		#里面有颜色 "colorBrush"
		self.nextLines = []		#可以出去的线段列表 
		self.preLines = []		#可以进来的线段 
		self._map = None
		self.turnable = True	#是否可以旋转 
		self._isRotation = None #是否带有旋转
		self._isLeaf = None
		 
	@property
	def isApType(self):
		if len(self.name) < 2:
			return False
		return self.name[0:2].upper() == "AP"
		 
	#返回当前点的AgvId，不存在则返回None 
	@property
	def agvId(self):
		for agv in self._map.agvs: 
			if self.contains(agv.x,agv.y):
				return agv.agvId
		return None
		
	@property
	def mapId(self):
		if self._map is None:
			return None
		return self._map.mapId
		
	@property
	def isChargePoint(self):
		return self.className == "ChargePoint"
 
	def __str__(self):
		return "[%s]X=%0.2f,Y=%0.2f"%(self.name,self.x,self.y)
	
	def equal(self,other):
		return self.name == other.name
	
	@property
	def x(self):
		return self.pos.x
	
	@property
	def y(self):
		return self.pos.y
	
	@property
	def r(self):
		if self.ignoreDir:
			return None
		return self.dir
	
	def distance(self,x,y):
		def _distance(p1,p2):
			return math.sqrt(math.pow((p1[0]-p2[0]),2) + math.pow(p1[1]-p2[1],2))
		return _distance((self.x,self.y),(x,y))
		
	@property
	def color(self):
		if "colorBrush" in self.attribute:
			return "#" + "%02X"%self.attribute["colorBrush"]
		return "#0000FF"
	
	@property
	def index(self): 
		return self._map.positions.index(self)
	
	def draw(self,fig,showText=True): 
		import matplotlib.path as mpath  
		import matplotlib.patches as mpatches
		from matplotlib import colors  
		c = "black"
		if not self.turnable:
			c = "red"
		#if self.backward:
		#	c = "orange"
		circle = mpatches.Circle((self.x,self.y),0.3,facecolor="#AAFFEE",edgecolor=c)
		fig.gca().add_patch(circle) 
		if showText:
			fig.gca().text(self.x,self.y, self.name,color="blue",zorder=10000,alpha=0.8,fontsize=9)
		if not self.ignoreDir: 
			drawArrow(fig,self.x,self.y,self.dir,width=0.3,head_width=0.1, head_length=0.1,color="b")
	
	def boundPath(self,w,h):
		r = max(w,h) 
		if not hasattr(self,"_boundPath"):
			p = PyQt5.QtGui.QPainterPath()
			cx = self.x - r/2
			cy = self.y - r/2
			p.addEllipse(cx, cy,r,r)  #因为会转圈，所以是个圆  
			self._boundPath = p
		return self._boundPath
		
	def contains(self,x,y):
		return self.boundPath(0.6,0.6).contains(PyQt5.QtCore.QPointF(x,y))
	
	#是否为叶子节点 
	@property
	def isLeaf(self):
		def _isLeaf():
			if len(self.nextLines) == 1:
				if len(self.preLines) == 1:
					return self.preLines[0].oposite == self.nextLines[0]
				if len(self.preLines) == 0:
					return True
			if len(self.preLines) == 1:
				if len(self.nextLines) == 0:
					return True
			if len(self.nextLines) + len(self.preLines)  ==0:
				return True
			return False
		if self._isLeaf is None:
			self._isLeaf = _isLeaf()
		return self._isLeaf
	
	@property
	def backward(self):
		if not self.isLeaf:
			return False
		return not self.rotation
	
	#取出相临点 
	@property
	def neighbors(self):
		pp = set()
		for l in self.nextLines:
			pp.add(l.endPosName)
		#for l in self.preLines:
		#	pp.add(l.startPosName)
		return list(pp)
		
	def inElevator(self):
		import elevatorMgr
		return elevatorMgr.getFloor(self.mapId,self.name) is not None
		
	@property
	def rotation(self):
		#判断是否带有旋转 
		def _hasRotation():
			#if not self.ignoreDir:
			#	return True
			if self.isLeaf: 
				for line in self.nextLines:
					#正进正出，会旋转 
					if line.oposite and line.backward == line.oposite.backward:
						return True
				for line in self.preLines:
					#正进正出，会旋转 
					if line.oposite and line.backward == line.oposite.backward:
						return True
			else:
				rr = []
				for line in self.nextLines:
					for line2 in self.preLines:
						if line2 == line.oposite:
							continue
						if abs(normAngle(line.r-line2.end_r)) > math.pi/6.:
							#大于30度，算是有旋转
							return True
			return False
			
		if self._isRotation is None:
			self._isRotation = _hasRotation()
		return self._isRotation
		
	
@json.rename("minPoint","minPos")
@json.rename("maxPoint","maxPos")
@json.list_type("minPos",point())
@json.list_type("maxPos",point())
class headerInfo:
	def __init__(self):
		self.mapName = ""
		self.minPoint = None
		self.maxPoint = None
		self.resolution = 0.0
		self.version = ""
		
#############  unit test ############# 
def testbackward():
	import mapMgr
	m = mapMgr.mapInfo.load("fp20190712-1") 
	assert m.getLine("AP30","LM41").backward
	assert not m.getLine("LM41","AP30").backward
	assert not m.getLine("LM38","LM39").backward
	#m.show()
 
	
def test_block():
	import mapMgr,agvControl,time,agvList
	utility.start()
	agvList.g_agvList = None
	mapMgr.g_agvs = {}
	m = mapMgr.mapInfo.load("408.smap") 
	while True: 
		#等待所有agv上线 
		aa = agvControl.getAgvList()
		for a in aa:
			if aa[a].status is None:
				time.sleep(0.5) 
				break
		else:
			time.sleep(0.5)
			break  
	p = m.getPath("LM19","AP7")[0][1]
	pp = m.getStartLines(None,p)
	c = m.getLine("LM19","LM20")
	assert c.block("agv1",pp) 
	bb = m.getBlockLines()
	assert 10 == len(bb)
	assert m.getLine("AP7","LM15") in bb
	assert m.getLine("LM15","AP7") in bb
	assert m.getLine("LM24","LM15") in bb
	assert m.getLine("LM23","LM24") in bb
	assert m.getLine("LM22","LM23") in bb
	assert m.getLine("LM21","LM22") in bb
	assert m.getLine("LM21","LM20") in bb
	assert m.getLine("LM20","LM21") in bb
	assert m.getLine("LM19","LM20") in bb
	assert m.getLine("LM20","LM19") in bb
	c.unblock("agv2")
	assert 10 == len(m.getBlockLines())
	c = m.getLine("LM19","LM20")
	c.unblock("agv1") 
	assert 8 == len(m.getBlockLines())
	bb = m.getBlockLines()
	assert m.getLine("LM19","LM20") not in bb
	assert m.getLine("LM20","LM19") not in bb
	m.getLine("LM22","LM23").unblock("agv1")
	assert 7 == len(m.getBlockLines())
	bb = m.getBlockLines()
	assert m.getLine("LM22","LM23") not in bb

def test_updateBlockGroup():
	import mapMgr
	m = mapMgr.mapInfo.load("408.smap") 
	assert len(m.getLine("LM19","LM20")._blockGroup) == 39
	assert len(m.getLine("AP7","LM1")._blockGroup) == 39 
	m = mapMgr.mapInfo.load("test430.smap") 
	assert len(m.getLine("LM26","LM23")._blockGroup) == 1
	assert len(m.getLine("AP7","LM23")._blockGroup) == 2 
	
def test_neighbors():
	import mapMgr
	m = mapMgr.mapInfo.load("408.smap")
	assert utility.assert_array_noorder(["CP9","LM10"] , m.getPos("LM11").neighbors)
	assert ["LM20"] == m.getPos("LM19").neighbors
	assert utility.assert_array_noorder(["LM23","LM10","AP8"], m.getPos("LM12").neighbors)
	m = mapMgr.mapInfo.load("testmap.smap")
	assert ["LM10"] == m.getPos("LM11").neighbors
	assert [] == m.getPos("LM10").neighbors
	
	
def testagv():
	import utility
	local.set("project","agvcfg","agv.cfg")
	import agvControl
	agvControl.agvList.g_agvList = None
	import mapMgr
	import driver.seerAgv.mockAgvCtrl as agvCtrl
	agvCtrl.disableBattery() 
	import time
	utility.start() 
	mapMgr.g_agvs = {}
	
	while True:
		#等待所有agv上线 
		aa = agvControl.getAgvList()
		for a in aa:
			if aa[a].status is None:
				time.sleep(0.5) 
				break
		else:
			time.sleep(0.5)
			break 
			 
	mapMgr.setActive("8-222")
	m = agvControl.getMap("8-222")
	assert "agv21" == m.getPos("LM18").agvId
	assert "agv22" == m.getPos("LM19").agvId
	assert "agv23" == m.getPos("LM11").agvId
	assert m.getPos("LM13").agvId is None
	assert m.getLine("LM13","LM15").agvId is None
	assert m.getLine("LM16","LM11").agvId == "agv23"
	mapMgr.setActive("408")
	m = agvControl.getMap("408")
	a1 = m.getAgv("agv51")
	a2 = m.getAgv("agv52") 
	pp = m.getPath("LM19","AP7")[0][1]
	a1.setTargetList(pp)
	a1.nextTargetPosName = pp[1] 

	#test getUnfinishLine
	a1.setPos("LM19")  
	assert "LM19" == a1.currentPosName
	assert 7 == len(a1.getUnfinishLine())
	
	a1.setPos("LM21")  
	assert 5 == len(a1.getUnfinishLine())
	
	a1.setPos("LM23")  
	assert 3 == len(a1.getUnfinishLine())
	
	a1.setPos("LM14")  
	assert 0 == len(a1.getUnfinishLine())
	
	#test unblock 
	a1.setPos("LM21")   
	assert m.block("agv51","LM21","LM22",pp) 
	assert 6 == len(m.getBlockLines())  
	assert m.getLine("LM21","LM22").blockType == BLOCK_SHARE
	assert m.getLine("LM22","LM23").blockType == BLOCK_SHARE
	assert m.getLine("LM23","LM24").blockType == BLOCK_SHARE
	assert m.getLine("LM24","LM15").blockType == BLOCK_SHARE
	assert m.getLine("LM15","AP7").blockType == BLOCK_EXCLUDE
	assert m.getLine("AP7","LM15").blockType == BLOCK_EXCLUDE 
	a1.unblock()  
	assert 6 == len(m.getBlockLines())  
	a1.setPos("LM23")   
	a1.unblock()
	assert 4 == len(m.getBlockLines())  
	a1.setPos("AP7")   
	a1.unblock()
	assert 0 == len(m.getBlockLines())  
	a1.setPos("LM14")   
	assert 0 == len(m.getBlockLines()) 
	
	
def testisLeaf():
	import mapMgr
	m = mapMgr.mapInfo.load("testmap.smap")
	assert m.getPos("CP12").isChargePoint
	assert not m.getPos("Y1").isChargePoint
	ll = ["LM11","LM10","Y1","Y2","LM13","CP12"] 
	for p in m.positions:
		if p.name not in ll:
			assert not p.isLeaf
		else:
			assert p.isLeaf 
			
#	cc = ["LM2","LM3","LM4"]
#	for p in m.positions:
#		if p.name not in cc:
#			assert not p.isLevel()
#		else:
#			assert p.isLevel()
	
	m = mapMgr.mapInfo.load("408.smap")
	ll = ["CP13","AP3","AP6","CP9","LM18","LM19"] 
	for p in m.positions:
		if p.name not in ll:
			assert not p.isLeaf
		else:
			assert p.isLeaf  
#	cc = ["LM14","AP7","LM2","LM1","LM4","LM5","LM11"]
#	for p in m.positions:
#		if p.name not in cc:
#			assert not p.isLevel()
#		else:
#			assert p.isLevel()
	assert m.getPos("CP13").isChargePoint
	assert m.getPos("CP9").isChargePoint
	assert not m.getPos("LM4").isChargePoint
			
			

def test_contain():
	import local
	import ui
	local.set("project","agvcfg","testagv2.cfg")
	import utility
	import agvControl
	import mapMgr
	from matplotlib import pyplot as plt
	mapMgr.setActive("testscada")
	m = agvControl.getMap("testscada")
	line = m.getLine("LM28","LM29")
	
	box = line._lineBound 
	aa = []
	for p in line.ptrList:
		assert line.contains(p[0],p[1])
		if not line.contains(p[0],p[1]):
			#aa.append(box.containsPoint(PyQt5.QtCore.QPointF(p[0],p[1]),1),p[0],p[1])
			aa.append(p) 
	
	ui.pltUtil.addPath(box,inverse=False)
#	plt.plot(np.array(line.ptrList).T[0],np.array(line.ptrList).T[1],"g*")
#	plt.plot(np.array(aa).T[0],np.array(aa).T[1],"r*")
#	ui.pltUtil.fix()
#	ui.pltUtil.show()
	
	
def test_check_path():
	import local
	local.set("project","agvcfg","testagv2.cfg") 
	import utility
	import agvControl
	import mapMgr
	m = mapMgr.getMap("big")
	assert m.getPos("AP749").isApType
	assert m.getPos("AP742").isApType
	assert not m.getPos("LM111").isApType
	assert m.getPos("AP29").isApType
	import agvList
	import driver.seerAgv.mockAgvCtrl as agvCtrl
	agvCtrl.disableBattery() 
	import time
	utility.start()
	agvList.g_agvList = None
	mapMgr.g_agvs = {}
	
	
	while True:  
		#等待所有agv上线 
		aa = agvControl.getAgvList()
		for a in aa:
			if aa[a].status is None:
				time.sleep(0.5) 
				break
		else:
			time.sleep(0.5)
			break 
			 
#	mapMgr.setActive("testscada")
	m = agvControl.getMap("testscada")
	t = utility.ticks()
	#for i in range(10):
	#	pp = m.getPath("LM38","LM25")	#旧版本耗时：4377ms，新版本3197
	#print(utility.ticks() - t)
	agv1 = m.getAgv("agv91")
	pp = m.getPath("LM41","LM36")[0][1]
	agv1.setTargetList(pp)  
	agv1.nextTargetPosName = pp[-1]
	agv1.setPos("LM28") 
	agvCtrl.setXY(agv1.agvId,2.84,1.77,math.pi)
#	agvControl.show() #查看check的路径是否显示正常 
	
def test_slow():
	import mapMgr,counter
	m = mapMgr.mapInfo.load("big")
	line = m.getLine("LM300","LM301")
	c = counter.counter()
	a = line.blockPath(x=0,y=1,w=1.2,h=1.2)
	b = line.blockPath(x=0,y=1,w=1.2,h=1.2)
	a.intersects(b)
	c.check()
	m.show()
		
if __name__ == "__main__":  
	utility.run_tests()
	
	
	
	
	
	
