# coding: utf-8
# author: ives
# date: 2018-03-01
# desc: 综科智控IO控制模块接口

import sys
import os
import time
import operator
import threading
import copy

if "../../common" not in sys.path:
	sys.path.append("../../common")

if __name__ == '__main__':
	currentPath = os.path.dirname(__file__)
	if currentPath != "":
		os.chdir(currentPath)

import log
import ioutility
import modbusapi
import mqtt
import config

if "../../devStat" not in sys.path:
	sys.path.append("../../devStat")
import devApi


# 基类
class baseObj(object):
	def __init__(self, objType, conf): 
		self.devId = conf['ioCtrl']['info']['id']
		self.devObj = None
		self.objType = objType
		self.__polling = (int(conf['ioCtrl']['control']['polling']) / 1000)
		if self.__polling < 0.1:
			self.__polling = 0.1
		self.__threadRun = True
		self.__threadPtr = threading.Thread(target=self.__threadFunc, args=('baseObj',))
		self.__initDevice(conf)
		self.__dataQuery = []
		self.__dataLock = threading.RLock()

	def __initDevice(self, conf):
		self.__devs = {}
		self.__devsCtrl = {}
		self.__collection = {}
		for key in conf:
			if operator.ne("dev_", key[:4]):
				continue
			devId = key[4:]
			if not self.checkKeys('error', conf[key], ['id', 'fcode', 'addr', 'value', 'msg', 'level']):
				continue
			if not self.checkKeys('status', conf[key], ['id', 'fcode', 'addr', 'value']):
				continue
			if not self.checkKeys('counter', conf[key], ['id', 'fcode', 'addr', 'value', 'factor']):
				continue
			if not self.checkKeys('ctrl', conf[key], ['id', 'fcode', 'addr', 'value']):
				continue
			self.__devs[devId] = conf[key]
			self.__devsCtrl[devId] = 1
			self.__collection[devId] = {'error': {}, 'status': {}, 'counter': {}}
			self.parseValue()

	def parseValue(self):
		for key in self.__devs:
			for type in ('error', 'status', 'counter'):
				if type not in self.__devs[key]:
					continue
				if type not in self.__collection[key]:
					self.__collection[key][type] = {}
				for idx in range(len(self.__devs[key][type])):
					conf = self.__devs[key][type][idx]
					typeId = conf['id']
					self.__collection[key][type][typeId] = []
					for idy in range(len(conf['value'])):
						self.__collection[key][type][typeId].append([])
						if not isinstance(conf['value'][idy], list):
							conf['value'][idy] = [conf['value'][idy]]

	def checkKeys(self, section, devConf, keys):
		if section not in devConf:
			return True
		confList = devConf[section]
		for idx in range(len(confList)):
			for col in keys:
				if col not in confList[idx]:
					log.warning("[%s: %s] key %s is not exists in %s section." %(self.objType, self.devId, col, section))
					return False
		return True

	def __threadFunc(self, args):
		while self.__threadRun:
			time.sleep(self.__polling)

			if not self.devObj:
				continue
			try:
				self.doCtrl()
				for key in self.__devs:
					if self.criticalError(key):
						continue
					self.collectStatus(key)
					self.collectData(key)
			except Exception as e:
				log.exception("[%s: %s] catct except: " %(self.objType, self.devId), e)

	def criticalError(self, devId):
		if 'error' not in self.__devs[devId]:
			return
		conf = self.__devs[devId]['error']
		collection = self.__collection[devId]['error']
		isCritical = False
		for idx in range(len(conf)):
			id,flag = self.getModbusVal(conf[idx], collection)
			if flag and (operator.eq("critical", conf[idx]['level'])):
				isCritical = True
				devApi.reportStatus(devId, "stop", 5)
			if devApi.reportAlarm(devId, conf[idx]['id'], 5, flag, conf[idx]['msg']):
				log.info("[%s: %s] send alarm, dev=%s, id=%s, flag=%d " %(self.objType, self.devId, devId, conf[idx]['id'], flag))
		return isCritical

	def getModbusVal(self, conf, collection):
		typeId = conf['id']
		if (len(conf['addr']) != len(conf['value'])) or (len(conf['addr']) < 1) or (len(conf['addr']) != len(collection[typeId])):
			log.warning("[%s: %s] addr and value size is invalid." %(self.objType, self.devId))
			return [typeId, False]

		isOk = True
		for idx in range(len(conf['addr'])):
			result = self.devObj.read(conf['fcode'], conf['addr'][idx]['start'], conf['addr'][idx]['num'])
			valLen = len(conf['value'][idx])
			if result is None:
				isOk = False
				continue
			for val in result:
				if len(collection[typeId][idx]) >= valLen:
					collection[typeId][idx].pop(0)
				collection[typeId][idx].append(val)
			if not isOk:
				continue
			if len(collection[typeId][idx]) == valLen:
				for idy in range(len(collection[typeId][idx])):
					if collection[typeId][idx][idy] != conf['value'][idx][idy]:
						isOk = False
						break
			else:
				isOk = False
				
		return [typeId, isOk]

	def collectStatus(self, devId):
		if 'status' not in self.__devs[devId]:
			return
		conf = self.__devs[devId]['status']
		collection = self.__collection[devId]['status']
		for idx in range(len(conf)):
			id,flag = self.getModbusVal(conf[idx], collection)
			if flag:
				if devApi.reportStatus(devId, conf[idx]['id'], 5):
					log.info("[%s: %s] send status, dev=%s, id=%s" %(self.objType, self.devId, devId, conf[idx]['id']))
				break

	def collectData(self, devId):
		if 'counter' not in self.__devs[devId]:
			return
		conf = self.__devs[devId]['counter']
		collection = self.__collection[devId]['counter']
		for idx in range(len(conf)):
			id,flag = self.getModbusVal(conf[idx], collection)
			if flag:
				devApi.reportCounter(devId, conf[idx]['id'], int(conf[idx]['factor']))
	
	def start(self):
		self.__threadRun = True
		if not self.__threadPtr.isAlive():
			self.__threadPtr.start()
		log.info("[%s: %s] start thread." %(self.objType, self.devId))

	def stop(self):
		self.__threadRun = False
		if self.__threadPtr.isAlive():
			self.__threadPtr.join()
		log.info("[%s: %s] stop thread." %(self.objType, self.devId))

	def hasDev(self, devId):
		return devId in self.__devsCtrl

	def recvCtrl(self, data):
		self.__dataLock.acquire()
		self.__dataQuery.append(data)
		self.__dataLock.release()

	def doCtrl(self):
		dataList = []
		self.__dataLock.acquire()
		dataList = copy.deepcopy(self.__dataQuery)
		self.__dataQuery.clear()
		self.__dataLock.release()
		if len(dataList) < 1:
			return
		for data in dataList:
			cmd = data['cmd']
			args = data['args']
			log.info("[%s: %s] excute cmd %s..." %(self.objType, self.devId, cmd))


# 创建串口对象
class commObj(baseObj):
	def __init__(self, conf): 
		super(commObj, self).__init__('commObj', conf)
		self.__initConnect(conf)

	def __initConnect(self, conf):
		comm = conf['ioCtrl']['connect']['comm']
		if operator.ne("slave", comm['type']):
			log.warning('[%s: %s] only support slave!' %(self.objType, self.__devId))
			raise Exception('only support slave!')

		slaveId = ioutility.str2Int(comm['devId'])
		self.devObj = modbusapi.rtuSlave(slaveId, comm['port'], comm['baud'], comm['stopBits'], \
			comm['byteSize'], comm['parity'])
		log.warning("[%s: %s] connect device from %s." %(self.objType, self.devId, comm['port']))


# 创建TCP对象
class tcpObj(baseObj):
	def __init__(self, conf): 
		super(tcpObj, self).__init__('tcpObj', conf)
		self.__initConnect(conf)

	def __initConnect(self, conf):
		tcp = conf['ioCtrl']['connect']['tcp']
		if operator.ne("server", tcp['type']):
			log.warning('[%s: %s] only support server!' %(self.objType, self.__devId))
			raise Exception('only support server!')

		slaveId = ioutility.str2Int(tcp['devId'])
		self.devObj = modbusapi.tcpServer(slaveId, tcp['ip'], tcp['port'])
		log.warning("[%s: %s] connect device from %s." %(self.objType, self.devId, tcp['ip']))


#启动服务
g_objList = []


def doCtrlCmd(topic, data):
	if (not data.has_key('devId')) or (not data.has_key('cmd')) or (not data.has_key('args')) or \
		(not data.has_key('mainDevId')):
		log.warning("[doCtrlCmd] invalid param: ", data)
		return
	mainDev = data['mainDevId']
	global g_objList
	for obj in g_objList:
		if operator.ne(obj.devId, mainDev):
			continue
		if obj.hasDev(data['devId']):
			obj.recvCtrl(data)
			break


def runApp():
	global g_objList
	cfgPath = os.path.realpath(sys.path[0]) + '/config'
	confList = ioutility.getConfs(cfgPath)
	try:
		svrIp = config.get("mqtt", "server_ip", "127.0.0.1")
		mqtt.initMqttObj(svrIp)
		mqtt.registerMqttObj(id(g_objList), 'dev/msg/scada/ctrl', doCtrlCmd)
		
		for conf in confList:
			connect = conf['ioCtrl']['connect']
			if operator.eq("comm", connect['type']):
				obj = commObj(conf)
				obj.start()
				g_objList.append(obj)
			elif operator.eq("tcp", connect['type']):
				obj = tcpObj(conf)
				obj.start()
				g_objList.append(obj)
			else:
				pass
	except Exception as e:
			log.exception("[zkzkApi: runApp] catct except: ", e)
	while True:
		time.sleep(1)


#========================================== unit test ==========================================
def test_getModbusVal():
	conf = {'ioCtrl': {'info': {"id": "ives"}, 'control': {'polling': 500}, \
		'connect': {'comm': {"type": "slave", "devId": "0x01", "port":"COM5", "baud":115200, \
		"byteSize":8, "parity":"N", "stopBits":1}}}}
	obj = commObj( conf)
	conf = {"id": "4001", "fcode": 2, "addr": [{"start": 1, "num": 2}, {"start": 3, "num": 1}],"value": [[0,0,0,0], [1,1]]}
	collection = {"4001": []}
	id, flag = obj.getModbusVal(conf, collection)
	print(id, flag)
	assert id == '4001'
	assert flag == False
	

if __name__ == '__main__':
	#test_getModbusVal()
	runApp()



