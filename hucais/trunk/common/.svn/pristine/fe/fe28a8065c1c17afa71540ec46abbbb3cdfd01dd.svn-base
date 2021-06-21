# coding=utf-8
# ycat			2021-03-27	  create
# 跟踪接口 
import sys,os
import glob
import struct
import time,datetime
import matplotlib.pyplot as plt
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__) 
import utility
import buffer
import enhance
import lock as lockImp
import json_codec as json
import log
import mytimer

#编码器，格式类型，可以主动添加，或者通过判断是否有encoder函数来自动执行 
#def encoder(obj) 返回bytearray
g_encoders = {}

TRACE_VERSION = "1.0"

def addEncoder(type,func):
	global g_encoders
	g_encoders[type.__name__] = func

class writer:
	def __init__(self,filename=""):
		self.filename = filename
		self.m_lock = lockImp.create("trace_lock")
		self.meta = {"version":TRACE_VERSION}
		self.intervals = {}
		self.interval_ticks = {}
		
		self._mapId = None
		self._map = None	#当前地图内容 
		self._currentFileWriteMap = False	#当前文件是否写入过地图 
		
		self.buf = list()   
		self._writeMetaFile = None
		
	
	#添加模型文件
	@lockImp.lock(None)
	def addConf(self,conf):
		if hasattr(conf,"getData"):
			dd = conf.getData()
		else:
			assert isinstance(conf,dict)
			dd = conf
		self.meta["_config"] = dd
		

	#添加地图文件
	@lockImp.lock(None)
	def addMap(self,filename,t=None):
		if t is None:
			t = time.time()
		f = open(filename,"rb")
		bb = f.read()
		f.close()
		self._mapId = filename
		self._map = bb
		self._currentFileWriteMap = True
		self.buf.append(("@@r:%f:%s@@"%(t,filename),bb))
		log.info("trace add map:",filename)
		
		
	@lockImp.lock(None)
	def addObj(self,key,obj,t=None):
		if key in self.intervals:
			tt = self.interval_ticks[key]
			now = utility.ticks()
			if now - self.interval_ticks[key] < self.intervals[key]:
				print("traceWriter skip",key,now)
				return False
			self.interval_ticks[key] = now
			print("traceWriter add",key)
		k = type(obj).__name__ 
		key = k + "@" + key
		if t is None:
			t = time.time()
		if k != "dict":
			if k not in g_encoders:
				raise Exception("can't find encoder for " + k)
			o = g_encoders[k](obj)
		else:
			o = json.dump(obj).encode("utf8")
		self.buf.append(("@@o:%f:%s@@"%(t,key),o))
		return True
		
	@lockImp.lock(None)
	def add(self,key,value,t=None):
		if t is None:
			t = time.time()
		if isinstance(value,float):
			self.buf.append("@@f:%f:%s@@%f"%(t,key,value))
		elif isinstance(value,int):
			self.buf.append("@@i:%f:%s@@%d"%(t,key,value))
		elif isinstance(value,dict):
			self.buf.append("@@d:%f:%s@@%s"%(t,key,json.dump(value)))
		else:
			self.buf.append("@@f:%f:%s@@%f"%(t,key,float(value)))
		
	@lockImp.lock(None)
	def addEvent(self,key,value=None,t=None):
		if t is None:
			t = time.time()
		if value is not None:
			if not isinstance(value,dict):
				log.error("traceWriter.addEvent value must be dict",type(value),value)
			assert isinstance(value,dict)
		self.buf.append("@@e:%f:%s@@%s"%(t,key,json.dump(value)))
		
	@lockImp.lock(None)
	def addLog(self,key,value=None,t=None):
		if t is None:
			t = time.time()
		if value is not None:
			assert isinstance(value,dict)
		self.buf.append("@@l:%f:%s@@%s"%(t,key,json.dump(value)))
	
	@lockImp.lock(None)
	def addAlarm(self,key,value=None,t=None):
		if t is None:
			t = time.time()
		if value is not None:
			assert isinstance(value,dict)
		self.buf.append("@@a:%f:%s@@%s"%(t,key,json.dump(value)))
		
	@lockImp.lock(None)
	def clearAlarm(self,key,value=None,t=None):
		if t is None:
			t = time.time()
		if value is not None:
			assert isinstance(value,dict)
		self.buf.append("@@c:%f:%s@@%s"%(t,key,json.dump(value)))
		
	
	def flush(self,filename=None):
		def makeFileName():
			n = utility.now()
			#i = (int)(n.hour/2)+1	#每2小时生成一个文件 
			return n.strftime("%Y%m%d")+"_%02d.data"%n.hour
		if not filename:
			filename = self.filename 
		filename = filename+makeFileName()
		return self.save(filename)
		
	@lockImp.lock(None)
	def save(self,filename):
		f = open(filename,"a+b")
		if self._writeMetaFile != filename:
			self._writeMetaFile = filename
			if len(self.meta):
				self.buf.insert(0,"@@m@%s"%json.dump(self.meta))
			if self._map is not None and not self._currentFileWriteMap:
				self.buf.insert(0,("@@r:%f:%s@@"%(0,self._mapId),self._map)) #每个文件都要带上地图 
		
		if len(self.buf) == 0:
			f.close()
			return filename 

		
		for ss in self.buf:
			f.write(b"\xAA\xBB\xCC\xDD")
			if isinstance(ss,tuple):
				bb = ss[0].encode("utf8")
				f.write(struct.pack("I",len(bb) + len(ss[1])))
				f.write(bb)
				f.write(ss[1])
			else:
				bb = ss.encode("utf8")
				f.write(struct.pack("I",len(bb)))
				f.write(bb)
		f.close()
		#log.debug("write trace count",len(self.buf))
		self._currentFileWriteMap = False
		self.buf.clear()
		return filename
		
		
	#设置元数据，用于显示 
	@lockImp.lock(None)
	def setmeta(self,key,min,max,color=None,type=None):
		pp = {"min":min,"max":max,"color":None,"type":type}
		self.meta[key] = pp
		
	def show(self):
		for v in self.buf:
			print(v)
		print()
		

if utility.is_win():
	g_trace = writer("")
else:
	_filename = os.path.join(os.path.dirname(os.path.realpath(__file__)),"../logNode/log/trace/")
	if not os.path.exists(_filename):
		os.mkdir(_filename)
	g_trace = writer(_filename)
	

def addObj(key,obj):
	return g_trace.addObj(key,obj)
	
def add(key,value):
	#assert isinstance(value,float)
	return g_trace.add(key,value)
		
def addEvent(key,value=None):
	return g_trace.addEvent(key,value)

def addLog(key,value=None):
	return g_trace.addLog(key,value)

def addAlarm(key,value=None):
	return g_trace.addAlarm(key,value)
	

def clearAlarm(key,value=None):
	return g_trace.clearAlarm(key,value)
	
	
#设置数据显示范围，用于显示 
def setmeta(key,min,max,color=None,type=None):
	return g_trace.setmeta(key,min,max,color,type)
	

def resetInterval(key):
	g_trace.interval_ticks[key] = 0

#设置最小时间间隔，防止数据量过大 
def setInterval(key,seconds):
	resetInterval(key)
	g_trace.intervals[key] = seconds*1000.0
	
	
#增加元数据 
def addmeta(key,data):
	g_trace.meta[key] = data

	
#添加模型文件
def addConf(conf):
	return g_trace.addConf(conf)
	

#添加地图文件
def addMap(smap):
	return g_trace.addMap(smap)
	
@mytimer.interval(10000)
def autoSaveData():			
	return g_trace.flush()
	
@utility.fini()
def onclose():
	log.info("trace close flush")
	g_trace.flush()
	
def show():
	g_trace.show()
	
def flush(filename=None):
	g_trace.addEvent("system.quit",{"pid":os.getpid(),"time":utility.running_time()})
	return g_trace.flush(filename)
		
##################### Unit Test #############################	
def test_trace(): 
	import slam.smap
	import traceReader
	import config 
	w = writer("./test/")
	try:
		os.remove(w.flush())
	except:
		pass
	w.setmeta("ycat.test",0,200)
	w.addConf(config)
	w.addAlarm("low_battery",{"thr":10})
	w.addMap("test/fp-neiwei.smap")
	 
	w.add("ycat.test2",100)
	w.add("ycat.test",101)
	w.addEvent("ycat_start",{"th22r":1022})
	#time.sleep(10)
	w.addEvent("ycat_stop",None)
	w.add("ycat.test2",1220)
	w.clearAlarm("low_battery")
	filename = w.flush()
	r = traceReader.reader()
	r.load(filename)
	r.setKeyFilter(list(r.keys))
	r.setEventFilter(list(r.events))
	r.setAlarmFilter(list(r.alarms))
	r.map.show()
	print(r.getConf())
	#r.setKeyFilter("ycat.test")
	r.show()
	
def testwrite():
	#测试同时写文件的效果 
	import threading
	def run1(i):
		f = open("./test.log","a+t")
		for k in range(10):
			f.write(str(k+i)+"\n") 
			time.sleep(1)
			print(threading.currentThread().ident,k+i)
		f.close()
	t1 = threading.Thread(target=run1,args=[0,])
	t1.start()
	t2 = threading.Thread(target=run1,args=[10000,])
	t2.start()
	t1.join()
	
def test_map(): 
	import slam.smap
	import traceReader
	import config 
	w = writer("./test/")
	
	try:
		os.remove(w.flush("./test/test1"))
	except:
		pass
		
	try:
		os.remove(w.flush("./test/test2"))
	except:
		pass  
	w.addMap("test/fp-neiwei.smap")
	f1 = w.flush("./test/test1")
	f2 = w.flush("./test/test2")
	r1 = traceReader.reader()
	r1.load(f1)
	r2 = traceReader.reader()
	r2.load(f2)
	print(r1.map,r2.map)
	
	
if __name__ == '__main__':
	test_map()
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
