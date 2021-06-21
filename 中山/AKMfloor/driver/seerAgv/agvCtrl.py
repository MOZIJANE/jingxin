#coding=utf-8
# ycat			2018-8-2	  create
# seerAgv的语义调用 
import sys,os 
import datetime
import math
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import driver.seerAgv.agvApi as agvApi
import local
import log
import time
import json

g_agvList = agvApi.g_agvList


def _getAgvType(agvId):
	type_ = g_agvList[agvId]["type"]
	return g_agvType[type_]

def _loadAgvType():
	proName = local.get("project","name") 
	file = "/../../agvCtrl/projects/"+proName+"/" + local.get("project","agvType")  
	with open(os.path.abspath(os.path.dirname(__file__) + file), 'r') as f:		
		agvTypeDict = {}
		aa = json.load(f)
		for a in aa:
			agvTypeDict[a] = aa[a]
		return agvTypeDict

g_agvType = _loadAgvType()

def checkLink(agvId):
	return agvApi.checkLink(agvId)

def cancelTask(agvId):
	agvApi.task(agvId,"robot_task_cancel_req",None)

#机器人启动后会有一定的初始化时间，通过 (1111) 可查询机器人的初始化状态 
#0 = FAILED(初始化失败), 1 = SUCCESS(初始化成功), 2 = INITING(正在初始化) 
def checkInit(agvId):
	data= agvApi.status(agvId,"robot_status_init_req",None)
	return data["init_status"]

#重定位,pos为(x,y,r)三元组 
def reloc(agvId,pos=None):
	if pos is None:
		agvApi.ctrl(agvId,"robot_control_reloc_req",{"home":True})
	else:
		agvApi.ctrl(agvId,"robot_control_reloc_req",{"home":False,"x":pos[0],"y":pos[1],"angle":pos[2]})

#重定位,pos为(x,y,r)三元组 
def reloc2(agvId,pos=None,loc=None):
	if loc is not None:
		agvApi.ctrl(agvId,"robot_control_reloc_req",{"loc": loc})
	else:
		agvApi.ctrl(agvId,"robot_control_reloc_req",{"loc":'',"x":pos[0],"y":pos[1],"angle":pos[2]})

#确认定位正确 
def confirmReloc(agvId):
	data= agvApi.ctrl(agvId,"robot_control_comfirmloc_req",None)

def goCharge(agvId):
	agvApi.task(agvId, "robot_task_gocharge_req", None)

def goHome(agvId):
	agvApi.task(agvId,"robot_task_goend_req",None)

def goPoint(agvId, x, y, angle):
	data = {"x": x, "y": y, "angle": angle}
	agvApi.task(agvId, "robot_task_gopoint_req", data)


def goTarget(agvId, loc,ignoreAngle=None):
	data = {"id": loc}
	if ignoreAngle is not None:
		data["ignoreAngle"] = ignoreAngle
	log.info("goTarget",data)
	agvApi.task(agvId, "robot_task_gotarget_req", data)

move=goTarget

def _load():
	try:
		file = "pgv.cfg" 
		file = os.path.abspath(os.path.dirname(__file__)) + "/" + file
		with open(file, 'r') as f:
			data = json.load(f)
			return data
	except Exception as e:
		data = {'pgv_adjust_dist': 0.05}
		return data
		

def goTargetAndDoWork(agvId, loc, operation, recognize=False,use_pgv=False, pgv_adjust_dist=False,ignoreAngle=None,pgv_type=1):
	if int(pgv_type) == 3:
		dist = _load()['pgv_adjust_dist']
		data = {"id": loc, 'operation': operation, 'recognize': recognize,'use_pgv':use_pgv, 'pgv_adjust_dist':dist}
	elif int(pgv_type)  == 4:
		data = {"id": loc, 'operation': operation, 'recognize': recognize,'use_pgv':use_pgv,'pgv_adjust_dist':0.3,'pgv_adjust_cx':-0.1}
	elif int(pgv_type)  == 1:
		data = {"id": loc, 'operation': operation, 'recognize': recognize,'use_pgv':use_pgv}
	else:
		data = {"id": loc, 'operation': operation, 'recognize': recognize,'use_pgv':use_pgv}
	if ignoreAngle is not None:
		data["ignoreAngle"] = ignoreAngle
	agvApi.task(agvId, "robot_task_gotarget_req", data)
 
  
def jackUp2(agvId):
	agvApi.other(agvId, "robot_other_jack_load_req", None)

def jackDown2(agvId):
	agvApi.other(agvId, "robot_other_jack_unload_req", None)

def jackUpLoadStatus(agvId, loc):
	# data = {"object_path":"C:/SeerRobotics/Robokit/resources/objects/shelf/s0002.shelf"}
	data = {"object_path":"shelf/s0002.shelf"}
	agvApi.conf(agvId, "robot_config_set_shelfshape_req", data)

def _jackUpSeer(agvId, loc):
	# agvApi.other(agvId, "robot_other_jack_load_req", None)
	data = {"id": loc, 'operation': 'JackLoad', 'recognize': False,'use_pgv':False}
	agvApi.task(agvId, "robot_task_gotarget_req", data)

def _jackDownSeer(agvId, loc):
	# agvApi.other(agvId, "robot_other_jack_load_req", None)
	data = {"id": loc, 'operation': 'JackUnload', 'recognize': False,'use_pgv':False}
	agvApi.task(agvId, "robot_task_gotarget_req", data)

def jackDownUnloadStatus(agvId, loc):
	# robot_config_clear_goodsshape_req
	agvApi.conf(agvId, "robot_config_clear_goodsshape_req", None)

def goFollowUwb(agvId,uwbId=''):
	data = {"uwbId": uwbId}
	agvApi.task(agvId, "robot_task_uwb_follow_req",data)
	
#def jackDownOld(agvId):
#	agvApi.other(agvId, "robot_other_jack_unload_req", None)
#
#def jackStopOld(agvId):
#	agvApi.other(agvId, "robot_other_jack_stop_req", None)


# {'DI': [{'id': 0, 'source': 'normal', 'status': False, 'valid': True}, {'id': 1, 'source': 'normal', 'status': False, 'valid': True}, {'id': 2, 'source': 'normal', 'status': False, 'valid': True}, {'id': 3, 'source': 'normal', 'status': False, 'valid': True}, {'id': 4, 'source': 'normal', 'status': False, 'valid': True}, {'id': 5, 'source': 'normal', 'status': False, 'valid': True}, {'id': 6, 'source': 'normal', 'status': False, 'valid': True}, {'id': 7, 'source': 'normal', 'status': False, 'valid': True}, {'id': 8, 'source': 'normal', 'status': False, 'valid': True}], 'DO': [{'id': 0, 'source': 'normal', 'status': True}, {'id': 1, 'source': 'normal', 'status': True}, {'id': 2, 'source': 'normal', 'status': True}, {'id': 3, 'source': 'normal', 'status': True}, {'id': 4, 'source': 'normal', 'status': True}, {'id': 5, 'source': 'normal', 'status': True}, {'id': 6, 'source': 'normal', 'status': True}, {'id': 7, 'source': 'reserve', 'status': True}, {'id': 8, 'source': 'modbus', 'status': False}, {'id': 9, 'source': 'modbus', 'status': False}, {'id': 10, 'source': 'modbus', 'status': False}, {'id': 11, 'source': 'modbus', 'status': False}, {'id': 12, 'source': 'modbus', 'status': False}, {'id': 13, 'source': 'modbus', 'status': False}, {'id': 14, 'source': 'modbus', 'status': False}, {'id': 15, 'source': 'modbus', 'status': False}, {'id': 16, 'source': 'modbus', 'status': False}, {'id': 17, 'source': 'modbus', 'status': False}, {'id': 18, 'source': 'modbus', 'status': False}, {'id': 19, 'source': 'modbus', 'status': True}], 'ret_code': 0}
def checkCfgIO(agvId):
	if _getAgvType(agvId)['jackType'].lower()=="io":
		return True
	else:
		return False

def checkCfgSeer(agvId):
	if _getAgvType(agvId)['jackType'].lower()=="seer": 
		return True
	else:
		return False


def checkIOSJackzero(agvId, direction):
	status = readIOs(agvId)
	s1 = ''
	s2 = ''
	s3 = ''
	s4 = ''
	for x in status['DO']:
		if int(x['id'])==31:
			s1 = x['status']
			
		elif int(x['id'])==32:
			s2 = x['status']

	if s1 and direction=='up':
		return False 
	elif s2 and direction=='down':
		return False
	elif s2 and direction=='up':
		return True
	elif s1 and direction=='down':
		return True 

def checkIOSRotate(agvId, target):
	status = readIOs(agvId)
	s1 = ''
	s2 = ''
	s3 = ''
	s4 = ''
	for x in status['DO']:
		if int(x['id'])==33: # 0 
			s1 = x['status']
		elif int(x['id'])==34: # 90
			s2 = x['status']
		elif int(x['id'])==35: # 180
			s3 = x['status'] 
		elif int(x['id'])==36: # 270
			s4 = x['status']
	
	if s1 and str(target)=='0':
		return False
	elif s2 and str(target)=='90':
		return False
	elif s3 and str(target)=='180':
		return False
	elif s4 and str(target)=='270':
		return False
	else:
		return True


def setOperation(agvId,id1,v1):
	# 清除动作状态位
	agvApi.other(agvId, "robot_other_setdo_req", {"id":20, "status":False})
	time.sleep(0.2)
	time.sleep(0.1)
	data1 = {"id":id1, "status":v1}
	agvApi.other(agvId, "robot_other_setdo_req", data1)
	time.sleep(0.2)
	time.sleep(0.2)
	# 设置动作状态位
	agvApi.other(agvId, "robot_other_setdo_req", {"id":20, "status":True})

def shelveUpStatus(agvId):
	s = None
	status = readIOs(agvId)
	# log.info('shelveUpStatus:', agvId, '-->', status)
	for x in status['DO']:
		if int(x['id'])==31:
			s = {'status':x['status']}
	return s

def shelveDownStatus(agvId):
	s = None
	status = readIOs(agvId)
	for x in status['DO']:
		if int(x['id'])==32:
			s = {'status':x['status']}
	return s

def typeIOinitStatus(agvId):
	s = None
	status = readIOs(agvId)
	# log.info('shelveUpStatus:', agvId, '-->', status)
	for x in status['DO']:
		if x['id'] == 30 and x["status"]==1:#IO型顶升旋转告警
			return {"status":0}
		if x['id'] == 37 and x["status"]==0:#IO型顶升旋转agv需要DO37代表初始化完成
			return {"status":0}
	return {"status": 1}


def jackUp(agvId,speed=5000,distance=60000,loc=None):
	if checkCfgIO(agvId):
		# io 
		time.sleep(0.5)
		if checkIOSJackzero(agvId, 'up'):
			setOperation(agvId,21,True)
			data = {"object_path":"shelf/s0002.shelf"}
			agvApi.conf(agvId, "robot_config_set_shelfshape_req", data)
	elif checkCfgSeer(agvId):
		# _jackUpSeer(agvId=agvId,loc=loc)
		jackUpLoadStatus(agvId, loc)
		jackUp2(agvId)
	else:
		# 常规方式
		data = {"speed": speed, "distance": distance}
		agvApi.perpherial(agvId, "robot_other_robot07", data)


def checkInitSuccess(agvId):
	if checkCfgIO(agvId):
		return typeIOinitStatus(agvId)
	elif checkCfgSeer(agvId):
		return {"status":1}
	else:
		return {"status":1}


def jackUpStatus(agvId):
	if checkCfgIO(agvId):
		# io 
		return shelveUpStatus(agvId)
	elif checkCfgSeer(agvId):
		ret = agvApi.status(agvId, "robot_status_jack_req",None)
		if ret["jack_state"]==1:
			return {"status":1}
	else:
		# 常规方式,工控机
		return agvApi.perpherial(agvId, "robot_other_robot10", None)


def jackDown(agvId,speed=5000,distance=60000,loc=None):
	if checkCfgIO(agvId):
		# io 
		time.sleep(0.5)
		if checkIOSJackzero(agvId, 'down'):
			setOperation(agvId,22,True)
			agvApi.conf(agvId, "robot_config_clear_goodsshape_req", None)
	elif checkCfgSeer(agvId):
		# _jackDownSeer(agvId=agvId,loc=loc)
		jackDown2(agvId)
		jackDownUnloadStatus(agvId,loc)
	else:
		# 常规方式
		data = {"speed": speed, "distance": distance}
		agvApi.perpherial(agvId, "robot_other_robot08", data)


def jackDownStatus(agvId):
	if checkCfgIO(agvId):
		# io 
		s = None
		status = readIOs(agvId)
		for x in status['DO']:
			if int(x['id'])==30:
				if x['status']:
					return {'isJackAlarm':x['status']} # 报警
		time.sleep(0.5)
		s = shelveUpStatus(agvId)
		if s is not None and 'status' in s and s['status']==1:
			return {'status':0}
		return shelveDownStatus(agvId)     # jackdown status
	elif checkCfgSeer(agvId):
		#  {'jack_emc': False, 'jack_enable': True, 'jack_error_code': 0, 'jack_height': 0.0, 'jack_isFull': False, 'jack_mode': False, 'jack_speed': 0, 'jack_state': 3, 'peripheral_data': [], 'ret_code': 0}
		ret = agvApi.status(agvId, "robot_status_jack_req",None)
		if ret["jack_state"]==3:
			return {"status":1}
	else:
		# 常规方式,工控机
		return agvApi.perpherial(agvId, "robot_other_robot11", None)



def jackMaxStatus(agvId):
	return agvApi.perpherial(agvId, "robot_other_robot12", None)

def jackMinStatus(agvId):
	return agvApi.perpherial(agvId, "robot_other_robot13", None)

def jackStop(agvId):
	agvApi.perpherial(agvId, "robot_other_robot09", None)

def jackDistanceStatus(agvId):
	return agvApi.perpherial(agvId, "robot_other_robot14", None)

#-rotation start-

def rotationSeer(agvId,angle=90,direction=0):
	data = {"robot_spin_angle": angle, "spin_direction": direction}
	agvApi.task(agvId, "robot_task_spin_req", data)
 
def rotationLeft(agvId,speed=30,target=90):
	if checkCfgIO(agvId):
		# io 
		if target==0:
			id_ = 23
		elif target==90:
			id_ = 24
		elif target==180:
			id_ = 25
		elif target==270:
			id_ = 26
		time.sleep(0.5)
		if checkIOSRotate(agvId, target):
			setOperation(agvId,id_, True)
	elif checkCfgSeer(agvId):
		target = (math.pi * target/180)
		rotationSeer(agvId,angle=target,direction=-1)
		# rotationSeer(agvId,angle=target, direction=0)
	else:
		# 常规方式
		data = {"speed": speed, "target": target}
		agvApi.perpherial(agvId, "robot_other_robot16", data)


def rotationRight(agvId,speed=30,target=90):
	if checkCfgIO(agvId):
		# io 
		if target==0:
			id_ = 23
		elif target==90:
			id_ = 24
		elif target==180:
			id_ = 25
		elif target==270:
			id_ = 26
		time.sleep(0.5)
		if checkIOSRotate(agvId, target):
			setOperation(agvId,id_,True)
	elif checkCfgSeer(agvId):
		target = (math.pi * target/180)
		rotationSeer(agvId,angle=target,direction=1)
		# rotationSeer(agvId,angle=target,direction=0)
	else:
		# 常规方式
		data = {"speed": speed, "target": target}
		agvApi.perpherial(agvId, "robot_other_robot17", data)


def rotationLeftStatus(agvId, target):
	if checkCfgIO(agvId):
		# io 
		if target==0:
			i = 33
		elif target==90:
			i = 34
		elif target==180:
			i = 35
		elif target==270:
			i = 36

		s = None
		status = readIOs(agvId)
		for x in status['DO']:
			if int(x['id'])==i:
				s = {'status':x['status']}
		return s
	
	else:
		# 常规方式,工控机
		data = {"target": target}
		return agvApi.perpherial(agvId, "robot_other_robot24", data)


def rotationRightStatus(agvId, target):
	if checkCfgIO(agvId):
		# io 
		if target==0:
			i = 33
		elif target==90:
			i = 34
		elif target==180:
			i = 35
		elif target==270:
			i = 36

		s = None
		status = readIOs(agvId)
		for x in status['DO']:
			if int(x['id'])==i:
				s = {'status':x['status']}
		return s

	else:
		# 常规方式,工控机
		data = {"target": target}
		return agvApi.perpherial(agvId, "robot_other_robot25", data)



def rotationDistanceStatus(agvId):
	if checkCfgIO(agvId):
		# io 
		s = None
		status = readIOs(agvId)
		# log.info('rotationDistanceStatus:', agvId, '-->', status)
		for x in status['DO']:
			if int(x['id'])==30:
				s = {'isRotationALarm':x['status']}
		return s
	else:
		# 常规方式,工控机
		return agvApi.perpherial(agvId, "robot_other_robot19", None)
	
 
def rotationReset(agvId):
	if checkCfgIO(agvId):
		# io 
		time.sleep(0.5)
		setOperation(agvId,27,True)
	else:
		# 常规方式,工控机
		return agvApi.perpherial(agvId, "robot_other_robot27", None)

def rotationResetStatus(agvId):
	if checkCfgIO(agvId):
		# io 
		s = None
		status = readIOs(agvId)
		for x in status['DO']:
			if int(x['id'])==37:
				s = {'status':x['status']}
		return s

	else:
		# 常规方式,工控机
		return agvApi.perpherial(agvId, "robot_other_robot28", None)
	
def rotationClear(agvId):
	if checkCfgIO(agvId):
		# io 
		time.sleep(1)
		if checkIOSRotate(agvId,0):
			setOperation(agvId,23,True)
	else:
		# 常规方式,工控机
		return agvApi.perpherial(agvId, "robot_other_robot32", None)
	
def rotationClearStatus(agvId):
	if checkCfgIO(agvId):
		# io 
		s = None
		status = readIOs(agvId)
		for x in status['DO']:
			if int(x['id'])==33:
				s = {'status':x['status']}
		return s

	else:
		# 常规方式,工控机
		return agvApi.perpherial(agvId, "robot_other_robot33", None)


def rotationStop(agvId):
	agvApi.perpherial(agvId, "robot_other_robot18", None)

#-rotation end-

# -pgv start-

def statusPgv(agvId):
	s = agvApi.status(agvId, "robot_status_pgv_req", None)
	log.info("agvApi.statusPgv",s)
	return s



# -pgv end-


# -audio start-

def playAudio(agvId, name, loop):
	data = {"name": name, "loop": loop}
	agvApi.other(agvId, "robot_other_speaker_req", data)

def pauseAudio(agvId):
	agvApi.other(agvId, "robot_other_pause_audio_req", None)

def resumeAudio(agvId):
	agvApi.other(agvId, "robot_other_resume_audio_req", None)

def stopAudio(agvId):
	agvApi.other(agvId, "robot_other_stop_audio_req", None)

def uploadAudio(agvId):
	agvApi.other(agvId, "robot_other_uploadaudio_req", None)

def downloadAudio(agvId,name):
	data = {"name": name}
	return agvApi.other(agvId, "robot_other_downloadaudio_req", data)

def lookupAudio(agvId):
	return agvApi.other(agvId, "robot_other_audio_list_req", None)


# -audio end-

def jackDeviceInfo(agvId):
	return agvApi.perpherial(agvId, "robot_other_robot26", None)


def ironArmLoad(agvId):
	agvApi.perpherial(agvId, "robot_other_robot20", None)


def ironArmLoadStatus(agvId):
	return agvApi.perpherial(agvId, "robot_other_robot22", None)


def motion(agvId, vx, vy, w):
	data = {"vx": vx, "vy": vy, "w": w}
	agvApi.ctrl(agvId, "robot_control_motion_req", data)


def stop(agvId):
	agvApi.ctrl(agvId, "robot_control_stop_req", None)


def deleteMap(agvId,mapName):
	data = {"map_name": mapName}
	agvApi.conf(agvId, "robot_config_removemap_req", data)


def downloadMap(agvId, mapName):
	data={"map_name":mapName}
	result= agvApi.conf(agvId,"robot_config_downloadmap_req",data)
	return result
 
def uploadMap(agvId,data):
	agvApi.conf(agvId,"robot_config_uploadmap_req",data)
	
def requireControl(agvId):
	return agvApi.conf(agvId, "robot_config_require_req", None)

def releaseControl(agvId):
	return agvApi.conf(agvId, "robot_config_release_req", None)

def getMapList(agvId):
	result = agvApi.status(agvId,"robot_status_map_req",None)
	return result


def switchMap(agvId, mapName):
	data = {"map_name": mapName}
	agvApi.ctrl(agvId, "robot_control_loadmap_req", data)


def clampStatus(agvId, direction):
	Data = {"direction": direction}
	return agvApi.perpherial(agvId, "robot_other_robot179", Data)


def clampOpen(agvId, direction):
	Data = {"direction": direction}
	return agvApi.perpherial(agvId, "robot_other_robot180", Data)


def clampClose(agvId, direction):
	Data = {"direction": direction}
	return agvApi.perpherial(agvId, "robot_other_robot181", Data)


def finishButtonStatus(agvId):
	return agvApi.perpherial(agvId, "robot_other_robot182", None)




def rollerSetUnit(agvId, unitId):
	Data = {"unit": unitId}
	return agvApi.perpherial(agvId, "robot_other_robot170", Data)


def rollerBackLoad(agvId):
	return agvApi.perpherial(agvId, "robot_other_roller_back_load_req", None)


def rollerBackUnload(agvId):
	return agvApi.perpherial(agvId, "robot_other_roller_back_unload_req", None)


def rollerFrontLoad(agvId):
	return agvApi.perpherial(agvId, "robot_other_roller_front_load_req", None)


def rollerFrontUnload(agvId):
	return agvApi.perpherial(agvId, "robot_other_roller_front_unload_req", None)


def rollerLoadStatus(agvId, unitId):
	Data = {"unit": unitId}
	return agvApi.perpherial(agvId, "robot_other_robot175", Data)

def rollerUnloadStatus(agvId, unitId):
	Data = {"unit": unitId}
	return agvApi.perpherial(agvId, "robot_other_robot176", Data)

def unitStatus(agvId,unitId):
	Data = {"unit": unitId}
	return agvApi.perpherial(agvId, "robot_other_robot177", Data)

def rollerStop(agvId):
	return agvApi.perpherial(agvId, "robot_other_roller_stop_req", None)

def rollerReset(agvId):
	return agvApi.perpherial(agvId, "robot_other_roller_reset_req", None)

def rollerDeviceInfo(agvId):
	return agvApi.perpherial(agvId, "robot_other_robot178", None)



#读输入IO列表 [True,False,....]
def readIO(agvId):
	data= agvApi.status(agvId,"robot_status_io_res",None)
	for d in data["DI_valid"]:
		assert d #确保都是valid
	assert len(data["DI"]) >= 16 #确保至少16个IO
	return data["DI"]

def checkEmergency(agvId):
	data = agvApi.status(agvId, "robot_status__emergency_req", None)
	return data

def readIOs(agvId):
	data = agvApi.status(agvId, "robot_status_io_req", None)
	return data

def setDOs(agvId,data):
	return  agvApi.other(agvId,"robot_other_setdo_reqs",data)



#清除输出IO 
def clearIO(agvId):
	data= agvApi.status(agvId,"robot_status_io_res",None)
	for i,s in enumerate(data["DO"]):
		if not s:
			continue
		writeIO(agvId,i,False)


#设置写IO 
#id		:	number DO的id号, 从0开始 
#status	: 	boolean true为高电平,false为低电
def writeIO(agvId,id,status):
	# 从零开始
	data={"id":id,"status":status}
	agvApi.other(agvId,"robot_other_setdo_req",data)

#针对seer-None，自研协议param{"updateClock": True/None} 时钟同步
def readStatus1(agvId,param=None):
	return agvApi.status(agvId,"robot_status_all1_req",param)
  
def setDI(agvId,id,valid):
	data = {"id":id, "valid":valid}
	return agvApi.conf(agvId,'robot_config_DI_req',data)

if __name__ == '__main__':
	import counter
	c = counter.counter()
	for i in range(10):
		move("AGV01","LM6")
	for i in range(0, 100):
		s = readStatus1("AGV01")
		c.check()






