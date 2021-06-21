#-*- coding: utf-8 -*--
import json
import platform  
import sys,os
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)  
import mqtt
import utility
import config
import queue
import mytimer
import log

class mqueue:
	def __init__(self,session,maxsize,timeoutSec):
		self.session = session
		self.timeout = timeoutSec*1000
		self.ticks = mytimer.ticks()
		self.queue = queue.Queue(maxsize = maxsize)
		self.topics = set()
	
	def subscribe(self,topic):
		mqtt.subscribe(topic,self._callback)
		self.topics.add(topic)
	
	def close(self):
		if len(self.topics):
			mqtt.unsubscribe(self._callback) 
	
	def _callback(self,topic,data):
		self._put(topic,data)
	  
	def _put(self,topic,dict):
		while self.queue.full():
			self.queue.get_nowait()
		self.queue.put((topic,dict))
		
	def get(self):
		self.ticks = mytimer.ticks()
		if self.queue.empty():
			return None
		return self.queue.get_nowait()
		
	def isTimeout(self,now):
		t = now - self.ticks
		if t > self.timeout:
			return True
		else:
			return False
				

g_queues = {} 

def create(session,queueNum,timeoutSec):
	global g_queues
	if session in g_queues:
		return g_queues[session]
	m = mqueue(session,queueNum,timeoutSec)
	g_queues[session] = m
	return m
	

def subscribe(session,topic):
	return _getQueue(session).subscribe(topic)
 
def send(topic,data):
	mqtt.send(topic,data)	
	
def get(session):
	return _getQueue(session).get()

def _getQueue(session):
	global g_queues
	if session  not in g_queues:
		raise Exception("wmqtt找不到Session:"+str(session))
	return g_queues[session]	
	
@mytimer.interval(300*1000)	
def _checkTimeout():  
	global g_queues
	now = mytimer.ticks()
	delList = []
	for q in g_queues: 
		if g_queues[q].isTimeout(now):
			g_queues[q].close()
			delList.append(q)
	for d in delList:  
		del g_queues[d]
		log.info("delete timeout queue",d)
	
##################### unit test ##################### 
def testweb():
	def func():
		os.system("python main_wmqtt.py") 
	import threading,time
	import webutility
	t = threading.Thread(target=func)
	t.start()
	time.sleep(0.8)
	ret = webutility.http_get("http://127.0.0.1:20013/api/wmqtt/create",{"session":"ycatwebtest","maxSize":5,"timeSec":60})
	ret = webutility.http_get("http://127.0.0.1:20013/api/wmqtt/get",{"session":"ycatwebtest"})
	ret = json.loads(ret)
	assert ret["data"] == None
	assert ret["topic"] == None
	
	send("ycat1/yyy/11/222",{"data":1})
	ret = webutility.http_get("http://127.0.0.1:20013/api/wmqtt/get",{"session":"ycatwebtest"})
	ret = json.loads(ret)
	assert ret["data"] == None
	assert ret["topic"] == None
	
	ret = webutility.http_get("http://127.0.0.1:20013/api/wmqtt/register",{"session":"ycatwebtest","topic":"ycat1/#"})
	time.sleep(0.5)
	send("ycat1/yyy/11/222",{"data":2})
	time.sleep(0.5)
	ret = webutility.http_get("http://127.0.0.1:20013/api/wmqtt/get",{"session":"ycatwebtest"})
	ret = json.loads(ret)
	assert ret["topic"] == "ycat1/yyy/11/222"
	assert ret["data"] ==  {"data": 2}
	utility.killThread(t) 
	#TODO:这个测试会退不出 
	
#支持通配符	
def testqueue2(): 
	import time
	create("ycattest9",1,3600)
	subscribe("ycattest9","ycat1/#")  
	assert get("ycattest9") == None
	
	send("ycat1/yyy/11/222",{"data":1})
	time.sleep(1)
	r = get("ycattest9") 
	assert r 
	assert r == ("ycat1/yyy/11/222",{"data":1}) 
	
def testtimeout(): 
	import time
	global g_queues
	q1 = create("ycattest11",9,10*60)
	q2 = create("ycattest22",9,10*60)
	subscribe("ycattest11","ycat/test1")
	subscribe("ycattest22","ycat/test2")
	assert "ycattest11" in g_queues
	assert "ycattest22" in g_queues
	
	time.sleep(3)
	mytimer.set_pass_ticks(5*60*1000+1000)
	time.sleep(1.5)
	assert "ycattest11" in g_queues
	assert "ycattest22" in g_queues
	
 
	get("ycattest11")
	time.sleep(3.5)
	mytimer.set_pass_ticks(5*60*1000+1000)
	time.sleep(1.5) 
	assert "ycattest11" in g_queues 
	assert "ycattest22" not in g_queues
	
	time.sleep(5)
	mytimer.set_pass_ticks(5*60*1000+1000)
	time.sleep(1.5)
	assert "ycattest11" not in g_queues 
	
def testput():
	q = create("ycattest6",1,3600)
	q._put("ytopic",{"data":1111})
	assert q.get() == ("ytopic",{"data":1111})
	assert q.get() == None
	assert q.get() == None
	q._put("ytopic",{"data":1112})
	q._put("ytopic",{"data":1113})
	q._put("ytopic",{"data":1114})
	assert q.get() == ("ytopic",{"data":1114})
	assert q.get() == None
	assert q.get() == None
	
	q = create("ycattest5",4,3600)
	for i in range(1000):
		q._put("ytopic",{"data":i})
	assert q.get() == ("ytopic",{"data":996})	
	assert q.get() == ("ytopic",{"data":997})
	assert q.get() == ("ytopic",{"data":998})
	assert q.get() == ("ytopic",{"data":999})
	assert q.get() == None


	
def testqueeu():	
	import time
	create("ycattest",1,3600)
	create("ycattest2",2,3600)
	subscribe("ycattest","ycat1")
	subscribe("ycattest","ycat2")
	subscribe("ycattest","ycat3")
	subscribe("ycattest2","ycat1")
	assert get("ycattest") == None
	
	send("ycat1",{"data":1})
	time.sleep(0.5)
	assert get("ycattest") == ("ycat1",{"data":1})
	assert get("ycattest2") == ("ycat1",{"data":1})
	assert get("ycattest") == None
	assert get("ycattest2") == None
	send("ycat1",{"data":2})
	time.sleep(0.5)
	assert get("ycattest") == ("ycat1",{"data":2})
	assert get("ycattest2") == ("ycat1",{"data":2})
	assert get("ycattest2") == None
	assert get("ycattest") == None
	send("ycat1",{"data":3})
	time.sleep(0.5)
	send("ycat1",{"data":4})
	time.sleep(0.5)
	send("ycat1",{"data":5})
	time.sleep(0.5)
	assert get("ycattest") == ("ycat1",{"data":5})
	assert get("ycattest") == None
	assert get("ycattest2") == ("ycat1",{"data":4})
	assert get("ycattest2") == ("ycat1",{"data":5})
	assert get("ycattest2") == None
	send("ycat3",{"data":15})
	time.sleep(0.5)
	assert get("ycattest2") == None
	assert get("ycattest") == ("ycat3",{"data":15})
	try:
		get("nonono")
		assert 0
	except Exception as e:
		pass
	try:
		register("nonono","ycat1")
		assert 0
	except Exception as e:
		pass
		
if __name__ == '__main__':   
	import utility
	utility.start()
	utility.run_tests()
	utility.finish()
	


