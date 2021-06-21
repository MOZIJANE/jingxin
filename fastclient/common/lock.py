#coding=utf-8 
# ycat	  2015/05/14      create
import sys,os
import threading,time
import log,utility

g_lock_names = {}

def _getLockName(lockObj):
	global g_lock_names
	i = id(lockObj)
	if i in g_lock_names:
		return "<lock name:"+g_lock_names[i] +"," + str(lockObj) + ">"
	return str(lockObj)

#checkTime表示是否判断长时间占锁 
def create(name):
	global g_lock_names
	r = threading.RLock()
	g_lock_names[id(r)] = name
	log.info("create lock",_getLockName(r))
	return r
	
def empty():
	assert 0

def get_thread_id():
	return threading.current_thread().ident

def sleep(seconds):
	time.sleep(seconds)

def try_lock(lock):
	return lock.acquire(blocking=False)

def get_stack():
	import inspect
	r = ""
	s = inspect.stack()
	for ss in s:
		r += str(ss) + "\n"
	return r

class lockInfo:
	def __init__(self,lockObj,ticks):
		self.ticks = ticks
		self.count = 1
		self.lockObj = lockObj
		t = threading.currentThread()
		self.tid = t.ident
		self.tname = t.name
	
	def __str__(self):
		return "%s[tid:%d] %s ,hold %d ms"%(self.tname,self.tid,_getLockName(self.lockObj),utility.ticks()-self.ticks)
		

g_lockInfo = {}
g_waitInfo = {}

def _getKey(tid,obj):
	return str(tid)+"."+str(id(obj))

def acquire(lockObj):
	global g_lockInfo,g_waitInfo
	ticks = utility.ticks()
	tid = threading.currentThread().ident
	tname = threading.currentThread().name
	key = _getKey(tid,lockObj)
	
	g_waitInfo[key] = (tname,tid,lockObj,ticks)
	
	while not lockObj.acquire(timeout=60):
		import log
		l = "try get lock failed! lock={0} name={1} tid={2}".format(_getLockName(lockObj),tname,tid)
		log.error(l)
		s = show()
		import enhance
		s = enhance.getTrace(showAll=True)
		log.info(s)
		
	del g_waitInfo[key]
	
	if key not in g_lockInfo:
		g_lockInfo[key] = lockInfo(lockObj,ticks)
	else:
		g_lockInfo[key].count += 1
			
	
def release(lockObj):
	global g_lockInfo
	tid = threading.currentThread().ident
	key = _getKey(tid,lockObj)
	if key in g_lockInfo:
		count = g_lockInfo[key].count
		if count == 1:
			dt = utility.ticks() - g_lockInfo[key].ticks
			if dt > 3000:
				log.warning(str(g_lockInfo[key]))
				import enhance
				s = enhance.getTrace()
				log.info(s)
			del g_lockInfo[key]
		else:
			g_lockInfo[key].count = count - 1

	if lockObj._is_owned():
		lockObj.release()
	
 
#自动处理异常的修饰符
#@lock(None) 可用于成员函数，这里要求该类有m_lock的对象 
def lock(lock_obj):
	def call(func):
		def _call(*p,**pp):
			obj = lock_obj
			if lock_obj is None:
				obj = p[0].m_lock
			acquire(obj)
			try:
				return func(*p,**pp)
			finally: 
				release(obj)
		_call.__name__ = func.__name__
		return _call
	return call


def show():
	#g_lock.acquire()
	s = "lock info: count %d\n"%len(g_lockInfo)
	for p in g_lockInfo:
		if g_lockInfo[p].count == 0:
			continue
		s += str(g_lockInfo[p])+"\n"
	
	s += "\ntry lock info: count %d\n"%len(g_waitInfo)
	for p in g_waitInfo.values():
		s += "%s[tid:%d] %s ,wait %d ms\n"%(p[0],p[1],str(p[2]),utility.ticks()-p[3])
	log.info(s)
	return s

########################## unit test ############################

			
def test_lock_class():
	class aaa:
		def __init__(self):
			self.m_lock = threading.RLock()
			self.v = 0
			
		@lock(None)
		def add(self):
			v = self.v
			time.sleep(1)
			self.v = v + 1
			return v
			
	a = aaa()
	def rr():
		for i in range(5):
			print(a.add())
			time.sleep(1)
		
	t = threading.Thread(target=rr)
	t.start()
	t2 = threading.Thread(target=rr)
	t2.start()
	t.join()
	t2.join()
		
def test_lock_decorate():
	ll = threading.RLock()
	d = {0:0}
	threads = []
	@lock(ll)
	def lockfunc1(dd):
		a = dd[0]
		sleep(1)
		dd[0] = a+1 

	def thread_func(d):
		for i in range(3):
			lockfunc1(d)

	for i in range(2):
		threads.append(threading.Thread(target=thread_func,args=(d,)))
	for t in threads:
	        t.start()
	for t in threads:
		t.join()
	assert ll.acquire()
	ll.release()
	assert d[0] == len(threads)*3
	
	#test exception
	@lock(ll)
	def errorfunc():
		raise Exception("lalalala")
	
	def thread_func2():
		try:
			errorfunc()
		except Exception:
			pass
		
	t = threading.Thread(target=thread_func2)
	t.start()
	t.join()
	assert try_lock(ll)
	ll.release()

def test_lock():
	#test recursive lock
	def thread_func1(lock):
		assert not try_lock(lock)
	lock = threading.RLock()	
	lock.acquire()
	assert lock.acquire()
	assert lock.acquire()
	assert try_lock(lock)
	t = threading.Thread(target=thread_func1,args=(lock,))
	t.start()
	sleep(1)
	t.join()
	lock.release()
	lock.release()
	lock.release()
	lock.release()
	
	def thread_func(ll,d):
		for i in range(3):
			ll.acquire()
			a = d[0]
			sleep(1)
			d[0] = a+1
			ll.release()
			
	d = {0:0}
	threads = []
	for i in range(2):
		threads.append(threading.Thread(target=thread_func,args=(lock,d)))
	for t in threads:
	        t.start()
	for t in threads:
		t.join()
	assert d[0] == len(threads)*3

def test_lock_timeout():
	def thread_func1(lock):
		assert lock.acquire()
		sleep(10)
		lock.release()
	ll = threading.RLock()		
	t = threading.Thread(target=thread_func1,args=(ll,))
	t.start()
	@lock(ll)
	def get_lock():
		print("get_lock")
	get_lock()
	t.join()

def catch(func):
	def __call(*p):
		try:
			return func(*p)
		except:
			print("11")
			
	return __call

test_ll = threading.RLock()
@catch
@lock(test_ll)
def test_multiTry():
	raise "hello"
	

if __name__ == '__main__':
	import utility
	test_lock_class()
	assert 0
	test_multiTry()
	test_lock_decorate()
	
	test_lock_timeout()
	test_lock()
	print("test finish")
	#utility.run_tests()

