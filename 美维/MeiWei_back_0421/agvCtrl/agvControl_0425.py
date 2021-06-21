# -*- coding: UTF-8 -*-
import os, sys
import time
import uuid
import datetime
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import mqtt  
import agvList 
import agvTask as task
import mytimer
#import querySet
import mapMgr
import log
import utility
import random
import mongodb as db
import threading
import local
import taskList
import lock as lockImp
import elevatorMgr 
import counter
import math
import enhance
from utils import toolsUtil

#g_dataCountQS = querySet.querySet(os.path.dirname(os.path.realpath(__file__)) + '/dbscript.xml')
#g_dataCountQS.setup()
NEAR_DISTANCE = 1
NEAR_LINE_DISTANCE = 10		#直线情况下的连续发送路距离 

projectName = local.get("project","name")
g_startCharge = local.getbool("charge","startCharge",True)

def startCharge():
	global g_startCharge
	g_startCharge = True

# @mytimer.interval(30000)
# def recordAgvInfo():
	# if not db.isConnect():
		# return
	# agv = agvList.g_agvList
	# if not agv:
		# return
	# for agvId in agv.keys():
		# info = agv[agvId].status
		# if info is None:
			# continue
		# ret = {
			# "agvId": agvId,
			# "battery": float("%.2f"%(info["battery_level"]*100)) if "battery_level" in info else None,
			# "confidence": info["confidence"]*100,
			# "time": utility.now()
		# }
		# db.insert("r_agv_info",ret)
	
#TODO
# @mytimer.interval(60000)
# def updatedb():
	# if not db.isConnect():
		# return
	# t = utility.now()
	# db.delete_many("r_agv_info",{"time": {"$lt": (datetime.datetime(t.year,t.month,t.day,0,0,0) - datetime.timedelta(days=30))}})

	
def getMap(mapId):
	return mapMgr.getMap(mapId) 

def onBatteryChanged(agvId, level, isCharge):
	if not agvList.hasAgv(agvId):
		return
	mapId = agvList.getAgv(agvId).mapId 
	if not mapId:
		return
	mqtt.send("agv/" + mapId + "/battery", {'agvId': agvId, 'level': level, 'isCharge': isCharge})

def onLocationChanged(agvId, x, y, angle): 
	if not agvList.hasAgv(agvId):
		return
	mapId = agvList.getAgv(agvId).mapId 
	if not mapId:
		return
	mqtt.send("agv/" + mapId + "/location", {'agvId': agvId, 'x': x, 'y': y, "angle": angle})

def onTargetChanged(agvId,pos):
	if not agvList.hasAgv(agvId):
		return
	mapId = agvList.getAgv(agvId).mapId 
	if not mapId:
		return
	mqtt.send("agv/" + mapId + "/pos", {'agvId': agvId, 'pos': pos})

agvList.batteryEvent.connect(onBatteryChanged)
agvList.locationEvent.connect(onLocationChanged)
agvList.targetLocEvent.connect(onTargetChanged)

#解析 00:00:00-00:10:00,00:00:00-00:10:00 
def getChargeFixTime(fixTime):
	global g_charge_policy 
	fixTime = fixTime.strip('"\'')
	ret = []
	tt = fixTime.split(",")
	for t in tt:
		n = t.split("-")
		if len(n) != 2:
			continue 
		t1,t2 = n[0].strip(),n[1].strip()
		ret.append((datetime.datetime.strptime(t1,'%H:%M:%S').time(),datetime.datetime.strptime(t2,'%H:%M:%S').time()))
	s = "" 
	if ret:
		for t in ret:
			s += str(t[0])+" - " +str(t[1]) + "; " 
	log.info("charge policy",g_charge_policy,", fix time",s)
	return ret
		
g_charge_policy = local.getint("charge","charge_policy",0)
g_charge_fix_times = getChargeFixTime(local.get("charge","fix_time",""))
g_charge_unlock_time = local.getint("charge","unlock_charge_sec",0)
g_charge_unlock_level = local.getfloat("charge","unlock_charge_level",0)


def getAvalidChargePoint(mapId,curPos,excludePos,agvId):
	#充电只支持本层充电 
	cpList = mapMgr.getMap(mapId).getChargePosList() 
	agvs = agvList.getAgvList()
	#desc = ""
	for a in agvs:
		agv = agvs[a]
		if agv.mapId != mapId:
			continue
		if not agv.isChargeTask:
			continue
		if agv.agvId == agvId:
			continue
		if agv.targetPosName in cpList:
			cpList.remove(agv.targetPosName)
		if agv.curTarget in cpList:
			cpList.remove(agv.curTarget)
			
	if len(cpList) == 0: 
		return None
	cp = None
	minWeight = sys.maxsize
	for p in cpList:
		if p in excludePos:
			continue
		w = mapMgr.getMap(mapId).getPathWeight(curPos,p,agvId=agvId)
		if w and w < minWeight:
			minWeight = min(w,minWeight)
			cp = p
	return cp
	
	
def checkStartCharge(agv):  
	if agv.isChargeTask:
		return False
	if g_charge_policy == 0 or g_charge_policy == 1:
		if agv.batteryLevel <= agv.start_charge_level:
			log.warning(agv.agvId, "low battery charge,batteryLevel=", agv.batteryLevel,"start charge level=",agv.start_charge_level)
			return True
	if g_charge_policy == 0 or g_charge_policy == 2:
		now = utility.now().time()
		for t in g_charge_fix_times:
			if t[0] < now and now <= t[1] and agv.batteryLevel <= agv.full_charge_level:
				log.warning(agv.agvId, "fix time charge, batteryLevel=",agv.batteryLevel,",time from",t[0],"to",t[1])
				return True
		if g_charge_unlock_time != 0:
			t = int(agv.unlockSeconds)
			# log.info("unlock time charge:",t," g_charge_unlock_time",g_charge_unlock_time)
			# log.info("batteryLevele:", agv.batteryLevel, " g_charge_unlock_level", g_charge_unlock_level)
			if t > g_charge_unlock_time and agv.batteryLevel < g_charge_unlock_level:
				log.warning(agv.agvId, "unlock time charge, batteryLevel=", agv.batteryLevel, ",charge_unlock_level", g_charge_unlock_level, ",charge_unlock_time",
							g_charge_unlock_time)
				log.info("batteryLevele:",agv.batteryLevel, " g_charge_unlock_level", g_charge_unlock_level)
				return True
	return False
	
	
def checkFinishCharge(agv): 
	if not agv.isCharge:
		return False
	if agv.batteryLevel >= agv.full_charge_level:
		return True
	return False 

@mytimer.interval(10000)
def onCheckCharge(): 
	try:
		mapMgr.checkDoorClose()	
	except Exception as e:
		log.exception("checkDoorClose",e)
			
	if not g_startCharge:
		log.info("startCharge is false")
		return
	agvs = agvList.g_agvList
	if not agvs:
		log.info("check charge no agv")
		return 
	cpList = []
	for a in agvs:
		try:
			agv = agvs[a]
			if agv.isChargeTask:
				continue 
			if checkStartCharge(agv):  
				ret = agv.isChargeAvailable()
				if ret:
					log.warning(agv.agvId, "battery",agv.batteryLevel,"check failed:",ret)
					continue
				else:
					log.info(agv.agvId, "battery",agv.batteryLevel,"check success")
					
				cps = getAvalidChargePoint(agv.mapId,agv.curTarget,cpList,agv.agvId)
				if cps is None:
					log.warning(agv.agvId,"Can't find charge point at",agv.mapId,"battery:",agv.batteryLevel)
					continue
				if goCharge(agv.agvId,cps):
					cpList.append(cps)
					log.info(agv.agvId,"start go charge,batteryLevel=",agv.batteryLevel,",charge point=",cps)
				else:
					log.warning(agv.agvId,"start go charge faild,batteryLevel=",agv.batteryLevel,",charge point=",cps)
		except Exception as e:
			log.exception("check charge",e)
					
	for a in agvs:
		try:
			agv = agvs[a]
			if checkFinishCharge(agv):
				log.info(agv.agvId,"finish charge,batteryLevel=",agv.batteryLevel)
				if not agv.isLock() and not agv.isRunning():
					goHome(agv.agvId,force=False)
					log.info(agv.agvId, "charge finish, go home,batteryLevel=", agv.batteryLevel)
		except Exception as e:
			log.exception("check charge finish",e)

 

def sendFinish(agvId,taskId, error=None): 
	taskList.finish(taskId,agvId,error)
		

def onfinished(result,params):  
	try: 
		if len(params['paths']):
			endPos = params['paths'][-1]
		else:
			endPos = "empty"
			
		error = None
		if "exception" in params or not result:
			error = params['exception'] 
			
		if result:
			log.success("Finish: ",params["agvId"],"arrived",mapMgr.formatLoc(params["mapId"],endPos),",task:",params['taskId'])
		else:
			log.error(params["agvId"],"failed to arrived",mapMgr.formatLoc(params["mapId"],endPos),",task:",params['taskId'],"error",str(error))
			#ss = enhance.showTrace()
			#log.error(ss)
		
		sendFinish(params["agvId"],params['taskId'], error) 
		if params["userCallback"]:
			params["userCallback"](result,params)
		return  
	except Exception as e:
		log.exception("onfinish",e)
		sendFinish(params["agvId"],params['taskId'], str(e))
		if params["userCallback"]:
			params["userCallback"](result,params)
		return  
 

g_lastCheckState = {} #减少打印日志 

def getLogFlag(agvId,key):
	global g_lastCheckState
	if agvId not in g_lastCheckState: 
		g_lastCheckState[agvId] = {"checkFail":False,"blockFail":False,"deadlock":False}
	return g_lastCheckState[agvId][key]
	
	
def setLogFlag(agvId,key,value):
	global g_lastCheckState
	if agvId not in g_lastCheckState: 
		g_lastCheckState[agvId] = {"checkFail":False,"blockFail":False,"deadlock":False}
	g_lastCheckState[agvId][key] = value

def checkMoveJackup(agvId, params):
	agvInfo = agvList.getAgv(agvId)
	if "seer_jackup" in params and params["seer_jackup"] == "JackLoad" and "use_pgv" in params and params['use_pgv']:
		#moveJackup使用二维码失败，导航不会自动停止，需要判断52952告警 
		if 52952 in agvInfo._allAlarmId or 54070 in agvInfo._allAlarmId:
			if "failedPgvTicks" not in params:
					params["failedPgvTicks"] = utility.ticks()
					log.warning(agvId, "moveJackup error: Cannot Find PGV code：%s"%agvInfo._allAlarmId)
					return
			t = params["failedPgvTicks"]
			if utility.ticks() - t < 40000:
				log.warning(agvId, "moveJackup error: Cannot Find PGV code2：%s"%agvInfo._allAlarmId)
				return
			# pgv_msg = agvInfo.getPgv()
			# if pgv_msg is not None:
				# log.warning(agvId, "moveJackup error: Cannot Find PGV code3 %s"%pgv_msg)
				# if pgv_msg["tag_value"] != 0:
					# return
			log.error(agvId, "moveJackup error: Cannot Find PGV code, cancel task")
			agvInfo.cancelTask()

#0.5秒被调用一次，返回True则表示已经到达目标点 
def oncheck(params):  
	cc = counter.counter()
	
	#返回路径和是否为直线 
	def getDistance(x,y,r,cur,next,paths):
		if cur == next:
			return 0,False
			
		lines = map.getStartLines(cur,paths)
		nextLine = None
		endLine = None
		find = None
		checkLines = []
		ret = 0
		for line in lines:
			if find:
				checkLines.append(line)
				if not nextLine:
					ret += line.length
			elif line.contains(x,y):
				find = line
				checkLines.append(line)
				if not nextLine:
					ret += (1-line.percentAtPoint(x,y))*line.length
			elif line.startPos.contains(x,y):
				find = line
				checkLines.append(line)
				ret += line.length
					
			if line.endPosName == next:
				nextLine = line
				continue
			if nextLine:
				checkLines.append(line)
				endLine = line
				break
		if not endLine or not lines or not find or not nextLine:
			return ret,False
			
		for line in checkLines:
			if abs(mapMgr.normAngle(line.r-find.r)) >= math.pi/10:
				return ret,False
		return ret,True
		
	@lockImp.lock(mapMgr.g_lock)
	def checkLost(curPos):
		#判断当前位置是否在paths中
		if curPos not in paths:
			if agvInfo.lostTicks == 0:
				agvInfo.lostTicks = utility.ticks()
			dt = utility.ticks() - agvInfo.lostTicks
			target = agvElement.targetPosName
			log.warning(agvId,curPos,"not in path:[",mapMgr.strPaths(paths),
				"],map:",params["mapId"],",ticks:",dt,",isMoving:",agvInfo.isMoving(),",confidence:",agvInfo.confidence,",target:",target)
			if agvInfo.isMoving():
				return False
			if agvInfo.confidence < 0.75:
				return False
			if target == curPos:
				params["status"] = "waitFinish"
				return False
			if dt < 45000:
				return False
			newPaths = map.getPath(curPos,target,agvId = agvId)
			agvInfo.updatePath(newPaths)
			pp = agvInfo.params
			if pp:
				params["paths"] = pp["paths"]
				params["mapId"] = pp["mapId"]
				params["paths"] = pp["paths"]
				params["pathIndex"] = pp["pathIndex"]
				params["pathsList"] = pp["pathsList"]
			return True
		agvInfo.lostTicks = 0
		if agvElement.nextTargetPosName in paths:
			try:
				curIndex = paths.index(curPos)
				nextIndex = paths.index(agvElement.nextTargetPosName,curIndex)
				if nextIndex < curIndex:
					log.warning(agvId,"status:",agvInfo.action,",taskId:",taskId,",nextIndex:",nextIndex,",curIndex:",curIndex,
						",curPos:",curPos,",nextPos:",agvElement.nextTargetPosName,",paths:",paths)
					agvElement.nextTargetPosName = curPos
			except ValueError as e:
				pass 
		return True 
		
	@lockImp.lock(mapMgr.g_lock)
	def checkAgv(curPos, endPosName): 	
		paths = params['paths']  
		failed = False
		if not checkLost(curPos):
			return False
			
		# 判断小车路线是否有阻挡  
		if not agvElement.check(mapMgr.getAgvList(agvElement.mapId)): 
			if not getLogFlag(agvId,"checkFail"): 
				setLogFlag(agvId,"checkFail",True)
				log.warning(agvId,"check failed",map.getAgv(agvId).blockAgvs,mapMgr.strPaths(paths),",map:",params["mapId"])
			failed = True

		# 判断路径是否有被block
		elif not map.block(agvId,curPos,endPosName,paths):
			setLogFlag(agvId,"checkFail",False) 
			if not getLogFlag(agvId,"blockFail"): 
				setLogFlag(agvId,"blockFail",True)
				log.warning(agvId,"block failed",map.getAgv(agvId).blockAgvs,mapMgr.strPaths(paths),",map:",params["mapId"])
			failed = True
		else:
			setLogFlag(agvId,"blockFail",False)  
		if failed:
			return False
		pp = agvElement.getCheckLines()
		lockImp.release(mapMgr.g_lock)
		if not agvElement.checkElevator(pp):
			return False
		agvInfo.status["task_status"] = 2 #主动配置这个值，这样更新速度最快
		agvInfo.status["target_id"] = agvElement.nextTargetPosName
		return True
		
	def tryCheck(curPos,nextPos,paths):
		lines = map.getStartLines(curPos,paths)
		for line in lines:
			a = line.endPos.agvId
			if a is not None and a != agvId:
				return False
			if line.endPosName == nextPos:
				break
		return True
	
	def getNextPos(agvId,pos,paths):
		find = False
		for p in paths:
			if find:
				return p
			if pos == p:
				find = True
		#if not find:
		#	log.error(agvId,"path:",mapMgr.strPaths(paths),"can't find next pos",mapMgr.formatLoc(params["mapId"],pos))
		return None
	
	def getPrePos(pos,paths):
		pre = None
		for p in paths:  
			if pos == p:
				return pre
			pre = p
		return None 
		
	def checkCancel(): 
		taskState = agvInfo.status["task_status"] 
		#急停之后，让其继续运行 
		#if taskState == 6: 
		#	params["status"] = "waitCheck" 
		#	log.error("task cancel",params["taskId"],"change status",params["status"],"to waitCheck")
		#	return False
		#	
		# if projectName == "fastprint":
		# 	return False
		if taskState == 5 or taskState == 6:  
			agvInfo.clearTask()
			# 0 = NONE, 1 = WAITING, 2 = RUNNING, 3 = SUSPENDED, 4 = COMPLETED, 5 = FAILED, 6 = CANCELED
			if taskState == 5: # TASK_STATUS_FAILED 
				e = Exception(agvId + "执行" + "move " + paths[-1] + "失败"+",taskId:"+params["taskId"])
				e.noprint = True
				raise(e)
			elif taskState == 6: # TASK_STATUS_CANCELED
				e = Exception(agvId + "执行" + "move " + paths[-1] + "取消"+",taskId:"+params["taskId"])
				e.noprint = True
				raise(e)
			return True
		return False
	
	@lockImp.lock(mapMgr.g_lock)
	def _begin(): 
		mapId = params['mapId'] 
		map = getMap(mapId)
#		params["paths"] = map.updateNoTurnPath(params["paths"],agvInfo.angle)
		agvElement.setTargetList(params["paths"])
		agvElement.taskId = params["taskId"]
		assert len(params["paths"]) != 0 
		if len(params["paths"]) == 1:
			agvElement.nextTargetPosName =  params["paths"][0]
		else:
			agvElement.nextTargetPosName =  params["paths"][1] 
	
	# 后避障
	def checkSetDI(cur):
		if projectName != "fastprint" and projectName != "hucais":
			return

		try:
			lines = map.getStartLines(cur,paths)
			if len(lines) == 0:
				return
				
			line = lines[0]
			try:
				if line.backward:
					if params['setDI'] in params and not params[params['setDI']]:
						agvInfo.setDI(7,True)
						params[params['setDI']] = True
						params[params['resetDI']] = False
						log.info(agvId, line, '%s True'%params['setDI'])
				elif params['resetDI'] in params and not params[params['resetDI']]:
					agvInfo.setDI(7,False)
					params[params['setDI']] = False
					params[params['resetDI']] = True
					log.info(agvId, line, '%s False'%params['setDI'])
			except Exception as e:
				log.exception('%s %s error:'%(agvId,params['setDI']),e)
				return
		except Exception as e:
			log.exception('%s check %s error:'%(agvId,params['setDI']),e)
			return
			
	taskId = params["taskId"]
	agvId = params['agvId']
	paths = params['paths']  
	status = params['status'] 
	if not paths or len(paths) <= 1:
		if status not in ["waitFinish","closeElevator","switchMap","gotoElevator","waitReloc"]:
			log.warning(agvId,"path is empty",paths,params["status"])
			#params["status"] = "waitFinish"
			return
	mapId = params['mapId'] 
	status = params['status'] 
	agvInfo = agvList.getAgv(agvId) 
	map = getMap(mapId)
	agvElement = agvInfo.agvElement
	map.unblock(agvId)  

	if not agvInfo.isActive:
		log.warning(agvId,"is inactived",taskId)
		# params["exception"] = agvId + " is disconnected"
		# agvInfo.clearTask(showLog=True,sendCallback=False)
		return
		
	if not agvInfo.isLinked:
		log.warning(agvId,"is disconnected",taskId)
		return
	
	if "send_move_cmd" in params and agvInfo.ticks and agvInfo.ticks!=params["send_move_cmd"]:
		checkCancel()  
		status = params['status'] 
		
	if status == "begin": 
		_begin()
		if projectName=='fastprint':
			params['setDI'],params['resetDI'] = 'setDI8', 'resetDI8'
			params[params['setDI']] = False
			params[params['resetDI']] = False
		elif projectName=='hucais':
			params['setDI'],params['resetDI'] = 'setDI7', 'resetDI7'
			params[params['setDI']] = False
			params[params['resetDI']] = False
		params["status"] = "waitCheck" 
		checkSetDI(agvInfo.curTarget)
		return 
	elif status == "waitNext":  
		if agvElement.nextTargetPosName is None:
			log.error(agvId,"waitNext error nextTargetPosName is None")
			return
		if not checkLost(agvInfo.curTarget):
			return
		paths = params['paths']  
		status = params['status'] 
		if agvInfo.nextTarget == paths[-1]:
			params["status"] = "waitFinish"
			return
		nextPos = getNextPos(agvId,agvElement.nextTargetPosName,paths)
		if nextPos is None:
			return

		checkSetDI(agvInfo.curTarget)

		distance,straight = getDistance(agvInfo.x,agvInfo.y,agvInfo.angle,agvInfo.curTarget,agvElement.nextTargetPosName,paths)
		if not straight and distance > NEAR_DISTANCE:
			return
		if straight and distance > NEAR_LINE_DISTANCE:
			return
		i = 0 
		prePos = None
		while distance and distance < NEAR_LINE_DISTANCE:
			#继续选择下一个点位
			if i > 10:
				break
			i += 1
			cur = agvInfo.curTarget
			if not tryCheck(cur,nextPos,paths):
				log.debug(agvId,"tryCheck failed, choise return from",nextPos,"to",prePos)
				if prePos:
					nextPos = prePos
				break
			if not straight:
				break
			nextPos = getNextPos(agvId,agvElement.nextTargetPosName,paths)
			if nextPos is None:
				break
			x,y,r = agvInfo.x,agvInfo.y,agvInfo.angle
			prePos = agvElement.nextTargetPosName
			agvElement.nextTargetPosName = nextPos
			distance,straight = getDistance(x,y,r,cur,agvElement.nextTargetPosName,paths)
			log.debug(agvId,"choise next pos","cur",cur,"next",agvElement.nextTargetPosName,"pre",prePos,distance,straight)
		if nextPos == agvInfo.curTarget:
			log.debug(agvId,"waitNext","cur",agvInfo.curTarget,"next",agvElement.nextTargetPosName,distance,straight)
			return
		agvElement.nextTargetPosName = nextPos
		log.debug(agvId,"turn to wait check","cur",agvInfo.curTarget,"next",agvElement.nextTargetPosName,distance,straight)
		params["status"] = "waitCheck"
		return
	elif status == "waitCheck":  
		if mapId != agvInfo.mapId:
			log.warning(agvId,"mapId is diff:",mapId,"agv map:",agvInfo.mapId)
			return
		if agvElement.nextTargetPosName is None:
			log.error(agvId,"waitCheck no nextTargetPosName",agvElement.nextTargetPosName)
			return
		if not checkAgv(agvInfo.curTarget,paths[-1]):
			return
		paths = params['paths'] 
		taskList.update(taskId,agvId,"action","move") 
		taskList.update(taskId,agvId,"unfinishPaths",mapMgr.strPaths(agvElement.getUnfinishPos()))
		taskList.update(taskId,agvId,"step",taskList.get(taskId)["step"]+1)
		
		ignoreDir = True
		if agvElement.nextTargetPosName == paths[-1]:
			ignoreDir = False
		
		checkSetDI(agvInfo.curTarget)

		if "seer_jackup" in params and params["seer_jackup"] != None and agvElement.nextTargetPosName == paths[-1]:
			#仙知识别货架腿的移动，没有顶伸动作的 
			if params["seer_jackup"] == "JackLoad":
				agvInfo.moveJackup(agvElement.nextTargetPosName,timeout=params["timeout"],taskId=taskId,use_pgv=params['use_pgv'],ignoreAngle=ignoreDir,pgv_type=params['pgv_type'],recognize=params['recognize'])
			else:
				agvInfo.moveJackdown(agvElement.nextTargetPosName,timeout=params["timeout"],taskId=taskId,ignoreAngle=ignoreDir)
		else: 
			agvInfo.move(agvElement.nextTargetPosName,timeout=params["timeout"],taskId=taskId,ignoreAngle=ignoreDir)
		params["send_move_cmd"] = agvInfo.ticks
		params["status"] = "waitNext"
		return  
	elif status == "waitFinish": 
		#如果这里出异常，会导致不停调用  
		# 0 = NONE, 1 = WAITING, 2 = RUNNING, 3 = SUSPENDED, 4 = COMPLETED, 5 = FAILED, 6 = CANCELED
		taskState = agvInfo.status["task_status"]
		if taskState == 1:
			return
		if taskState == 3:
			return	  
		if paths and agvInfo.curTarget != paths[-1]:
			log.warning(agvInfo.agvId,"waitFinish: loc is diff",agvInfo.curTarget,paths[-1],"task_status=",taskState)
			return  
		
		if taskState == 2:
			checkMoveJackup(agvId,params)
			return
		map.unblock(agvId) 
		
		#继续运行到下一个路径 
		if params["pathIndex"] < len(params['pathsList']) - 1:	
			newMapId = params['pathsList'][params["pathIndex"]+ 1][0]
			if newMapId == mapId:
				params["status"] = "switchMap"
			elif len(elevatorMgr.getElevator(mapId,newMapId)) == 0:
				params["status"] = "switchMap"
			else:
				params["status"] = "closeElevator"
			return
		#所有路径都结束了 
		
		agvInfo.clearTask(showLog=False,sendCallback=False)
		if "seer_jackup" in params and params["seer_jackup"] != None:
			#标记是否带有货架 
			if params["seer_jackup"] == "JackLoad":
				agvInfo.hasShelve = True
			else:
				agvInfo.hasShelve = False
		return True 
	elif status == "closeElevator": #确保电梯处于关门状态 
		# if elevatorMgr.checkClose(agvId,mapId,paths[-1]):
		# 	params["status"] = "switchMap"
		# time.sleep(1)
		elevatorMgr.checkClose(agvId,mapId,paths[-1])
		params["status"] = "switchMap"
		return
	elif status == "gotoElevator": #进入相应的楼层  
		#i = params["pathIndex"] + 1
		i = params["pathIndex"]
		if not elevatorMgr.isBlocked(agvId):
			#在电梯里直接运行有可能会出现这种情况 
			log.warning(agvId,"gotoElevator but not block")
			elevatorMgr.block(agvId,agvInfo.mapId,agvInfo.curTarget)
		if not elevatorMgr.checkOpen(agvId,params['pathsList'][i][0],params['pathsList'][i][1][0],force=True):
			return 
		params["status"] = "waitReloc"
	elif status == "switchMap":	#切换地图	
		index = params["pathIndex"] + 1  
		newMapId = params['pathsList'][index][0]
		newLoc = params['pathsList'][index][1][0]
		if mapId != newMapId:
			#地图切换，电梯管理  
			if not agvInfo.switchMap(newMapId,newLoc):
				return
			params["status"] = "gotoElevator"
			if utility.is_test():	#实际运行会自动重定向 
				agvInfo.reloc(newMapId,newLoc)
		else:
			params["status"] = "begin"
			
		agvInfo.mapId = newMapId
		params["pathIndex"] = index
		params["mapId"] = newMapId
		params["paths"] = params['pathsList'][index][1] 
		_begin() #这句不能删除,agvElement同时也要更改状态 
		
		taskList.update(taskId,agvId,"map",params["mapId"])
		ss = mapMgr.strPaths(params["paths"])
		taskList.update(taskId,agvId,"unfinishPaths",ss)
		taskList.update(taskId,agvId,"paths",ss)
		return
	elif status == "waitReloc":		#等待重定位结束
		if not elevatorMgr.checkOpen(agvId,params["mapId"],params['paths'][0],force=True):
			return   
		if agvInfo.status['reloc_status'] != 1: 
			return
		if agvInfo.status['loadmap_status'] != 1: 
			return
		if params["paths"][0] != agvInfo.curTarget:
			log.info(agvId,"wait loc changed, cur",agvInfo.curTarget,"target",params["paths"][0])
			return
		params["status"] = "begin" 
	else: 
		log.error(agvId,"unknow status",status)
		assert 0	#unknow status 
		 
		 
@lockImp.lock(mapMgr.g_lock)
def solveDeadlock():	
	import itertools
	c = counter.counter()
	def getDeadAgv(a):
		if not a.agvElement:
			return False
		if not a.agvElement.isDeadlock:
			return False
		if a.agvElement.inElevator():
			return False
		if elevatorMgr.isBlocked(a.agvId):
			return False
		return a.action == "waitCheck"
		
	#检查这个解是否可用 
	def check(agvs2):
		blockAgvs = set()
		for a in agvs2:
			if not a.agvElement.check(mapMgr.getAgvList(a.agvElement.mapId)):
				continue
			ret = a.map.block(a.agvId,a.curTarget,a.agvElement.targetList[-1],a.agvElement.targetList)
			if not ret:
				continue
			return True
		ret = hasDeadlock(waitFlag=False)
		return not ret
		
	#1. 正在移动的车子路径不能影响 
	#2. 只能影响死循环的几台车子 
	aa = list(agvList.getAgvList().values())
	aa = [a for a in aa if a.agvElement is not None and a.isActive]
	
	#死锁而且和电梯无关的节点  
	agvs2 = [ a for a in aa if getDeadAgv(a)]
	log.warning("start solve deadlock",[a.agvId for a in agvs2])	#TODO:这里有时候会出现agv01,agv01还未找到原因 
	if not agvs2 and len(agv2) == 1:
		log.info("no deadlock list")
		return
	agvs1 = [ a for a in aa if not a.agvElement.isDeadlock ]
	targets = [ a.agvElement.targetPosName for a in agvs2 ]
	oldStatus = [ utility.clone(a.getStatus()) for a in agvs2]
	indexs = list(range(0, len(targets)))
	isSuccess = False
	solutions = list(itertools.permutations(indexs,len(agvs2)))
	random.shuffle(solutions) 
	for k,indexs in enumerate(solutions):
		if k > 10:
			break
		#寻找一个解
		name = ""
		for i in indexs:
			agv = agvs2[i]
			name += agv.agvId + ","
			nn = agv.map.getPath(agv.curTarget, targets[i], agvId=agv.agvId)
			agv.updatePath(nn)
			if len(agvs2) == 2:
				#如果有两个agv，只需要一台车避让就可以了 
				#name += agv.agvId + ","
				break
		log.info("check solution:",name)
		#测试一个解 
		if check(agvs2):
			isSuccess = True
			log.success("solve deadlock success, used",c.get(),"ms",",order:",name)
			break
		for i in indexs:
			agvs2[i].loadStatus(oldStatus[i])
		log.error("solve deadlock failed %d/%d"%(k+1,len(solutions)),",order:",name)
	else:
		for a in agvList.getAgvList().values():
			if a.agvElement:
				a.agvElement.isDeadlock = False 
			
	#第二种解法
	if not isSuccess:
		log.warning("start solve deadlock2",agvs2)
		for k,indexs in enumerate(solutions):
			if k > 10:
				break
			#寻找一个解
			name = ""
			for i in indexs:
				agv = agvs2[i]
				name += agv.agvId + ","
				if i == 0:
					#选择第一个agv，把之前的路径进行避让 
					oplines = agv.agvElement.getFailLines()
					nn = agv.map.getPath(agv.curTarget, targets[i], agvId=agv.agvId,oplines=oplines)
				else:
					nn = agv.map.getPath(agv.curTarget, targets[i], agvId=agv.agvId)
				agv.updatePath(nn)
				if len(agvs2) == 2:
					#如果有两个agv，只需要一台车避让就可以了 
					name += agv.agvId + ","
					break
			log.info("check solution2:",name)
			#测试一个解
			if check(agvs2):
				isSuccess = True
				log.success("solve deadlock2 success, used",c.get(),"ms",",order:",name)
				break
			for i in indexs:
				agvs2[i].loadStatus(oldStatus[i])
			log.error("solve deadlock2 failed %d/%d"%(k+1,len(solutions)),",order:",name)
		else:
			for a in agvList.getAgvList().values():
				a.agvElement.isDeadlock = False 
			
	log.info("end solve deadlock, used",c.get(),"ms")
	

def hasDeadlock(waitFlag=True):
	def isStop(agv):
		if agv.action != "waitCheck":
			return False
		if agv.isMoving():
			return False
		if agv.agvElement.isBlocked:
			return True
		if agv.agvElement.checkFailed:
			if not waitFlag:
				return True
			elif agv.agvElement.checkFailedTick != 0 and utility.ticks() - agv.agvElement.checkFailedTick > 5000:
				return True
		return False
	
	def _hasDeadlock(agv):
		if not isStop(agv):
			return False 
		visit = [agv.agvId,]
		agvs = agv.agvElement.blockAgvs[:]
		if not agvs:
			return False
		while agvs:
			a = agvs.pop()
			if a in visit:
				continue
			if not isStop(agvList.getAgv(a)):
				return False
			visit.append(a)
			for k in agvList.getAgv(a).agvElement.blockAgvs[:]:
				if k not in visit:
					agvs.append(k)
		return True
	
	@lockImp.lock(mapMgr.g_lock)
	def clearAll():
		for a in agvList.getAgvList().values():
			if a.agvElement:
				a.agvElement.isDeadlock = False 
		
	agvs = [a for a in agvList.getAgvList().values() if isStop(a)]
	if not agvs or len(agvs) <= 1:
		clearAll()		
		return False 
	
	for a in agvs:
		if not a.agvElement.isDeadlock:
			break
	#else:
	#	if waitFlag:
	#		return True
	
	clearAll()
	results = []
	for a in agvs:
		if _hasDeadlock(a):
			log.error("find deadlock agv",a.agvId,a.agvElement.blockAgvs)
			a.agvElement.isDeadlock = True
			results.append(a.agvId)
			
	if results:
		log.error("find deadlock result:",",".join(results))	
		return True
	return False
			
	
 
#重新安排路径  
@lockImp.lock(mapMgr.g_lock)
def rearrange(agv):    
	c = counter.counter()
	def hasPaths(paths1,paths):
		for i in range(len(paths)-1):
			p = "%s->%s" % (paths[i],paths[i+1])
			if p in paths1:
				return True
		return False
		
	def updateNewPath(p,ticks,t):
		log.warning(agvId,"rearrange",t,"from",mapMgr.formatLoc(map.mapId,agv.agvElement.currentPosName),"to",mapMgr.formatLoc(map.mapId,oldPaths[-1].endPosName),
			"by paths:",mapMgr.strPaths(p),"task:",taskId,"len:",w,"used:",ticks,"ms")
		agv.agvElement.setTargetList(p)
		agv.agvElement.nextTargetPosName = p[1]  
		params["status"] = "waitCheck"  
		params["paths"] = p			 #清除原来路径   
		
		ss = mapMgr.strPaths(params["paths"])
		taskList.update(taskId,agvId,"unfinishPaths",ss)
		taskList.update(taskId,agvId,"paths",ss)
		return True	
		
	params = agv.params
	map = agv.map
	if not params:  
		return False
	if agv.isMoving(): #正在运行中，不进行重安排路径   
		return False
	agvId = agv.agvId 
	oldPaths = map.getStartLines(agv.agvElement.currentPosName,params['paths'])
	if not oldPaths:  
		return False
	taskId = params["taskId"] 
	oldWeight = map.getWeight(oldPaths)
	diff = local.getfloat("ctrl","pathDiff")
	stopCount = local.getint("ctrl","deadlockPathCount",30)
	lines,oplines = map.getAgvPath(agvId) 
	stopCount = 10 #TODO 
	newPaths = map.getAllPaths(agv.agvElement.currentPosName, oldPaths[-1].endPosName,stopCount=stopCount,maxWeight=oldWeight+diff,lines=lines,oplines=oplines,exlines=agv.agvElement.getFailLines())
	newPath2 = []
	for pp in newPaths: 
		w = pp[0]
		p = pp[1] 
		if w == oldWeight and len(p) == len(oldPaths):
			continue
		if w - oldWeight > diff:
			continue
		if len(p) < 2:
			continue 
		if agv.agvElement.failPos in p: 
			continue
		if hasPaths(agv.agvElement.blockFailLines,p) or hasPaths(agv.agvElement.checkFailLines,p):
			#新路径也存在相同旧路径的block失败的路径   
			newPath2.append(p)
			continue
		updateNewPath(p,c.get(),t=1)
		return True
		
	if len(newPath2):
		#还是选一条路第一个点不相同的路，继续执行 
		for p in newPath2: 
			if p and p[1] != oldPaths[0].endPosName: 
				updateNewPath(p,c.get(),t=2) 
				return True	
	
	if len(newPath2):
		p = random.choice(newPath2) 
		updateNewPath(p,c.get(),t=3) #还是选一条路，继续执行 
		return True	
		
	log.warning(agvId,"can't find new path from",agv.agvElement.currentPosName,"to",oldPaths[-1].endPosName,
			"old path",mapMgr.strPaths(oldPaths),",used:",c.get(),"ms")
	return False
		 
def _threadFunc(): 
	while not utility.is_exited():
		try:
			if hasDeadlock():
				time.sleep(5)
				if hasDeadlock():
					solveDeadlock()
		except Exception as e:
			log.exception("check deadlock failed,thread quit!",e)
			time.sleep(30)
		time.sleep(10)

def isAvailable(agvId):
		if not agvList.hasAgv(agvId):
			return False
		a = agvList.getAgv(agvId)
		if not a.curTarget:
			return False
		ret = a.isAvailable()
		if ret == "":
				return True
		log.error(agvId,"no isAvailable",ret)
		return False
		
@lockImp.lock(mapMgr.g_lock)
def _apply(mapId, autoLock, exclude, loc, taskId, appName):
	c = counter.counter()
	posList = []
	agvLists = agvList.getAgvList()
	failed = ""
	mapId2,loc = mapMgr.decodeLoc(loc)
	if mapId2 and mapId2 != mapId:
		raise Exception("map冲突,mapId="+mapId+",loc="+mapId2) 
	loc = mapMgr.formatLoc(mapId,loc)
	
	for a in agvLists:
		#同一任务，多次上锁，可重入 
		if agvLists[a].lockTaskId == taskId:
			log.warning("apply",agvLists[a].agvId,"with same task",taskId)
			return agvLists[a].agvId
			
	for a in agvLists:
		if a in exclude:
			failed += a + "[exclude],"
			continue
		agv = agvLists[a]
		if agv.mapId != mapId:
			if not elevatorMgr.getElevator(agv.mapId,mapId):	
				continue
		ret = agv.isAvailable()
		if ret == "":
			if agv.isHandCharge:
				failed += a + "[hand charge], "
				continue
			if agv.agvElement.inElevator():
				failed += a + "[in elevator], "
				continue
			
			pos = agv.agvElement.nextTargetPosName
			if pos is None:
				pos = agv.curTarget
			if pos is None:
				continue
			posList.append((mapMgr.formatLoc(agv.mapId,pos),a))
		else:
			failed += a + "["+str(ret)+"]" 
	if len(posList) == 0:
		if failed == "":
			failed = "[no agv in map "+mapId+"]"
		log.error("apply agv failed! ",failed,"taskId",taskId,"loc",loc)
		e = Exception(loc+"找不到可用的小车")
		e.noprint = True
		raise e 
	paths = []
	map = getMap(mapId) 
	maxWeight = sys.maxsize
	for pos in posList:  
		agv = agvList.getAgv(pos[1])
		if agv.isLock():
			continue
		w = map.getPathWeight(pos[0], loc, agvId=pos[1])
		if  w is None:
			continue
		if agv._taskInfo is not None: #isRunning
			w += 20
		if agv.batteryLevel <= agv.start_charge_level:
			w += 30
		if agv.batteryLevel <= agv.available_charge_level:
			w += 40
		maxWeight = min(w,maxWeight)
		paths.append((w,pos[1])) 
	if not paths:
		log.error("apply agv failed2!","taskId",taskId,"loc",loc)
		raise Exception("找不到可用的位置"+loc)
	agvId = min(paths, key=lambda x: x[0])[1] 
	log.info("apply",agvId,",taskId:",taskId,",loc",loc,",autoLock",autoLock,", used",c.get(),"ms")
	if autoLock: 
		try:
			lock(agvId,taskId,appName)
		except Exception as e: 
			log.error("apply autolock",e)
			return agvId
	return agvId


def apply(mapId, autoLock, exclude, loc, taskId, appName=""):
	for i in range(5):
		try:
			agvId = _apply(mapId, autoLock, exclude, loc, taskId=taskId,appName=appName)
			#apply和lock有个时间差，中间unlock了，可能apply成功，但lock失败 
			if agvId is not None:
				if not autoLock or agvList.getAgv(agvId).isLock():
					return agvId
		except Exception as e:
			log.exception("apply agv failed, count="+str(i),e)
	e = Exception("apply agv failed3!","taskId",taskId,"loc",loc)
	e.noprint = True
	raise e

g_thread = None

def initClient(appName):
	log.info("**********************状态************:",utility.is_test())
	log.info(appName,"init client agvApi")
	agvList.resetLock(appName)
	_init()
		
def _init():
	global g_thread
	if g_thread is None:
		agvList.getAgvList()
		g_thread = threading.Thread(target=_threadFunc,name="agv.hasDeadlock")
		g_thread.start()

def lock(agvId,taskId,appName,force=False):
	_init()
	agv = agvList.getAgv(agvId)
	agv.lock(taskId,appName,force)
	if not agv.clearTask(): #20秒内，小车要停止运行（这种情况一般为回home点的情况) 
		raise Exception("当前小车未停止运行,agvId="+agv.agvId+",targetPos="+str(agv.targetPosName))
	#taskList.update(taskId,agvId,"status","begin") 
	return True

def unlock(agvId,taskId,force=False):
	_init()
	agv = agvList.getAgv(agvId)
	if agv.isLock():
		if force or agv.isLockByTask(taskId):
			if agv.isRunning():
				if not agv.clearTask(): #20秒内，小车要停止运行（这种情况一般为回home点的情况) 
					raise Exception("unlock:当前小车未停止运行2,agvId="+str(agv.agvId)+",taskId="+str(taskId))
	if agv.mapId:
		if force or agv.isLockByTask(taskId):
			agv.map.unblock(agv.agvId)   
	agv.unlock(taskId,force=force)


def move(agvId, target, taskId, timeout,finishCallback=None,paramObj=None):
	assert finishCallback != onfinished
	c = counter.counter()
	_init()
	params = {}
	params["taskId"] = taskId
	params["agvId"] = agvId 
	params["timeout"] = timeout
	params["userCallback"] = finishCallback
	params["finishCallback"] = onfinished
	if paramObj is not None:
		params.update(paramObj)

	agv = agvList.getAgv(agvId) 
	
	if taskId[0:6] != "charge" and not agv.isLock():
		#gocharge 不用上锁滴 
		if taskId[0:5] != "home_":
			raise Exception("当前小车未锁定,agvId="+agv.agvId)
	if agv.curTarget == "":
		raise Exception("当前小车的位置为空,agvId="+agv.agvId) 
	
	@lockImp.lock(mapMgr.g_lock)
	def _func():   
		taskList.add(taskId,agvId)
		taskList.update(taskId,agvId,"start",mapMgr.formatLoc(agv.mapId,agv.curTarget))
		mapId,targetId = mapMgr.decodeLoc(target)
		if mapId:	
			taskList.update(taskId,agvId,"target",target)
		else:
			taskList.update(taskId,agvId,"target",mapMgr.formatLoc(agv.mapId,target))
		
		if agv.curTarget == targetId and (mapId == "" or mapId == agv.mapId):
			if "seer_jackup" in params:
				if params["seer_jackup"] == "JackLoad":
					agv.moveJackup(agv.curTarget,timeout,taskId,use_pgv=params['use_pgv'],pgv_type=params['pgv_type'],recognize=params['recognize'])
				elif params["seer_jackup"] == "JackUnload":
					agv.moveJackdown(agv.curTarget,timeout,taskId)
			if finishCallback: 
				params["paths"] = [targetId,]
				params["status"] = "waitFinish"
				params["pathIndex"] = 0
				params["pathsList"] = [params["paths"],]	
				params["mapId"] = agv.mapId   
				agv.agvElement.setTargetList(params["paths"])
				agv.movePath(timeout=timeout,checkCallback=oncheck,finishCallback=onfinished,params=params) 
			else:
				taskList.finish(taskId,agvId)	
			return  
		paths = getMap(agv.mapId).getPath(agv.curTarget, target,agvId = agvId)
		if not paths:
			raise Exception(mapMgr.formatLoc(agv.mapId,agv.curTarget)+"->"+target+" 路径不存在1,agvId="+agv.agvId) 
		log.info("Begin:",agvId,"move from",mapMgr.formatLoc(agv.mapId,agv.curTarget),"to",mapMgr.formatLoc(agv.mapId,target),"by paths:",paths,"task:",taskId,"timeout",timeout,"used",c.get(),"ms")
		params["paths"] = paths[0][1]
		params["mapId"] = paths[0][0]
		params["pathIndex"] = 0
		params["pathsList"] = paths		
		params["status"] = "begin"
		taskList.update(taskId,agvId,"map",params["mapId"])
		s = mapMgr.strPaths(params["paths"])
		#toolsUtil.setTaskPath(taskId, s)
		taskList.update(taskId,agvId,"unfinishPaths",s)
		taskList.update(taskId,agvId,"paths",s) 
		agv.agvElement.setTargetList(paths[0][1]) #这句和oncheck里_begin有重复，这里可以保证分配路径顺路算法
		agv.movePath(timeout=timeout,checkCallback=oncheck,finishCallback=onfinished,params=params)  


	if agv.isRunning(): 
		log.warning(agv.agvId,"is running, task_status=",agv.task_status,",running taskId=",agv.taskId,",taskId=",taskId)
		for i in range(600):
			#等待退出循环处理 
			if not agv._inHandle:
				break
			time.sleep(0.1)
		else:
			raise Exception("agv is running 4,agvId="+agv.agvId+",targetPos="+str(agv.targetPosName))
			
		if not agv.clearTask(): #20秒内，小车要停止运行（这种情况一般为回home点的情况) 
			raise Exception("agv is running,agvId="+agv.agvId+",targetPos="+str(agv.targetPosName))
			
		for i in range(600):
			#等待退出循环处理 
			if not agv._inHandle:
				break
			time.sleep(0.1)
		else:
			raise Exception("agv is running 5,agvId="+agv.agvId+",targetPos="+str(agv.targetPosName))
	_func()
 

def goCharge(agvId,chargeLoc): 
	taskId = "charge_" + getSn()
	agv = agvList.getAgv(agvId)
	if agv.curTarget == chargeLoc:
		return True
	if agv.isLock():
		log.error(agvId,"gocharge agv is locked")
		return False
	if agv.isRunning():
		log.error(agvId,"gocharge agv is running")
		return False
	# projectName = local.get("project","name")
	# if projectName=='fastprint':
	# 	if agv.isAtHome:
	# 		agv.resetRotation()
	try: 
		move(agvId=agvId, target=chargeLoc, taskId=taskId, timeout=90 * 60)
		return True
	except Exception as e:
		log.exception(agvId+" gocharge",e)
		return False
		
		
def goHome(agvId,force,timeout=120*60):
	@utility.catch
	def goHomeFinish(result,params):
		unlock(params["agvId"],params["taskId"],force=False)
		
	agv = agvList.getAgv(agvId)
	if not agv.homeLoc:
		log.info(agvId,"has not homeLoc")
		return ""
	if agv.isAtHome:
		log.info(agvId,"is in home loc",agv.homeLoc)
		return ""
	if agv.isHomeTask:
		log.info(agvId,"is in goHome task")
		return ""
	if agv.mapId is None:
		raise Exception("gohome failed: no map,agvId="+agv.agvId)
	if agv._initState != 1:
		raise Exception("gohome failed: no init,agvId="+agv.agvId)
	if agv.status:
		if "loadmap_status" in agv.status and agv.status["loadmap_status"] != 1:
			raise Exception("gohome failed: loadmap error,agvId="+agv.agvId)
		if "reloc_status" in agv.status and agv.status["reloc_status"] != 1:
			raise Exception("gohome failed: reloc error,agvId="+agv.agvId)
	print("********************************agv的 状态：",agv.isRunning)
	if agv.isRunning():
		if force:
			if not agv.clearTask(): #20秒内，小车要停止运行（这种情况一般为回home点的情况) 
				raise Exception("小车任务未结束，调用goHome失败,agvId="+agv.agvId)
		else: 
			raise Exception("小车任务未结束2，调用goHome失败,agvId="+agv.agvId)
	if force:
		taskId = "force_home_" + getSn()
		if not agv.isLock():
			lock(agvId=agvId,taskId=taskId,appName="gohomeforce")
	else:
		taskId = "home_" + getSn()
	assert agv.homeLoc
	log.info(agvId,"gohome",taskId,"force",force,"taskId",taskId,":",mapMgr.formatLoc(agv.agvId,agv.curTarget),"->",agv.homeLoc)
	move(agvId=agvId, target=agv.homeLoc, taskId=taskId, timeout=timeout,finishCallback=goHomeFinish)
	return taskId


def cancel(agvId):
	log.warning("user cancel ",agvId)
	agv = agvList.getAgv(agvId)
	agv.clearTask(showLog=True,sendCallback=True)


def setChargeState(agvId,value):
	agv = agvList.getAgv(agvId)
	assert isinstance(value,bool)
	agv.canCharge = value
	
def getChargeState(agvId):
	agv = agvList.getAgv(agvId)
	return agv.canCharge

	
def getAgvStatue(agvId):
	return agvList.getAgv(agvId).status

getAgvList = agvList.getAgvList

g_sn = 0


def getSn():
	global g_sn
	g_sn += 1
	return str(g_sn)
 
	
def show():  
	import mainFrame
	mainFrame.show()
	 

######################## unit test ########################
def waitTask(taskId,timeout=100):
	#global g_taskIds
	for i in range(timeout):
		rr = taskList.get(taskId)
		if not rr:
			continue 
		if rr["status"] == "finish":	
			if rr["success"]:
				return True
			raise Exception(rr["exception"])
		time.sleep(1)
	log.error("wait task timeout",taskId)
	return False

	
def waitAgv(file="agv.cfg"):
	local.set("project","agvcfg",file)
	agvList.clear()
	mapMgr.g_agvs = {}
	while True:
		#等待所有agv上线 
		aa = getAgvList()
		for a in aa:
			if aa[a].status is None:
				time.sleep(0.5) 
				break
		else:
			time.sleep(0.5)
			break 
	
def _isBatteryOut():
	assert utility.is_test()
	for a in agvList.getAgvList():
		if agvList.getAgv(a).batteryLevel != 0:
			return False
	log.error("--- all agv is out")
	return True
 
 
def testRun(locs, taskId,exclude=[]):
	import utility
	if not utility.is_test():
		time.sleep(10)
	try:
		while True:
			try:
				agvId = apply(mapId='8-222', autoLock=True, exclude=exclude, loc=locs[0],taskId=taskId) 
				agvId2 = apply(mapId='8-222', autoLock=True, exclude=exclude, loc=locs[0],taskId=taskId) 
				assert agvId == agvId2 
			except Exception as e:
				log.error("apply failed",str(e),", taskId",taskId) 
				if _isBatteryOut():
					return
				time.sleep(10) 
				continue
			for loc in locs:
				move(agvId, loc, taskId, 200)
				if not waitTask(taskId):
					print("--- wait task timeout",agvId)
				else:
					print("--- arrived ",agvId,loc)
			print("-----finish move---------",agvId,",".join(locs))
			#taskId = goHome(agvId)
			#waitTask(taskId)
			unlock(agvId,taskId)
			time.sleep(6)
	except Exception as e:
		log.exception("runthread",e)


#双车会产生死锁，同时还能解锁继续运行 
#难度：一般
#结果: 2019.11.13通过 
def testdeadlock():
	local.set("ctrl","enlargeValue","1.2")
	local.set("ctrl","handleDeadlock",True)
	local.set("ctrl","pathDiff","15") 
	
	import driver.seerAgv_0427.mockAgvCtrl as agvCtrl
	agvCtrl.disableBattery()
	mapMgr.setActive("8-222")  
	t1 = threading.Thread(target=testRun, args=(["LM12", "LM20"] , "taskA"+str(utility.ticks()),["agv22",]))
	t1.start() 
	t2 = threading.Thread(target=testRun, args=(["LM20", "LM12"], "taskB"+str(utility.ticks()),["agv21",]))
	t2.start()
	m = getMap("8-222")
	#m.getAgv("agv22").setPos("LM12") 
	#m.getAgv("agv23").setPos("LM20") 
	m.show()
	t1.join()
	t2.join()


def testRun2(locs,mapId, taskId,exclude=[],timeout=1):
	import utility
	if not utility.is_test():
		time.sleep(2)
	try:
		while True: 
			for loc in locs:
				try:
					taskId = str(uuid.uuid4())
					agvId = apply(mapId=mapId, autoLock=True, exclude=exclude, loc=locs[0],taskId=taskId) 
				except Exception as e:
					raise e
					print("----- apply failed",str(e))  
					time.sleep(5) 
					continue
				
				move(agvId, loc, taskId, 200)
				if waitTask(taskId,100): 
					print("-----wait task finish",agvId,taskId)
				unlock(agvId,taskId)
				time.sleep(timeout) 	 
	except Exception as e: 
		log.exception("--- runthread",e)
		raise e
	

#观察其是否会低电量自动充电，是否有能有序的排队充电 
#难度：一般
#结果: 2019.11.13通过 
def testcharge():
	import agvList
	import driver.seerAgv_0427.mockAgvCtrl as agvCtrl
	mapMgr.setActive("test430")  
	local.set("ctrl","enlargeValue","1.2")
	local.set("ctrl","handleDeadlock",True) 

	agvList.g_agvList = None 
	mapMgr.g_agvs = {}
	initClient("test")
	waitAgv() 
 
	mapMgr.setActive("test430") 
	import threading 
	t1 = threading.Thread(target=testRun2, args=(["AP7","LM30"], "test430","task"+str(utility.ticks()),["agv62","agv63"],10))
	t1.start()                                                    
	t2 = threading.Thread(target=testRun2, args=(["AP7","LM31"], "test430","task"+str(utility.ticks()),["agv61","agv62"],10))
	t2.start()  
	t3 = threading.Thread(target=testRun2, args=(["AP7","LM30"], "test430","task"+str(utility.ticks()),["agv61","agv63"],10))
	t3.start()  
	m = getMap("test430")
	m.show()
	t1.join()   
	
	
#观察其是否会定时自动充电，是否分配到LM31和CP1充电 
#难度：一般
#结果: 2019.11.13通过 
def testcharge2():
	import agvList
	import driver.seerAgv_0427.mockAgvCtrl as agvCtrl
	global g_charge_fix_times,g_charge_policy
	now = datetime.datetime.now()
	g_charge_policy = 2
	g_charge_fix_times = [((now + datetime.timedelta(seconds=10)).time(),(now + datetime.timedelta(minutes=30)).time()),] 
	
	getMap("test430").getPos("LM31").className = "ChargePoint" 
	getMap("test430").getPos("LM32").className = "ChargePoint" 

	mapMgr.setActive("test430")  
	local.set("ctrl","enlargeValue","1.2")
	local.set("ctrl","handleDeadlock",True) 

	agvList.g_agvList = None 
	mapMgr.g_agvs = {}
	initClient("test")
	waitAgv() 
 
	mapMgr.setActive("test430") 
	import threading 
	t1 = threading.Thread(target=testRun2, args=(["AP7","LM30"], "test430","task"+str(utility.ticks()),["agv62","agv63"],60))
#	t1.start()                                                    
	t2 = threading.Thread(target=testRun2, args=(["AP7","LM31"], "test430","task"+str(utility.ticks()),["agv61","agv62"],60))
#	t2.start()  
	t3 = threading.Thread(target=testRun2, args=(["AP7","LM30"], "test430","task"+str(utility.ticks()),["agv61","agv63"],60))
#	t3.start()  
	m = getMap("test430")
	m.show()
	t1.join()  
	
	
#测试三台车在不停gohome的过程中会被打断，同时还会产生死锁解锁的过程 
#成功判断：跑一小时不出现问题（无block失败，无crush)
#难度：困难
#结果: 2019.11.13通过 
def testgohome():
	import agvList
	def gohomethread(agvIds):
		while True:
			for agvId in agvIds:
				if not agvList.getAgv(agvId).isLock():
					try:
						goHome(agvId,False)
					except Exception as e:
						print(e)
			time.sleep(1)
	agvList.g_agvList = None 
	waitAgv()
	
	import agvList
	import driver.seerAgv_0427.mockAgvCtrl as agvCtrl
	agvCtrl.disableBattery() 
  
	mapMgr.setActive("test430") 
	 
	import threading 
	t1 = threading.Thread(target=testRun2, args=(["LM32","LM30"], "test430","task"+str(utility.ticks()),["agv62","agv63"],15))
	t1.start()                                                    
	t2 = threading.Thread(target=testRun2, args=(["LM32","LM31"], "test430","task"+str(utility.ticks()),["agv61","agv62"],10))
	t2.start()  
	t3 = threading.Thread(target=testRun2, args=(["LM32","LM26"], "test430","task"+str(utility.ticks()),["agv61","agv63"],15))
	t3.start() 
	t4 = threading.Thread(target=gohomethread, args=(["agv61"],))#,,"agv62","agv63"
	t4.start()  
	m = getMap("test430")
	m.show()
	t1.join()   

	 
def runLine(mapId="shuqin",startPos="LM1",endPos="LM6",repeat=1,goHomeTimeout=0,agvId=""): 	
	time.sleep(10)
	import threading
	for i in range(repeat):	
		taskId = str(uuid.uuid4())
		if agvId:
			agvId2 = agvId
			lock(agvId2,taskId=taskId,appName="ycat")
		else:
			agvId2 = apply(mapId=mapId, autoLock=True, exclude=[], loc=startPos,taskId=taskId)  
		try: 
			if endPos:
				move(agvId2, endPos, taskId=taskId,timeout= 600000)
				waitTask(taskId,timeout= 600000)
			if startPos:
				move(agvId2, startPos, taskId=taskId,timeout= 600000)
				waitTask(taskId,timeout= 600000) 
			if goHomeTimeout:
				goHome(agvId2,force=False)
				time.sleep(goHomeTimeout)
		except Exception as e:
			log.exception("runlinetest",e)
		print("-------- repeat ",i+1,agvId2)
		unlock(agvId2,taskId=taskId,force=False)  
		
		
def runLineTest(mapId="shuqin",endPos="LM6",exclude=None,repeat=1): 
	import threading

	for i in range(repeat):
		taskId = str(uuid.uuid4())
		agvId = apply(mapId=mapId, autoLock=True,exclude=exclude, loc=endPos,taskId=taskId) 
		try:
			move(agvId, endPos, taskId=taskId,timeout= 200)
			waitTask(taskId) 
		except Exception as e:
			log.exception("runlinetest",e)
		unlock(agvId,taskId=taskId)
		goHome(agvId,False)
		print("-------- repeat ",i)
	
	
#观察一条直线的运行情况
#难度：简单
#结果: 2019.11.13通过 
def testline():
	mapMgr.setActive("shuqin")
	import utility,threading
	t = threading.Thread(target=runLine)
	t.start()
	m = getMap("shuqin")  
	m.show() 
	t.join()
		 
		 
#测试两个环，中间为oneway，同向而行的情况  
#成功判断：跑一小时不出现问题（无block失败，无crush)
#难度：中
#结果: 2019.11.13通过 
def testbell():
	import driver.seerAgv_0427.mockAgvCtrl as agvCtrl
	agvCtrl.disableBattery()
	
	mapMgr.setActive("bell")
	agvCtrl.setPos("agv41","LM5")
	agvCtrl.setPos("agv42","LM6") 
	time.sleep(1) 
	import utility,threading
	t = threading.Thread(target=runLine,args=["bell","LM1","LM12",10])
	t.start()
	t2 = threading.Thread(target=runLine,args=["bell","LM1","LM12",10])
	t2.start()
	m = getMap("bell")  
	m.show() 
	t.join()
	t2.join()
	

#结果: 2019.11.13通过 
def testbell2():
	import driver.seerAgv_0427.mockAgvCtrl as agvCtrl
	agvCtrl.disableBattery()
	mapMgr.setActive("bell")
	agvCtrl.setPos("agv41","LM4")
	agvCtrl.setPos("agv42","LM12") 
	time.sleep(1) 
	import utility,threading
	t = threading.Thread(target=runLine,args=["bell","LM4","LM9",10])
	t.start()
	t2 = threading.Thread(target=runLine,args=["bell","LM3","LM12",10])
	t2.start()
	m = getMap("bell")  
	m.show() 
	t.join()
	t2.join()
	

#结果: 2019.11.13通过 
def testbell3():
	import driver.seerAgv_0427.mockAgvCtrl as agvCtrl
	agvCtrl.disableBattery()
	mapMgr.setActive("bell")
	agvCtrl.setPos("agv41","LM12")
	agvCtrl.setPos("agv42","LM5") 
	time.sleep(0.5) 
	import utility,threading
	t = threading.Thread(target=runLine,args=["bell","LM14","LM6",10])
	t.start()
	t2 = threading.Thread(target=runLine,args=["bell","LM14","LM6",10])
	t2.start()
	m = getMap("bell")  
	m.show() 
	t.join()
	t2.join() 
	

#测试死锁解锁(第二种方法能解) 
def testfastprint():
	import driver.seerAgv_0427.mockAgvCtrl as agvCtrl
	agvCtrl.disableBattery() 
	waitAgv("fastprint2.cfg")
	mapMgr.setActive("fp20190712-1")   
	m = getMap("fp20190712-1")    
	time.sleep(0.5)  
	agvCtrl.setPos("AGV01","AP88")  
	agvCtrl.setPos("AGV02","AP814")  
	#agvCtrl.setPos("AGV04","LM776")  
	import utility,threading
	t = threading.Thread(target=runLine,args=["fp20190712-1","fp20190712-1.AP88","fp20190712-1.CP86",1])

	t.start()
	t2 = threading.Thread(target=runLine,args=["fp20190712-1","fp20190712-1.AP814","fp20190712-1.AP863",50])
	t2.start()
	#t3 = threading.Thread(target=runLine,args=["fp20190712-1","fp20190712-1.LM776","fp20190712-1.LM722",50])
	#t3.start()
	m.show() 
	t.join()  
	
#测试地图510.smap 
#成功判断：跑到结束为止（无block失败，无crush)
#难度：简单
#结果: 2019.11.13通过 
def test510(): 
	import driver.seerAgv_0427.mockAgvCtrl as agvCtrl
	agvCtrl.disableBattery()
	local.set("ctrl","enlargeValue","1.2")
	local.set("ctrl","handleDeadlock",True)
	mapMgr.setActive("510")   
	m = getMap("510")   
	# m.show()
	time.sleep(0.5)  
	import utility,threading
	t = threading.Thread(target=runLineTest,args=["510","LM30",["agv72"],30])
	t.start()
	t2 = threading.Thread(target=runLine,args=["510","LM31","LM25",50])
	t2.start() 
	m.show() 
	t.join()  
	
#测试多图运行效果 
#结果: 2019.11.13通过 
def test_scada(): 
	import driver.seerAgv_0427.mockAgvCtrl as agvCtrl
	waitAgv("testagv2.cfg") 
	agvCtrl.disableBattery()    
	m = getMap("testscada")    

	agvCtrl.setPos("agv91","LM41")  
	time.sleep(0.5)  
	import utility,threading
	t = threading.Thread(target=runLine,args=["testscada","LM36","LM41",50])
	t.start()
	t2 = threading.Thread(target=runLine,args=["testscada","LM36","LM41",50])
	t2.start() 
	show() 
	t2.join()  

 
#大地图运行效果 
#结果: 2019.11.14通过 
def testfastprint2():  
	import driver.seerAgv_0427.mockAgvCtrl as agvCtrl
	agvCtrl.disableBattery()  
	waitAgv("testagv4.cfg") 
	agvList.getAgv("AGV01").hasShelve = True
	agvList.getAgv("AGV02").hasShelve = True
	agvList.getAgv("AGV03").hasShelve = True
	agvList.getAgv("AGV04").hasShelve = True
	agvList.getAgv("AGV05").hasShelve = True
	agvList.getAgv("AGV06").hasShelve = True
	agvList.getAgv("AGV07").hasShelve = True
	agvList.getAgv("AGV08").hasShelve = True
	
	m = getMap("big")  
	time.sleep(0.5)  
	import utility,threading 
	t = threading.Thread(target=runLine,args=["big","AP185","AP753",10]) 
	#t = threading.Thread(target=runLine,args=["big","LM903","LM903",1]) 
	t2 = threading.Thread(target=runLine,args=["big","AP187","AP750",10])
	t3 = threading.Thread(target=runLine,args=["big","AP188","AP749",10])
	t4 = threading.Thread(target=runLine,args=["big","AP191","AP748",10])
	
	t5 = threading.Thread(target=runLine,args=["big","AP264","AP305",10])
	t6 = threading.Thread(target=runLine,args=["big","AP262","AP192",10])
	t7 = threading.Thread(target=runLine,args=["big","AP287","AP193",10])
	t8 = threading.Thread(target=runLine,args=["big","AP286","AP194",10])

	t.start() 
	t2.start()
	t3.start()	 
	t4.start()	  
	t5.start() 
	t6.start()
	t7.start()	 
	t8.start()	
	m.show() 
	t.join()    
	
	
	 
#测试电梯切换
#效果多车可以来回经过电梯 
#难度：困难
#结果: 2019.11.14通过
def testswitchmap():
	import driver.seerAgv_0427.mockAgvCtrl as agvCtrl
	agvCtrl.disableBattery()
	local.set("project","agvcfg","testagv5.cfg")
	file = local.get("project","agvcfg") 
	
	agvList.g_agvList = None  
	agvList.getAgv("AGV01").createMock("testscada","LM33")
	agvList.getAgv("AGV02").createMock("testscada","LM34")
	agvList.getAgv("AGV03").createMock("testscada","LM24")
	
	waitAgv("testagv5.cfg")
	mapMgr.g_agvs = {} 
	time.sleep(0.5)  
	t = threading.Thread(target=runLine,args=["408","408.LM24","testscada.LM1",10])
	t2 = threading.Thread(target=runLine,args=["testscada","testscada.LM1","408.LM14",10])
	t3 = threading.Thread(target=runLine,args=["testscada","testscada.LM5","408.LM4",10])
	time.sleep(1)  
	t.start()  
	t2.start()  
	t3.start()  
	show() 
	t.join()
	t2.join()	
	t3.join()
	
def testgetChargeFixTime():
	assert [] == getChargeFixTime("") 
	assert [(datetime.time(12,53,31),datetime.time(13,5,9)),] == getChargeFixTime("12:53:31 - 13:5:9")
	assert [(datetime.time(12,53,31),datetime.time(13,5,9)),(datetime.time(12,53,1),datetime.time(13,35,29)),(datetime.time(12,53,31),datetime.time(13,25,49))] == getChargeFixTime("12:53:31 - 13:5:9 , 12:53:1 - 13:35:29 , 12:53:31 - 13:25:49  ")
		
		
def testscadafunc(source,s_prepoint,target,t_prepoint):
	time.sleep(5)
	#->source->s_prepoint->target->t_prepoint->gohome
	taskId = str(uuid.uuid4())
	agvId = apply(mapId="testscada", autoLock=True, exclude=[], loc=source,taskId=taskId) 
	
	# ->source
	taskId1 = taskId+"_1"
	move(agvId, source, taskId=taskId1,timeout=1200)
	waitTask(taskId1)
	# ->s_prepoint
	taskId2 = taskId+"_2"
	move(agvId, s_prepoint, taskId=taskId2,timeout=1200)
	waitTask(taskId2)
	#->target
	taskId3 = taskId+"_3"
	move(agvId, target, taskId=taskId3,timeout=1200)
	waitTask(taskId3)
	#->t_prepoint
	taskId4 = taskId+"_4"
	move(agvId, t_prepoint, taskId=taskId4,timeout=1200)
	waitTask(taskId4)
	unlock(agvId,taskId=taskId)
	goHome(agvId,False)
		
def test_testscada():
	import utility,threading
	t = threading.Thread(target=testscadafunc,args=["testscada.AP1","testscada.LM3","testscada.AP50","testscada.LM40"])
	t.start()
	t2 = threading.Thread(target=testscadafunc,args=["testscada.AP2","testscada.LM4","testscada.AP51","testscada.LM43"])
	t2.start() 
	show() 
	t2.join()  
		
		
#测试任务取消
#难度：一般
#结果: 2019.12.14通过 
def testcancel(): 
	def cancelThread():
		time.sleep(6) 
		#cancel("agv21")
	import driver.seerAgv_0427.mockAgvCtrl as agvCtrl
	agvCtrl.disableBattery()
	mapMgr.setActive("8-222")  
	t1 = threading.Thread(target=testRun, args=(["LM12", "LM20"] , "taskA"+str(utility.ticks())))
	t1.start() 
	t2 = threading.Thread(target=cancelThread)
	t2.start()
	m = getMap("8-222") 
	m.show()
	t1.join() 

def testfastprint3():
	import driver.seerAgv_0427.mockAgvCtrl as agvCtrl
	agvCtrl.disableBattery()
	local.set("project","agvcfg","testagv4.cfg")
	file = local.get("project","agvcfg")
	
	agvList.g_agvList = None
	agvList.getAgv("AGV01").createMock("big","AP61")
	agvList.getAgv("AGV02").createMock("big","LM124")
	agvList.getAgv("AGV03").createMock("big","AP864")
	agvList.getAgv("AGV04").createMock("big","LM898")
	
	waitAgv("testagv4.cfg")
	#agvCtrl.setPos("AGV04","AP80")  #TODO 
	#agvCtrl.setPos("AGV01","LM103")  #TODO 
	mapMgr.g_agvs = {}
	time.sleep(0.5)
	t1 =threading.Thread(target=runLine,args=["big","LM71","LM174",10],name="agvCtrl.test")
	t2 =threading.Thread(target=runLine,args=["big","AP224","AP237",10],name="agvCtrl.test")
	t3 =threading.Thread(target=runLine,args=["big","AP225","AP238",10],name="agvCtrl.test")
	t4 =threading.Thread(target=runLine,args=["big","AP226","AP239",10],name="agvCtrl.test")
	t5 =threading.Thread(target=runLine,args=["big","AP227","AP240",10],name="agvCtrl.test")
	t6 =threading.Thread(target=runLine,args=["big","AP228","LM285",10],name="agvCtrl.test")
	t7 =threading.Thread(target=runLine,args=["big","CP860","AP612",10],name="agvCtrl.test")
	t8 =threading.Thread(target=runLine,args=["big","LM134","AP688",10],name="agvCtrl.test")
	time.sleep(1)
	t1.start() 
	t2.start() 
	t3.start() 
	t4.start() 
	t5.start() 
	t6.start() 
	t7.start() 
	t8.start() 
	show()
	t1.join()  
	
def testNoBlockPath():
	import driver.seerAgv_0427.mockAgvCtrl as agvCtrl
	agvCtrl.disableBattery()
	#local.set("project","agvcfg","testagv4.cfg")
	file = local.get("project","agvcfg")
	
	#agvList.g_agvList = None
	#agvList.getAgv("AGV01").createMock("big","AP61")
	#agvList.getAgv("AGV02").createMock("big","LM124")
	#agvList.getAgv("AGV03").createMock("big","AP864")
	#agvList.getAgv("AGV04").createMock("big","LM898")
	t1 =threading.Thread(target=runLine,args=["408","LM18","AP3",10,True],name="agvCtrl.test")
	t2 =threading.Thread(target=runLine,args=["408","LM19","AP6",10,True],name="agvCtrl.test")
	t3 =threading.Thread(target=runLine,args=["408","LM11","LM14",10,True],name="agvCtrl.test")
	
	t1.start() 
	t2.start() 
	t3.start() 
	show()
	t1.join() 
	waitAgv()
	
def skipLocThread(agvId,locs):
	import time
	time.sleep(5)
	while True:
		for loc in locs:
			agvList.getAgv(agvId).setPos(loc)
			print(agvId,"set loc",loc)
			time.sleep(1)
	
	 
#测试带电梯的场景 
def testfastprint4():
	import driver.seerAgv_0427.mockAgvCtrl as agvCtrl
	agvCtrl.disableBattery()
	#local.set("project","agvcfg","fastprint.cfg")
	file = local.get("project","agvcfg")
	
	#agvList.g_agvList = None
	#agvList.getAgv("AGV01").createMock("big","AP61")
	#agvList.getAgv("AGV02").createMock("big","LM124")
	#agvList.getAgv("AGV03").createMock("big","AP864")
	#agvList.getAgv("AGV04").createMock("big","LM898")
	
	waitAgv("fastprint.cfg")
	#agvCtrl.setPos("AGV04","AP80")  #TODO 
	#agvCtrl.setPos("AGV01","LM103")  #TODO 
	#mapMgr.g_agvs = {}
	time.sleep(0.5)
	t1 =threading.Thread(target=runLine,args=["fp20190712-1","fp20190712-1.AP227","20190911_F1.AP47"],name="agvCtrl.test")
	t2 =threading.Thread(target=runLine,args=["fp20190712-1","fp20190712-1.AP228","20190911_F1.AP48"],name="agvCtrl.test")
	t3 =threading.Thread(target=runLine,args=["fp20190712-1","fp20190712-1.AP225","20190911_F1.AP49"],name="agvCtrl.test")
	t4 =threading.Thread(target=runLine,args=["fp20190712-1","fp20190712-1.AP226","20190911_F1.AP50"],name="agvCtrl.test")
	t5 =threading.Thread(target=runLine,args=["fp20190712-1","fp20190712-1.AP226","20190911_F1.AP50"],name="agvCtrl.test")
	t6 =threading.Thread(target=runLine,args=["fp20190712-1","fp20190712-1.AP226","20190911_F1.AP50"],name="agvCtrl.test")
	t7 =threading.Thread(target=runLine,args=["fp20190712-1","fp20190712-1.AP226","20190911_F1.AP50"],name="agvCtrl.test")
	t8 =threading.Thread(target=runLine,args=["fp20190712-1","fp20190712-1.AP226","20190911_F1.AP50"],name="agvCtrl.test")
	t1.start() 
	t2.start() 
	t3.start() 
	t4.start() 
	t5.start() 
	t6.start() 
	t7.start() 
	t8.start() 
	show()
	t1.join()  
	

#测试goHome打断的异常 
def testfastprint5():
	import driver.seerAgv_0427.mockAgvCtrl as agvCtrl
	agvCtrl.disableBattery()
	local.set("project","agvcfg","fastprint.cfg")
	file = local.get("project","agvcfg")
	
	#agvList.g_agvList = None
	#agvList.getAgv("AGV01").createMock("big","AP61")
	#agvList.getAgv("AGV02").createMock("big","LM124")
	#agvList.getAgv("AGV03").createMock("big","AP864")
	#agvList.getAgv("AGV04").createMock("big","LM898")
	
	waitAgv("fastprint.cfg")
	#agvCtrl.setPos("AGV04","AP80")  #TODO 
	#agvCtrl.setPos("AGV01","LM103")  #TODO 
	#mapMgr.g_agvs = {}
	time.sleep(0.5)
	agvList.agvCtrl.jackUp("AGV01")
	agvList.agvCtrl.jackUp("AGV02")
	agvList.agvCtrl.jackUp("AGV03")
	agvList.agvCtrl.jackUp("AGV04")
	agvList.agvCtrl.jackUp("AGV05")
	t1 =threading.Thread(target=runLine,args=["fp20190712-1","AP302","AP757",10,30],name="agvCtrl.test")   #AP701
	t2 =threading.Thread(target=runLine,args=["fp20190712-1","AP143","AP756",10,30],name="agvCtrl.test")   #AP702
	t3 =threading.Thread(target=runLine,args=["fp20190712-1","AP257","AP290",10,30],name="agvCtrl.test")   #AP700
	t4 =threading.Thread(target=runLine,args=["fp20190712-1","AP303","AP291",10,20],name="agvCtrl.test")   #AP699
	t5 =threading.Thread(target=runLine,args=["fp20190712-1","AP741","AP753",10,30],name="agvCtrl.test")   #AP698
	t6 =threading.Thread(target=runLine,args=["fp20190712-1","AP742","AP749",10,30],name="agvCtrl.test")   #AP697
	t7 =threading.Thread(target=runLine,args=["fp20190712-1","AP255","AP748",10,30],name="agvCtrl.test")   #AP696
	t8 =threading.Thread(target=runLine,args=["fp20190712-1","AP286","AP750",10,30],name="agvCtrl.test")   #AP695
	t1.start() 
	t2.start() 
	t3.start() 
	t4.start() 
	#t5.start() 
	#t6.start() 
	#t7.start() 
	#t8.start() 
	show()
	t1.join()  
	
#测试01车在02后面，但01车先占用deadend的路线，02车block失败的问题，最后死锁
#期望结果: 死锁恢复继续运行
def testbigdeadlock1():
	import driver.seerAgv_0427.mockAgvCtrl as agvCtrl
	agvCtrl.disableBattery()
	local.set("project","agvcfg","fastprint.cfg")
	file = local.get("project","agvcfg")
	waitAgv("fastprint.cfg")
	agvList.agvCtrl.jackUp("AGV01")
	agvList.getAgv("AGV01").setPos("LM921")
	agvList.getAgv("AGV02").setPos("LM111")
	time.sleep(2)
	t1 =threading.Thread(target=runLine,args=["fp20190712-1","","AP757",10,30,"AGV01"],name="agvCtrl.test")   #AP701
	t2 =threading.Thread(target=runLine,args=["fp20190712-1","","AP757",10,30,"AGV02"],name="agvCtrl.test")   #AP702
	t1.start() 
	time.sleep(0.5)
	t2.start() 
	show()
	t1.join() 

#能正常解锁，不会死锁 
def testbigdeadlock2():
	import driver.seerAgv_0427.mockAgvCtrl as agvCtrl
	agvCtrl.disableBattery()
	waitAgv("fastprint.cfg")
	
	agvList.getAgv("AGV01").setPos("LM924")
	agvList.getAgv("AGV01").pause()
	lock("AGV01","T1","app")
	move("AGV01","LM877","T1",timeout=50000)
	
	agvList.getAgv("AGV05").setPos("LM925")
	agvList.getAgv("AGV05").pause()
	lock("AGV05","T55","app")
	move("AGV05","LM876","T55",timeout=50000)
	
	agvList.getAgv("AGV02").setPos("LM34")
	agvList.getAgv("AGV02").pause()
	lock("AGV02","T2","app")
	move("AGV02","LM924","T2",timeout=50000)
	
	agvList.getAgv("AGV03").setPos("LM927")
	agvList.getAgv("AGV03").pause()
	lock("AGV03","T2","app")
	move("AGV03","LM924","T2",timeout=50000)
	
	agvList.getAgv("AGV04").setPos("LM928")
	agvList.getAgv("AGV04").pause()
	lock("AGV04","T2","app")
	move("AGV04","LM924","T2",timeout=50000)
	
	agvList.getAgv("AGV07").setPos("LM926")
	agvList.getAgv("AGV07").pause()
	lock("AGV07","T22","app")
	move("AGV07","LM924","T22",timeout=50000)
	
	for a in agvList.getAgvList().values():
		a.resume() 
		
	show()
	t1.join()	
	

#能正常解锁，不会死锁 
def testbigdeadlock3():
	import driver.seerAgv_0427.mockAgvCtrl as agvCtrl
	agvCtrl.disableBattery()
	waitAgv("fastprint.cfg")
	
	agvList.getAgv("AGV01").setPos("LM924")
	agvList.getAgv("AGV01").jackUp()
	agvList.getAgv("AGV01").pause()
	lock("AGV01","T1","app")
	move("AGV01","AP742","T1",timeout=50000)
	
	agvList.getAgv("AGV05").setPos("LM925")
	agvList.getAgv("AGV05").pause()
	lock("AGV05","T55","app")
	move("AGV05","LM876","T55",timeout=50000)
	
	agvList.getAgv("AGV02").setPos("LM34")
	agvList.getAgv("AGV02").pause()
	lock("AGV02","T2","app")
	move("AGV02","LM924","T2",timeout=50000)
	
	agvList.getAgv("AGV03").setPos("LM927")
	agvList.getAgv("AGV03").pause()
	lock("AGV03","T2","app")
	move("AGV03","LM924","T2",timeout=50000)
	
	agvList.getAgv("AGV04").setPos("LM928")
	agvList.getAgv("AGV04").pause()
	lock("AGV04","T2","app")
	move("AGV04","LM924","T2",timeout=50000)
	
	agvList.getAgv("AGV07").setPos("LM926")
	agvList.getAgv("AGV07").pause()
	lock("AGV07","T22","app")
	move("AGV07","LM924","T22",timeout=50000)
	
	for a in agvList.getAgvList().values():
		a.resume() 
		
	show()
	t1.join()
	
	
#能正常解锁，不会死锁 
def testbigdeadlock4():
	import driver.seerAgv_0427.mockAgvCtrl as agvCtrl
	agvCtrl.disableBattery()
	waitAgv("fastprint.cfg")
	
	agvList.getAgv("AGV01").setPos("LM752")
	agvList.getAgv("AGV01").pause()
	lock("AGV01","T1","app")
	move("AGV01","LM877","T1",timeout=50000)
	
	agvList.getAgv("AGV05").setPos("LM925")
	agvList.getAgv("AGV05").pause()
	lock("AGV05","T55","app")
	move("AGV05","LM876","T55",timeout=50000)
	
	agvList.getAgv("AGV02").setPos("LM34")
	agvList.getAgv("AGV02").pause()
	lock("AGV02","T2","app")
	move("AGV02","LM924","T2",timeout=50000)
	
	agvList.getAgv("AGV03").setPos("LM927")
	agvList.getAgv("AGV03").pause()
	lock("AGV03","T2","app")
	move("AGV03","LM924","T2",timeout=50000)
	
	agvList.getAgv("AGV04").setPos("LM928")
	agvList.getAgv("AGV04").pause()
	lock("AGV04","T2","app")
	move("AGV04","LM924","T2",timeout=50000)
	
	agvList.getAgv("AGV07").setPos("LM926")
	agvList.getAgv("AGV07").pause()
	lock("AGV07","T22","app")
	move("AGV07","LM924","T22",timeout=50000)
	
	for a in agvList.getAgvList().values():
		a.resume() 
		
	show()
	t1.join()

	
#测试在路线起点或终点就在电梯里的场景
#期望结果: 不会有异常，能正常运行 
def testelevator():
	import driver.seerAgv_0427.mockAgvCtrl as agvCtrl
	agvCtrl.disableBattery()
	local.set("project","agvcfg","fastprint.cfg")
	file = local.get("project","agvcfg")
	waitAgv("fastprint.cfg")
	agvList.agvCtrl.jackUp("AGV01")
	agvList.getAgv("AGV01").setPos("LM921")
	agvList.getAgv("AGV02").setPos("LM111")
	time.sleep(2)
	t1 =threading.Thread(target=runLine,args=["fp20190712-1","20190911_F1.LM28","fp20190712-1.LM285",10,0,"AGV05"],name="agvCtrl.test")   #AP701
	t2 =threading.Thread(target=runLine,args=["fp20190712-1","fp20190712-1.AP240","20190911_F1.LM79",10,0,"AGV01"],name="agvCtrl.test")   #AP702
	t1.start() 
	t2.start() 
	show()
	t1.join() 
	
#测试跨电梯绕道，无界面，无assert异常 
def testdetour():
	import driver.seerAgv_0427.mockAgvCtrl as agvCtrl
	agvCtrl.disableBattery()
	waitAgv("fastprint.cfg")
	
	agvList.getAgv("AGV01").switchMap("20190911_F1","LM78")
	agvList.getAgv("AGV01").mapId = "20190911_F1"
	agvList.getAgv("AGV01").setPos("LM78")
	agvList.agvCtrl.jackUp("AGV01")
	agvList.getAgv("AGV01").pause()
	lock("AGV01","T1","app")
	
	agvList.getAgv("AGV02").setPos("LM866")
	agvList.getAgv("AGV02").pause()
	lock("AGV02","T2","app")
	move("AGV02","20190911_F1.AP59","T2",timeout=50000)
	time.sleep(1)	
	move("AGV01","fp20190712-1.LM866","T1",timeout=50000)
	assert agvList.getAgv("AGV01").params["pathsList"] == [('20190911_F1', ['LM78', 'LM92', 'LM79', 'LM17', 'LM28'], 
		16.403054642798132),('fp20190712-1', ['LM285', 'LM130', 'LM133', 'LM244', 'LM243', 'LM242', 'LM918', 'LM917', 
		'LM912', 'LM866'], 38.58756886807938)]
	
	agvList.getAgv("AGV01").clearTask()
	agvList.agvCtrl.jackDown("AGV01")
	time.sleep(2)
	move("AGV01","fp20190712-1.LM866","T1",timeout=50000)
	assert agvList.getAgv("AGV01").params["pathsList"] ==  [('20190911_F1', ['LM78', 'LM92', 'LM79', 'LM17', 'LM28'], 16.403054642798132), ('fp20190712-1', ['LM285', 'LM130', 'LM133', 'LM244', 'AP240'], 52.03957816556366), ('fp20190712-1', ['AP240', 'LM244', 'LM243', 'LM242', 'LM918', 'LM917', 'LM912', 'LM866'], 13.45200929748428)]
	 
	
#测试5台车，都向一个点运行
#期望结果: 死锁恢复继续运行
def testbigdeadlock111():
	import driver.seerAgv_0427.mockAgvCtrl as agvCtrl
	agvCtrl.disableBattery()
	local.set("project","agvcfg","fastprint2.cfg")
	file = local.get("project","agvcfg")
	waitAgv("fastprint2.cfg")
	# agvList.agvCtrl.jackUp("AGV01")
	# agvList.getAgv("AGV01").setPos("LM921")
	# agvList.getAgv("AGV02").setPos("LM111")
	time.sleep(2)
	t1 =threading.Thread(target=runLine,args=["fp20190712-1","AP820","AP716",1,30],name="agvCtrl.test")   #AP701
	t2 =threading.Thread(target=runLine,args=["fp20190712-1","AP820","AP716",1,30],name="agvCtrl.test")   #AP702
	t3 =threading.Thread(target=runLine,args=["fp20190712-1","AP820","AP716",1,30],name="agvCtrl.test")   #AP701
	t4 =threading.Thread(target=runLine,args=["fp20190712-1","AP820","AP716",1,30],name="agvCtrl.test")   #AP702
	t5 =threading.Thread(target=runLine,args=["fp20190712-1","AP820","AP716",1,30],name="agvCtrl.test")   #AP701
	t6 =threading.Thread(target=runLine,args=["fp20190712-1","AP820","AP716",1,30],name="agvCtrl.test")   #AP702
	t1.start()  
	t2.start()  
	t3.start()  
	t4.start() 
	t5.start()  
	t6.start()
	
	
	show()
	t1.join() 
	 

#测试小车是否按路线运行
def testbigfollowPath():
	import driver.seerAgv_0427.mockAgvCtrl as agvCtrl
	agvCtrl.disableBattery()
	local.set("project","agvcfg","fastprint2.cfg")
	file = local.get("project","agvcfg")
	waitAgv("fastprint2.cfg")
	agvList.getAgv("AGV01").setPos("AP862")
	agvList.getAgv("AGV02").setPos("LM73")
	time.sleep(2)
	
	
	t1 =threading.Thread(target=runLine,args=["fp20190712-1","AP862","CP86",1],name="agvCtrl.test")   #AP701
	t2 =threading.Thread(target=runLine,args=["fp20190712-1","LM73","AP30",1],name="agvCtrl.test")   #AP702
#	mapMgr.g_lock.acquire()
	time.sleep(10)
	t2.start()  
	time.sleep(1)
	t1.start()  
	show()
	t1.join() 
	 
	
	
#测试check路径是否连续，无assert异常 
def testintersect():
	import driver.seerAgv_0427.mockAgvCtrl as agvCtrl
	agvCtrl.disableBattery()
	waitAgv("fastprint2.cfg")
	agvList.getAgv("AGV01").setPos("LM71")
	agvList.getAgv("AGV02").setPos("LM826")#LM715
	agvList.getAgv("AGV02").selected = True
	lock("AGV02","T55","app")
	time.sleep(2)
	b = mapMgr.getAgv("AGV01").boundPath
	a = mapMgr.getAgv("AGV02")
	a.targetList = ["LM826","LM145","LM38","LM39","LM922","LM103"]
	a.nextTargetPosName = "LM103"
	c = a.boundPath 
	import ui.pltUtil
	import bezierPath
	import matplotlib.path as mpath  
	import matplotlib.patches as mpatches
	from matplotlib import pyplot as plt
	m = getMap("fp20190712-1")
	plt.plot(agvList.getAgv("AGV01").x,agvList.getAgv("AGV01").y,"r*")
	plt.plot(agvList.getAgv("AGV02").x,agvList.getAgv("AGV02").y,"r*")
	
	for p in a.targetList:
		n = m.getPos(p)
		plt.plot(n.x,n.y,"g+")
	
	p1 = a.blockPath
	p2 = b
	aa = plt.gca().add_patch(mpatches.PathPatch(ui.pltUtil.qt2path(p2,inverse=False), 
		edgecolor="black",facecolor="green",alpha=0.8,zorder=20000))
	bb = plt.gca().add_patch(mpatches.PathPatch(ui.pltUtil.qt2path(p1,inverse=False), 
		edgecolor="black",facecolor="yellow",alpha=0.8,zorder=20000))
		
	cc = m.getLine("LM145","LM38")._ptrList 
	for c in cc:
		plt.plot(c[0],c[1],"b+")
	ui.pltUtil.fix(-100,100)
	assert not p1.intersects(p2)
	plt.show() 
	

def testbigdeadlock113():
#[INFO]2020-05-28 09:26:30,435: AGV04 getPathSingle fp20190712-1.LM666 -> fp20190712-1.AP612 ,index 0 ,add path1: ['LM666', 'LM667', 'LM678', 'LM681', 'LM677', 'LM913'] ,path2: ['LM913', 'LM677', 'LM681', 'LM678', 'LM667', 'LM666', 'AP612'] ,shelf: True
#[DEBUG]2020-05-28 09:24:27,798: agvInfo: AGV06 fp20190712-1.AP612 move to fp20190712-1.LM667 ,taskId force_home_127

	import driver.seerAgv_0427.mockAgvCtrl as agvCtrl
	agvCtrl.disableBattery()
	local.set("project","agvcfg","fastprint2.cfg")
	file = local.get("project","agvcfg")
	waitAgv("fastprint2.cfg")
	# agvList.agvCtrl.jackUp("AGV01")
	agvList.getAgv("AGV01").setPos("AP612")
	agvList.getAgv("AGV02").setPos("LM133")
	time.sleep(2)
	
	#lock("AGV01",taskId="333",appName="ycat")
	#move("AGV01", "LM677", taskId="333",timeout= 600000)
	#time.sleep(8)
	#b = agvList.getAgv("AGV01").agvElement.getTargetLines(agvList.getAgv("AGV01").map)

	t1 =threading.Thread(target=runLine,args=["fp20190712-1","AP612","AP24",1,0,"AGV01"],name="agvCtrl.test")    
	t2 =threading.Thread(target=runLine,args=["fp20190712-1","LM667","LM667",1,0,"AGV02"],name="agvCtrl.test")
	t1.start()                                                                                          
	t2.start()  
	time.sleep(2)
	show()
	t1.join() 
	
def testdesai():
	import driver.seerAgv_0427.mockAgvCtrl as agvCtrl
	agvCtrl.disableBattery()
	local.set("project","agvcfg","desai.cfg")
	file = local.get("project","agvcfg")
	waitAgv("desai.cfg")
	# agvList.agvCtrl.jackUp("AGV01")
	agvList.getAgv("AGV01").setPos("LM222")
	agvList.getAgv("AGV02").setPos("LM14")
	m = getMap("desai-all-20191223")
	l = m.getLine("LM52","LM26")
	time.sleep(2)
	t1 =threading.Thread(target=runLine,args=["desai-all-20191223","AP34","LM14",4],name="agvCtrl.test")   #AP701
	t2 =threading.Thread(target=runLine,args=["desai-all-20191223","LM32","LM14",4],name="agvCtrl.test")   #AP702
	t1.start()  
	time.sleep(2)
	t2.start()  
	show()
	t1.join() 
	
#测试block.cfg的死锁解锁  
def testfastprint6():
	import driver.seerAgv_0427.mockAgvCtrl as agvCtrl
	agvCtrl.disableBattery() 
	waitAgv("fastprint2.cfg")
	mapMgr.setActive("fp20190712-1")   
	m = getMap("fp20190712-1")    
	time.sleep(0.5)  
	agvList.agvCtrl.jackUp("AGV01")
	agvCtrl.setPos("AGV02","AP46")  
	agvCtrl.setPos("AGV01","AP13")  
	agvCtrl.setPos("AGV03","LM73")  
	import utility,threading
	t = threading.Thread(target=runLine,args=["fp20190712-1","fp20190712-1.AP46","fp20190712-1.LM844",50])

	t.start()
	t2 = threading.Thread(target=runLine,args=["fp20190712-1","fp20190712-1.AP13","fp20190712-1.LM1123",50])
	t2.start()
	#t3 = threading.Thread(target=runLine,args=["fp20190712-1","fp20190712-1.LM776","fp20190712-1.LM722",50])
	#t3.start()
	m.show() 
	t.join()  
	
	
if __name__ == '__main__':
	utility.start()  
	agvList.clear() 
	
	mapMgr.g_agvs = {} 
	initClient("test")
	#testdesai()
	#assert 0
	# testbigdeadlock113()
	
	#testdetour()
	#testbigdeadlock112()
#	testbigfollowPath()
	testfastprint6()
	# assert 0
	#testfastprint3()
	
	# waitAgv("agv.cfg")
	#testcancel()
	# testbigdeadlock111() #pass
	#testcharge()	#pass
	#testcharge2()	#pass
	#testgohome()   #pass
	#testline()		#pass
	#testbell()		#pass
	#testbell2()	#pass 
	#testbell3()	#pass 
#	testfastprint()#pass 
	#test510()		#pass
	#test_scada()	#pass
	#testswitchmap() #pass
	#testfastprint2() #pass
	#testgetChargeFixTime()#pass

	#test_testscada() 
	
	 
	
	
