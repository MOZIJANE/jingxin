import sys, os
import bottle
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import log
import webutility
import scadaUtility
import utility 
import mapMgr 
import agvControl
import agvApi
import agvList
import taskList
import time

if __name__ == '__main__': 		 
	if webutility.is_bottle():
		mapMgr.loadAllMap()
else:
	mapMgr.loadAllMap()

########## AGV运动相关 ##########
@scadaUtility.get('/api/agv/init')
def urlInit(): 
	agvControl.initClient(appName=webutility.get_param("appName") )
	
@scadaUtility.get('/api/agv/taskStatus')
def urlTask(): 
	taskId = webutility.get_param("taskId")
	if taskId is None:
		taskId = ""
	return {"taskList": taskList.getList(taskId.split(","))}
	

@scadaUtility.get('/api/agv/taskList')
def urlTaskList():  
	return {"taskList": taskList.getAllList()}
	
	
@scadaUtility.get('/api/agv/apply')
def urlApply():
	autoLock = webutility.get_param_bool("autoLock")
	exclude = webutility.get_param("exclude")
	appName = webutility.get_param('appName')
	timeout = webutility.get_param_int("timeout")
	excludes = []
	if exclude is not None:
		excludes = exclude.split(",")
	loc = webutility.get_param("loc")
	mapId = webutility.get_param("mapId")
	taskId = webutility.get_param("taskId")
	ticks = utility.ticks()
	i = 0
	while utility.ticks() - ticks < timeout:
		try:
			agvId = agvControl.apply(mapId=mapId,autoLock=autoLock, exclude=excludes, loc=loc,taskId=taskId,appName=appName)
			return {"agvId": agvId}
		except Exception as e:
			log.exception("apply failed, count="+str(i+1),e)
		i+=1
		time.sleep(3)
	log.error("apply agv timeout")
	
@scadaUtility.get('/api/agv/isAvailable')
def isAvailable():
	agvId=webutility.get_param("agv") 
	return {"value":agvControl.isAvailable(agvId=agvId)}

@scadaUtility.get('/api/agv/lock')
def urlLock():
	agvId=webutility.get_param("agv") 
	force = webutility.get_param_bool("force",False)
	agvControl.lock(agvId=agvId,taskId=webutility.get_param('taskId'),appName=webutility.get_param('appName'),force=force)
 

@scadaUtility.get('/api/agv/release')
def urlUnlock():
	agvId = webutility.get_param("agv")
	force = webutility.get_param_bool("force",False)
	agvControl.unlock(agvId=agvId,taskId=webutility.get_param('taskId'),force=force)

@scadaUtility.get('/api/agv/isLocked')
def urlIsLocked():
	agvId = webutility.get_param("agv") 
	taskId = webutility.get_param("taskId")
	if not taskId:
		return {"isLocked":agvList.getAgv(agvId).isLocked()}
	else:
		return {"isLocked":agvList.getAgv(agvId).isLockByTask(taskId)}


@scadaUtility.get('/api/agv/goHome')
def urlGoHome():
	agvId = webutility.get_param("agv") 
	force = webutility.get_param_bool("force",False)
	timeout = webutility.get_param_int("timeout",30*60)
	agvControl.goHome(agvId=agvId,force=force,timeout=timeout)


@scadaUtility.get('/api/agv/move')
def urlMove():
	agvId= webutility.get_param("agv")
	target= webutility.get_param("loc")
	timeout= webutility.get_param("timeoutSec")
	taskId = webutility.get_param("taskId")
	seer_jackup = webutility.get_param("seer_jackup")
	paramObj = {}
	if seer_jackup != None: 
		recognize = webutility.get_param_bool("recognize")
		paramObj["seer_jackup"] = seer_jackup
		paramObj["recognize"] = recognize
	agvControl.move(target=target, agvId=agvId, taskId=taskId, timeout=timeout,paramObj=paramObj)
	return {"taskId": taskId}

@scadaUtility.get('/api/agv/cancel')
def urlCancel():
	agvId = webutility.get_param("agv")
	agvControl.cancel(agvId)
	
@scadaUtility.get('/api/agv/startCharge')
def urlStartCharge():
	agvControl.startCharge()


#设置agv是否可以进入行充电的状态，默认为True 
#例如在agv带有货框不能充电时，设置False，
#要记得设置回True,要不然会导致agv无法充电 
@scadaUtility.get('/api/agv/setChargeState')
def urlSetChargeState():
	agvId= webutility.get_param("agv")
	v = webutility.get_param_bool("value")
	agvControl.setChargeState(agvId,v)
	
	
@scadaUtility.get('/api/agv/getChargeState')
def urlGetChargeState():
	agvId= webutility.get_param("agv")
	return {"value":agvControl.getChargeState(agvId)}

@scadaUtility.get('/api/agv/agvStatusList')
def urlStatusList():
	mapId = webutility.get_param("mapId")
	ret = {}
	aa = agvControl.getAgvList()
	for a in aa:
		if aa[a].mapId == mapId:
			if aa[a].status:
				ret[a] = aa[a].status
				ret[a]["isActive"] = aa[a].isActive
			else:
				ret[a]=dict()
				ret[a]["isActive"]=False
			ret[a]['isLocked'] = aa[a].isLock()
	return {"list":ret}


@scadaUtility.get('/api/agv/status')
def urlStatus():
	agvId= webutility.get_param("agv")
	info = agvControl.getAgvStatue(agvId=agvId)
	assert info
	block_reason = ["Ultrasonic超声检测到被阻挡","Laser激光检测到被阻挡","Fallingdown防跌落传感器检测到被阻挡","Collision碰撞传感器检测到被阻挡","Infrared红外传感器检测到被阻挡","Lock锁车开关被触"]
	task_status = ["NONE", "WAITING", "RUNNING", "SUSPENDED", "COMPLETED", "FAILED", "CANCELED"]
	task_type = ["没有任务", "自由导航到任意点", "自由导航到站点", "固定路径导航到站点", "其他"]
	reloc_status = ["FAILED(重定位失败)", "SUCCESS(重定位正确)", "RELOCING(正在重定位)", "COMPLETED(重定位完成)"]
	loadmap_status = ["FAILED(载入地图失败)", "SUCCESS(载入地图成功)", "LOADING(正在载入地图)"]
	slam_status = ["没有扫图", "正在扫图", "正在实时扫图否"]
	ret = [
		{"name": "上锁状态","fieldId": "isLocked","value": agvList.getAgv(agvId).isLock()},
		{"name": "模式","fieldId": "mode","value": "自动" if info["mode"]==1 else "手动"},
		{"name": "急停","fieldId": "emergency","value": info["emergency"] if "emergency" in info else None}, 
		{"name": "充电状态","fieldId": "charging","value": info["charging"] if "charging" in info else None},
		{"name": "电压（V）","fieldId": "voltage","value": info["voltage"] if "voltage" in info else None}, 
		{"name": "电流（A）","fieldId": "current","value": info["current"] if "current" in info else None}, 
		{"name": "累计里程(m)","fieldId": "odo","value": "%.2f"%info["odo"]},
		{"name": "本次运行(ms)","fieldId": "time","value": info["time"]},
		{"name": "累计运行(ms)","fieldId": "total_time","value": info["total_time"]},
		{"name": "电池电量","fieldId": "battery_level","value": "%.2f"%(info["battery_level"]*100) if "battery_level" in info else None}, 
		{"name": "电池温度(℃)","fieldId": "battery_temp","value": info["battery_temp"] if "battery_temp" in info else None}, 
		{"name": "x 坐标(m)","fieldId": "x","value": "%.2f"%info["x"]},
		{"name": "y 坐标(m)","fieldId": "y","value": "%.2f"%info["y"]},
		{"name": "angle 坐标(rad)","fieldId": "angle","value": "%.2f"%info["angle"]},
		{"name": "置信度","fieldId": "confidence","value": "%.2f"%(info["confidence"]*100)},
		{"name": "x 速度(m/s)","fieldId": "vx","value": "%.2f"%float(info["vx"])},
		{"name": "y 速度(m/s)","fieldId": "vy","value": "%.2f"%info["vy"]},
		{"name": "角速度(rad/s)","fieldId": "w","value": "%.2f"%info["w"]},
		{"name": "舵角","fieldId": "steer","value": info["steer"] if "steer" in info else None}, 
		{"name": "DI数据","fieldId": "DI","value": info["DI"] if "DI" in info else None,"isArrary": True},
		{"name": "DO数据","fieldId": "DO","value": info["DO"] if "DO" in info else None,"isArrary": True}, 
		{"name": "DI激活状态","fieldId": "DI_valid","value": info["DI_valid"] if "DI_valid" in info else None},
		{"name": "任务状态","fieldId": "task_status","value": task_status[info["task_status"]]}, 
		{"name": "任务类型","fieldId": "task_type","value": task_type[info["task_type"]]}, 
		{"name": "任务目标站点","fieldId": "target_id","value": info["target_id"] if "target_id" in info else None}, 
		{"name": "任务目标坐标","fieldId": "target_point","value": info["target_point"] if "target_point" in info else None,"isArrary": True},  
		{"name": "路径已过站点","fieldId": "finished_path","value": info["finished_path"] if "finished_path" in info else None,"isArrary": True}, 
		{"name": "路径未经站点","fieldId": "unfinished_path","value": info["unfinished_path"] if "unfinished_path" in info else None,"isArrary": True}, 
		{"name": "重定位状态","fieldId": "reloc_status","value": reloc_status[info["reloc_status"]]}, 
		{"name": "载入地图状态","fieldId": "loadmap_status","value": loadmap_status[info["loadmap_status"]]}, 
		{"name": "扫图状态","fieldId": "slam_status","value": slam_status[info["slam_status"]]}, 
		{"name": "任务列表状态","fieldId": "tasklist_status","value": info["tasklist_status"] if "tasklist_status" in info else None}, 
		{"name": "阻挡","fieldId": "blocked","value": info["blocked"]},
		{"name": "阻挡原因","fieldId": "block_reason","value": block_reason[info["block_reason"]] if "block_reason" in info else None}, 
		{"name": "阻挡x坐标(m)","fieldId": "block_x","value": info["block_x"] if "block_x" in info else None}, 
		{"name": "阻挡y坐标(m)","fieldId": "block_y","value": info["block_y"] if "block_y" in info else None}, 
		{"name": "阻挡DI的ID","fieldId": "block_di","value": info["block_di"] if "block_di" in info else None}, 
		{"name": "阻挡超声 的 ID","fieldId": "block_ultrasonic_id","value": info["block_ultrasonic_id"] if "block_ultrasonic_id" in info else None},
		{"name": "控制器温度(℃)","fieldId": "controller_temp","value": info["controller_temp"] if "controller_temp" in info else None},
		{"name": "控制器湿度(%)","fieldId": "controller_humi","value": info["controller_humi"] if "controller_humi" in info else None},
		{"name": "控制器电压(V)","fieldId": "controller_voltage","value": info["controller_voltage"] if "controller_voltage" in info else None}, 
		{"name": "是否抱闸","fieldId": "brake","value": info["brake"] if "brake" in info else None}, 
		{"name": "所在区域id","fieldId": "area_ids","value": info["area_ids"],"isArrary": True}, 
		{"name": "Fatal数组","fieldId": "fatals","value": info["fatals"] if "fatals" in info else None,"isArrary": True}, 
		{"name": "Error数组","fieldId": "errors","value": info["errors"] if "errors" in info else None,"isArrary": True}, 
		{"name": "Warning数组","fieldId": "warnings","value": info["warnings"] if "warnings" in info else None,"isArrary": True}, 
		{"name": "错误码","fieldId": "ret_code","value": info["ret_code"] if "ret_code" in info else None}, 
		{"name": "错误信息","fieldId": "err_msg","value": info["err_msg"] if "err_msg" in info else None}
	]
	return {"data": {"info": ret}}

########## 外围设备相关 ##########
# 返回读输入IO列表 [True,False,....]
@scadaUtility.get('/api/agv/readIO')
def urlReadIO():
	agvId = webutility.get_param("agv")
	return {"data":agvList.getAgv(agvId).readIO()}	


# 清除输出IO
@scadaUtility.get('/api/agv/clearIO')
def urlClearIO():
	agvId = webutility.get_param("agv")
	agvList.getAgv(agvId).clearIO()	


# 设置写IO
# id		:	number DO的id号, 从0开始
# status	: 	boolean true为高电平,false为低电
@scadaUtility.get('/api/agv/writeIO')
def urlWriteIO():
	agvId = webutility.get_param("agv")
	id = webutility.get_param("id")
	s = webutility.get_param("status")
	agvList.getAgv(agvId).writeIO(id,s)


########## web接口 ##########
@scadaUtility.get('/api/map/load')
def urlStatic():
	floor= webutility.get_param("floor")
	return agvControl.getMap(floor).webInfo()

@scadaUtility.get('/api/map/floor')
def urlFloor():  
	return {'list':mapMgr.getMapList()}
	
@scadaUtility.get('/api/agv/agvList')
def urlAgvList():
	ret = []
	aa = agvControl.getAgvList()
	for a in aa:
		ret.append({"id": a})
	return {"list": ret}
	
######### map接口 ############
@scadaUtility.get('/api/map/save')
def urlSave():
	info = {
		'name' : webutility.get_param("name"),
		'scale' : webutility.get_param("scale"),
		'rotateX' : webutility.get_param("rotateX"),
		'rotateY' : webutility.get_param("rotateY"),
		'theta' : webutility.get_param("theta"),
		'offsetX' : webutility.get_param("offsetX"),
		'offsetY' : webutility.get_param("offsetY")
	}
	return {"result": mapMgr.saveMapInfo(info)}

@scadaUtility.get('/api/map/get')
def urlGet():
	name = webutility.get_param("name")
	return {"result": mapMgr.getMapInfo(name)}
	  
	
def showThread(): 
	#time.sleep(5)
	agvControl.show()

#for uwsgi 
app = application = bottle.default_app()
webutility.add_ignore('/api/agv/taskList')
webutility.add_ignore('/api/agv/taskStatus')

if __name__ == '__main__': 		 
	if webutility.is_bottle():
		utility.start() 
		import threading
		import mainFrame 
		t = threading.Thread(target=showThread)
		t.start()
	webutility.run()
else: 
	import threading
	t = threading.Thread(target=showThread)
	t.start() 
	
	



