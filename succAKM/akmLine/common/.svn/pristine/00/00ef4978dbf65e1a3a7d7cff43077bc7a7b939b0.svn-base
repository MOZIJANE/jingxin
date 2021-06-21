#coding=utf-8
# ycat			2017-07-27	  create
# 可以用于软件统计 
import sys,os 
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import utility
import threading
import datetime
import enhance
import log 
import numpy as np

g_stat = {}
g_printResult = False

def setPrint(value):
	global g_printResult
	g_printResult = value

def count(func):	
	def __call(*p,**pp):
		start = utility.ticks()
		r = func(*p,**pp)
		title = func.__module__+"."+str(func)
		diff = utility.ticks()-start
		global g_printResult
		if g_printResult:
			print("<%s> time used %d ms"%(title,diff))
			
		global g_stat
		if title in g_stat:
			g_stat[title].add(diff)
		else:
			b = bucket(name = str(func.__name__))
			b.add(diff)
			g_stat[title] = b
		return r
	__call.__name__ = func.__name__
	return __call
	
	
def show():
	import matplotlib.pyplot as plt 
	for i,b in enumerate(g_stat.values()):
		b.draw(plt,i) 
	plt.legend(loc='upper right')
	plt.show()
	

	
class counter:
	def __init__(self):
		self.ticks = utility.ticks()
		self.count = 0
	
	def get(self):
		return self._writeLog(None,enhance.fileInfo(),seconds=0)
	
	def check(self,msg="",seconds=0): 
		return self._writeLog(print,enhance.fileInfo(),seconds)
		
	def _getMsg(self,msg,diff,fileInfo): 
		if msg:
			ret = "[%02d][%s] %s used %d ms"%(self.count,str(msg),fileInfo,diff)
		else:
			ret =  "[%02d] %s used %d ms"%(self.count,fileInfo,diff) 
		return ret 
	
	def info(self,msg="",seconds=0): 
		self._writeLog(log.info,enhance.fileInfo(),msg,seconds)
		
	def warning(self,msg="",seconds=0):	
		self._writeLog(log.warning,enhance.fileInfo(),msg,seconds)

	def error(self,msg="",seconds=0):
		self._writeLog(log.error,enhance.fileInfo(),msg,seconds)
		
	def _writeLog(self,printFunc,fileInfo,msg="",seconds=0):
		t = utility.ticks()
		diff =  t - self.ticks
		if diff < seconds*1000: 
			self.ticks = t 
			self.count += 1 
			return  
		if printFunc:
			printFunc(self._getMsg(msg,diff,fileInfo))
		self.ticks = t 
		self.count += 1 
		return diff 
		
		
class bucket:
	defaultSize = [10,100,500,1000,5000,10000,30000,sys.maxsize]
	 
	def __init__(self,name="",bucketSize=None):
		if bucketSize is None:
			bucketSize = bucket.defaultSize
		self.name = str(name)
		self.bucketSize = bucketSize
		self.counts = [0]*len(bucketSize)
		self.total = 0
		self.count = 0
		
	def add(self,value):
		self.total += value
		self.count += 1
		for i,c in enumerate(self.bucketSize): 
			if value < c:
				self.counts[i] += 1
				return
		assert 0		
	
	@property
	def average(self):
		if self.count == 0:
			return 0
		return self.total/self.count
		
	def titles(self):
		r = []
		for b in self.bucketSize:
			if b == sys.maxsize:
				r.append("<+∞")
			else:
				r.append("<%d(ms)"%b)
		return r
		
	def draw(self,plt,index = 0):
		w = 0.3
		tt = self.titles()
		yy = [ c for c in self.counts] 
		xx = [i + index*w for i in range(len(tt))] 
		plt.bar(xx,yy,label=self.name+" ("+str(self.count)+")",width=w) 
		for i, y in enumerate(yy):
			plt.text(i + index*w, y, str(y) if y != 0 else None, ha='center', va='top', fontsize=10) 
		plt.xticks(xx,self.titles())
		
	def show(self): 
		import matplotlib.pyplot as plt 
		t = "total count %d\ntotal %d,average %f"%(self.count,self.total,self.average)
		if self.name:
			t = self.name + "\n" + t
		plt.title(t, fontsize=10)
		self.draw(plt) 
		plt.show()
	
		
#######################################	
def testbucket():
	b = bucket("unit test")
	assert b.average == 0
	assert b.total == 0
	assert b.count == 0
	b.add(2)
	b.add(8)
	b.add(9)
	b.add(8)
	b.add(0)
	assert b.counts[0] == 5
	assert b.count == 5
	assert b.average == 5.4
	b.add(1001)
	b.add(1002)
	b.add(1003)
	assert b.counts[1] == 0
	assert b.counts[2] == 0
	assert b.counts[3] == 0
	assert b.counts[4] == 3
	assert b.count == 8
	b.add(999999999)
	b.add(999999991)
	assert b.counts[5] == 0
	assert b.counts[6] == 0
	assert b.counts[7] == 2
	assert b.count == 10
	b.show()
	 
	
def testcount():
	setPrint(True)
	import time
	@count
	def foo(t):
		time.sleep(t) 
	foo(0.1)		
	c = counter()
	time.sleep(0.5)
	c.check()
	time.sleep(0.2)
	c.check()
	import log
	@count
	def foo2(t):
		time.sleep(t)
		return 1
	foo2(0.2) 
	foo2(0.1)
	foo2(0)
	foo(0.5)		
	foo2(0.3)
	show()
	
def testwritelog():
	import time
	c = counter()
	time.sleep(0.2)
	c.warning("ycat test",0.1) #显示
	time.sleep(0.2)
	c.error(0.1)	#显示
	time.sleep(0.1)
	c.error("ycat test",0.5)  #不显示 
	
if __name__ == '__main__':
	testwritelog()
	import utility
	utility.start() 
	testcount()
	
	utility.run_tests()
