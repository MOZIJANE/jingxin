#coding=utf-8 
# ycat			 2014/04/08      create
import os,time,sys
import threading
import time
import utility 
import log
import lock as lockImp

g_ticks = 0	
def set_pass_ticks(ms):
	global g_ticks	
	g_ticks += ms

def ticks():
	global g_ticks		
	return g_ticks + int(time.time()*1000) 		

sleepH = time.sleep

if utility.is_win():
	import time,ctypes
	g_longlong = ctypes.c_longlong(0)
	ctypes.windll.kernel32.QueryPerformanceFrequency(ctypes.byref(g_longlong))
	g_freq = g_longlong.value/1000.
	
	def ticks():
		global g_ticks
		v = ctypes.c_longlong(0)
		ctypes.windll.kernel32.QueryPerformanceCounter(ctypes.byref(v))
		return v.value/g_freq + g_ticks
	
	ticksH = ticks
	
	def sleepH(sec):
		s = ticks()
		while True:
			if ticks() - s > sec*1000:
				break
			pass

class timer:	
	class timer_info:
		def __init__(self,func,ms,args,repeat):
			self.func = func
			self.timeout = ticks() + ms
			self.ms = ms
			self.args = args
			self.repeat = repeat
		
	def __init__(self,sleepMs=1000): 
		self.m_lock = lockImp.create("timer.lock_"+str(id(self)))
		self._time_map = {}
		self._thread = None
		self._exited = False
		self._id = 0
		self.sleepSec = sleepMs/1000
		if self.sleepSec == 0:
			self.sleepSec = 1
	
	def __del__(self):
		#self.stop()
		pass
	
	def setTimeout(self,func,timeoutMs,args=()):
		#只调用一次func，返回timerID 
		return self._add_timer(func,timeoutMs,args,False)
	
	def setInterval(self,func,timeoutMs,args=()):
		#会循环调用func，返回timerID 
		#log.error("register",func,timeoutMs) 
		return self._add_timer(func,timeoutMs,args,True)
	
	@lockImp.lock(None)
	def remove(self,timeID):
		self._remove_timer(timeID)
	
	def init(self):
		if self._thread:
			return
		assert not self._exited 
		log.debug("start timer")
		self._thread = threading.Thread(target=self._loop,name="timer_thread")
		self._thread.start()
	
	def fini(self):
		self._exited = True
		if self._thread:
			self._thread.join()
	
	def _loop(self): 
		while not self._exited: 
			removeList = []
			callbackList = []
			now = ticks()
			lockImp.acquire(self.m_lock)
			for key in self._time_map:
				value = self._time_map[key]
				if now >= value.timeout:
					callbackList.append(value)
					if value.repeat:
						value.timeout = now + value.ms
					else:
						removeList.append(key)
			
			for k in removeList:
				self._remove_timer(k)
				
			lockImp.release(self.m_lock)
			
			for v in callbackList:
				try:
					v.func(*v.args)
				except Exception as e:
					log.exception("invoke timer func"+str(v.func),e)
				
			time.sleep(self.sleepSec) 

	@lockImp.lock(None)
	def _add_timer(self,func,ms,args,repeat):
		while True:
			self._id+=1
			if self._id not in self._time_map:
				break
		id = self._id 
		self._time_map[id] = timer.timer_info(func,ms,args,repeat)
		return id
	
	def _remove_timer(self,key):
		if key in self._time_map:
			del self._time_map[key]
		
g_timer = None

#全局函数只注册一次 
def _findFunc(func):
	global g_timer
	import enhance
	if g_timer is None:
		return False
	name = enhance.funcname(func)
	for t in g_timer._time_map.values():
		if name == enhance.funcname(t.func): 
			return True
	return False
		
	
#实现定时器的修饰符
def timeout(timeoutMs):
	def __call(func):
		global g_timer
		if g_timer is None:
			g_timer = timer() 
		if _findFunc(func):
			return func
		g_timer.setTimeout(func,timeoutMs)
		return func
	# __call.__name__ = func.__name__
	return __call

@utility.init()
def init():
	global g_timer 
	if g_timer is None:
		g_timer = timer()
	g_timer.init() #解决bottle多进程情况 
		
	
#实现定时器的修饰符
def interval(timeoutMs):
	def __call(func): 
		global g_timer
		if g_timer is None:
			g_timer = timer() 
		if _findFunc(func):
			return func
		g_timer.setInterval(func,timeoutMs)
		return func
	# __call.__name__ = func.__name__
	return __call

@utility.fini()
def fini():
	global g_timer
	if g_timer:
		g_timer.fini()
 		

########## for unit test ############
y = x = 1000
def my_func1(step):
	global x
	x = x+step

def my_func2(step):
	global y
	y = y+step	
	
def testinterval():
	utility.start()
	global y,x
	x = y =0
	@interval(1000)
	def foo():
		global y 
		y += 1
		
	@timeout(1000)
	def foo2():
		global x 
		x += 1
	time.sleep(3.8) 
	assert y == 3
	assert x == 1
	utility.finish()
	
def test_setInterval():
	utility.start()
	t = timer(200)
	t.init()
	global x,y
	y = x = 1000
	id = t.setInterval(my_func1 ,2001,(1,))
	id2 = t.setInterval(my_func2 ,2002,(2,))
	assert 2 == len(t._time_map)
	time.sleep(1.2)
	assert x == 1000
	assert y == 1000
	time.sleep(1.2)
	assert x == 1001
	assert y == 1002 #timeout

	time.sleep(2.2)
	assert x == 1002
	assert y == 1004
	assert 2 == len(t._time_map)
	t.remove(id2)
	assert 1 == len(t._time_map)
	
	time.sleep(2.2)
	assert x == 1003
	assert y == 1004
	assert 1 == len(t._time_map)
	t.fini()
	
def test_setTimeout():
	utility.start()
	t = timer(200)
	t.init()
	global x,y
	y = x = 1000
	id = t.setTimeout(my_func1 ,1000,(1,))
	assert 1 == len(t._time_map)
	assert id == 1
	id2 = t.setTimeout(my_func2 ,1000,(2,))
	assert 2 == len(t._time_map)
	assert id2 == 2
	
	id3 = t.setTimeout(my_func2 ,4000,(2,))
	assert 3 == len(t._time_map)
	assert id3 == 3
	
	time.sleep(1.2)
	assert 1 == len(t._time_map)
	assert x == 1001
	assert y == 1002
	
	time.sleep(1.2)
	assert 1 == len(t._time_map)
	t.remove(id3)
	assert 0 == len(t._time_map)
	t.remove(1545)
	assert x == 1001
	assert y == 1002
	t.fini()     
	 
def testticks():
	import ctypes
	import PyQt5.QtCore 
	err = 0
	for i in range(100):
		t1 = ticks()
		sleepH(0.01)
		t2 = ticks()
		err += abs(t2 - t1 - 10)
	assert err < 10  #总误差不超过10ms 
	
	t1 = ticks()
	sleepH(0.1)
	t2 = ticks()
	assert abs(t2-t1) < 101
	assert abs(t2-t1) > 99
	 
if __name__ == '__main__':
	sleepH(10000)
	testticks()
	utility.run_tests()
	#testinterval()
			
