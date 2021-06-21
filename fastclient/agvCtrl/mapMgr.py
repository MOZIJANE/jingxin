# coding=utf-8
# 地图的管理
import os, sys
import glob
import math
import time
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import counter
import json_codec as json
import utility
import PyQt5.QtGui
import PyQt5.QtCore 
import log
import local
import lock as lockImp 
import mongodb as db
import agvCtrl.doorMgr as doorMgr
import agvCtrl.elevatorMgr as elevatorMgr 
from mapElement import *
# if utility.is_test(): 
	# import driver.seerAgv.mockAgvCtrl as agvCtrl 
# else:
	# import driver.seerAgv.agvCtrl as agvCtrl
from matplotlib import pyplot as plt
from matplotlib import animation
import blockCfg
import enhance  

g_map = {} 
g_agvs = {}
g_actived_map = set()
g_lock = lockImp.create("mapMgr.lock")  
projectName = local.get("project","name")

def printLines(lines):
	print([str(l) for l in lines])
	

def isActived(mapId):
	global g_actived_map
	if len(g_actived_map) == 0:
		return True
	return mapId in g_actived_map

def setActive(mapId):
	global g_actived_map
	g_actived_map.add(mapId)
	
def getMap(mapId):
	global g_map 
	if mapId not in g_map:
		g_map[mapId] = mapInfo.load(mapId + ".smap")
	return g_map[mapId]
 
def getMapList():
	import json as json2
	proName = local.get("project","name")
	if utility.is_test():
		proName = "test" 
	pp = os.path.abspath(os.path.dirname(__file__)) + "/projects/" + proName + "/"
	mapPath = pp + "*.smap" 
	ret = []
	for f in glob.glob(mapPath):
		id = os.path.splitext(os.path.split(f)[1])
		if id[1] != ".smap":
			continue
		file = open(f, "t+r")
		gg = json2.load(file)
		file.close()
		ret.append({"id": id[0], "name": gg["header"]["mapName"]})
	return ret

@lockImp.lock(g_lock)
def loadAllMap():
	for m in getMapList():
		getMap(m["id"])
		

#解析出楼层信息 
def decodeLoc(loc):
	index = loc.find(".")
	if index == -1:
		return "",loc
	return loc[0:index],loc[index+1:]
	
#格式化地图上的点  
def formatLoc(mapId,loc):
	if mapId and loc.find(".") == -1:
		return mapId + "." + loc
	return loc

	
def isSameMap(loc1,loc2):
	m1,_ = decodeLoc(loc1)
	m2,_ = decodeLoc(loc2)
	return m1 == m2


def getMapRawData(fileName):
	import json as json2
	mapId = fileName
	
	proName = local.get("project","name")
	if utility.is_test():
		proName = "test" 
	mapPath = os.path.abspath(os.path.dirname(__file__)) + "/projects/" + proName + "/" + fileName 
	if mapPath[-5:] != ".smap":
		mapPath += ".smap"
	else:
		mapId = mapId[0:-5]
	with open(mapPath, "r") as fp:
		# jsonObj = json2.loads(fp.read())
		return fp.read()
 

def saveMapInfo(params):
	id = params["name"]
	del params["name"]
	db.update_one("r_map_info",{"_id": id},params,True)
	return True
	
def getMapInfo(name):
	ds = db.find("r_map_info",{"_id": name})
	info = {}
	while ds.next():
		info = {
		'name' : ds["_id"],
		'scale' : ds["scale"],
		'rotateX' : ds["rotateX"],
		'rotateY' : ds["rotateY"],
		'theta' : ds["theta"],
		'offsetX' : ds["offsetX"],
		'offsetY' : ds["offsetY"]
		}
	return info

def checkDoorClose():
	global g_map
	for m in g_map.values():
		m.checkDoorClose()
	
	
def _getAgvs():
	global g_agvs,g_lock
	if g_agvs:
		return g_agvs
	import agvList 
	mm = agvList.getAgvList()  
	r = {}
	for a in mm: 
		agv = mm[a]
		agvElement = agvPoint(agv.agvId)
		agvElement.agvInfo = agv
		r[a] = agvElement
	g_agvs = r
	return g_agvs 
	
	
def getAgv(agvId):
	aa = _getAgvs() 
	if agvId not in aa:
		return None
	return aa[agvId]
	
	
def getAgvList(mapId):
	r = []
	aa = _getAgvs()
	for a in aa:
		if not mapId or aa[a].mapId == mapId:
			r.append(aa[a])
	return r
	
@json.rename("points", "normalPosList")
@json.list_type("normalPosList", point())
@json.list_type("header", headerInfo())
@json.rename("positions", "advancedPointList")
@json.list_type("advancedPointList", advancedPoint())
@json.rename("curves", "advancedCurveList")
@json.list_type("advancedCurveList", advancedCurve())
class mapInfo:
	def __init__(self):
		self.header = None
		self.points = []		#点云
		self.positions = []  	#特殊点
		self._posMap = {}  		#特殊点字典
		self.curves = []  		#曲线
		self._curvesMap = {}  	#曲线字典
		self.mapId = ""  		#地图id   
		self.tableFigure = None
		self.doors = None
		self.dijkstraMap = None
		self.blockCfg = blockCfg.blocks()	#静态配置的block线段 
	
	@property
	def width(self):
		return 	abs(self.header.maxPoint.x - self.header.minPoint.x)
	
	@property
	def height(self):
		return abs(self.header.maxPoint.y - self.header.minPoint.y)
		
	def index(self,pos):
		return self.getPos(pos).index
	
	@property
	def agvs(self):
		return getAgvList(self.mapId)
		
	
	def hasAgv(self,agvId):
		return self.getAgv(agvId) is not None
		
		
	def getAgv(self, agvId):
		aa = self.agvs
		for a in self.agvs: 
			if a.agvId == agvId:
				if a.mapId == self.mapId:
					return a
				else:
					return None
		return None 
	
	#取出除agvId的所有路线，返回顺路和逆行的线段(返回字符串，不是ID)  
	@lockImp.lock(g_lock)
	def getAgvPath(self,agvId):
		def tryBlock(line):
			#if line.isBlocked:
			#	return True
			o = line.oposite
			if not o:
				return True
			if not o.isBlocked:
				return True
			if 1 == len(o.blockAgvId) and agvId in o.blockAgvId:
				return True
			return False
			
		ret1 = []
		ret2 = []
		resPath = []
		#stopAgvPos = [] 
		for a in getAgvList(None): 
			if a.agvId == agvId:
				continue
			try:
				ppp = a.getTargetLines(self) 
			except Exception as e:
				log.exception(a.agvId+" getTargetLines error",e)
				ppp = []
			
			if ppp:
				#先添加第一段路径 
				for p in ppp[0]:
					#去重复 
					if p not in ret1:
						ret1.append(p)
				if len(ppp) > 1:
					for pp in ppp[1:]:
						resPath += pp
			#if not a.agvInfo.isMoving() and a.agvInfo.curTarget and a.mapId == self.mapId:
			#	stopAgvPos.append(self.getPos(a.agvInfo.curTarget))			
			
		#添加后继路径
		for p in resPath:
			if p.oposite and p.oposite in ret1:
				continue
			if p in ret1:
				continue
			ret1.append(p)
		
		ret3 = []
		for r in ret1:
			if tryBlock(r):
				ret3.append(str(r))
			if r.oposite:
				ret2.append(str(r.oposite))
		#for p in stopAgvPos:
		#	#有车停在路上
		#	ret2 += [str(l) for l in p.nextLines]
		#	ret2 += [str(l) for l in p.preLines]
		#print(agvId,[str(r) for r in ret1],ret2)
		return ret3,ret2
	
	
	
	@staticmethod
	def load(fileName):
		def saveTrimMap(old,pp):
			f = open(old,"r")
			ss = f.read()
			f.close()
			index = ss.find('"normalPosList":[')
			if index == -1:
				return
			end = ss.find("]",index)
			f = open(pp,"w")
			f.write(ss[0:index])
			f.write('"normalPosList":[]')
			f.write(ss[end+1:])
			f.close()
		
		if fileName is None:
			raise Exception("map file name is None")
			
		count = counter.counter() 
		mapId = fileName
		proName = local.get("project","name")
		if utility.is_test():
			proName = "test"
		
		pp = os.path.abspath(os.path.dirname(__file__) + "/projects/" + proName + "/" + fileName)
		if pp[-5:] != ".smap":
			pp += ".smap"
		else:
			mapId = mapId[0:-5] 
		log.info("start load map",pp)
		ctime = str(os.path.getmtime(pp))
		cacheDir = os.path.dirname(__file__) + "/projects/" + proName + "/cache"
		cacheFile = cacheDir+"/"+mapId+"_trim_"+ctime+".smap"
		if not os.path.exists(cacheDir):
			os.mkdir(cacheDir)
		oldPath = pp
		if os.path.exists(cacheFile):
			pp = cacheFile
		else:
			saveTrimMap(pp,cacheFile)
		if not os.path.exists(pp):
			raise Exception("No such map file:"+pp)
		ret = json.load_file(pp, tmpclass=mapInfo())
		for p in ret.positions:
			assert p.name not in ret._posMap
			ret._posMap[p.name] = p
			p.property = mapInfo._decodeProperty(p._p)
			p._map = ret
		for c in ret.curves:
			c._positions = ret._posMap
			c._map = ret
			c.property = mapInfo._decodeProperty(c._p)
			ret._curvesMap[str(c)] = c
		for c in ret.curves:
			o = ret.getLine(c.endPos.name, c.startPos.name)
			if o is None:
				continue
			c._opositeLine = o
			p = o.ptrList #初始化bezier 

		ret.mapId = mapId
		ret._init(oldPath,ctime)		
		log.info("load map",oldPath,",used",count.get(),"ms")
		return ret

	
	#@lockImp.lock(g_lock)
	@utility.catch
	def drawAgv(self,fig):  
		if fig is None:
			fig = plt.figure(self.mapId)   
		aa = _getAgvs()
		for a in aa.values():
			if a.mapId == self.mapId:
				try:
					a.draw(fig)
				except Exception as e:
					log.exception("drawAgv",e)
		if self.doors:
			self.doors.draw() 
		elevatorMgr.draw(self.mapId) 
		
	#@lockImp.lock(g_lock)
	@utility.catch
	def draw(self,showPoint,showText=True,fig=None):
		if fig is None:
			fig = plt.figure(self.mapId)
		plt.axis('off')
		#for key, spine in plt.gca().spines.items():
		#	# 'left', 'right', 'bottom', 'top'
		#	if key == 'right' or key == 'top':
		#		spine.set_visible(False)
		if showPoint:
			# draw min,max point
			fig.gca().plot(self.header.minPoint.x, self.header.minPoint.y, 'r+')
			fig.gca().plot(self.header.maxPoint.x, self.header.maxPoint.y, 'r+')
			# draw points
			fig.gca().scatter([p.x for p in self.points], [p.y for p in self.points], c="gray", s=1)
		
		# draw advance points
		for s in self.positions:
			try:
				s.draw(fig,showText)
			except Exception as e:
				log.exception("drawPos",e)
		#draw advance curves
		fig.gca().autoscale_view() 
		for c in self.curves:
			try:
				c.draw(fig)
			except Exception as e:
				log.exception("drawCurve",e)
		fig.gca().axis('equal') #变方型  

	
	def show(self, showPoint=False, showText=True,useQt=True):  
		self.draw(showPoint=showPoint, showText=showText)
		if useQt:
			import mainFrame 
			mainFrame.show(self.mapId) 
		else:
			plt.show()
	
	# 属性都是跟软件GUI或者算法相关的
	@staticmethod
	def _decodeProperty(propertys):
		def _getValue(p):
			tt = ["stringValue", "boolValue", "int32Value", "uint32Value", "int64Value", "uint64Value", "floatValue",
			      "doubleValue", "bytesValue"]
			cc = [str, bool, int, int, int, int, float, float, bytes]
			# TODO:没有bytes的样例
			for i, t in enumerate(tt):
				if t in p:
					return cc[i](p[t])

		ret = {}
		for p in propertys:
			ret[p["key"]] = _getValue(p)
		return ret 

	
	def getPathWeight(self, posStart, posEnd, agvId):
		if formatLoc(self.mapId,posStart) == formatLoc(self.mapId,posEnd):
			return 0
		pp = self.getPath(posStart,posEnd,agvId,writeLog=False)
		w = 0
		for p in pp:
			w += p[2]
			if p != pp[0]:
				if p[0] == self.mapId:
					w += 20	 #回头加20米
				else:
					w += 100 #每部电梯加100米权重 
		return w
		
		
	#返回[(mapId1,[path1,path2,...],w),(mapId2,[path1,path2,...],w)...] 列表
	def getPath(self,posStart, posEnd, agvId=None,writeLog=True,oplines = None):	
		posStart = formatLoc(self.mapId,posStart)
		posEnd = formatLoc(self.mapId,posEnd)
		if isSameMap(posStart,posEnd):
			if posStart == posEnd:
				return [(self.mapId,[],0),]
			w,pp,w2,pp2 = self.getPathSingle(posStart,posEnd,agvId,oplines=oplines)
			if len(pp) == 0:
				return []
			if pp2:
				return [(self.mapId,pp,w),(self.mapId,pp2,w2)]
			else:
				return [(self.mapId,pp,w)]
		#可能在另一张地图里 
		map1,pos1 = decodeLoc(posStart)
		map2,pos2 = decodeLoc(posEnd)
		ee = elevatorMgr.getElevator(map1,map2)
		if len(ee) == 0:
			return []
			
		#不支持一次导航走两部电梯的情况  
		w = sys.maxsize
		n = ""
		path = []
		for e in ee:   
			w1,path1,w11,path11 = getMap(map1).getPathSingle(pos1,e.findFloor(map1).loc,agvId,oplines=oplines) 
			w2,path2,w22,path22 = getMap(map2).getPathSingle(e.findFloor(map2).loc,pos2,agvId,oplines=oplines) 
			if w1 + w11 + w2 + w22 < w:
				w = w1 + w11 + w22 + w2
				path = [(map1,path1,w1),]
				if path11:
					path.append((map1,path11,w11))
					
				path.append((map2,path2,w2))
				if path22:
					path.append((map2,path22,w22))
				n = e.name
		if agvId is None:
			agvId = ""
		if writeLog:
			log.info(agvId,"use elevator: " + n, "," + strPaths(path))
		return path
		
	
	#根据其它的agv路线，来规划最短路径   
	#取节点最短的路径，如果需要调头，则返回两条路径  
	#返回：(权重1,路径1,权重2,路径2)
	def getPathSingle(self,posStart, posEnd, agvId, oplines = None):
		lines = []
		if oplines is None:
			oplines = []
		if agvId:
			#getAgvPath这会返回的line字符串 
			lines,oplines2 = self.getAgvPath(agvId) 
			oplines += oplines2
		w,pp = self.dijkstra(posStart, posEnd,lines=lines,oplines=oplines)
		if w is None: 
			return sys.maxsize,[],sys.maxsize,[] 
		if not pp or len(pp) < 2:
			return 0,pp,0,[]
			
		pp2 = []
		w2 = 0
		#交错时，一部车先倒车，再前进 
		line = self.getLine(pp[0],pp[1])
		newPath = None
		newWeight = 0
		index = 0
		if str(line) in oplines:
			log.info(agvId,line,"in oplines",oplines)
			newPath,newWeight,index = self.getNoBlockPaths(agvId,pp,oplines=oplines)
		#TODO:else: 暂不支持旋转判断 
		#TODO:	agv = getAgv(agvId)
		#TODO:	if agv:
		#TODO:		newPath,newWeight = self.updateNoTurnPath(pp,agv.r)
		if newPath:
			w += newWeight
			w2 = newWeight
			pp2 = newPath[::-1] + pp[1+index:]
			pp = pp[:index] + newPath
			log.info(agvId,"getPathSingle",posStart, "->", posEnd,",index",index,",add path1:",newPath,",path2:",pp2,",shelf:",getAgv(agvId).agvInfo.hasShelve)
		elif sys.maxsize == newWeight:
			log.error(agvId,"getPathSingle",posStart, "->", posEnd, "can't find detour path:",pp,",shelf:",getAgv(agvId).agvInfo.hasShelve)
		return w,pp,w2,pp2
		
	# 取出剩余的路线，并转换成advanceCurve列表
	def getStartLines(self, startPosName,lines):
		ret = []  
		for i in range(len(lines) - 1):
			if isinstance(lines[i],str):
				if startPosName is None or lines[i] == startPosName:
					start = lines[i + 1]
					line = self.getLine(lines[i], lines[i + 1])
					if line is None:
						raise Exception(self.mapId,"路径不存在3, " + str(lines[i])+"->"+str(lines[i+1])+", path : "+strPaths(lines))
					ret.append(line) 
					startPosName = None
		if len(lines):
			if isinstance(lines[0],advancedCurve):
				for line in lines:
					assert isinstance(line,advancedCurve)
					if startPosName is None or line.startPosName == startPosName:
						ret.append(line)
					elif len(ret):
						ret.append(line)
		return ret
					
	
	def getChargePosList(self):
		r = []
		for p in self.positions:
			if p.isChargePoint:
				r.append(p.name)
		return r
		
	def getPosByIndex(self,index):
		return self.positions[index]
	
	def getPos(self, posName): 
		m,loc = decodeLoc(posName)
		if m and m != self.mapId:
			raise Exception("getPos("+posName+")地图ID对应错误"+self.mapId)
		if loc not in self._posMap:
			raise Exception("getPos(),在地图"+self.mapId+"找不到位置"+loc)
		return self._posMap[loc]

	def getPosByPoint(self, x, y):
		pp = []
		for p in self.positions:
			if p.contains(x, y):
				d = p.distance(x,y)
				if d >= 0.2: #相差0.2米，才认为到达 
					continue
				pp.append((p,d))
		if not pp:
			return None
		return min(pp,key=lambda x : x[1])[0]
	
	def isNearPos(self,x,y,posName,distance=1.2):
		pos = self.getPos(posName)
		assert pos
		return pos.distance(x,y) < distance #小于1米算是接近 
	
	def getLine(self, startPosName, endPosName):
		key = decodeLoc(startPosName)[1] + "->" + decodeLoc(endPosName)[1]
		if key in self._curvesMap:
			return self._curvesMap[key]
		return None
		
	def getLineByPoint(self,x,y,paths):
		if len(paths) == 0:
			paths = self.curves
		for i in range(len(paths)-1): 
			line = self.getLine(paths[i],paths[i+1])
			if line and line.contains(x,y):
				return line
		return None

	 
	# 给web提供数据
	def webInfo(self):
		ap = []
		for a in self.positions:
			ap.append(
				{"name": a.name, "className": a.className, "ignoreDir": a.ignoreDir, "dir": a.dir, "color": a.color,
				 "x": a.x, "y": a.y})
		cc = []
		for a in self.curves:
			cc.append({"name": a.name, "className": a.className, "endPoint": a.endPos.name,
			           "startPoint": a.startPos.name, "controlPos1": a.ctrlPoint1, "controlPos2": a.ctrlPoint2})
		return {"header": self.header, "points": self.points, "advancedPointList": ap, "advancedCurveList": cc}

	# 取出当前所有被Block的线段信息，用于web显示
	def getBlockLines(self):
		return [x for x in self.curves if x.isBlocked]
	
	def _saveOneway(self,cacheFile,ret):
		json.dump_file(cacheFile,ret)
		
	def _loadOneway(self,filename,ctime): 
		cacheFile = os.path.dirname(filename)+"/cache/"+self.mapId+"_oneway_"+ctime+".cache"
		if os.path.exists(cacheFile): 
			return json.load_file(cacheFile)["oneway"]
		ret = []
		diff = local.getfloat("ctrl","pathDiff")
		for c in self.curves: 
			t = utility.ticks()
			pp,ww = self._getPaths(c.endPosName,c.startPosName,stopCount=2,maxWeight=diff+c.length)
			if len(pp) <= 1:
				ret.append([c.startPosName,c.endPosName]) 
		self._saveOneway(cacheFile,{"oneway":ret})
		return ret
		
	
	# 用于判断需要上锁的路径，解决断头路的问题
	def _init(self,filename,ctime):
		for c in self.curves:
			c.startPos.nextLines.append(c)  # 可以出去的线段列表
			c.endPos.preLines.append(c)  # 可以进来的线段
		onewayList = []
		for p in self._loadOneway(filename,ctime):
			c = self.getLine(p[0],p[1])
			c.isOneway = True
			onewayList.append(c)
		self._initDeadend() 
		self.blockCfg.load(self)
		for c in self.curves:
			c._updateBlockGroup(self)  
		self.doors = doorMgr.doors(self.mapId)
		self.doors.update(self.curves)
		elevatorMgr.updateMap(self) 
		self._updatePos(filename,ctime) 
		return onewayList
		  
		  
	def _updatePos(self,filename,ctime):
		def _save(cacheFile,ret):
			json.dump_file(cacheFile,ret)
		
		w = local.getint("ctrl","agv_turn_length",1)
		cacheFile = os.path.dirname(filename)+"/cache/"+self.mapId+"_turnable_"+str(w)+ctime+".cache"
		if os.path.exists(cacheFile): 
			pp = json.load_file(cacheFile)["no_turn_pos"]
			for p in pp:
				self.getPos(p).turnable = False
			return
 
		def checkTurnable(pos):
			for p in self.points: 
				if abs(pos.x-p.x) > w:
					continue
				if abs(pos.y-p.y) > w:
					continue
				d = math.sqrt((pos.x-p.x)**2+(pos.y-p.y)**2)
				if d < w:
					return False
			return True
		
		ret = []
		for pos in self.positions: 
			if not pos.rotation: 
				#倒退的，不需要判断，因为也不会旋转 
				pos.turnable = checkTurnable(pos)
			if not pos.turnable:
				ret.append(pos.name)
		_save(cacheFile,{"no_turn_pos":ret})
		return
		#通过配置方式	
		#proName = local.get("project","name")
		#if utility.is_test():
		#	proName = "test"
		#file = "projects/"+proName + "/no_turn_pos.cfg"
		#file = os.path.abspath(os.path.dirname(__file__)) + "/" + file
		#info = {}
		#if os.path.exists(file):
		#	info = json.load_file(file)
		#if self.mapId not in info:
		#	return
		#pp = info[self.mapId]
		#for p in pp:
		#	if p not in self.positions:
		#		continue
		#	pos = self.getPos(p)
		#	if len(pos.nextLines) <= 2:
		#		pos.turnable = False
			

	# 计算断头路的情况
	def _initDeadend(self):
		def findDeadend():
			find = False
			for p in self.positions:
				if True: #local.getint("ctrl","blockRangeType") == 2:
					if len(p.nextLines) > 2:	#小范围计算，大于2条路径，不计入deadend 
						continue
					if len(p.preLines) > 2:
						continue
				# 取出非deadend的列表，判断是否为deadend
				nn = [n for n in p.nextLines if not n.isDeadend]
				pp = [n for n in p.preLines if not n.isDeadend]
				if len(nn) == 1 and len(pp) == 1:
					# 来去都是A|B点，是deadend
					if nn[0].equal(pp[0].endPos.name, pp[0].startPos.name):
						nn[0].isDeadend = True
						pp[0].isDeadend = True
						find = True
				elif len(nn) == 0 and len(pp) == 1:
					pp[0].isDeadend = True
					find = True
				elif len(nn) == 1 and len(pp) == 0:
					nn[0].isDeadend = True
					find = True
			return find

		# 循环到找不到deadend为止
		while findDeadend():
			pass
		for p in self.positions:
			p.nextLines = sorted(p.nextLines,key=lambda x: x.length)
	
	
	def getNoBlockPaths(self,agvId,paths,oplines):
		for i,p in enumerate(paths):
			if paths[i] == paths[-1]:
				break
			if str(self.getLine(paths[i],paths[i+1])) not in oplines: #已经逃离路径
				return [],0,0
			ret,w = self._getNoBlockPaths(agvId,paths[i],paths[-1],oplines=oplines)
			if w != sys.maxsize:
				return ret,w + i * 4,i	#每逆行一格，加4米权重 
		return [],sys.maxsize,0
			
	
	#在这个点上查找不冲突的路径，找一条离开冲突的路径 
	def _getNoBlockPaths(self,agvId,startPos,endPos,oplines): 
		if not oplines:
			return [],0
			
		def arrive(pos):
			if pos == endPos:
				return True
			if pos in opPos:
				return False
			p = self.getPos(pos)
			return p.turnable or p.isLeaf
		
		def nextLine(line):
			if str(line) in oplines:
				return False
			if line.oposite is None:
				return False
			if line.endPos.isLeaf:
				if projectName == "fastprint":
					if line.endPosName in ["AP286","AP287"]:
						return False
				if agv and agv.agvInfo.hasShelve:
					return False
			if line.endPos.inElevator():
				return False
			a = line.endPos.agvId
			if a:
				agv2 = getAgv(a)
				return agv2.agvInfo.isRunning()
			return True
		
		agv = getAgv(agvId)
		opPos = set()
		for l in oplines:
			line = self._curvesMap[l]
			opPos.add(line.startPosName)
			opPos.add(line.endPosName)
			
		if arrive(startPos):
			return [],0
		
		pos = startPos
		stack = [startPos,]
		paths = [] 
		weights = []
		visit = set()
		weight = sys.maxsize 
		#stack.append(pos)  
		wstack = [] #权重的堆栈 
		wstack.append(0)  
		while stack:  
			pos = stack[-1]
			ww = sum(wstack) 
			if arrive(pos):   
				#找到一条路径
				if weight > ww:
					weight = ww
					paths = stack[:]
				pos = stack.pop()
				continue 
				
			find = False 
			for line in self.getPos(pos).nextLines:   
				if line in visit:
					continue 
				visit.add(line)
				if not nextLine(line):
					continue
				if line.endPosName in stack: 	
					continue  
				if (ww + line.length) > weight:
					continue
				stack.append(line.endPosName) 
				wstack.append(line.length)
				find = True 
				break 
			if not find:  
				for line in self.getPos(pos).nextLines:  
					if line in visit:
						visit.remove(line)  
				pos = stack.pop()  
				wstack.pop() 
		return paths,weight
		
		
	#更新不能转头的路径，让其走更远再转头 
	def updateNoTurnPath(self,path,r):
		if len(path) < 2:
			return [],0
		if self.getPos(path[0]).turnable:
			return [],0
		line = self.getLine(path[0],path[1])
		if abs(normAngle(r - line.r)) <= math.radians(100):
			return [],0
		next = path[0]
		newPath = [next,]
		pp = path[:]
		w = 0
		for i in range(100):
			pos = self.getPos(next)
			if pos.turnable: 
				break
			
			otherLine = None
			for other in pos.nextLines:
				if abs(normAngle(r - other.r)) >= math.radians(45):
					continue
				if other.endPosName not in pp:
					otherLine = other
					break
			if otherLine is None:
				break
			w += otherLine.length
			next = otherLine.endPosName 
			pp.insert(0,next)
			newPath.append(next) 
		if newPath:
			log.info("add noturn path:",newPath,",old path:",path)
		return newPath,w
		
		
	#判断是否有个AGV在路径并，并具堵着路 
	def _hasBlockAgv(self,agvId,line):
		a = line.agvId 
		if a is None:
			return None
		if a == agvId:
			return None
		agv = self.getAgv(a)
		if not agv.agvInfo.isMoving(): #不移动的，才算堵路 
			return a
		return None
	
	def checkDeadline(self,agvId,startPos,paths):
		#判断这条线段是否存死锁的agv 
		def hasDeadlockAgv(pos):
			a = self.getPos(p).agvId
			if not a:
				return ""
			if a == agvId:
				return ""
			if self.getAgv(a).isDeadlock:
				return a
			return ""
		
		find = False
		i = 0
		for p in paths:
			if i >= 5:
				return ""
			if p == startPos:
				find = True
			if find:
				a = hasDeadlockAgv(p)
				if a:
					return a
				i+=1
			if i >= 5:
				return ""
		return ""
	
	@lockImp.lock(g_lock)
	def block(self, agvId, startPosName, endPosName, paths):   
		def _tryBlock(agv,line, paths):
			ret = line.tryBlock(agv.agvId,paths)
			a = self._hasBlockAgv(agv.agvId,line)
			if len(ret) != 0 or a is not None:
				agv.isBlocked = True
				if ret:
					agv.blockAgvs = ret 
				else:
					agv.blockAgvs = [a,] 
				agv.blockFailLines = [str(line),]
				return False 
			#ret = self._hasBlockAgv(agv.agvId,line)
			#if ret is not None:
			#	agv.isBlocked = True
			#	agv.blockAgvs = [ret,] 
			#	agv.blockFailLines = [str(line),]
			#	#log.warning("block",agv.agvId,"failed,",ret,"is in the way,line",str(line))
			#	return False
			return True
		
		assert isinstance(paths,list)
		for p in paths:
			if not isinstance(p,str):
				log.error("block wrong type",p,type(p))
			assert isinstance(p,str)
				
		if startPosName == endPosName:
			return True
		agv = self.getAgv(agvId)
		checkLines = self.getStartLines(startPosName, paths) 
		if len(checkLines) == 0: 
			raise Exception(agvId+" block failed, mapId:"+str(self.mapId)+",unknow line:" + startPosName + ", paths:" + ",".join([ str(x) for x in paths ])) 
		
		cc = []
		for i in range(len(checkLines)):	
			cur = checkLines[i]
			cc.append(cur) 
			if cur.endPosName == agv.nextTargetPosName:
				if len(cur.endPos.neighbors) <= 2:#同一条线，没有分叉 
					break
				if i+1 < len(checkLines):
					next = checkLines[i+1]
					#if next.isOneway:
					cc.append(next) 
				break 
		
		for c in cc:
			if not _tryBlock(agv,c,checkLines):
				return False 
		
		agv.isBlocked = False
		agv.blockFailLines = []
		for c in cc:
			c.block(agvId,checkLines)
		return True
			 
	
	@lockImp.lock(g_lock)
	def unblock(self, agvId):
		a = self.getAgv(agvId)
		if a:
			a.unblock()

	
	@lockImp.lock(g_lock)
	def checkDoorClose(self):
		ret = []
		for a in self.agvs:
			ret += a.getCheckLines()
		self.doors.checkClose(ret)   
	
	def getWeight(self,paths):
		if isinstance(paths,advancedCurve):
			return paths.length
		pp = self.getStartLines(None,paths) 
		return sum([line.length for line in pp])
	 
	#https://www.jb51.net/article/126882.htm 
	#用递归的方法会很慢，该算法用了深度优先算法DFS 
	#返回路径和对应的权重  
	def _getPaths(self,startPos,endPos,stopCount=sys.maxsize,maxWeight=sys.maxsize,lines=None,oplines=None,exlines=None): 
		pos = self.getPos(endPos)
		x,y = pos.x,pos.y
		pos = startPos
		stack = []
		paths = [] 
		weights = []
		visit = set()
		curWeight = sys.maxsize 
		stack.append(pos)  
		wstack = [] #权重的堆栈 
		wstack.append(0) 
		diff = local.getfloat("ctrl","pathDiff") 
		while stack:  
			if len(paths) >= stopCount:
				return paths,weights   
			pos = stack[-1]
			ww = sum(wstack) 
			if pos == endPos:   
				#找到一条路径 
				weights.append(ww)  
				paths.append(stack[:]) 
				pos = stack.pop() 
				wstack.pop()
				curWeight = min(ww,curWeight)  
				maxWeight = min(curWeight + diff,maxWeight)
				continue 
				
			find = False 
			for line in self.getPos(pos).nextLines:   
				if line in visit:
					continue 
				visit.add(line)
				ss = str(line)
				if exlines and ss in exlines:
					continue
				if line.endPosName in stack: 	
					continue  
				lw = line.length
				
				if lines and ss in lines:
					lw *= 0.5
				elif oplines and ss in oplines:
					lw *= 4.  	
				if (ww + lw) > maxWeight+0.1:
					continue
				distance = line.endPos.distance(x,y)
				if (ww + lw + distance) > maxWeight+0.1:
					continue
				stack.append(line.endPosName) 
				wstack.append(lw)
				find = True 
				break 
			if not find:  
				for line in self.getPos(pos).nextLines:  
					if line in visit:
						visit.remove(line)  
				pos = stack.pop()  
				wstack.pop() 
		return (paths,weights)

			
	#查找点与点之间的所有路径 [[w1,[LM1,LM2]],...[w2,[LM1,LM2]]]
	def getAllPaths(self,startPos,endPos,stopCount=sys.maxsize,maxWeight=sys.maxsize,lines=None,oplines=None,exlines=None):
		_,startPos = decodeLoc(startPos)
		_,endPos = decodeLoc(endPos)  
		allPaths,ww = self._getPaths(startPos,endPos,stopCount=stopCount,maxWeight=maxWeight,lines=lines,oplines=oplines,exlines=exlines)
		ret = zip(ww,allPaths)
		ret = sorted(ret)
		return ret
		
	#最短路径的算法 
	def dijkstra(self, startPos, endPos,lines=None,oplines=None): 
		_,startPos = decodeLoc(startPos)
		_,endPos = decodeLoc(endPos)
		import routeCalc
		dict = routeCalc.dijkstra(self._getDijkstraMap(lines=lines,oplines=oplines), startPos)
		if endPos not in dict:
			return None,[]
		ret = dict[endPos]
		return ret[0], ret[1]
	 
	
	# 取出用于最短路径算法的结构体，lines表示顺路的线段 
	def _getDijkstraMap(self,lines,oplines): 
		if self.dijkstraMap and lines is None:
			return self.dijkstraMap 
		def _getw(line):
			if lines and str(line) in lines:
				return line.length*0.5
			elif oplines and str(line) in oplines: 
				return line.length*4.
			else:	
				return line.length
				
		# 取出和posName相临的线段及长度
		def _getPosDirectLines(self, posName):
			pos = self.getPos(posName)
			return [(l.endPosName,_getw(l)) for l in pos.nextLines]

		ret = {}
		for pos in self.positions:
			currentDict = {}
			for line in _getPosDirectLines(self, pos.name):
				currentDict[line[0]] = line[1]
			currentDict[pos.name] = 0
			ret[pos.name] = currentDict
		if lines is None:
			return ret
		self.dijkstraMap = ret
		return self.dijkstraMap
		 
	
	
################## unit test ##################  
def testbegin(file="agv.cfg"):
	import time,local
	import agvList,mapMgr 
	global g_agvs
	local.set("project","agvcfg",file)
	#第一个测试上所有agv先上线 
	utility.start()    
	g_agvs = {} 
	agvList.g_agvList = None
	while True:
		#等待所有agv上线 
		aa = agvList.getAgvList()
		for a in aa:
			if aa[a].mapId is None:
				time.sleep(0.5) 
				break
			if aa[a].status is None:
				time.sleep(0.5) 
				break
		else:
			time.sleep(0.5)
			break    
	mapMgr.g_agvs = g_agvs
	if file!="agv.cfg":
		return
	m = mapInfo.load("test430.smap") 
	aa = agvList.getAgvList()   
	assert m.getAgv("agv61")
	assert m.getAgv("agv62")
	m2 = mapMgr.getMap("test430")
	assert m2.getAgv("agv61")
	assert m2.getAgv("agv62")
	

def testshortPath(): 
	import agvList
	m = mapInfo.load("testscada.smap")
	assert 3 == len(m.getPos("LM14").nextLines)
	ret = m.shortPath("LM14", "LM27")
	assert ret[1] == ["LM14", "LM27"]
	m = mapInfo.load("testmap.smap")
	ret = m.shortPath("LM11", "LM10")
	assert utility.equal(ret[0], 4.63, 0.01)
	assert ["LM11", "LM10"] == ret[1]

	ret = m.shortPath("LM10", "LM11")
	assert ret[0] is None
	assert [] == ret[1]

	ret = m.shortPath("LM13", "LM6")
	assert ret == (18.6837017378557, ['LM13', 'LM1', 'LM2', 'LM3', 'LM4', 'LM5', 'LM6'])
 
	oneway = ["LM11", "LM14", "LM13", "LM15"]
	m = mapInfo.load("test430.smap") 
	
	agv = m.getAgv("agv61")
	assert agv
	agv2 = m.getAgv("agv63")
	assert agv2
	agv2.setPos("LM26")
	 
	assert m.getPos("LM26").contains(agv2.x,agv2.y) 
	assert "agv63" == m.getLine("LM26","LM23").agvId
	assert "agv63" == m.getLine("LM23","LM26").agvId
	 
	pp = m.getPath("LM23", "LM1",agvId = "agv61") 

	assert pp[0][0] == "test430"
	pp = pp[0][1]

	assert len(pp) == 5
	assert utility.assert_array_noorder(pp,["LM23","LM12","LM28","LM29","LM1"])
	agv2.setPos("LM25")
	pp = m.getPath("LM23", "LM1",agvId = "agv61")[0][1]
	
	assert len(pp) == 3
	assert utility.assert_array_noorder(pp,["LM23","LM26","LM1"])

	pp = m.getPath("LM23", "LM30",agvId = "agv61")[0][1]
	assert len(pp) == 5
	assert utility.assert_array_noorder(pp,["LM23","LM26","LM1","LM25","LM30"])
			

	
def testdecodeLoc():
	assert ("ycat","LM190") == decodeLoc("ycat.LM190")
	assert ("","LM11") == decodeLoc("LM11")
	assert ("ycat","LM19.0") == decodeLoc("ycat.LM19.0")
	
def testgetallpath():
	import agvList
	m = mapInfo.load("test430.smap")  
	ww = m.getWeight([m.getLine("LM23","LM26"),])
	assert  ww == m.getLine("LM23","LM26").length  
	pp = m.getAllPaths("LM29","LM23")  
	pp = m.getAllPaths("AP7","LM26") 
	assert 2 == len(pp)
	assert ['AP7', 'LM23', 'LM26'] == pp[0][1]
	assert ['AP7', 'LM23', 'LM12', 'LM28', 'LM26'] == pp[1][1]
	
	pp = m.getAllPaths("LM29","LM29") 
	assert [(0, ['LM29'])] == pp
	
	pp = m.getAllPaths("LM29","LM23")
	assert 12 == len(pp)
	
	pp = m.getAllPaths("LM23","LM23")
	assert len(pp) == 1
	assert pp[0][0] == 0 
	for p1 in m.positions:
		for p2 in m.positions:
			pp = m.getAllPaths(p1.name,p2.name)
	
	m = mapInfo.load("testmap.smap")
	pp = m.getAllPaths("LM11","LM13")
	assert len(pp) == 0
	for p1 in m.positions:
		for p2 in m.positions:
			pp = m.getAllPaths(p1.name,p2.name)

	
		
def testnear():
	m = mapInfo.load("8-222.smap") 
	assert m.isNearPos(-0.4,0.5,"LM15")
	assert not m.isNearPos(-2.4,0.5,"LM15")
	assert m.getLineByPoint(5.43,-2.65,["LM18","LM16","LM11","LM14"]) == m.getLine("LM16","LM11")
	assert m.getLineByPoint(15.43,-2.65,["LM18","LM16","LM11","LM14"]) == None 
	assert m.getLineByPoint(6.88,-4.54,["LM19","LM17","LM16"]) == m.getLine("LM19","LM17") 
	
def testangle():
	m = mapInfo.load("8-222.smap") 
	line = m.getLine("LM15","LM8")
	#line = m.getLine("LM18","LM16")
	step = 0.0 
	for i in range(10):
		print(line.angleAtPercent(step)/3.14*180,step)
		step += 0.1
	step = 0.0 
	for i in range(10):
		print(line.pointAtPercent(step),step)
		step += 0.1 
 

def testblockpath(): 
	import threading, time
	import agvList
	import matplotlib.path as mpath
	import matplotlib.patches as mpatches
	m = mapInfo.load("testmap.smap")    
	agv1 = m.getAgv("agv1")
	#assert agv1.currentPos == "LM13"
	agv1.setPos("LM13")
	agv1.nextTargetPosName = "LM1" 
	agv1.setTargetList(["LM13","LM1"])
	m.block(agv1.agvId, "LM13", "LM1", ["LM13", "LM1"]) 
	agv2 = m.getAgv("agv2")
	agv2.setPos("Y2")
	agv2.nextTargetPosName = "Y1" 
	agv2.setTargetList(["Y2","Y1"])
	agv3 = m.getAgv("agv3") 
	agv3.setPos("LM11") 
	assert agv2.check([agv3,]) 
	assert agv1.check([agv3,])   
	assert not agv2.check([agv1,agv3])  
	assert agv1.check([agv2,agv3]) 
	assert agv1.check([agv2,agv3])
	 
	m.block(agv2.agvId, "Y2", "Y1", ["Y2", "Y1"]) 


def testblock_oneway(): 
	import agvList
	import mapMgr
	oneway = ["LM11", "LM14", "LM13", "LM15"]
	mapMgr.g_map = {}
	m = mapMgr.getMap("test2")
	agv = m.getAgv("agv12")   
	assert agv
	agv2 = m.getAgv("agv13")
	assert agv
	assert m.block("agv12", "LM11", "LM14", oneway) 
	assert 4 == len(m.getBlockLines())
	assert "agv12" in m.getLine("LM11","LM14").blockAgvId
	m.unblock("agv12")  
	assert 0 == len(m.getBlockLines())

	# 测试单线的断头路
	# 把deadend全部锁定
	assert m.block("agv12", "LM14", "LM13", oneway) 
	assert 3 == len(m.getBlockLines())
	assert m.getLine("LM14", "LM13").blockType == BLOCK_SHARE
	assert m.getLine("LM13", "LM15").blockType == BLOCK_EXCLUDE 
	assert m.getLine("LM15", "LM13").blockType == BLOCK_EXCLUDE
		
	# 在这个deaden区内，自己是可以重复block的
	ll = ["CP7", "LM8", "LM15", "LM13"]
	assert m.block("agv12", "CP7", "LM8", ll)
	assert m.block("agv12", "LM15", "LM8", ["LM11", "LM14", "LM13", "LM15", "LM8", "CP7"])
	assert m.block("agv12", "LM8", "LM15", ll)
	assert m.block("agv12", "LM8", "CP7", ["LM11", "LM14", "LM13", "LM15", "LM8", "CP7"])
	assert m.block("agv12", "LM13", "LM15", ["LM11", "LM14", "LM13", "LM15", "LM8", "CP7"])

	# agv在独占区，是无法unblock的
	for o in ["LM13", "LM15", "LM8", "CP7"]:
		agv.setPos(o) 
		agvCtrl.setPos(agv.agvId,o) 
		m.unblock("agv13")  
		#print([str(l) for l in m.getBlockLines()]) 
		assert 7 == len(m.getBlockLines()) 
		# 别的agv进不来
		assert not m.block("agv13", "LM14", "LM13", oneway)

	# agv离开，可以unblock了
	agv.setPos("LM12")
	agvCtrl.setPos(agv.agvId,"LM12")
	m.unblock("agv12")
	assert 0 == len(m.getBlockLines())
 
def testblock_oneway2():
	import agvList
	import mapMgr
	mapMgr.g_map = {}
	oneway = ["LM16", "LM18", "Y1", "Y2", "Y3"]
	m = mapMgr.getMap("test2")  
 
	agv = m.getAgv("agv12")
	agv2 = m.getAgv("agv13")
	agv3 = m.getAgv("agv11") 
	agv3.setPos("LM19")
	agv2.setPos("LM15")
	agvCtrl.setPos(agv2.agvId,"LM15")
	 
	# 测试单线的断头路
	# 把deadend全部锁定 
	assert m.block("agv12", "LM16", "LM18", oneway)   
 
	assert 5 == len(m.getBlockLines())
	assert m.getLine("LM16", "LM18").blockType == BLOCK_SHARE
	assert m.getLine("LM18", "Y1").blockType == BLOCK_SHARE
	assert m.getLine("Y1", "Y2").blockType == BLOCK_SHARE
	assert m.getLine("Y2", "Y3").blockType == BLOCK_EXCLUDE
	assert m.getLine("Y3", "Y2").blockType == BLOCK_EXCLUDE
	agv.setTargetList(oneway)
	agv.setPos("LM16")
	m.unblock("agv12")    
	assert 5 == len(m.getBlockLines()) 
	
	# agv在独占区，是无法unblock的 , "Y1", "Y2", "Y3"
	agv.setPos("LM18")
	m.unblock("agv12")    
	assert 4 == len(m.getBlockLines()) 
	agv.setPos("Y1")
	m.unblock("agv12")    
	assert 3 == len(m.getBlockLines()) 
	agv.setPos("Y2")
	m.unblock("agv12")    
	assert 2 == len(m.getBlockLines())
	agv.setPos("Y1")
	m.unblock("agv12")    
	assert 2 == len(m.getBlockLines())
	
	# 在这个deaden区内，自己是可以重复block的 
	assert m.block("agv12", "LM18", "Y1", oneway)
	assert m.block("agv12", "Y2", "Y3", oneway)
	 
	# 别的agv进不来
	assert not m.block("agv13", "LM16", "LM18", oneway) 
		 
	# agv离开，可以unblock了
	agv.setPos("LM12") 
	m.unblock("agv12")
	assert 0 == len(m.getBlockLines())


def testblock_oneway3():
	import agvList
	import mapMgr
	m = mapMgr.getMap("testmap")
	agv3 = m.getAgv("agv3") 
	agv3.setPos("LM11")
	oneway = ["LM6", "LM7", "LM5", "LM4", "LM3", "LM2", "LM1"]
	agvCtrl.setXY("agv1", 0, 0, 0)
	agvCtrl.setXY("agv2", 0, 0, 0)
	agv = m.getAgv("agv1") 
	agv2 = m.getAgv("agv2")
	assert m.block("agv1", "LM6", "LM7", oneway)
	assert 6 == len(m.getBlockLines())
	m.unblock("agv1")
	assert m.block("agv1", "LM7", "LM5", oneway) 
	assert 5 == len(m.getBlockLines())
	agv.setPos("LM6")
	agvCtrl.setPos(agv.agvId,"LM6")
	m.unblock("agv1")
	assert 0 == len(m.getBlockLines())
	
	agv3.setPos("LM5")
	assert m.block("agv1", "LM11", "LM10", ["LM11", "LM10"])
	assert 1 == len(m.getBlockLines())
	m.unblock("agv1")
	assert 0 == len(m.getBlockLines())

def testoneway_4():
	import agvList
	import mapMgr
	def equalLines(line1,line2):
		if len(line1) != len(line2):
			return False
		l1 = [str(x) for x in line1]
		l2 = [str(x) for x in line2]
		for a in l1:
			if a not in l2:
				return False
		return True
		
	m = mapMgr.getMap("bell")  
	assert 15 == len(m.getLine("LM3", "LM7")._blockGroup)
	#printLines(m.getLine("LM7", "LM8")._blockGroup)
	assert 15 == len(m.getLine("LM7", "LM8")._blockGroup)
	assert 15 == len(m.getLine("LM8", "LM9")._blockGroup)
	assert equalLines(m.getLine("LM8", "LM9")._blockGroup,m.getLine("LM7", "LM8")._blockGroup)
	assert equalLines(m.getLine("LM3", "LM7")._blockGroup,m.getLine("LM7", "LM8")._blockGroup)
	assert not equalLines(m.getLine("LM3", "LM7")._blockGroup,m.getLine("LM7", "LM3")._blockGroup)
	assert 15 == len(m.getLine("LM9", "LM8")._blockGroup)
	assert 15 == len(m.getLine("LM8", "LM7")._blockGroup)
	assert 15 == len(m.getLine("LM7", "LM3")._blockGroup)
	assert equalLines(m.getLine("LM9", "LM8")._blockGroup,m.getLine("LM8", "LM7")._blockGroup)
	assert equalLines(m.getLine("LM7", "LM3")._blockGroup,m.getLine("LM8", "LM7")._blockGroup) 
	oneway = ["LM3","LM7","LM8","LM9"]
	oneway2 = oneway[::-1] 
	agv1 = m.getAgv("agv41")
	agv2 = m.getAgv("agv42")
	agv2.setPos("LM1")
	agvCtrl.setPos(agv2.agvId,"LM1")
	 
	assert m.block("agv41", "LM3", "LM7", oneway)
	assert 3 == len(m.getBlockLines())  
	ll = m.getPathSingle("LM3", "LM9","agv41")[1]
	ll = m.getStartLines("LM3",ll) 
	assert equalLines(ll,m.getBlockLines())
	
	assert m.block("agv42", "LM3", "LM7", oneway) #another agv,block share 
	assert 3 == len(m.getBlockLines())
	assert equalLines(ll,m.getBlockLines())
	
	assert m.block("agv41", "LM3", "LM7", oneway) #repeat 
	assert 3 == len(m.getBlockLines())
	assert equalLines(ll,m.getBlockLines())
	for l in m.getBlockLines():
		assert l.blockType == BLOCK_SHARE
		assert l.oposite.blockType == BLOCK_NONE
		assert l.blockAgvId == set(["agv41","agv42"])
	 
	assert not m.block("agv42", "LM7", "LM3", oneway2) #oposite block failed 
	assert not m.block("agv42", "LM9", "LM8", oneway2) #oposite block failed 
	assert not m.block("agv42", "LM8", "LM7", oneway2) #oposite block failed 
	#oneway有两台小车，回来的路不可以占用
	assert not m.block("agv41", "LM8", "LM7", oneway2) #oposite block failed 
	
	#oneway只有一台小车，回来的路可以占用 
	m = mapInfo.load("bell.smap") 
	assert m.block("agv42", "LM3", "LM7", oneway)  
	assert 3 == len(m.getBlockLines())
	assert m.block("agv42", "LM7", "LM3", oneway2)   
	assert 4 == len(m.getBlockLines())
	assert not m.block("agv41", "LM7", "LM3", oneway2)  
	assert not m.block("agv41", "LM3", "LM7", oneway)  
	

def test_updateBlockGroup():
	# 测试特殊线段分组的情况
	m = mapInfo.load("test2.smap")  
	assert 8 == len(m.getLine("LM14", "LM13")._blockGroup)
	assert 7 == len(m.getLine("LM15", "LM13")._blockGroup) 
	assert 8 == len(m.getLine("LM13", "LM15")._blockGroup)
	assert 7 == len(m.getLine("LM15", "LM8")._blockGroup)
	assert 7 == len(m.getLine("LM8", "LM15")._blockGroup)
	assert 7 == len(m.getLine("LM8", "CP7")._blockGroup)
	assert 7 == len(m.getLine("CP7", "LM8")._blockGroup)
 
	assert 7 == len(m.getLine("Y2", "Y4")._blockGroup)
	assert 7 == len(m.getLine("Y4", "Y2")._blockGroup)
	assert 7 == len(m.getLine("Y3", "Y2")._blockGroup)
	assert 7 == len(m.getLine("Y2", "Y3")._blockGroup)
	assert 14 == len(m.getLine("Y1", "Y2")._blockGroup)
	assert 7 == len(m.getLine("Y2", "Y1")._blockGroup)
	assert 7 == len(m.getLine("Y1", "LM18")._blockGroup)
	assert 14 == len(m.getLine("LM18", "Y1")._blockGroup)
	assert 14 == len(m.getLine("LM16", "LM18")._blockGroup) 


def test_normal_block():
	# 正常的block情况
	import agvList
	import mapMgr
	global g_map
	g_map = {}
	mapMgr.g_map = {}
	m = mapMgr.getMap("test2") 
	agv = m.getAgv("agv11")
	agv2 = m.getAgv("agv12")
	agv.setPos("Y1")
	agv2.setPos("Y1")
	m.getAgv("agv13").setPos("Y1")
	assert agv
	assert agv2
	oneway = ["LM11", "LM14", "LM13", "LM15"]

	assert m.block("agv11", "LM11", "LM14", oneway)
	bb = m.getBlockLines() 
	assert len(bb) == 4
	assert bb[0].equal("LM11", "LM14")
#	assert m.block("agv12", "LM11", "LM14", oneway)
#	m.unblock("agv12")
	# 重复block
	assert m.block("agv11", "LM11", "LM14", oneway)
	assert m.block("agv11", "LM11", "LM14", oneway)
	assert m.block("agv11", "LM11", "LM14", oneway)
	m.unblock("agv11")
	assert 0 == len(m.getBlockLines())
	m.unblock("agv11")
	assert 0 == len(m.getBlockLines())
	assert 0 == len(m.getBlockLines())
	assert m.block("agv12", "LM11", "LM14", oneway)
	assert len(bb) == 4
	assert bb[0].equal("LM11", "LM14")
	m.unblock("agv12")
	assert 0 == len(m.getBlockLines())


def testtryblock():
	import mapMgr
	global g_map
	g_map = {}
	mapMgr.g_map = {}
	m = mapMgr.getMap("test2")  
	c = m.getLine("LM14", "LM13")
	c2 = m.getLine("LM13", "LM15")
	c3 = m.getLine("LM15", "LM13")
	pp = [c,c2,c3]
	assert c2.oposite == c3
	assert c3.oposite == c2
	assert c.tryBlock("agv11",pp) == []
	c.block("agv11",pp)
	assert c.blockType == BLOCK_SHARE

	assert c.tryBlock("agv11",pp) == []
	assert c.tryBlock("agv12",pp) == ["agv11",]
	assert c.tryBlock("agv12",pp) == ["agv11",]
	m.unblock("agv11") 
	assert c.tryBlock("agv12",pp) == []
	c.block("agv12",pp)
	assert c.tryBlock("agv11",pp) == ["agv12"]
	assert c.tryBlock("agv11",pp) == ["agv12"]
	assert c2.block("agv13",pp)
	assert c3.isBlocked  # 对向被block 


def testgetStartLines():
	import agvList
	m = mapInfo.load("test2.smap")
	oneway = ["LM9", "LM12", "LM11", "LM14", "LM13", "LM15"]
	lines = m.getStartLines("LM9", oneway)
	assert 5 == len(lines)
	assert lines[0].equal("LM9", "LM12")
	assert lines[1].equal("LM12", "LM11")
	assert lines[2].equal("LM11", "LM14")
	assert lines[3].equal("LM14", "LM13")
	assert lines[4].equal("LM13", "LM15")
	lines = m.getStartLines("LM1", oneway)  # no exist
	assert 0 == len(lines)
	lines = m.getStartLines("LM11", oneway)
	assert 3 == len(lines)
	lines = m.getStartLines("LM15", oneway)
	assert 0 == len(lines)
	lines = m.getStartLines("LM13", oneway)
	assert 1 == len(lines)
	assert lines[0].equal("LM13", "LM15")

	## 测试agv取当前位置
	#agvCtrl.setXY("agv11", -0.88, 0.16, 0)
	#assert m.getAgv("agv11").currentPos.name == "LM15"
	#agvCtrl.setXY("agv11", 9.9, -8.6, 3.14)
	#assert m.getAgv("agv11").currentPos.name == "Y4"
	#agvCtrl.setXY("agv11", 9.9, -100, 3.14)
	#assert m.getAgv("agv11").currentPos is None
 
def testdeadend1():
	m = mapInfo.load("testmap")
	assert m.mapId == "testmap"
	assert m.getLine("LM11", "LM10").isDeadend
	assert m.getLine("LM11", "LM10").isOneway
	assert m.getLine("LM13", "LM1").isDeadend
	assert m.getLine("LM13", "LM1").isOneway
	assert m.getLine("LM1", "LM13").isDeadend
	assert m.getLine("LM1", "LM13").isOneway

	assert m.getLine("LM1", "LM8").isOneway 
	assert ["LM11", "LM10"] == m.shortPath("LM11", "LM10")[1]
	assert None == m.shortPath("LM10", "LM11")[0]
	assert m.shortPath("LM5", "LM7")[1] == ["LM5", "LM6", "LM7"]
	m = mapInfo.load("test2.smap")
	assert m.mapId == "test2"
	agvCtrl.setXY("agv1", 10, 5, 0) 
	assert ["LM8", "CP7"] == m.shortPath("LM8", "CP7")[1]
	assert not m.getLine("LM18", "Y1").isDeadend
	assert m.getLine("LM18", "Y1").isOneway
	assert not m.getLine("LM9", "LM10").isDeadend
	assert m.getLine("LM9", "LM10").isOneway
	assert not m.getLine("LM12", "LM11").isDeadend
	assert not m.getLine("LM12", "LM11").isOneway


def testconnctList():
	m = mapInfo.load("testmap.smap")
	assert m.mapId == "testmap"
	assert m.getPos("LM10").nextLines == []
	assert m.getPos("LM10").preLines == [m.getLine("LM11", "LM10")]
	assert m.getPos("LM11").nextLines == [m.getLine("LM11", "LM10")]
	assert m.getPos("LM11").preLines == []
	n = m.getPos("LM1").nextLines
	p = m.getPos("LM1").preLines
	assert 3 == len(n)
	assert m.getLine("LM1", "LM2") in n
	assert m.getLine("LM1", "LM13") in n
	assert m.getLine("LM1", "LM8") in n
	assert 3 == len(p)
	assert m.getLine("LM2", "LM1") in p
	assert m.getLine("LM9", "LM1") in p
	assert m.getLine("LM13", "LM1") in p


def testwebInfo():
	m = mapInfo.load("test2.smap")
	ret = m.shortPath("LM13", "LM18")
	assert ret[1] == ['LM13', 'LM12', 'LM11', 'LM14', 'LM4', 'LM16', 'LM18']

	m = mapInfo.load("testmap.smap")
	w = m.webInfo()
	#f = open("webMapInfo.txt","r+t")
	#f.write(json.dump(w))
	#f.close()
	f = open("webMapInfo.txt", "r+t")
	ss = f.read()
	f.close()
	assert ss == json.dump(w)
	l = m.getLine("LM5", "LM6")
	assert l.contains(16, 5.7)
	assert not l.contains(10.5, 8.17)
	assert m.getPos("LM13").contains(-1.07, 6.4)
	assert m.getPos("CP12").contains(2.11, 5.0)
	assert m.getPosByPoint(-1.07, 6.4).name == "LM13"
	assert m.getPosByPoint(2.11, 5.0).name == "CP12"
	assert m.getPosByPoint(-3, 1) is None
 

def testgetMapList():
	ll = getMapList() 
	assert {"id": "testmap", "name": "20170908b"} in ll


def testdecodeProperty():
	sss = """[{
			"key": "direction",
			"type": "int",
			"value": "MA==",
			"int32Value": 0
		}, 
		{
			"key": "maxacc",
			"type": "double",
			"value": "MC4z",
			"doubleValue": 0.3
		},
		{
			"key": "maxrotacc",
			"type": "double",
			"value": "MC43ODU0",
			"doubleValue": 0.7854
		},
		{
			"key": "reachangle",
			"type": "double",
			"value": "MC4wMDg3Mw==",
			"doubleValue": 0.00873
		}]"""
	ll = json.load(sss)
	rr = mapInfo._decodeProperty(ll)
	assert 4 == len(rr)
	assert rr["direction"] == 0
	assert rr["maxacc"] == 0.3
	assert rr["maxrotacc"] == 0.7854
	assert rr["reachangle"] == 0.00873

 

def testload():
	m = mapInfo.load("testmap")
	assert len(m.points) == 8797
	assert len(m.curves) == 19 
	assert len(m.positions) == 15
	assert m.header.mapName == '20170908b'
	assert m.header.minPoint.x == -5.132
	assert m.header.minPoint.y == -0.158
	assert m.header.maxPoint.x == 18.256
	assert m.header.maxPoint.y == 10.86
	assert m.points[0].x == -0.006
	assert m.points[0].y == 8.199
	assert m.points[1].x == -0.006
	assert m.points[1].y == 8.219
	assert m.points[len(m.points) - 1].x == 9.994
	assert m.points[len(m.points) - 1].y == 9.559
	assert m.getPos("LM1").x == 7.116
	assert m.getPos("LM1").y == 6.428
 


def test_getMapRawData():
	data = getMapRawData("8-222")
	assert data

def te2stbell():
	m = mapInfo.load("bell.smap") 
	agv = m.getAgv("agv41")
	agv2 = m.getAgv("agv42") 
	m.show()

	agv.setPos("LM5")
	agv.nextTargetPosName = "LM12" 
	agv2.setPos("LM6")
	agv2.nextTargetPosName = "LM12" 
	
	#agv.setTargetList(["LM3","LM7","LM8","LM9","LM10","LM11","LM12"])
	ret = m.block(agv.agvId, "LM3", "LM7", ["LM3","LM7","LM8","LM9","LM10","LM11","LM12"])  
	assert ret
	ret = m.getLine("LM3","LM7").tryBlock("agv42")
	print("==========",ret)
	assert 0
	assert m.block(agv2.agvId, "LM6", "LM7", ["LM6","LM3","LM7","LM8","LM9","LM10","LM11","LM12"])  
	#agv2.setTargetList(["LM6","LM3","LM7","LM8","LM9","LM10","LM11","LM12"])
	m.show()
	m.block(agv1.agvId, "LM13", "LM1", ["LM13", "LM1"])  
	assert agv2.check(agv3) 
	assert agv1.check(agv3)   
	assert not agv2.check(agv1) 
	assert not agv1.check(agv2) 
	assert not agv1.check(agv2)
	assert not m.check(agv1.agvId)
	#assert m.check(agv2.agvId)
	
def test408block():  
	import mapMgr,agvCtrl 
	m = mapMgr.getMap("408") 
	agv = m.getAgv("agv51")
	assert 2 == len(m.getChargePosList())
	assert "CP13" in m.getChargePosList()
	assert "CP9" in m.getChargePosList()
	agv.setPos("LM19") 
	assert m.block(agv.agvId,"LM19","LM22",["LM19","LM20","LM21","LM22"]) 

	assert 5 == len(m.getBlockLines())
	assert m.getLine("LM19", "LM20").isBlocked
	assert m.getLine("LM20", "LM19").isBlocked
	assert m.getLine("LM20", "LM21").isBlocked
	assert m.getLine("LM21", "LM20").isBlocked
	assert m.getLine("LM21", "LM22").isBlocked
	agv.setPos("LM23") 
	m.unblock(agv.agvId)
	assert 0 == len(m.getBlockLines())
	 
	agv.setPos("LM19") 
	assert m.block(agv.agvId,"LM19","LM20",["LM19","LM20"])  
	assert 2 == len(m.getBlockLines())
	assert m.getLine("LM19", "LM20").isBlocked 
	assert m.getLine("LM20", "LM19").isBlocked 
	m.unblock("agv51")  
	 
	assert 0 == len(m.getBlockLines())
	assert not m.getLine("LM19", "LM20").isBlocked 
	agv.setPos("LM23") 
	m.unblock("agv51")
	assert 0 == len(m.getBlockLines()) 

def testissamemap():
	assert isSameMap("505.LM1","505.LM2")
	assert isSameMap("LM1","LM2")
	assert not isSameMap("505.LM1","LM2")
	assert not isSameMap("505.LM1","45.LM2")
	assert formatLoc("222","43.LM2") == "43.LM2"
	assert formatLoc("222","LM2") == "222.LM2"
	
	m = getMap("testscada")  
	m1 = getMap("408")  
	assert [("408",['CP13', 'LM14', 'LM17', 'LM15', 'LM24', 'LM23', 'LM22'])] == m1.getPath("408.CP13","408.LM22") 
	assert [('testscada', ['LM1', 'LM25', 'LM35']), ('408', ['AP3'])] == m1.getPath("testscada.LM1","408.AP3")
	assert [('testscada', ['LM1', 'LM25', 'LM35']), ('408', ['AP3', 'LM2', 'LM1', 'AP7', 'LM15', 'LM17'])] ==  m1.getPath("testscada.LM1","408.LM17")
	assert [('408', ['AP6', 'LM4', 'LM5', 'AP8', 'LM12', 'LM10']), ('testscada', ['LM32', 'LM27', 'LM4', 'LM5'])] == m1.getPath("408.AP6","testscada.LM5")
	
	w,p = m1.shortPath("testscada.LM4","408.CP9")
	assert ['testscada.LM4', 'testscada.LM27', 'testscada.LM14', 'testscada.LM24', 'testscada.LM25', 'testscada.LM35', '408.AP3', '408.LM2', '408.LM1', '408.AP7', '408.LM15', '408.LM24', '408.LM23', '408.LM12', '408.LM10', '408.LM11', '408.CP9'] == p

def testloadmap2(): 
	m = mapInfo.load("test430")   

	ret = m.shortPath("LM31", "AP7") 
	assert ret[1] == ['LM31', 'LM1', 'LM29', 'LM28', 'LM26', 'LM23', 'AP7']

	m = mapInfo.load("big2") 
	func = m.getPath 
	import counter
	c = counter.counter() 
	ret = m.getPath("LM129","LM734")  
	c.check() 
	assert ret[0][1] == ['LM129', 'LM229', 'LM234', 'LM233', 'LM232', 'LM231', 'LM230', 'LM296', 'LM126', 'LM16', 'LM63', 'LM727', 'LM728', 'LM903', 'LM901', 'LM722', 'LM721', 'LM62', 'LM94', 'LM15', 'LM895', 'LM887', 'LM897', 'LM885', 'LM891', 'LM861', 'LM198', 'LM197', 'LM196', 'LM195', 'LM190', 'LM189', 'LM186', 'LM5', 'LM60', 'LM59', 'LM842', 'LM841', 'LM840', 'LM692', 'LM691', 'LM45', 'LM103', 'LM39', 'LM38', 'LM145', 'LM826', 'LM825', 'LM146', 'LM147', 'LM148', 'LM735', 'LM731', 'LM734']

	
	##### test block   测试block group有断开的情况
	c3 = m.getLine("LM296","LM126")
	paths =  ['LM129', 'LM298', 'LM783', 'LM296', 'LM126', 'LM16', 'LM63', 'LM727', 'LM728', 'LM722', 'LM721', 'LM62', 'LM94', 'LM15', 'LM14', 'LM198', 'LM197', 'LM196', 'LM195', 'LM190', 'LM189', 'LM186', 'LM5', 'LM60', 'LM59', 'LM58', 'LM7', 'LM840', 'LM692', 'LM691', 'LM45', 'LM103', 'LM39', 'LM38', 'LM145', 'LM826', 'LM825', 'LM146', 'LM147', 'LM148', 'LM735', 'LM731', 'LM734']
	paths = m.getStartLines('LM129', paths)
	cc = c3._getBlockPath(paths)
	assert ['LM296->LM126', 'LM126->LM16', 'LM16->LM63', 'LM63->LM727', 'LM727->LM728', 'LM728->LM722', 'LM722->LM721', 'LM721->LM62', 'LM62->LM94'] == [str(c) for c in cc]
	 
	######
	
	pp = func("LM692","LM840")	#第一次要1秒多，不知道为啥 
	c.check()
	assert func("LM692","LM840")[0][1] == ["LM692","LM840"]
	assert func("LM14","LM15")[0][1] == ["LM14","LM15"]  
	assert func("LM181","LM180")[0][1] == ["LM181","LM180"]  
	assert func("LM692","LM690")[0][1] == ["LM692","LM690"]  
	assert func("LM690","LM180") == [('big', ['LM690', 'LM692', 'LM12', 'LM184', 'LM181', 'LM180'])]
	assert func("LM12","LM184")[0][1] == ["LM12","LM184"]  
	assert func("LM308","LM96")[0][1] == ["LM308","LM96"]  
	assert func("LM96","LM52")[0][1] == ["LM96","LM52"]    
	assert c.check() < 500 
 
	p1 = m.shortPath("LM734","LM285") 
	c.check()
	 

#测试顺路算法
def testdijkstra2():
	import driver.seerAgv.mockAgvCtrl as agvCtrl 
	import agvList
	global g_agvs
	g_agvs = None
	agvCtrl.disableBattery()
	local.set("project","agvcfg","testagv4.cfg")
	file = local.get("project","agvcfg")
	
	agvList.g_agvList = None
	agvList.getAgv("AGV01").createMock("big","AP61")
	agvList.getAgv("AGV02").createMock("big","LM124")
	agvList.getAgv("AGV03").createMock("big","AP864")
	agvList.getAgv("AGV04").createMock("big","LM889")
	
	m = getMap("big")
	paths = m.getPath("AP185", "AP753",agvId = "AGV01") 
	assert paths == [('big', ['AP185', 'LM186', 'LM189', 'LM190', 'LM195', 'LM196', 'LM197', 'LM198', 'LM861', 'LM891', 'LM885', 'LM897', 'LM887', 'LM895', 'LM15', 'LM94', 'LM62', 'LM721', 'LM722', 'LM901', 'LM930', 'LM932', 'LM903', 'LM728', 'LM727', 'LM63', 'LM16', 'LM921', 'LM126', 'LM110', 'LM900', 'LM111', 'LM309', 'LM256', 'LM299', 'LM288', 'LM289', 'LM275', 'LM276', 'LM751', 'LM295', 'LM744', 'LM745', 'LM746', 'LM752', 'AP753'])]
	getAgv("AGV01").agvInfo.mapId = "big"
	getAgv("AGV02").agvInfo.mapId = "big"
	getAgv("AGV03").agvInfo.mapId = "big"
	getAgv("AGV04").agvInfo.mapId = "big"
	getAgv("AGV01").setTargetList(paths[0][1])
	ll = getAgv("AGV01").getTargetLines(m)
	assert strPaths(ll) == "AP185->LM186,LM186->LM189,LM189->LM190,LM190->LM195,LM195->LM196,LM196->LM197,LM197->LM198,LM198->LM861,LM861->LM891,LM891->LM885,LM885->LM897,LM897->LM887,LM887->LM895,LM895->LM15,LM15->LM94,LM94->LM62,LM62->LM721,LM721->LM722,LM722->LM901,LM901->LM930,LM930->LM932,LM932->LM903,LM903->LM728,LM728->LM727,LM727->LM63,LM63->LM16,LM16->LM921,LM921->LM126,LM126->LM110,LM110->LM900,LM900->LM111,LM111->LM309,LM309->LM256,LM256->LM299,LM299->LM288,LM288->LM289,LM289->LM275,LM275->LM276,LM276->LM751,LM751->LM295,LM295->LM744,LM744->LM745,LM745->LM746,LM746->LM752,LM752->AP753" 
	lines,oplines = m.getAgvPath("AGV01") 
	assert lines == []
	lines,oplines = m.getAgvPath("AGV02") 
	assert strPaths(ll) == strPaths(lines)
	assert utility.assert_array_noorder(oplines , ['LM186->AP185', 'LM189->LM186', 'LM190->LM189', 'LM195->LM190', 'LM196->LM195', 'LM197->LM196', 'LM198->LM197', 'LM861->LM198', 'LM891->LM861', 'LM885->LM891', 'LM897->LM885', 'LM887->LM897', 'LM895->LM887', 'LM15->LM895', 'LM94->LM15', 'LM62->LM94', 'LM721->LM62', 'LM722->LM721', 'LM901->LM722', 'LM930->LM901', 'LM932->LM930', 'LM903->LM932', 'LM728->LM903', 'LM727->LM728', 'LM63->LM727', 'LM16->LM63', 'LM921->LM16', 'LM126->LM921', 'LM110->LM126', 'LM900->LM110', 'LM111->LM900', 'LM309->LM111', 'LM256->LM309', 'LM299->LM256', 'LM288->LM299', 'LM289->LM288', 'LM275->LM289', 'LM276->LM275', 'LM751->LM276', 'LM295->LM751', 'LM744->LM295', 'LM745->LM744', 'LM746->LM745', 'LM752->LM746', 'AP753->LM752'])
	w,pp = m.dijkstra("AP753", "AP185",lines=lines,oplines=oplines)
	paths2 = m.getPath("AP753", "AP185",agvId = "AGV02") 
	assert paths2[0][1] == pp
	getAgv("AGV02").setTargetList(pp)
	ss = strPaths(pp)
	assert ss == "AP753,LM752,LM746,LM745,LM744,LM295,LM751,LM276,LM275,LM289,LM288,LM299,LM256,LM309,LM111,LM900,LM110,LM126,LM921,LM16,LM904,LM892,LM890,LM933,LM931,LM902,LM889,LM934,LM899,LM888,LM896,LM886,LM898,LM884,LM14,LM891,LM894,LM848,LM847,LM846,LM845,LM186,AP185"
	#应该要选另一条路 
	assert ss.find("LM903,LM901,LM722,LM721,LM62,LM94,LM15") == -1 
	
	#agv03和agv01走一样的路  
	paths3 = m.getPath("AP185", "AP753",agvId = "AGV03") 
	getAgv("AGV03").setTargetList(paths3[0][1])
	assert paths == paths3
	
	paths4 = m.getPath("AP753", "AP185",agvId = "AGV04") 
	assert paths2 == paths4
	
#测试顺路算法
def testdijkstra3():
	import driver.seerAgv.mockAgvCtrl as agvCtrl 
	import agvList,counter
	global g_agvs
	g_agvs = None
	agvCtrl.disableBattery()
	local.set("project","agvcfg","testagv4.cfg")  
	agvList.g_agvList = None
	agvList.getAgv("AGV01").createMock("big","AP61")
	agvList.getAgv("AGV02").createMock("big","LM94") 
	agvList.getAgv("AGV03").createMock("big","AP864")
	agvList.getAgv("AGV04").createMock("big","LM889")
	getAgv("AGV01").agvInfo.mapId = "big"
	getAgv("AGV02").agvInfo.mapId = "big"
	getAgv("AGV03").agvInfo.mapId = "big"
	getAgv("AGV04").agvInfo.mapId = "big"
	agvList.getAgv("AGV02")._curTarget = "LM94"#挡路了
	
	m = getMap("big")
	lines,oplines = m.getAgvPath("AGV01") 
	assert not lines
	assert not oplines
	#挡路的，没计算到oplines里
	#assert utility.assert_array_noorder(oplines , ['LM94->LM15', 'LM94->LM899', 'LM94->LM62', 'LM62->LM94', 'LM15->LM94', 'LM899->LM94', 'AP864->LM722', 'LM722->AP864', 'LM889->LM902', 'LM889->LM934', 'LM902->LM889', 'LM934->LM889', 'AP264->LM265', 'LM265->AP264', 'AP262->LM263', 'LM263->AP262', 'AP287->LM289', 'LM289->AP287', 'AP286->LM288', 'LM288->AP286'])
	paths = m.getPath("LM887", "LM930",agvId = "AGV01")
	assert paths == [('big', ['LM887', 'LM895', 'LM15', 'LM94', 'LM62', 'LM721', 'LM722', 'LM901', 'LM930'])]
	
	c = counter.counter()
	paths = m.getPath("LM15", "AP286",agvId = "AGV01") 
	pp = paths[0][1]
	pp = m.getStartLines(pp[0],pp)
	c.check()
	ww = sum([l.length for l in pp])
	lines,oplines = m.getAgvPath("AGV01")  
	m._getPaths("LM15", "AP286",stopCount=30,maxWeight=10000,lines=lines,oplines=oplines) 
	c.check() #2373 ms
	
	m.getAllPaths("LM230", "LM134",stopCount=30,maxWeight=10000) 
	c.check() #2373 ms
 

def testupdateNoTurnPath():
	import agvList
	m = mapInfo.load("akmsmt")
	m.getPos("LM5").turnable = False
	lines=[]
	oplines = []
	w,pp = m.dijkstra("LM2", "LM3",lines=lines,oplines=oplines)
	assert pp == ['LM2', 'LM102', 'LM103', 'LM3']
	lines = [str(x) for x in m.getStartLines(pp[0],pp)]
	oplines = [str(x.oposite) for x in m.getStartLines(pp[0],pp)]
	
	w,pp = m.dijkstra("LM2", "LM3",lines=lines,oplines=oplines)
	assert pp == ['LM2', 'LM102', 'LM103', 'LM3']
	w,pp = m.dijkstra("LM3", "LM2",lines=lines,oplines=oplines)
	import time
	#time.sleep(10)
	#TODO: 用getPath还未测试成功，因为getPath的agv.r不对 
	nn,_ = m.updateNoTurnPath(pp,m.getLine("LM3","LM5").r)
	assert nn == ['LM3','LM5','LM8']
	agv = agvList.getAgv("agv1").createMock("akmsmt","LM2")
	getAgv("agv1").agvInfo.mapId = "akmsmt"
	pp = m.getPath("LM2","LM3","agv1")
	assert [('akmsmt', ['LM2', 'LM102', 'LM103', 'LM3'])] == pp
	
	agv.setPoint(0,0,m.getLine("LM3","LM5").r)
	pp = m.getPath("LM2","LM3","agv1")
	print(pp)
	assert 0
	
	path = ["LM102","LM2","LM13","LM101"]
	path2,_ = m.updateNoTurnPath(path[:],0)
	assert ['LM102', 'LM103'] == path2 
	assert m.updateNoTurnPath(path[:],math.pi) == ([],0)	#不用旋转 
	assert m.updateNoTurnPath(['LM102', 'LM103', 'LM3', 'LM5'],math.pi)[0] == ['LM102', 'LM2']
	assert m.updateNoTurnPath(["LM102","LM103"],0) == ([],0)
		
def test_getNoBlockPaths():
	m = mapInfo.load("408")
	lines=[]
	oplines = []
	w,pp = m.dijkstra("LM21", "LM5",lines=lines,oplines=oplines)
	assert pp == ['LM21', 'LM22', 'LM23', 'LM12', 'AP8', 'LM5']
	oplines = [str(x.oposite) for x in m.getStartLines(pp[0],pp)]
	
	aa = m._getNoBlockPaths("AGV01","AP8","LM21",oplines=oplines)
	assert aa[0] == ['AP8', 'LM5', 'LM4']
	
	aa = m._getNoBlockPaths("AGV01","LM23",'LM21',oplines=oplines)
	assert aa[0] == ['LM23', 'LM12', 'AP8', 'LM5', 'LM4']
	
	aa = m._getNoBlockPaths("AGV01","LM24",'LM21',oplines=oplines)
	assert aa == ([],0)
	
	aa = m._getNoBlockPaths("AGV01","LM22",'LM21',oplines=oplines)
	assert aa[0] == ['LM22', 'LM23', 'LM12', 'AP8', 'LM5', 'LM4']
	
	m = mapInfo.load("shuqin")
	lines=[]
	oplines = []
	w,pp = m.dijkstra("LM5", "LM3",lines=lines,oplines=oplines)
	assert pp == ['LM5', 'LM4', 'LM3']
	oplines = [str(x.oposite) for x in m.getStartLines(pp[0],pp)]
	assert ['LM4', 'LM3', 'LM2'] == m._getNoBlockPaths("AGV01","LM4",'LM21',oplines=oplines)[0]
	assert ['LM5','LM6'] == m._getNoBlockPaths("AGV01","LM5",'LM21',oplines=oplines)[0]
	
	m = mapInfo.load("big")
	w,pp = m.dijkstra("AP270", "LM100",lines=lines,oplines=oplines)
	oplines = [str(x.oposite) for x in m.getStartLines(pp[0],pp)]
	pp2 = m._getNoBlockPaths("AGV01","LM299",'AP272',oplines=oplines)
	assert (['LM299', 'LM256', 'AP255'], 1.8769999999999991) == pp2
	 

def testupdateNoBlockPath():
	import agvList,mapMgr,agvControl
	m = mapMgr.getMap("408")
	agvList.g_agvList = None
	local.set("project","agvcfg","agv.cfg")  
	agvList.g_agvList = None
	agvList.getAgv("agv51").createMock("408","LM24")
	agvList.getAgv("agv52").createMock("408","LM23") 
	mapMgr.getAgv("agv51").agvInfo.mapId = "408"
	mapMgr.getAgv("agv52").agvInfo.mapId = "408"
	rr = m.dijkstra("LM24", "LM24",lines=None,oplines=None)
	pp = m.getPath("LM15", "LM18",agvId = "agv51")
	m.getAgv("agv51").setTargetList(pp[0][1])
	pp = m.getPath("LM23", "LM14",agvId = "agv52")		
	assert pp == [('408', ['LM23', 'LM12'], 26.174), ('408', ['LM12', 'LM23', 'LM24', 'LM15', 'LM17', 'LM14'], 0.9580000000000001)] 
	pp = m.getPath("LM21", "LM14",agvId = "agv52")
	assert pp == [('408', ['LM21', 'LM20'], 46.209), ('408', ['LM20', 'LM21', 'LM22', 'LM23', 'LM24', 'LM15', 'LM17', 'LM14'], 1.085)]
	pp = m.getPath("LM24", "LM14",agvId = "agv52")
	assert pp ==[('408', ['LM24', 'LM23', 'LM12'], 11.318000000000001), ('408', ['LM12', 'LM23', 'LM24', 'LM15', 'LM17', 'LM14'], 5.91)]
	
	m = mapMgr.getMap("big")
	agvList.g_agvList = None
	mapMgr.g_agvs= None
	agvList.getAgv("agv51").createMock("big","LM930")
	agvList.getAgv("agv52").createMock("big","LM931") 
	agvList.getAgv("agv53").createMock("big","LM932")
	agvList.getAgv("agv51").mapId = "big"
	agvList.getAgv("agv52").mapId = "big"
	agvList.getAgv("agv53").mapId = "big"
	agvList.getAgv("agv51").pause()
	agvList.getAgv("agv52").pause()
	agvList.getAgv("agv53").pause()
	
	pp = m.getPath("LM930", "AP264",agvId = "agv51")
	agvControl.lock("agv51","1","ycat")
	agvControl.move("agv51", "AP264", taskId="1", timeout=1000)
	pp = m.getPath("LM932", "AP864",agvId = "agv52")
	
	assert pp == [('big', ['LM932', 'LM933', 'LM931', 'LM930', 'LM901', 'LM722', 'AP864'], 11.751999999999997)]
	pp = m.getPath("LM921", "AP864",agvId = "agv52")
	
	assert pp == [('big', ['LM921', 'LM126', 'LM920'], 51.28194042186678), ('big', ['LM920', 'LM126', 'LM921', 'LM16', 'LM904', 'LM892', 'LM890', 'LM933', 'LM931', 'LM930', 'LM901', 'LM722', 'AP864'], 9.367304340355384)]
	pp = m.getPath("LM309", "AP864",agvId = "agv52")
	assert pp == [('big', ['LM309', 'LM256', 'AP255'], 155.55849241157628), ('big', ['AP255', 'LM256', 'LM309', 'LM111', 'LM900', 'LM110', 'LM126', 'LM921', 'LM16', 'LM904', 'LM892', 'LM890', 'LM933', 'LM931', 'LM930', 'LM901', 'LM722', 'AP864'], 6.433999999999999)]
	agvControl.lock("agv53","1","ycat")
	agvControl.lock("agv52","1","ycat")
	agvCtrl.setPos("agv52","LM309")
	time.sleep(1)
	agvControl.move("agv52", "AP864", taskId="2", timeout=1000)
	assert mapMgr.getAgv("agv52").targetPosName == "AP864"
	assert [strPaths(p) for p in mapMgr.getAgv("agv52").getTargetLines(m)] == ['LM309->LM256,LM256->AP255', 'AP255->LM256,LM256->LM309,LM309->LM111,LM111->LM900,LM900->LM110,LM110->LM126,LM126->LM921,LM921->LM16,LM16->LM904,LM904->LM892,LM892->LM890,LM890->LM933,LM933->LM931,LM931->LM930,LM930->LM901,LM901->LM722,LM722->AP864']
	agvCtrl.setPos("agv53","LM111")
	mapMgr.getAgv("agv53").selected = True
	time.sleep(1)
	agvControl.move("agv53", "LM921", taskId="3", timeout=1000)
	assert ['LM111', 'LM740', 'LM740', 'LM111', 'LM900', 'LM110', 'LM126', 'LM921'] == mapMgr.getAgv("agv53").getTargetListAll()
	
	agvCtrl.setPos("agv53","LM288")
	time.sleep(1)
	agvControl.move("agv53", "LM921", taskId="3", timeout=1000)
	assert m.getPath("LM288", "LM921",agvId = "agv53") == [('big', ['LM288', 'LM289', 'LM275', 'LM276', 'LM267'], 133.19085633006492), ('big', ['LM267', 'LM276', 'LM275', 'LM289', 'LM288', 'LM299', 'LM256', 'LM309', 'LM111', 'LM900', 'LM110', 'LM126', 'LM921'], 5.521)]
	
	agvCtrl.setPos("agv53","AP264")
	agvList.agvCtrl.jackUp("agv53")
	agvList.getAgv("agv53").hasShelve= True
	time.sleep(1)
	pp = m.getPath("AP264", "LM276",agvId = "agv53") 
	assert pp == [('big', ['AP264', 'LM265', 'LM263', 'LM295', 'LM744'], 39.83960374025037), ('big', ['LM744', 'LM295', 'LM751', 'LM276'], 12.879000000000001)]
	agvList.agvCtrl.jackDown("agv53")
	agvList.getAgv("agv53").hasShelve= False
	time.sleep(1)
	agvControl.move("agv53", "LM276", taskId="4", timeout=1000)
	pp = m.getPath("AP264", "LM276",agvId = "agv53") 
	assert pp == [('big', ['AP264', 'LM265', 'LM263', 'AP262'], 36.228603740250364), ('big', ['AP262', 'LM263', 'LM295', 'LM751', 'LM276'], 9.268)]
	assert [('big', ['AP264', 'LM265', 'LM263'], 11.28799999999999)] == m.getPath("AP264", "LM263",agvId = "agv53")
	
	agvCtrl.setPos("agv52","AP809")
	agvCtrl.setPos("agv53","AP758")
	agvControl.move("agv52", "AP758", taskId="4", timeout=1000)
	agvControl.move("agv53", "AP809", taskId="4", timeout=1000)
	pp = m.getPath("AP758", "AP809",agvId = "agv53") 
	assert [('big', ['AP758', 'LM760', 'LM779', 'LM778', 'LM777', 'LM774', 'LM773', 'LM145', 'LM762', 'LM800', 'LM802', 'LM803', 'LM804', 'LM805', 'AP809'], 61.59813545402645)] == pp
	
	
if __name__ == "__main__":   
	#assert 0
	#getMap("big").show()
#	testdijkstra3()
#	testdijkstra2()
#	test_getNoBlockPaths() 
	getMap("fp-neiwei").show()
	testupdateNoBlockPath()
	assert 0
	
	import time
	import agvList  
	utility.start()    
	 
	g_agvs = {}
	while True:
		#等待所有agv上线 
		aa = agvList.getAgvList()
		for a in aa:
			if aa[a].status is None:
				time.sleep(0.5) 
				break
		else:
			time.sleep(0.5)
			break     
	time.sleep(1)   
	utility.run_tests() 
	
