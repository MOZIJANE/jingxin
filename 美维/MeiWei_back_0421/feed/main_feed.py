import os
import sys
import bottle
import datetime
import setup
import json

if __name__ == '__main__':
	setup.setCurPath(__file__)

import log
import meta as m
import webutility
import scadaUtility
# import lock as lockImp
import runTasks01
# import feedMgr
# import agvCtrl.mapMgr
import socket
import local
import threading
import tcpSocket
# import taskMgr
# import mytimer
import random
from utils import objectUtil,toolsUtil

g_lock = threading.RLock()

ip = '0.0.0.0'
# ip = '192.168.47.52'
port = 10001#local.getint("button", "port", 10001)
g_lock = threading.RLock()
#prefixBtn = objectUtil.getBtnPrefix()


def _loadButtonList():
	file = "/buttons.json"
	with open(os.path.abspath(os.path.dirname(__file__)) + file, 'r') as f:
		buttonList = json.load(f)
		ret = {}
		for buttonId in buttonList:
			if buttonList[buttonId]["enable"].lower() == "false":
				continue
			loc = buttonList[buttonId]["loc"]
			map = buttonList[buttonId]["map"]

			# remoteio = remoteioInfo(remoteioId, ip, port)
			ret[buttonId] = {"loc":loc, "map": map}
		return ret


def checkPosition():
	'''为了防止一个按钮控制多个任务这种场景设计的，增加一个临近点判断，只有车在放行工位才修改按钮值'''
	#同一个时间只会有一个车在放行工位
	pass

def checkAndSetBtnValues(btnKey,machineId):
	'''获取任务队列中的btn类型任务并且设置相应的按钮值为1'''
	tasksIdDict = findBtnTask()
	if tasksIdDict is not False:
		tasksId = tasksIdDict.keys()
		tasks = objectUtil.getG_taskMgr()
		for i in tasksId:
			task = tasks.getTask(i)
			#精确判断可以取具体的step再写,理论上到位了才设置才对，后期加防乱按
			if task.taskStep not in ["finish","waiting"]: #等待中的车，完成了任务的车排除
				setBtnValueInTask(task,btnKey,machineId)
			else:
				continue
	else:
		# log.info("没有相应的按钮任务，请勿随意点击按钮：",btnKey,machineId,toolsUtil.getCurTime())
		pass
#btnKey 输入应为0,1,2（代表三个位置的按钮）
def setBtnValueInTask(task,btnKey,machineId):
	'''设置在按钮任务中的放行位置的按钮值'''
	passPoint(str(btnKey))      #一句输出
	task.setBtnVluesById(machineId,btnKey)        #设置任务对象的按钮值，真正起放行作用的地方

def getTasks():
	'''从任务字典中获取任务'''
	return objectUtil.getG_taskMgr().tasks

def findBtnTask():
	'''迭代查找是否存在btn任务'''
	tasks = getTasks()
	log.info("*********************任务列表",tasks)
	if not bool(tasks):
		log.info("*********************任务列表为空！！！！！！！！！！！！", tasks)
		return False  # 任务列表为空
	taskDict = {}  # 为后续留点操作的余地所以用dict，不想用就改成list
	hasBtnTask = False
	for task in tasks.values():  # 很多任务的时候可能耗时会很长，这个任务Mgr如果定时清理过就没问题了
		log.info("****************任务*********：",task)
		log.info("****************任务类型*********：",type(task))
		if task.btTag is True:
			taskDict[task.taskId] = True
			if hasBtnTask is False:
				hasBtnTask = True
		else:
			log.info("任务标记",task.btTag)
			continue
	if hasBtnTask is False:
		return False
	else:
		return taskDict


# return type,map,loc,agv
# def getButtonInfo(devID, keyID=0):
# 	'''当前文件夹读取local.cfg的信息'''
# 	devID = "button_" + devID
# 	map = local.get(devID, "map")
# 	agvId = local.get(devID, "agv")
# 	type, loc = local.get(devID, keyID).split(",")
# 	log.info("信息*********map:", map, "agvId", agvId, "tyepe:", type, "loc", loc)
# 	return type, map, loc, agvId


def response(ser, client):
	'''serverSocet的写线程，每个设备配一个。如果太多就改select/epoll'''
	r_thread = threading.Thread(target=_handle, args=(ser, client,))
	r_thread.start()
	# log.info("**************回复线程启动**************")
#

def _handle(ser, client):
	'''处理按下按钮的地方'''
	while True:
		try:
			data = client.recv(6)
			devID = str(data[1])
			# log.info(devID)
			# staticDevID = "1"     #测试用
			# btnKey = data[-2]
			keyID = str(data[-2]) #旧，单个按钮盒
			# 松开按钮发过来的数据还每个按钮松开都发一样的- -！先归类为脏数据，直接扔掉
			if keyID == "0":
				# log.info("无效数据！按完后二次发过来的")
				continue
			# log.info("按钮任务状态：", objectUtil.getButtonTask())
			# 重复按发任务的按钮
			# if objectUtil.getButtonTask() and keyID == "4":
			# 	log.info("已存在一个按钮任务！勿重复发送任务")
			# 	continue
			buttonInfo = _loadButtonList()
			log.info(buttonInfo)
			# if devID is None or keyID is None:
			if devID not in buttonInfo or keyID is None:
				log.info("****没有这个盒子****")
				continue
			# log.info("****************接受到的数据**************：", "staticDevID:",staticDevID,
			#          "devID:", str(devID), "keyID:", str(keyID))

			# if keyID == "4":
			# 	#objectUtil.setSeatsByBt(keyID)
			# 	checkAndSetBtnValues(btnKey-1,prefixBtn + staticDevID)
			if keyID == "3":
				#objectUtil.setSeatsByBt(keyID)
				objectUtil.setAllownext(devID=devID, sig=2)
				# checkAndSetBtnValues(btnKey-1, prefixBtn + staticDevID)
			elif keyID == "2":
				# pass
				objectUtil.setAllownext(devID=devID, sig=1)
				# checkAndSetBtnValues(btnKey-1, prefixBtn + staticDevID)
			elif keyID == "1":  # 假设是这个添加任务
				log.info("测试添加任务，起点和目的地，固化在下面的方法中")
				target = buttonInfo[devID]['loc']
				if objectUtil.g_allowNext() is None:
					addTaskByButton(devID=devID, target=target)
				else:
					#讲target和devID存入一个全局变量，然后在scadaTaskBean中直接进行移动操作
					log.info('有任务还没有完成')
				objectUtil.setAllownext(devID=devID, sig=0)
				# tmp = random.randint(1, 10)
				# if tmp <= 5:
				# 	log.info("*****load 任务*****", tmp)
				# 	addTaskByButton()
				# else:
				# 	log.info("*****unload 任务*****", tmp)
				# 	addTaskByButton(taskKind="unload")


			# getButtonInfo(devID, keyID)

		# addTask(str(devID), str(keyID))
		except socket.timeout:
			# log.exception(client.desc + " time out", client)
			ser.closeClient(client)
			return
		except socket.error:
			log.exception(client.desc + " socket error", client)
			ser.closeClient(client)
			return
		except Exception as e:
			log.exception(client.desc + " error: ", e)
			ser.closeClient(client)
			return





def main():
	log.info("IP:", ip, "port:", port)
	buttonSer = tcpSocket.server(ip, port, connectLen=200, acceptCallback=response)
	buttonSer.start()


# g_locInfo ={}
# g_taskMgr = {}
# g_taskMgr["6"]={"1": None,"2": None,"3": None,"4": None}


def passPoint(keyID):
	log.info(keyID, "号工位放行")


# target 和 source 写到配置文件里面去
def addTaskByButton(devID, target, payloadId=None, priority=1, taskKind="unload"):  #unload下料
	btTag = True
	taskKind = taskKind
	source = 'Loc8' #写死了上料的地方
	target = str(target)
	taskId = runTasks01.addTaskByButton(source, target, payloadId, priority, btTag, taskKind, devID=devID)
	if taskId != None:
		objectUtil.setButtonTask(True)
		print("添加一个按钮任务，状态为：", objectUtil.getButtonTask())



# return type,map,loc,agv
# def getButtonInfo(devID,keyID):
# 	type,source,target = local.get(devID,keyID).split(",")
# 	return type,source,target

# @lockImp.lock(g_lock)
# @mytimer.interval(3000)
# def checktask():
# 	for devID in g_taskMgr:
# 		for keyID in g_taskMgr[devID]:
# 			id = g_taskMgr[devID][keyID]
# 			if id:
# 				ret = taskMgr.get(id)
# 				if ret is None or ret["status"] in ["success", "fail"]:
# 					g_taskMgr[devID][keyID] = None


# class mapSel(m.customSelect):
# 	def __init__(self):
# 		m.customSelect.__init__(self)
#
# 	def items(self, parentId):
# 		mapList = agvCtrl.mapMgr.getMapList()
# 		return [{"value": mapList[i]["id"], "label": mapList[i]["id"]} for i in range(len(mapList))]


# @m.table("u_loc_info", "工位信息", )
# @m.field(id="_id", name="工位", unique=True, type=str, rules=[m.require()])
# @m.field(id="floorId", name="地图", type=str, editCtrl=mapSel(), rules=[m.require()])
# @m.field(id="location", name="点位", type=str, rules=[m.require()])
# @m.field(id="location", name="前置点", type=str, rules=[m.require()])
# @m.field(id="p_direction", name="方向", type=float, rules=[m.require()])
# class seatManager(m.manager):
# 	def __init__(self):
# 		m.manager.__init__(self)


#
# @scadaUtility.post('/api/agv/feed')
# def urlFeed():
# 	proName = local.get("project","name")
# 	if proName=='hucais':
# 		param = {
# 			"source": webutility.get_param("source"),
# 			"target": webutility.get_param("target")
# 		}
# 		return {"taskId": runTasknanqu.feedTask(param)}

# param = {
# 	"seat1": webutility.get_param("seat1"),
# 	"location1": webutility.get_param("location1"),
# 	"floorId1": webutility.get_param("floorId1"),
# 	"direction1": webutility.get_param("direction1"),
# 	"seat2": webutility.get_param("seat2"),
# 	"location2": webutility.get_param("location2"),
# 	"floorId2": webutility.get_param("floorId2"),
# 	"direction2": webutility.get_param("direction2")
# }
# # if param["floorId1"] != param["floorId2"]:
# # 	raise Exception("工位不在同一地图上")
# param["floorId"] = param["floorId1"]
# return {"taskId": runTask.feedTask(param)}

# @scadaUtility.post('/api/agv/tasklist')
# def scadaTaskList():
# 	return feedMgr.getTaskList()
#
#
# @scadaUtility.get('/api/agv/seat')
# def getSeat():
# 	return feedMgr.getSeat()
#
#
# @scadaUtility.get('/api/scada/clearLoc')
# def setLoc():
# 	locId = webutility.get_param("locId"),
# 	status = webutility.get_param("status"),
# 	return feedMgr.setLoc(locId, status)


# for uwsgi
main()
app = application = bottle.default_app()

if __name__ == '__main__':
	webutility.run()
else:
	pass
