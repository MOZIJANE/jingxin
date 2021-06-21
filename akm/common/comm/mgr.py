#coding=utf-8 
# ycat			 2014/05/20      create
import os,time,sys
import zmq		#pip install zmq
import threading
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import log	 
import json_codec
import utility
import lock
import pickle

# 协议规定
# 1. 采用json编码，为了支持反射，把类名也编进json中
# 2. 格式为frame1为类型，frame2为json内容
# 3. 错误编码为负数的类型,其中客户端可发送-100让服务端退出 

KILL_SIGNAL = -907513130 #一串随机数，保证不重即可... 

def _decode(headtext,text):
	try:
		if utility.is_python3():
			headtext = headtext.decode("utf-8")
			text = text.decode("utf-8")
		t = json_codec.load(headtext)
		obj = json_codec.load(text)
		return (t,obj)
	except Exception as e:
		log.exception("mgr.decode",e)
		raise e
		

def _decode2(text):
	try:
		if utility.is_python3():
			text = text.decode("utf-8")
		return json_codec.load(text)
	except Exception as e:
		log.exception("mgr.decode2",e)
		raise e
		
def _decode3(headtext,text):
	try:
		#if utility.is_python3():
		#	headtext = headtext.decode("utf-8")
		#t = json_codec.load(headtext)
		t = pickle.loads(headtext)
		obj = pickle.loads(text)
		return (t,obj)
	except Exception as e:
		log.exception("mgr.decode",e)
		raise e

def _encode(typeid,obj):
	s = json_codec.dump(obj,True)
	t = json_codec.dump(typeid,True)
	if utility.is_python3():
		t = t.encode("utf-8")
		s = s.encode("utf-8") 	
	return (t,s)

def _encode2(obj):
	s = json_codec.dump(obj,True)
	if utility.is_python3():
		return s.encode("utf-8")
	else:
		return s
		
def _encode3(typeid,obj):
	s = pickle.dumps(obj)
	t = pickle.dumps(typeid)
	return (t,s)

_g_context = zmq.Context.instance(10)

def create_socket(socket_type):
	global _g_context
	return _g_context.socket(socket_type)

_g_poll_thread = None
_g_poll_lock = threading.RLock()
_g_poll_map = {}
_g_poll = zmq.Poller()
_g_existed = False

@lock.lock(_g_poll_lock)
def register(socket,func):
	global _g_poll,_g_poll_map
	_g_poll.register(socket,zmq.POLLIN)
	_g_poll_map[socket] = func
	log.debug("add poller len=%d"%len(_g_poll_map))

@lock.lock(_g_poll_lock)
def deregister(socket):
	global _g_poll,_g_poll_map
	if socket in _g_poll_map:
		_g_poll.unregister(socket)
		del _g_poll_map[socket]
	log.debug("del poller len=%d"%len(_g_poll_map))	

def register_count():
	global _g_poll_map
	return len(_g_poll_map)

@utility.catch
def _poll_thread_func():
	global _g_poll_lock
	global _g_poll_map
	@lock.lock(_g_poll_lock)
	def get_poll_socks(socks):
		r = []
		for s in _g_poll_map:
			if socks.get(s) == zmq.POLLIN:
				r.append(_g_poll_map[s])
		return r
	
	global _g_poll,_g_existed,_g_poll_map
	while not _g_existed:
		try:
			if len(_g_poll_map) == 0:
				time.sleep(0.3)
				continue
			socks = dict(_g_poll.poll(2000))
			funcs = get_poll_socks(socks)
			if len(funcs) == 0:
				pass #timeout 
			for f in funcs:
				f()
		except zmq.error.ZMQError as e:
			log.exception("poll",e)
		except zmq.ContextTerminated as e:
			break
	
	@lock.lock(_g_poll_lock)
	def close_all_socks():
		global _g_poll_map
		for s in _g_poll_map:
			_g_poll.unregister(s)
			s.close()
		_g_poll_map = {}	
			
	close_all_socks()
	log.warning("poller thread quited,pid=",os.getpid())	

#@utility.init()
def start():
	global _g_poll_thread,_g_poll_map,_g_existed
	if _g_poll_thread:
		return 
	_g_existed = False
	_g_poll_thread = threading.Thread(target=_poll_thread_func)
	log.warning("start comm.mgr, len = %d"%len(_g_poll_map),",pid =",os.getpid())		
	_g_poll_thread.start()

def wait():
	global _g_poll_thread
	if _g_poll_thread is None:
		return
	_g_poll_thread.join()
	_g_poll_thread = None

#@utility.fini()
def close(wait_thread=True):
	global _g_existed,_g_context
	_g_existed = True
	#_g_context.term()
	if wait_thread:
		wait()
	log.warning("close comm.mgr, pid =",os.getpid(),id(_g_existed))		
	
_close = close
	
def close_socket(socket):
	if socket is None:
		return 
	socket.setsockopt(zmq.LINGER, 0)
	deregister(socket)
	socket.close()
	
g_names = None	
def set_names(func):
	global g_names
	g_names = func
	
def get_names(addr):
	if g_names is None:
		return addr
	if addr[0:6] == "tcp://":
		return addr 
	return g_names(addr)

if __name__ == '__main__':
	pass
			