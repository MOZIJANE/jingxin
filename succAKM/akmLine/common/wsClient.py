#coding=utf-8
# ycat			2017-12-20	  create
# websocket的封装
#https://pypi.python.org/pypi/websocket-client/ 
#pip3 install websocket-client
#pip3 install websocket
#C:\Python34\lib\site-packages\websocket\_app.py +167有bug
import sys,os
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import websocket
import threading
import time
import log
import queue
import utility

class client:
	def __init__(self):
		self.ws = None
		self.isConnected = False
		self.onOpenCallback = None
		self.queue = queue.Queue(maxsize = 1024)
		self.isExisted = False
							
	def open(self,url,recCallback = None,protocol=None):
		log.info("try open ",url)
		assert self.ws is None
		assert url[0:5] == "ws://"
		self.url = url
		self.protocol = protocol
		self._recCallback = recCallback 
		self._open()
		self._thread = threading.Thread(target=self._run)
		self._thread.start()
		for i in range(50):
			if self.isConnected:
				return True
			time.sleep(0.1)
		return False 
		
	def _open(self):
		if self.ws:
			self.ws.close()
		self.ws = websocket.WebSocketApp(self.url,on_message = self._onMessage,on_error = self._onError,on_close = self._onClose,subprotocols=self.protocol)
		self.ws.on_open = self._onOpen
		
	def close(self):
		self.isExisted = True
		self.isConnected = False
		if self.ws:
			self.ws.close()
		if self._thread is not None:
			self._thread.join()
		self._thread = None
		self.ws = None
		log.info("Close",self.url)
		
	def setDebug(self,value):
		websocket.enableTrace(value)
		
	def send(self,msg):
		assert self.ws
		log.debug("ws send:",msg)
		return self.ws.send(msg)
		
	def read(self,timeout=5):
		assert self._recCallback is None
		try:
			return self.queue.get(timeout=timeout)
		except queue.Empty:
			msg = "read ws "+self.url+" timeout "+str(timeout)
			log.warning(msg)
			raise Exception(msg)
		
	def _onError(self,error): 
		self.isConnected = False 
		log.error("ws",self.url,error)
		
	def _onClose(self):
		if self.isConnected:
			log.warning("Peer close",self.url)
		self.isConnected = False
	
	def _isIngoreMsg(self,msg):
		if type(msg) != str:
			return True
		if '"topic":"pose"' in msg: 
			return True
		if '"topic":"roadpath"' in msg: 
			return True
		if '"topic":"posPositions"' in msg: 
			return True
		if '"type":"msg_exceptionInfo","content":"moving_state,has_obstacle"' in msg:
			return True
		if '"type":"msg_exceptionInfo","content":"moving_state,no_obstacle"' in msg:
			return True
		if '"type":"msg_exceptionInfo","content":"battery_level_badly_low,0"' in msg:
			return True
		return False
	
	def _onMessage(self,msg):
		if not self._isIngoreMsg(msg):
			log.debug("ws rec:",msg)
		try:
			if self._recCallback:
				self._recCallback(msg)
			else:
				self.queue.put(msg)
		except Exception as e:
			log.exception("onMessage",e)
			raise e
		
	def _onOpen(self):
		try:
			self.isConnected = True
			log.info("Open",self.url) 
			if self.onOpenCallback:
				self.onOpenCallback()
		except Exception as e:
			log.exception("onOpen",e)
			raise e
		
	def _run(self):
		while not self.isExisted:
			self._open()
			self.ws.run_forever(ping_interval=25,ping_timeout=20)
			if self.isExisted:
				break
			time.sleep(5)
	
def echoServer():
	import asyncio
	import websockets
	
	@asyncio.coroutine
	def echo(ws, path):
		while True:
			msg = yield from ws.recv()
			print("< {}".format(msg))
			yield from ws.send(msg)

	asyncio.get_event_loop().run_until_complete(
		websockets.serve(echo, 'localhost', 8765))
	asyncio.get_event_loop().run_forever()
	
################# unit test #################
_testRec = ""

def t1estautoconn():
	t = threading.Thread(target=echoServer)
	t.start()
	
	c = client() 
	#c.setDebug(True)
	 
	url = "ws://localhost:8765"
	c.open(url)  
	for i in range(30): 
		try:
			c.send("hello ycat1")
			msg = c.read()
			assert msg == "hello ycat1"
		except Exception as e:
			print(e)
		time.sleep(1)
	c.close()
	t.join()

#t1estautoconn()
#assert 0
	 
def testwsclient():
	global _testRec
	_testRec = ""
	def onRead(msg): 
		global _testRec
		_testRec = msg
		
	c = client() 
	
	#url = "ws://172.16.73.23:3000/"
	url = "ws://echo.websocket.org/"
	#url = "ws://localhost:8765"
	assert c.open(url,onRead)  
	c.send("hello ycat1")
	for i in range(10):
		if _testRec:
			break
		time.sleep(1)
	assert _testRec == "hello ycat1"
	
	_testRec = ""
	c.send("hello ycat2")
	for i in range(10):
		if _testRec:
			break
		time.sleep(1)
	assert _testRec == "hello ycat2"
	c.close() 
	 
def testwsclient2(): 
	c = client() 
	url = "ws://echo.websocket.org/"
	#url = "ws://localhost:8765"
	assert c.open(url)  
	c.send("hello ycat1")
	assert c.read(timeout=5) == "hello ycat1"
	c.send("hello ycat2")
	assert c.read(timeout=5) == "hello ycat2"
	try:
		r = c.read(timeout=1)
		assert 0
	except Exception:
		pass
	c.close()

if __name__ == "__main__":
	import utility
	utility.run_tests()
	
	
	
	
	
	
	
	
	
	
