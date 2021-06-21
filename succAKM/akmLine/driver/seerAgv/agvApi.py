# coding=utf-8
# ycat			2018-8-2	  create
# seerAgv的API封装 
import sys, os
import threading
import time
import socket
import setup 

if __name__ == '__main__':
	setup.setCurPath(__file__)
import json
import buffer
import log
import local
import tcpSocketLong
import lock as lockImp
import driver.seerAgv.agvServer as agvServer

g_cmd = {
	"robot_status_info_req": 1000,
	"robot_status_run_req": 1002,
	"robot_status_mode_req": 1003,
	"robot_status_loc_req": 1004,
	"robot_status_speed_req": 1005,
	"robot_status_area_req": 1011,
	"robot_status__emergency_req": 1012,
	"robot_status_io_req": 1013,
	"robot_status_task_req": 1020,
	"robot_status_all1_req": 1100,
	"robot_status_alarm_res": 1050,
	"robot_status_station_res": 1301,
	"robot_status_init_req": 1111,
	"robot_status_map_req": 1300,
	"robot_status_pgv_req": 1017,

	"robot_control_reloc_req": 2002,
	"robot_control_comfirmloc_req": 2003,
	"robot_control_motion_req": 2010,
	"robot_control_loadmap_req": 2022,

	"robot_task_cancel_req": 3003,
	"robot_task_gopoint_req": 3050,
	"robot_task_gotarget_req": 3051,
	"robot_task_translate_req": 3055,
	"robot_task_turn_req": 3056,
	"robot_task_spin_req":3057,
	"robot_task_gointo_shelf_req": 3063,
	"robot_task_uwb_follow_req": 3071,

	"robot_other_setdo_req": 6001,
	"robot_other_setdo_reqs": 6002,
	"robot_other_speaker_req": 6000,
	"robot_other_pause_audio_req": 6010,
	"robot_other_resume_audio_req": 6011,
	"robot_other_stop_audio_req": 6012,
	"robot_other_uploadaudio_req": 6030,
	"robot_other_downloadaudio_req": 6031,
	"robot_other_audio_list_req": 6033,


	"robot_other_wait_req": 6600,
	"robot_other_robot01": 6601,
	"robot_other_robot02": 6602,
	"robot_other_robot03": 6603,
	"robot_other_robot04": 6604,

	"robot_other_jack_load_req": 6070,
	"robot_other_jack_unload_req": 6071,
	"robot_other_jack_stop_req": 6072,

	"robot_other_robot07": 6080,	#顶升
	"robot_other_robot08": 6081,	#下降
	"robot_other_robot09": 6082,	#停止
	"robot_other_robot10": 6060,	# 上到位状态查询
	"robot_other_robot11": 6061,	# 下到位状态查询

	"robot_other_robot12": 6062,	# 上限位状态查询
	"robot_other_robot13": 6063,	# 下限位状态查询
	"robot_other_robot14": 6064,	# 顶升距离查询

	"robot_other_robot16": 6066,	# 控制左旋转命令
	"robot_other_robot17": 6067,	# 控制右旋转命令
	"robot_other_robot18": 6068,	# 旋转运动停止命令
	"robot_other_robot19": 6069,	# 旋转运动距离查询
	"robot_other_robot27": 6065,	# 旋转归中命令
	"robot_other_robot28": 6075,	# 旋转归中状态查询
	"robot_other_robot32": 6090,	# 旋转清0
	"robot_other_robot33": 6091,	# 旋转清0查询

	"robot_other_robot20": 6083,	# 机械臂上料
	"robot_other_robot21": 6084,	# 机械臂下料
	"robot_other_robot22": 6085,	# 机械臂上料状态查询
	"robot_other_robot23": 6086,	# 机械臂下料状态查询

	"robot_other_robot24": 6072,  # 机械臂上料状态查询
	"robot_other_robot25": 6073,  # 机械臂下料状态查询
	"robot_other_robot26": 6074,  # 机械臂下料状态查询

	"robot_config_downloadmap_req": 4011,
	"robot_config_uploadmap_req": 4010,
	"robot_config_removemap_req": 4012,
	"robot_config_require_req": 4001,
	"robot_config_release_req": 4002,


	"taskchain_wait_countdown": 10010,
	"taskchain_wait_other1": 10011,
	"taskchain_wait_other2": 10012,


	"robot_other_roller_front_roll_req": 6151,  # 预留6，
	"robot_other_roller_back_roll_req": 6152,  # 预留6，
	"robot_other_roller_left_roll_req": 6153,  # 预留6，
	"robot_other_roller_right_roll_req": 6154,  # 预留6，
	"robot_other_roller_front_load_req": 6155,  # 辊筒(皮带)前上料，
	"robot_other_roller_front_unload_req": 6156,  # 辊筒(皮带)前下料，
	"robot_other_roller_front_pre_load_req": 6157,  # 预留6，
	"robot_other_roller_back_load_req": 6158,  # 预留6，
	"robot_other_roller_back_unload_req": 6159,  # 预留6，
	"robot_other_roller_back_pre_load_req": 6160,  # 预留6，
	"robot_other_roller_left_load_req": 6161,  # 预留6，
	"robot_other_roller_left_unload_req": 6162,  # 预留6，
	"robot_other_roller_right_load_req": 6163,  # 预留6，
	"robot_other_roller_right_unload_req": 6164,  # 预留6，
	"robot_other_roller_left_pre_load_req": 6165,  # 预留6，
	"robot_other_roller_right_pre_load_req": 6166,  # 预留6，
	"robot_other_roller_stop_req": 6167,  # 停止，
	"robot_other_roller_reset_req": 6178,  # 停止，
	"robot_other_roller_left_right_inverse_req": 6168,  # 辊筒(皮带)左右反向，
	"robot_other_roller_front_back_inverse_req": 6169,  # 辊筒(皮带)前后反向，

	"robot_other_robot170": 6170,  # 层数设定
	"robot_other_robot175": 6175,  # 辊筒(皮带)前上料查询
	"robot_other_robot176": 6176,  # 辊筒(皮带)前下料查询
	"robot_other_robot177": 6177,  # 指定的层数是否有料查询
	"robot_other_robot178": 6178,  # 辊筒(皮带)信息

	"robot_other_robot179": 6179,  # 开关夹信息
	"robot_other_robot180": 6180,  # 开关夹打开
	"robot_other_robot181": 6181,  # 开关夹关闭
	"robot_other_robot182": 6182,  # 上下料完成按钮状态查询
	
	"robot_config_clear_goodsshape_req": 4356, # 清除货架描述文件
	"robot_config_set_shelfshape_req":4357,  # 设置货架描述文件
	"robot_config_DI_req": 4140,  # 配置 DI
	"robot_other_getdi_req": 6021,  # 获取虚拟 DI 状态
	"robot_other_setdi_req": 6020, # 设置虚拟 DI
	"robot_other_setdo_req": 6001, # 设置 DO

	"robot_status_jack_req": 1027, # 查询顶升机构状态
}

API_PORT_STATE = 19204
API_PORT_CTRL = 19205
API_PORT_TASK = 19206
API_PORT_CONFIG = 19207
API_PORT_KERNEL = 19208
API_PORT_OTHER = 19210
API_PORT_PERPHERIAL = 19214

#主动检测每个端口
def checkLink(agvId):
	ip = g_agvList[agvId]["ip"]
	ports = [API_PORT_STATE, API_PORT_CTRL, API_PORT_TASK, API_PORT_CONFIG,API_PORT_KERNEL, API_PORT_OTHER]
	for p in ports:
		pingType,lockType = agvServer.g_pingType[p]
		lock = _getLock(agvId, lockType)
		lockImp.acquire(lock)
		try:
			if _getClient(agvId,ip,p) is None:
				log.info(agvId,"checkLink failed",ip,p)
				return False
		finally:
			lockImp.release(lock)
	return True


# 机器人状态 API
def ctrl(agvId, type, data):
	return _handle(agvId, API_PORT_CTRL, type, data, "lock_ctrl")


# 机器人控制 API
def status(agvId, type, data):
	return _handle(agvId, API_PORT_STATE, type, data, "lock_status")


# 机器人任务 API
def task(agvId, type, data):
	for i in range(5):
		try:
			ret = _handle(agvId, API_PORT_TASK, type, data, "lock_task")
			return ret
		except Exception as e:
			log.exception("agvApi send task, agvId="+agvId,e)
			if i == 4:
				raise
		time.sleep(1)
		
 
# 机器人配置 API
def conf(agvId, type, data):
	return _handle(agvId, API_PORT_CONFIG, type, data, "lock_conf")


# 机器人核心 API
def core(agvId, type, data):
	return _handle(agvId, API_PORT_KERNEL, type, data, "lock_core")


# 其他API
def other(agvId, type, data):
	return _handle(agvId, API_PORT_OTHER, type, data, "lock_other")

#自研API
def perpherial(agvId, type, data):
	for i in range(5):
		try:
			ret = _handle(agvId, API_PORT_PERPHERIAL, type, data, "lock_perpherial")
			return ret
		except Exception as e:
			log.exception("agvApi send custom, agvId="+agvId,e)
			if i == 4:
				raise 
		time.sleep(1)
	
def getAgvInfo(agvId):
	global g_agvList
	return g_agvList[agvId]


def _handle(agvId, port, type, data, lockKey):
	global g_cmd
	typeId = type
	if isinstance(type, str):
		typeId = g_cmd[type]
	lock = _getLock(agvId, lockKey)
	try:
		lockImp.acquire(lock)
		result = _request(agvId, port, typeId, data)
		return result
	finally:
		lockImp.release(lock)


def _loadAgvList():
	proName = local.get("project","name") 
	file = "/../../agvCtrl/projects/"+proName+"/" + local.get("project","agvcfg")  
	with open(os.path.abspath(os.path.dirname(__file__) + file), 'r') as f:		
		agvList = {}
		aa = json.load(f)
		for a in aa:
			if aa[a]["enable"].lower() == "false":
				continue
			agvList[a] = aa[a]
		return agvList


g_agvList = _loadAgvList()
g_sn = -1

def _getLock(agvId, lockKey):
	global g_agvList
	if lockKey not in g_agvList[agvId]:
		g_agvList[agvId][lockKey] = lockImp.create("agv."+agvId+"."+lockKey)
	return g_agvList[agvId][lockKey]


def _request(agvId, port, type, data):
	if port == API_PORT_PERPHERIAL and "perpherialIP" in g_agvList[agvId]:
		ip = g_agvList[agvId]["perpherialIP"]
	else:
		ip = g_agvList[agvId]["ip"]
	# log.debug("send type " + str(type) + " " + agvId)
	buf = getSendingBuffer(agvId, data, type)
	# 长连接
	result = GetDataLong(agvId, buf, ip, port, type)
	# log.debug("read type " + str(type) + " " + agvId)
	return result
 
def GetDataLong(agvId, buf, ip, port, type):
	_send(agvId,ip, port, buf.buf)
	while True:
		while True:
			headData = _recv(agvId,ip, port, 1)
			if headData[0] != 0x5A:
				continue
			headData = _recv(agvId,ip, port, 1)
			if headData[0] == 0x01:
				break
				
		headData = _recv(agvId,ip, port, 14) 
		bodylen,retType = getDataLen(agvId, headData, ip ,port, buf.buf) 
		if bodylen == 0:
			return {}
		recData = _recv(agvId,ip, port, bodylen) 
		if not isClient(agvId) and str(retType)[1:] == str(agvServer.g_pingType[port][0]):
			agvServer.updateClient(agvId, ip, port)
			continue
		inBuf = buffer.inBuffer(recData)
		recJsonData = inBuf.getStr(inBuf.remainLen)#.replace("'", "\"")
		obj = json.loads(recJsonData)
		result= _checkError(agvId, type, obj) 
		if not isClient(agvId) and port == 19204:
			pingBuf = getSendingBuffer(agvId,None,agvServer.g_pingType[port][0])
			_send(agvId,ip,port,pingBuf.buf)
		return result 

def getSendingBuffer(agvId, data, type):
	def _getSn():
		global g_sn
		g_sn += 1
		if g_sn >= 65535:
			g_sn = 0
		return g_sn

	jsonData = ""
	if data:
		jsonData = json.dumps(data, separators=(',', ':'))
	buf = buffer.outBuffer()
	buf.setBytes(b"\x5A\x01")
	sn = _getSn()
	buf.setUInt16(sn)
	buf.setUInt32(len(jsonData))
	buf.setUInt16(type)
	buf.setBytes([0x0] * 6)
	buf.setStr(jsonData)
	# if type != 1100:
	# 	print("_request type " + str(type) + " " + agvId + " " + jsonData)
	return buf


def getDataLen(agvId, recData, ip ,port, raw):
	if recData is None:
		log.error(agvId, "agv head is none")
		raise IOError("AGV协议头为空")
	inBuf = buffer.inBuffer(recData)  
	sn= inBuf.getUInt16()
	len= inBuf.getUInt32() 
	retType = inBuf.getUInt16()
	if retType >= 60000:
		log.error(agvId, "decode error:", retType)
		raise IOError("AGV协议返回错误码" + str(retType)) 
	return len,retType


def _checkError(agvId, type, data):
	if "ret_code" not in data:
		return data
	code = data["ret_code"]
	if code == 0:
		return data
	msg = ""
	if "err_msg" in data:
		msg = data["err_msg"]
	raise IOError(agvId + "执行" + str(type) + "错误" + ",code=" + str(code) + ",msg=" + msg)

def isClient(agvId):
	global g_agvList
	if agvId in g_agvList:
		if "tcpType" in g_agvList[agvId]:
			return g_agvList[agvId]["tcpType"] == "client"
	return True
	
def _getClient(agvId,ip,port):
	if isClient(agvId):
		return tcpSocketLong._getClient(agvId,ip,port)
	return agvServer.getClient(agvId,ip, port)
	
def _send(agvId,ip, port, buf):
	if isClient(agvId):
		return tcpSocketLong.send(agvId,ip, port, buf)
	return agvServer.send(agvId,ip, port, buf)

def _recv(agvId,ip, port, len):
	if isClient(agvId):
		return tcpSocketLong.recv(agvId,ip, port, len)
	return agvServer.recv(agvId,ip, port, len)

def _checkClient():
	while True:
		for agvId in g_agvList:
			if isClient(a):
				continue
			for port in agvServer.g_pingType:
				if port == 19204: 
					continue
				pingType,lockType = agvServer.g_pingType[port]
				client = agvServer.getClient(agvId,'', port)
				if not client:
					continue
				lock = _getLock(agvId, lockType)
				try:
					lockImp.acquire(lock)
					headData = _recv(agvId,'', port, 2)
					if headData is None or headData[0] != 0x5A or headData[1] != 0x01:
						continue
					headData = _recv(agvId,'', port, 14)
					bodylen,retType = getDataLen('', headData, '' ,port, '') 
					if bodylen == 0:
						continue
					recData = _recv(agvId,'', port, bodylen) 
					if str(retType)[1:] == str(pingType):
						pingBuf = getSendingBuffer(agvId,None,pingType)
						agvServer.updateClient(agvId, '', port)
						_send(agvId,'',port,pingBuf.buf)
						continue
				except socket.timeout as e:
					# log.exception("%s %s wait connecting error: "%(agvId,port),e)
					# agvServer.delClient(agvId,'', port)
					# time.sleep(2)
					continue
				except Exception as e:
					log.exception("%s %s wait connecting error: "%(agvId,port),e)
					agvServer.delClient(agvId,'', port)
					# time.sleep(2)
					continue
				finally:
					lockImp.release(lock)
					# time.sleep(2)
		# time.sleep(5)
		continue
	
for a in g_agvList:
	if not isClient(a):
		agvServer.startServer()
		# log.info("startServerstartServerstartServer")
		r_thread = threading.Thread(target=_checkClient)
		r_thread.start()
		break
################## unit test ##################
def test_request():
	import utility
	import socket
	import threading, time
	global g_sn
	g_sn = 0
	# 这例子的type收发不一样的
	d22 = b"\x5A\x01\x00\x01\x00\x00\x00\x3C\x2A\xFC\x00\x00\x00\x00\x00\x00\x7B\x22\x72\x65\x74\x5F\x63\x6F\x64\x65\x22\x3A\x30\x2C\x22\x78\x22\x3A\x36\x2E\x30\x2C\x22\x79\x22\x3A\x32\x2E\x30\x2C\x22\x61\x6E\x67\x6C\x65\x22\x3A\x31\x2E\x35\x37\x2C\x22\x63\x6F\x6E\x66\x69\x64\x65\x6E\x63\x65\x22\x3A\x30\x2E\x39\x7D"

	def runFunc(server):
		client, address = server.accept()
		data = client.recv(4096)
		d = [0x5A, 0x01, 0x00, 0x01, 0x00, 0x00, 0x00, 0x1C, 0x07, 0xD2, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x7B, 0x22,
			 0x78, 0x22, 0x3A, 0x31, 0x30, 0x2E, 0x30, 0x2C, 0x22, 0x79, 0x22, 0x3A, 0x33, 0x2E, 0x30, 0x2C, 0x22, 0x61,
			 0x6E, 0x67, 0x6C, 0x65, 0x22, 0x3A, 0x30, 0x7D]
		obj = json.loads(
			b"\x7B\x22\x78\x22\x3A\x31\x30\x2E\x30\x2C\x22\x61\x6E\x67\x6C\x65\x22\x3A\x30\x2C\x22\x79\x22\x3A\x33\x2E\x30\x7D".decode(
				"utf-8"))
		try:
			assert len(data) == len(d)
			assert obj == {"x": 10.0, "y": 3.0, "angle": 0}
			client.send(d22)
		except Exception as e:
			print("agvApi",e)
			raise e
		time.sleep(0.1)

	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.bind(('192.168.31.111', 19205))
	server.listen(19205)
	t = threading.Thread(target=runFunc, args=(server,))
	t.start()
	time.sleep(2)
	d = {"x": 10.0, "y": 3.0, "angle": 0}
	global g_agvList
	g_agvList["AGVTEST"] = {"ip": "192.168.31.196"}
	d2 = _request("AGVTEST", 19205, 2002, d)
	obj = {"ret_code": 0,
		   "x": 6.0,
		   "y": 2.0,
		   "angle": 1.57,
		   "confidence": 0.9}
	assert d2 == obj


if __name__ == '__main__':
	# import utility
	# utility.run_tests(__file__)
	# test_request()
	while True:
		print (checkLink("AGV_wanji"))
		time.sleep(2)
