#coding=utf-8
# ycat			2017-09-27	  create 
# mqtt的基础实现 
import sys,os
import time
import paho.mqtt.client  #pip install paho-mqtt 
import threading
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import enhance 
import log 
import config
import utility
import re
import json_codec

def send(topic,data):
	_getMqttObj().send(topic,data)

#	回调函数的格式为  def callback(topic,data):
# 	https://blog.csdn.net/amwha/article/details/74364175
#	订阅者的Topic name支持通配符#和+ ：
#	通配符'#'：支持多个层次的主题的通配符,必须是主题过滤器的最后一个字符  
#	通配符'+'：只匹配一层主题级别的通配符,可以包括第一个和最后一个层级,必须占据过滤器的整个层级 
#	通配符'$'：表示匹配一个字符，只要不是放在主题的最开头
#	eg. 
#	finance/stock/#
#	finance/+/ibm/	
#	/financ$ 
def subscribe(topic,callbackFunc):
	_getMqttObj().subscribe(topic,callbackFunc)
	
# @注册函数的修饰符
def register(topic):
	def __call(func):
		subscribe(topic,func)
		return func
	return __call	
	
g_mqttObj = None

def unsubscribe(callbackFunc):
	_getMqttObj().unsubscribe(callbackFunc)

def _getMqttObj():
	global g_mqttObj
	if g_mqttObj is None:
		g_mqttObj = mqtt(initNow=False)
	return g_mqttObj
	
	
@utility.init()
def init():
	_getMqttObj().init()
	
	
@utility.fini()
def close():
	global g_mqttObj
	if g_mqttObj is None:
		return
	g_mqttObj.close()
	
def setDebug():
	_getMqttObj().debug = True
	
	
#用这个类，可以支持多个实例 
class mqtt:
	#msgType: 消息类型，可选["bytes" | "str" | "json"]
	def __init__(self,host=None,user=None,password=None,port=None,debug=False,msgType=None,initNow=True):
		self.disconnectEvent = enhance.event()
		self.connectEvent = enhance.event()
		self.host = host
		self.user = user
		self.password = password
		self.port = port
		self.debug = debug
		self.msgType = msgType
		self._isConnect = False 
		
		if not self.msgType:
			self.msgType = config.get("mqtt","msgType","json")
		if not self.host:
			self.host = config.get("mqtt","ip","")
		if not self.user:
			self.user = config.get("mqtt","user","root")
		if not self.password:
			self.password = config.get("mqtt","password","znzz")
		if not self.port:
			self.port = config.getint("mqtt","port",1883)
		if not self.debug:
			self.debug = config.getbool("mqtt","debug",False) 
		self._imp = None
		self._callbacks = {}  #key:topic, value: enhance.event 
		if not self.host:
			log.error("mqtt is disabled")
			return
		if initNow:
			self.init()
			
		
	def init(self):
		if not self.host:
			return
		try: 
			self._imp = paho.mqtt.client.Client(protocol=paho.mqtt.client.MQTTv31)
			self._imp.username_pw_set(self.user,self.password) 
			self._imp.on_connect = self._on_connect
			#self._imp.on_log = self._on_log
			self._imp._on_disconnect = self._on_disconnect
			self._imp.on_message = self._on_message  
			self._imp.connect(self.host, self.port, 60) 
			for i in range(20):
				self._imp.loop()
				if self.isConnect():
					break
				time.sleep(0.1)
		except Exception as e:
			log.error("try mqtt connect "+ self._name() + " failed",str(e))
		self._imp.loop_start() 
		
	def isConnect(self):
		return self._isConnect
	
	def __del__(self):
		if self._imp: 
			self.close()
		
	def close(self):
		if self._imp is None:
			return
		if self._imp._sock:
				self._imp._sock.close()
				self._imp._sock = None
		if self._imp._sockpairR: 
				self._imp._sockpairR.close()
				self._imp._sockpairR = None
		if self._imp._sockpairW: 
				self._imp._sockpairW.close()
				self._imp._sockpairW = None
		self._imp.loop_stop(force=True)
		self._imp = None
	
	def subscribe(self,topic,callbackFunc):
		log.info("mqtt: subscribe ["+topic+"]")
		sub = True
		if topic not in self._callbacks:
			sub = False
			self._callbacks[topic] = enhance.event()
		self._callbacks[topic].connect(callbackFunc)
		if not sub and self._imp is not None:
			self._imp.subscribe(topic)

	def unsubscribe(self,func):
		for topic in self._callbacks:
			if func not in self._callbacks[topic].funcs:
				continue
			self._callbacks[topic].disconnect(func) 
			
			if self._callbacks[topic].count() == 0:
				self._imp.unsubscribe(topic)
				del self._callbacks[topic]
				log.info("mqtt: unsubscribe ["+topic+"]")
			break

	def send(self,topic,data):
		msg = self._encode(data)
		if self._imp is None:
			if self.debug:
				log.error("mqtt is disconnected, drop",topic)
			return
		self._imp.publish(topic,msg)
		if self.debug:
			log.debug("mqtt send:["+topic+"]",msg)
	
	def _encode(self,data):
		if self.msgType == "json":
			return json_codec.dump(data).encode("utf-8")
		elif self.msgType == "str":
			return str(data).encode("utf-8")
		elif self.msgType == "bytes":
			if isinstance(data,bytes):
				return data
			return str(data).encode("utf-8")
		else:
			log.error("encode: unknow msgType",self.msgType)
			assert 0
			
	def _decode(self,data):	
		assert isinstance(data,bytes)
		if self.msgType == "bytes":
			return data
		msg = data.decode("utf-8")
		if self.msgType == "json":
			return json_codec.load(msg)
		elif self.msgType == "str":
			return msg
		else:
			log.error("decode: unknow msgType",self.msgType)
			assert 0
	
	def _on_connect(self, client, userdata, flags, rc): 
		self._isConnect = True 
		log.info("mqtt: connected",self._name(),len(self._callbacks)) 
		for topic in self._callbacks:
			self._imp.subscribe(topic) 
			log.info("mqtt resubscribe ["+topic+"]") 
		self.connectEvent.emit()
		try:
			import alarm.alarmApi
			alarm.alarmApi.clear("mqtt:"+self._name(),2007,"system")
		except ModuleNotFoundError as e:
			log.warning("no alarm module")
		
	def _on_disconnect(self, client, userdata, rc): 
		self._isConnect = False  
		errorMsg = "mqtt: disconnected, result="+str(rc)
		log.error(errorMsg)
		self.disconnectEvent.emit()
		try:
			import alarm.alarmApi
			alarm.alarmApi.alarm("mqtt:"+self._name(),2007,errorMsg,"system")
		except ModuleNotFoundError as e:
			log.warning("no alarm module")
		
	def _on_message(self, client, userdata, msg):
		if self.debug:
			log.debug("mqtt rec:["+msg.topic+"]",msg.payload)
		data = self._decode(msg.payload)
		for c in self._callbacks:
			if mqtt._match(c,msg.topic):
				try:
					self._callbacks[c].emit(msg.topic,data)
				except Exception as e:
					log.exception("handle mqtt:"+msg.topic,e)

	def _on_log(self,client, userdata, level, buf):
		log.debug(buf)
		
	@staticmethod
	def _match(topicTemp,topic):
		if topicTemp == topic:
			return True 
		
		#通配符“$”表示匹配一个字符  
		topicRe = "^" + topicTemp.replace("$",".") + "$"
		if topicTemp[-2] == "/" and topicTemp[-1] == "#": 
			topicRe = "^" + topicTemp[0:-2] + "(/.*)?$"
		if topicTemp.find("+") != -1:
			topicRe = topicRe.replace("+","[^/]+")  
		return re.match(topicRe,topic) is not None
		 
	def _name(self):
		return self.host+":"+str(self.port)

################ unit test ################
def test1():
	class foo:
		def __init__(self):
			self.count = 0
		def recieve(self,topic,data):
			self.count += 1
			self.topic = topic
			self.data = data
	f1 = foo()
	subscribe("ycat",f1.recieve)

	send("ycat","hello ycat")
	time.sleep(0.1)
	assert f1.count == 1
	assert f1.topic == "ycat"
	assert f1.data == "hello ycat" 

def test_match():
	assert mqtt._match("agv/#","agv/8-222/location/AGV01")
	assert mqtt._match("room401/light","room401/light")
	assert not mqtt._match("room401/light","room402/light")
	assert not mqtt._match("room401/light","room401/light/h")
	assert not mqtt._match("room401/light","room401/light2")
	#多层通配符—-“#” 
	
	assert mqtt._match("china/guangzhou/#","china/guangzhou")
	assert mqtt._match("china/guangzhou/#","china/guangzhou/huangpu")
	assert mqtt._match("china/guangzhou/#","china/guangzhou/tianhe/zhongshanlu")
	assert mqtt._match("china/guangzhou/#","china/guangzhou/tianhe/zhongshanlu/num123")
	assert not mqtt._match("china/guangzhou/#","china/guangzhou1")
	assert not mqtt._match("china/guangzhou/#","china/guangzhou1/huangpu")
	
	assert mqtt._match("china/+","china/guangzhou")
	assert mqtt._match("china/+","china/guangzhou222")
	assert not mqtt._match("china/+","china2/guangzhou")
	assert not mqtt._match("china/+","china/guangzhou/aaa")
	
	assert mqtt._match("+/china","guangzhou/china")
	assert mqtt._match("+/china","guangzhou222/china")
	assert not mqtt._match("+/china","guangzhou222/china2")
	assert not mqtt._match("+/china","aa/guangzhou222/china")
	
	assert mqtt._match("ycat/+/+/china/#","ycat/aaa/bbb/china/ccc/eee/ddd")
	assert mqtt._match("ycat/+/+/china/#","ycat/aaa/bbb/china")
	assert not mqtt._match("ycat/+/+/china/#","ycat/aaa/c/bbb/china/ccc/eee/ddd")
	assert mqtt._match("+/+/+/china/#","ycat/aaa/bbb/china/ccc/eee/ddd")
	assert not mqtt._match("+/+/+/china/#","ycat/aaa/c/bbb/china/ccc/eee/ddd")
	assert not mqtt._match("+/+/+/china/#","ycat/aaa/bbb/china2/ccc/eee/ddd")
	assert mqtt._match("ycat/+/a","ycat/tt0/a")
	
def testmsg():
	#os.system("systemctl restart mqtt")
	def tmestconn(msgType):
		print("test ",msgType)
		m = mqtt(host = "127.0.0.1" ,port=61613,debug=True)
		assert mqtt._match("ycat/+/a","ycat/tt0/a")
		class foo:
			def __init__(self):
				self.count = 0
			def recieve(self,topic,data):
				self.count += 1
				self.topic = topic
				self.data = data
		f1 = foo()
		f2 = foo()
		m.subscribe("ycat/+/a",f1.recieve)
		m.subscribe("+/a",f2.recieve)
		time.sleep(0.3)
		m.send("ycat/tttt/aw","hello") #wrong
		
		for i in range(10):
			m.send("ycat/tt"+str(i)+"/a","hello"+str(i))
			time.sleep(0.1)
			assert f1.count == i+1
			assert f1.topic == "ycat/tt"+str(i)+"/a"
			assert f1.data == "hello"+str(i)
		
		m.unsubscribe(f1.recieve)
		m.send("ycat/a/a","hello")
		time.sleep(0.5)	
		assert f1.count == 10
		assert f2.count == 0
		m.close() 
	tmestconn("bytes")
	tmestconn("json")
	tmestconn("str")
	
def testreconnect():
	#alarm recusive 
	os.system("systemctl stop mqtt")
	m = mqtt(host = "127.0.0.1" ,port=61613,debug=True)
	class foo:
		def __init__(self):
			self.count = 0
		def recieve(self,topic,data):
			self.count += 1
			self.topic = topic
			self.data = data
	time.sleep(3)
	assert not m.isConnect()
	os.system("systemctl start mqtt")
	time.sleep(5)
	assert m.isConnect()
	
	f1 = foo()
	m.subscribe("ycattest",f1.recieve)
	time.sleep(0.3)
	m.send("ycattest","hello world")
	time.sleep(0.1)
	assert f1.count == 1
	assert m.isConnect()
	
	for i in range(3):
		print("restart ",i)
		os.system("systemctl stop mqtt")
		time.sleep(4)  
		assert not m.isConnect()
		os.system("systemctl start mqtt")
		time.sleep(7) 
		assert m.isConnect()
		m.send("ycattest","hello world2")
		time.sleep(0.1)
		assert f1.count == 2
		f1.count = 1
	m.close() #可以不调用 
	os.system("systemctl start mqtt")

def test3():
	def recieve(topic,data):
		print(topic,data)
	subscribe("agv/8-222/location",recieve)
	time.sleep(100)
                                
def send2():
	def foo():
		for i in range(1000):
			print("send",i)
			send("agv/" + "8-222" + "/location/" + "agv01", {'agvId':  "agv01", 'x': 1, 'y':2, "angle": 3})
			time.sleep(1)
	import threading
	t = threading.Thread(target=foo)
	t.start()
	return t
	
if __name__ == '__main__':
	#send2()
	#test3()
	#assert 0
	#for linux only 
	utility.run_tests()  
	#testmsg()

