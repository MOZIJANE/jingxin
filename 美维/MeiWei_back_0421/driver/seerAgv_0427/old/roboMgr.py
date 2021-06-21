import struct
import json
import datetime
import uuid
import time
import threading
import driver.seerAgv_0427.roboKit as roboKit
import driver.seerAgv_0427.roboModel as roboModel
import driver.seerAgv_0427.roboTask as roboTask
import getRootPath
import setup

if __name__ == '__main__':
	setup.setCurPath(__file__)
import mytimer
import enhance
import config
import factoryMgr
import common.mqtt as mqtt
import os

finishEvent = enhance.event()


class roboManager():
	def __init__(self, g_addr):
		self.g_mapData = dict()
		self.g_taskList = list()
		self.g_statusData = None
		self.g_tasksData = None
		self.g_addr = g_addr
		self.g_flag = roboModel.TASK_STATUS_NONE
		self.__sourceId = None

	def assembleData(self, code, data):
		bodyData = None
		dataLen = 0
		if data is not None:
			bodyStr = json.dumps(data)
			bodyData = bodyStr.encode()
			dataLen = len(bodyStr)
		codeNum = int(code)
		sendObj = roboModel.protocolHeader(90, 1, 0, dataLen, codeNum, 0, 0)
		headData = sendObj.getsturct()
		if bodyData is None:
			sendData = headData
		else:
			sendData = headData + bodyData
		return sendData

	def putTask(self, id, code, data, type, groupsn):
		roboTask.putTask(id, code, data, type, groupsn)

	# @mytimer.interval(1000)
	def taskObserver(self):
		taskList = roboTask.getTask()
		pendingTaskList = list(filter(lambda x: x['status'] == -1, taskList))
		doneTaskList = list(filter(lambda x: x['status'] == 0, taskList))
		workingTaskList = list(filter(lambda x: x['status'] == 1, taskList))
		pausingTaskList = list(filter(lambda x: x['status'] == -3, taskList))
		nowtime = datetime.datetime.now()

		# 处理挂起的任务
		if len(pendingTaskList) > 0 and len(workingTaskList) == 0 and len(pausingTaskList) == 0:
			currentTask = pendingTaskList[0]
			id = currentTask['sn']
			code = currentTask['code']
			data = currentTask['data']
			type = currentTask['type']
			overrunTask = roboTask.getOverrunTask(code)
			if overrunTask is None:
				# 处理AGV任务
				if code < 6600:

					sourceId = self.g_statusData['target_id']
					targetId = data['id']
					str = {'sourceId': sourceId, 'targetId': targetId, 'type': 'request'}
					self.__sourceId = sourceId
					# 上报请求
					mqtt.send('agv/' + self.g_addr, str)
					# 任务暂停
					roboTask.editTask(id=id, code=code, status=-3, startTime=nowtime)


				# 处理自定义任务
				elif code >= 6600:
					self.runCustom(code=code, data=data)
			# todo:处理批量
			for pendingtaskItem in pendingTaskList:
				pass

		# 处理被管制任务
		for taskItem in pausingTaskList:
			id = taskItem['sn']
			code = taskItem['code']
			data = taskItem['data']
			type = taskItem['type']
			source = self.g_statusData['target_id']
			target = data['id']

			name = '{source} --- {target}'.format(source=source, target=target)
			currentAgv = factoryMgr.getWrokingByName(name)
			if currentAgv is None or currentAgv['status'] == 'continue':
				# 任务继续
				runResult = self.run(code=code, data=data, type=type)
				if runResult is not None and len(runResult) == 2:
					errorno = runResult['ret_code']
					errormsg = runResult['err_msg']
					roboTask.editTask(id=id, code=code, status=-2, errorno=errorno, errormsg=errormsg,
					                  startTime=nowtime,
					                  finishTime=nowtime)
				else:
					roboTask.editTask(id=id, code=code, status=1, startTime=nowtime)
				print(runResult)

		# 处理正在进行中的任务
		for taskItem in workingTaskList:
			id = taskItem['sn']
			code = taskItem['code']
			data = taskItem['data']
			type = taskItem['type']
			createTime = taskItem['createTime']
			startTime = taskItem['startTime']

			# 不处理查询类型的操作
			if type == roboModel.API_PORT_STATE:
				break

			duration = nowtime - startTime
			if duration > datetime.timedelta(minutes=5):
				roboTask.editTask(id=id, code=code, status=-2, errorno=-1, errormsg='任务超时', finishTime=nowtime)
				self.run(code=roboModel.robot_task_cancel_req, data=None, type=roboModel.API_PORT_TASK)

			if self.g_statusData is None:
				return
			currentStatus = self.__getStatus(code, self.g_statusData['task_status'])
			if currentStatus == roboModel.TASK_STATUS_COMPLETED:
				if duration < datetime.timedelta(seconds=5):
					continue
				roboTask.editTask(id=id, code=code, status=0, errormsg='任务运行成功', finishTime=nowtime)
				finishEvent.emit(id, code)
				targetId = self.g_statusData['target_id']
				str = {'sourceId': self.__sourceId, 'targetId': targetId, 'type': 'finished'}
				# 上报状态
				mqtt.send('agv/' + self.g_addr, str)


			elif currentStatus == roboModel.TASK_STATUS_FAILED:
				roboTask.editTask(id=id, code=code, status=-2, errorno=-1, errormsg='任务运行中失败', finishTime=nowtime)
			elif currentStatus == roboModel.TASK_STATUS_CANCELED:
				roboTask.editTask(id=id, code=code, status=-2, errorno=-1, errormsg='任务已经取消', finishTime=nowtime)
			elif currentStatus == roboModel.TASK_STATUS_NONE and self.g_statusData['emergency']:
				roboTask.editTask(id=id, code=code, status=-2, errorno=-1, errormsg='任务没有正确预位', finishTime=nowtime)

			# if code == roboModel.robot_task_gotarget_req:
			# 	if self.g_statusData is None:
			# 		return
			# 	targetId = data['id']
			# 	targetPoint = getPointFromMap(targetId)
			# 	targetX = targetPoint['pos']['x']
			# 	targetY = targetPoint['pos']['y']
			# 	currentX = self.g_statusData['x']
			# 	currentY = self.g_statusData['y']
			# 	print("[taskObserver] currentX,currentY|targetX,targetY:",
			# 	      "{cx},{cy}|{tx},{ty}".format(cx=currentX, cy=currentY, tx=targetX, ty=targetY))
			# 	tolerance = 0.1
			# 	if abs(targetX - currentX) < tolerance and abs(targetY - currentY) < tolerance:
			# 		roboTask.editTask(id=id, code=code, status=0,finishTime=nowtime)
			# 		finishEvent.emit(id, code)




			# elif code == roboModel.robot_task_translate_req:
			# 	if False:
			# 		print("[taskObserver] removing taskitem", id)
			# 		roboTask.editTask(id=id, code=code, status=0)
			# 		finishEvent.emit(id, code)

	def __getStatus(self, code, status):
		currentStatus = status
		if code == roboModel.robot_other_setdo_req:
			currentStatus = roboModel.TASK_STATUS_COMPLETED
		elif code == roboModel.robot_other_wait_req:
			currentStatus = self.g_flag
			pass

		return currentStatus

	# @mytimer.interval(1000)
	def runRefreshStatus(self):

		statusData = self.runTask(1100, None, roboModel.API_PORT_STATE)
		self.g_tasksData = self.__getAllTasks()
		# for tasksItem in  self.g_tasksData:
		#
		# 	isloop=tasksItem['loop']
		# 	status=tasksItem['status']
		# 	if isloop==True and status ==0:
		# 		pass

		# 上报电量
		energylevel = statusData['battery_level']
		isCharge = statusData['charging']
		str = {'energylevel': energylevel, 'isCharge': isCharge, 'type': 'status'}
		mqtt.send('agv/' + self.g_addr, str)
		self.g_statusData = statusData

	def runTask(self, code, data, type, isBatch=False, groupsn=None):
		id = uuid.uuid1().__str__()
		if type == roboModel.API_PORT_STATE:
			stateResult = self.run(code=code, data=data, type=type)
			return stateResult
		elif type != roboModel.API_PORT_STATE:
			taskList = roboTask.getTask()
			workingTaskList = list(filter(lambda x: x['status'] == 1, taskList))
			if len(workingTaskList) == 0 or isBatch:
				self.putTask(id, code, data, type, groupsn)
			else:
				raise Exception("AGV正忙")
		return id

	def countDown(self, dur):
		if dur < 0:
			return
		self.g_flag = roboModel.TASK_STATUS_RUNNING
		time.sleep(dur)
		self.g_flag = roboModel.TASK_STATUS_COMPLETED

	def run(self, code, data, type):
		dataresult = None
		with roboKit.robotClient(self.g_addr, type) as client:
			data1 = self.assembleData(code, data)
			if client:
				if type != roboModel.API_PORT_STATE:
					# todo:严格处理非队列任务
					currentTask = roboTask.getOverrunTask(code)
					if currentTask:
						raise Exception(
							"当前有相同任务正在执行,任务id{taskid},任务类型{taskcode},任务参数{taskdata}".format(taskid=currentTask['id'],
							                                                                taskcode=currentTask[
								                                                                'code'],
							                                                                taskdata=currentTask[
								                                                                'data']))
				reciveData = client.send(data1)
				if isinstance(reciveData, int):
					raise Exception("网络错误{data}".format(data=reciveData))
				result = reciveData.decode("utf-8")

				if len(result) == 0:
					return None
				try:
					dataresult = json.loads(result)
				except Exception as e:
					dataresult = None
				return dataresult
			else:
				return None

	def runCustom(self, code, data):
		if code == roboModel.robot_other_wait_req:
			duration = int(data['duration'])
			_thread = threading.Thread(target=self.countDown, kwargs={'dur': duration}, name="timer_thread")
			_thread.start()

	def getAllTask(self):
		taskList = roboTask.getTask()
		return taskList

	def delTasks(self, sn):
		roboTask.delTasks(sn)
		return sn

	def getTaskByCode(self, code):
		taskList = roboTask.getTask()
		currentTask = None
		for taskItem in taskList:
			if taskItem['code'] == code:
				currentTask = taskItem
		return currentTask

	def __getAllTasks(self):
		result = list()
		tasksList = roboTask.getTasks()
		taskList = roboTask.getTask()

		for tasksItem in tasksList:
			currentResult = dict()
			currentsn = tasksItem['sn']
			currenttask = list()
			currentRunning = None
			for taskItem in taskList:
				if 'groupsn' in taskItem and taskItem['groupsn'] == currentsn:
					if taskItem['status'] == 1:
						currentRunning = taskItem
					currenttask.append(taskItem)
			status = -1
			doneTaskList = list(filter(lambda x: x['status'] == 0, currenttask))

			total = len(currenttask)
			if total == 0:
				continue
			currentRunningIndex = 0
			if currentRunning:
				currentRunningIndex = currenttask.index(currentRunning)
			currentResult['sn'] = currentsn
			currentResult['name'] = tasksItem['name']
			currentResult['createTime'] = tasksItem['createTime']
			currentResult['loop'] = tasksItem['loop']
			currentResult['tasks'] = currenttask
			currentResult['total'] = total
			currentResult['current'] = currentRunningIndex

			finishTime = None

			if currentRunning is not None:
				status = 1
			elif total > 0 and len(doneTaskList) == total and currentRunning is None:
				status = 0

				last = currenttask[total - 1]
				finishTime = last['finishTime']
			currentResult['status'] = status
			currentResult['finishTime'] = finishTime
			result.append(currentResult)
		return result

	def __getMap(self, path):
		if len(self.g_mapData) == 0:
			schema = roboModel.mapInfo()
			with open(path) as f:
				jsonMap = f.read()
			data, result = schema.loads(jsonMap)
			self.g_mapData = data
		return self.g_mapData

	def __getLocalMapByRobot(self):
		result = self.runTask(roboModel.robot_status_map_res, None, roboModel.API_PORT_STATE)
		crtmap = result['current_map']
		maps = result['maps']
		rootpath = getRootPath.getRootPath()
		mapPath = rootpath + '/userfiles/{fileName}.smap'.format(fileName=crtmap)
		return mapPath

	def getPointFromMap(self, id):
		local = self.__getLocalMapByRobot()
		data = None
		result = None
		if local is not None:
			data = self.__getMap(local)
		if data:
			aplist = data['advancedPointList']
			for apitem in aplist:
				if apitem['instanceName'] == id:
					result = apitem
		return result

	def setTasks(self, data):
		schema = roboModel.taskInfo()
		obj, result = schema.dump(data)

		if len(result) != 0:
			raise Exception("参数不正确！")
		tasks = self.getTasks()

		name = obj['name']
		if data['sn'] == '':
			if len(list(filter(lambda x: x['name'] == name, tasks))) > 0:
				raise Exception("重名！")

		else:
			currentTask = roboTask.getTasksBySn(data['sn'])
		# if (name == currentTask['name']):
		# 	raise Exception("重名！")

		if data['sn'] == '':
			sn = uuid.uuid1().__str__()
		else:
			sn = data['sn']
		roboTask.setorUpdateTasks(ds=obj, sn=sn)
		return sn

	def runTasksFromSave(self, id):
		tasks = roboTask.getTasksBySn(id)
		if tasks is None:
			raise Exception("参数不正确！")
		for item in tasks['tasks']:
			code = item['actionCode']
			params = item['params']
			type = item['type']
			self.runTask(code=code, data=params, type=type, isBatch=True, groupsn=tasks['sn'])

	def runTasks(self, data):
		schema = roboModel.taskInfo(many=True)
		tasksList, result = schema.dump(data)
		tasks=dict()
		if len(result) != 0:
			raise Exception("参数不正确！")
		tasks["createTime"] = datetime.datetime.now()
		tasks["sn"] = uuid.uuid1().__str__()
		tasks["loop"] = False
		tasks["name"] = "即时任务链_{sn}".format(sn=tasks["sn"])
		tasks["lastRunningTime"] = None,
		tasks["runCount"] = 0
		tasks["tasks"]=tasksList
		for item in tasks['tasks']:
			code = item['actionCode']
			params = item['params']
			type = item['type']
			self.runTask(code=code, data=params, type=type, isBatch=True, groupsn=tasks['sn'])

	def stopTasks(self, id):
		tasks = roboTask.getTasksBySn(id)
		if tasks is None:
			raise Exception("参数不正确！")
		for item in tasks['tasks']:
			pass

	def getTasks(self):
		tasks = roboTask.getTasks()
		return tasks


agvaddr = config.get("agv", "servers")

g_roboManager = roboManager(agvaddr)


def test_sendMsg():
	global g_roboManager
	data1 = g_roboManager.runTask("1100", None, roboModel.API_PORT_STATE)
	assert data1


def test_timeout():
	global g_roboManager
	data1 = g_roboManager.assembleData('2002', None)
	assert data1
	client1 = roboKit.robotClient()
	client1.connect(g_roboManager.g_addr, 19204)
	i = 0
	while i < 100:
		startTime = datetime.datetime.now()
		result = client1.send(data1)
		if result == -1:
			endTime = datetime.datetime.now()
			span = endTime - startTime
			assert span < datetime.timedelta(seconds=11)
			assert span > datetime.timedelta(seconds=9)
		print(result)
		i += 1
		time.sleep(5)
	client1.disconnect()


def test_reconnect():
	global g_roboManager
	data1 = g_roboManager.assembleData('2002', None)
	assert data1
	client1 = roboKit.robotClient()
	client1.connect(g_roboManager.g_addr, 19204)
	i = 0
	while i < 100:
		startTime = datetime.datetime.now()
		result = client1.send(data1)
		if result == -2:
			endTime = datetime.datetime.now()
			span = endTime - startTime
			assert span < datetime.timedelta(seconds=6)
			assert span > datetime.timedelta(seconds=4)
		print(result)
		i += 1
		time.sleep(5)
	client1.disconnect()


def test_runTaskList():
	schema = roboModel.taskInfo()
	hello = {"name": "testname", "tasks": [
		{
			"name": "testTaskName",
			"actionCode": "3050",
			"params": {"x": "50.3", "y": "50.2", "angle": "50.2"}
		}
	], "loop": "false"}

	h2 = {'user': 'TODO:', 'loop': False,
	      'tasks': [{'params': {}, 'actionCode': 3057, 'active': True, 'label': '去起始点'}], 'name': '123456'}
	data, result = schema.dump(h2)
	if len(result) != 0:
		raise Exception("反序列化错误")
	assert len(data['tasks']) == 1
	assert data['name'] == 'testname'
	assert data['tasks'][0]['actionCode'] == 3050.0
	assert len(data['tasks'][0]['params']) == 3


def test_getMap():
	global g_roboManager
	result = g_roboManager.__getMap('./../../userfiles/testmap.smap')
	assert result
	assert len(result['advancedCurveList']) == 17
	assert len(result['advancedPointList']) == 13
	assert result['header']['mapName'] == '20170908b'


def test_getPointFromMap():
	global g_roboManager
	result = g_roboManager.getPointFromMap('LM9')
	assert result
	assert result['className'] == 'LandMark'
	assert result['instanceName'] == 'LM9'
	assert len(result['pos']) == 2


def test_countDown():
	global g_roboManager
	print(g_roboManager.g_flag)
	_thread = threading.Thread(target=g_roboManager.countDown, kwargs={'dur': 10}, name="timer_thread")
	_thread.start()
	while True:
		time.sleep(0.5)
		print(g_roboManager.g_flag)


if __name__ == '__main__':
	@mytimer.interval(1000)
	def taskObserv():
		global g_roboManager
		g_roboManager.taskObserver()


	@mytimer.interval(1000)
	def RefreshStatus():
		global g_roboManager
		g_roboManager.runRefreshStatus()
