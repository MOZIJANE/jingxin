#coding=utf-8
# ycat			2017-09-27	  create 
import sys,os
import time
import paho.mqtt.client  
import threading
import json


if __name__ == '__main__':
	currentPath = os.path.dirname(__file__)
	if currentPath != "":
		os.chdir(currentPath)

g_client = None 

def connect(hostIp,recieveCallback,user="admin",password="password",hostPort=61613):
	global g_client
	assert not g_client
	g_client = paho.mqtt.client.Client(protocol=paho.mqtt.client.MQTTv31)
	g_client.recieveCallback = recieveCallback
	g_client.username_pw_set(user,password)
	g_client.connect(hostIp, hostPort, 60)
	g_client.on_connect = _on_connect
	g_client._on_disconnect = _on_disconnect
	g_client.on_message = _on_message
	#g_client.on_log = _on_log
	time.sleep(0.1)
	g_client.loop_start()
	
def close():
	global g_client
	g_client.loop_stop()
	#g_client.close()
	g_client = None
	
	
#	订阅者的Topic name支持通配符#和+ ：
#	#支持多个层次的主题的通配符
#	+只匹配一层主题级别的通配符
#	eg：
#	finance/stock/#
#	finance/+/ibm/	
def subscribe(topic):
	global g_client
	g_client.subscribe(topic)

def unsubscribe(topic):
	global g_client
	g_client.unsubscribe(topic)	

def send(topic,data,qos=0):
	global g_client
	g_client.publish(topic,data)

publish = send	 
	
def _on_connect(client, userdata, flags, rc):
	print("mqtt: Connected with result code "+str(rc))
	
def _on_disconnect(client, userdata, rc):
	print("mqtt: disconnected with result code "+str(rc))

def _on_message(client, userdata, msg):
	global message
	client.recieveCallback(msg.topic,msg.payload)

def _on_log(client, userdata, level, buf):
	print(userdata,level,buf)


# ==============================  mqtt全局对象 ======================================
g_mqtt_obj = None
g_mqttObjClient = None

class mqttApi:
	def __init__(self):
		self.__initFinish = False
		self.__callbackLock = threading.RLock()
		self.__callbackList = {}	#first key: topic,  first value: list;  second list is dict

	def __receiveFromMqtt(self, topic, data):
		try:
			jsStr = json.loads(data.decode("utf-8"))
			self.__callbackLock.acquire()
			if topic in self.__callbackList:
				for idx in range(len(self.__callbackList[topic])):
					self.__callbackList[topic][idx]['func'](topic, jsStr)
		finally:
			self.__callbackLock.release()
			return None

	def initMqtt(self, svrIp,user="admin",password="password",hostPort=61613):
		global g_mqttObjClient
		if self.__initFinish or g_mqttObjClient:
			print("[mqttApi]: mqtt is already init succeed.")
			return

		g_mqttObjClient = paho.mqtt.client.Client(protocol=paho.mqtt.client.MQTTv31)
		g_mqttObjClient.recieveCallback = self.__receiveFromMqtt
		g_mqttObjClient.on_connect = self.__connectCallback
		g_mqttObjClient._on_disconnect = self.__disconnectCallback
		g_mqttObjClient.on_message = self.__onMessage
		g_mqttObjClient.username_pw_set(user,password)
		g_mqttObjClient.connect(svrIp, hostPort, 60)
		#g_client.on_log = _on_log
		time.sleep(0.1)
		g_mqttObjClient.loop_start()

		self.__initFinish = True
		print("[mqttApi]: init MQTT %s finish." %svrIp)

	def __connectCallback(self, client, userdata, flags, rc):
		global g_mqttObjClient
		print("[mqttApi: connect]: result code " + str(rc))
		topicList = []
		self.__callbackLock.acquire()
		for topic in self.__callbackList:
			topicList.append(topic)
		self.__callbackLock.release()
		for topic in topicList:
			g_mqttObjClient.subscribe(topic)
			print("[mqttApi: connect]: subscribe topic ", topic)

	def __disconnectCallback(self, client, userdata, rc):
		print("[mqttApi: disconnect]: result code " + str(rc))

	def __onMessage(self, client, userdata, msg):
		global g_mqttObjClient
		g_mqttObjClient.recieveCallback(msg.topic, msg.payload)

	def close(self):
		global g_mqttObjClient
		g_mqttObjClient.loop_stop()

	def sendMsg(self, topic, infoDic):
		global g_mqttObjClient
		if not self.__initFinish:
			print("[mqttApi]: mqtt need init!")
			return
		
		jsStr = json.dumps(infoDic)
		g_mqttObjClient.publish(topic, jsStr.encode("utf-8"))

	def registerCallback(self, objId, topic, callbackFunc):
		global g_mqttObjClient
		if not self.__initFinish:
			print("[mqttApi]: register topic failed, mqtt need init!")
			return
		self.__callbackLock.acquire()
		if topic not in self.__callbackList:
			self.__callbackList[topic] = []

		#判断是否存在
		for idx in range(len(self.__callbackList[topic])):
			callback = self.__callbackList[topic][idx]
			if callback['objId'] == objId and callback['func'] == callbackFunc:
				self.__callbackLock.release()
				return
		self.__callbackList[topic].append({'objId': objId, 'func': callbackFunc})
		self.__callbackLock.release()
		g_mqttObjClient.subscribe(topic)
		
		print('[mqttApi]: %s register topic %s finish.' %(str(objId), topic))

	def unregisterCallback(self, objId, topic):
		global g_mqttObjClient
		self.__callbackLock.acquire()
		if topic not in self.__callbackList:
			self.__callbackLock.release()
			return
		delList = []
		for idx in range(len(self.__callbackList[topic])):
			if self.__callbackList[topic][idx]['objId'] == objId:
				delList.append(self.__callbackList[topic][idx])
		for val in delList:
			self.__callbackList[topic].remove(val)
		size = len(self.__callbackList[topic])
		self.__callbackLock.release()
		
		if size < 1 and g_mqttObjClient:
			g_mqttObjClient.unsubscribe(topic)
			
		log.info('[mqttApi]: %s unregister topic %s finish.' %(str(objId), topic))
		
	
# mqtt对象
def _mqttObj():
	global g_mqtt_obj
	if g_mqtt_obj:
		return g_mqtt_obj
	else:
		g_mqtt_obj = mqttApi()
		return g_mqtt_obj


# 初始化
def initMqttObj(svrIp, user='admin', pwd='password', port=61613):
	_mqttObj().initMqtt(svrIp, user, pwd, port)


# 注册主题， objId: 注册者对象地址
def registerMqttObj(objId, topic, callbackFunc):
	_mqttObj().registerCallback(objId, topic, callbackFunc)


# 解注册主题， objId: 注册者对象地址
def unregisterMqttObj(objId, topic):
	_mqttObj().unregisterCallback(objId, topic)


# 发送主题消息， dataDic: 数据字典
def mqttObjSend(topic, dataDic):
	_mqttObj().sendMsg(topic, dataDic)



#################### unit test ####################	  


if __name__ == '__main__':
	pass


