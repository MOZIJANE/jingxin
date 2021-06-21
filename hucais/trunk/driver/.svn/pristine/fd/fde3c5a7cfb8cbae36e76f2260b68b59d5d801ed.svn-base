#coding=utf-8
# ycat			2017-07-27	  create
# 可以用于软件统计 
import sys,os 
import threading
import datetime
#import lock
#g_lock = threading.RLock()
#@lock.lock(g_lock)
g_stat = {}
g_printResult = False

def setPrint(value):
	global g_printResult
	g_printResult = value

def ticks():
	return int(time.time()*1000)

def count(func):	
	def __call(*p,**pp):
		start = ticks()
		r = func(*p,**pp)
		title = func.__module__+"."+str(func)
		time = ticks()-start
		global g_printResult
		if g_printResult:
			print("<%s> time consumed %s ms"%(title,str(datetime.timedelta(microseconds=time))))
			
		global g_stat
		if title in g_stat:
			g_stat[title].add(time)
		else:
			b = bucket()
			b.add(time)
			g_stat[title] = b
		return r
	return __call

g_stack = {}
g_stackEnabled = False

def enableStackTrace(value):
	g_stackEnabled = value

#def stacktrace():
#	import enhance
#	g_stat
	
class counter:
	def __init__(self,name="",printFunc=None):
		self.ticks = utility.ticks()
		self.count = 0
		self.name = name
		self.printFunc = printFunc
		
	def show(self,title=""):
		t = utility.ticks()
		if self.printFunc:
			self.printFunc("[%s.%s.%02d] time consumed %d ms"%(self.name,title,self.count,t-self.ticks))
		else:
			print("[%s.%s.%02d] time consumed %d ms"%(self.name,title,self.count,t-self.ticks))
		self.ticks = t
		self.count += 1
		
class bucket:
	bucketSize = [10,100,500,1000,5000,10000,30000,sys.maxsize]
	@staticmethod
	def titles():
		r = []
		for b in bucket.bucketSize:
			if b == sys.maxsize:
				r.append("<+∞")
			else:
				r.append("<%d(ms)"%b)
		return r
			
	def __init__(self):
		self.counts = [0]*len(bucket.bucketSize)
		self.total = 0
		self.count = 0
		
	def add(self,value):
		self.total += value
		self.count += 1
		for i,c in enumerate(bucket.bucketSize): 
			if value < c:
				self.counts[i] += 1
				return
		assert 0		
	
	@property
	def average(self):
		if self.count == 0:
			return 0
		return self.total/self.count
	
		
#######################################	

if __name__ == '__main__':
	pass
