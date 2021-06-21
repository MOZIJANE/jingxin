#coding=utf-8
# ycat			2020-06-27	  create
# 可以用于软件统计内存情况 
import sys,os 
import io
import threading
import datetime
g_enable = True

if g_enable:
	import memory_profiler	#	pip install memory_profiler
	
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import utility
import mytimer
import log

def getMem():
	mem = memory_profiler.memory_usage(-1)
	if len(mem):
		return mem[0]
	return 0


g_stat = {}
g_last_mem = getMem()
g_stream = io.StringIO()
MIN_MEMORY = 10

def check(func):	
	if not g_enable:
		return func
	return memory_profiler.profile(func,precision=2,stream=g_stream)  

	
class funcInfo:
	def __init__(self):
		self.filename = None
		self.funcname = None
		self.count = 0
		self.mem = 0	#增加内存 
		self.lineno = 0
		self.lines = [] #(lineno,mem,linestr) 
	
	def __str__(self):
		if self.mem < MIN_MEMORY:
			return ""
		f = self.funcname
		if len(f) > 30:
			f = f[0:30]
		n = os.path.basename(self.filename)
		#s = "%s+%d %s :\t%0.2f Mb	|\t%d times\n"%(n,self.lineno,f,self.mem,self.count)
		s = "%s\tline %d\t\tmem %0.2f Mb\t\t'%s'\t\t%d times\n"%(n,self.lineno,self.mem,f,self.count)
		for line in self.lines:
			if line[1] < MIN_MEMORY:
				continue
			s += "\t\tline %d\tmem %0.2f Mb\t\t'%s' \n"%(line[0],line[1],line[2])
		return s
		
	
	def show(self):
		log.info(str(self))
	
@utility.fini()
def show():
	global g_last_mem
	g_stream.seek(0)
	data = g_stream.read()
	if not data:
		return 
		
	_decode(data)
	
	if not g_stat:
		return
	
	ss = sorted(list(g_stat.values()),key=lambda x:x.mem,reverse=True)
	
	mem = getMem()
	v = "\n==================== Memmory usage %0.2f Mb, diff %0.2f Mb ====================\n"%(mem,mem-g_last_mem)
	g_last_mem = mem
	
	for s in ss:
		t = str(s)
		if not t:
			continue
		v += t + "\n"
	log.info(v)
		
@mytimer.interval(10000)
def autoShow():
	if g_enable:
		show()
	

def _decode(data):
	lineno = 0
	mem = 0
	increment = 0
	current = None
	current_file = None
	current_func = None
	lineStr = None
	mem = 0
	
	firstLine = False
	secondLine = False
	
	for line in data.splitlines():
		if len(line) == 0:
			continue
		if line.startswith("Filename: "):
			current_file = line[len("Filename: "):].strip()
			continue                               
		if line.startswith("Line"):
			continue
		if line.startswith("===="):
			firstLine = True
			secondLine = False
			continue
		
		if line.find(" MiB  ") == -1 and not secondLine:
			continue
		#['68', '17.50', 'MiB', '17.50', 'MiB   @memory_profiler.profile(precision=2,stream=g_stream)']
		#['69', 'def', 'testtt2():']
		#['70', '27.04', 'MiB', '9.54', 'MiB        import numpy as np']
		#['71', '27.11', 'MiB', '0.07', 'MiB        a = np.zeros((1024,1024*1024*4*8),dtype=np.uint8)']
		ss = line.split(maxsplit=5)
		f = funcInfo()
		
		if firstLine:
			firstLine = False
			secondLine = True
			mem = float(ss[3])
			continue
		if secondLine:
			secondLine = False
			current_func = ss[2][0:-1]
			key = current_file +"."+current_func
			if key not in g_stat:
				current = funcInfo()
				current.filename = current_file
				current.funcname = current_func
				current.mem = mem
				current.lineno = int(ss[0])
				current.count = 1
				g_stat[key] = current
			else:
				current = g_stat[key] 
				current.count += 1
				current.mem += mem
			continue
		else:
			lineno = int(ss[0])
			lineStr = ss[5]
			if len(lineStr) > 50:
				lineStr = lineStr[0:50]
			mem = float(ss[3])
			for l in current.lines:
				if l[0] == lineno:
					l[1] += mem
					break
			else:
				current.lines.append([lineno,mem,lineStr])
	

@check  
def testtt():
	import numpy as np
	a = np.zeros((1024,1024*1024*4*8),dtype=np.uint8)
	return a
	
@check           
def testtt2():
	import numpy as np
	a = np.zeros((1024,1024*1024*4*8),dtype=np.uint8)
	if True:
		pass
	return a
	
	
def testdecode():
	s = r"""

Filename: D:\Mywork\MyProject\py\robot\trunk\common\memcheck.py

Line #    Mem usage    Increment   Line Contents
================================================
   152    17.59 MiB    17.59 MiB   @memory_profiler.profile(precision=2,stream=g_stream)
   153                             def testtt():
   154    27.22 MiB     9.63 MiB        import numpy as np
   155    27.29 MiB     0.07 MiB        a = np.zeros((1024,1024*1024*4*8),dtype=np.uint8)
   156    27.29 MiB     0.00 MiB        return a


Filename: D:\Mywork\MyProject\py\robot\trunk\common\memcheck.py

Line #    Mem usage    Increment   Line Contents
================================================
   158    27.30 MiB    27.30 MiB   @memory_profiler.profile(precision=2,stream=g_stream)
   159                             def testtt2():
   160    27.30 MiB     0.00 MiB        import numpy as np
   161    27.30 MiB     4.00 MiB        a = np.zeros((1024,1024*1024*4*8),dtype=np.uint8)
   162                                  if True:
   163    27.30 MiB     0.00 MiB                print("")
   164    27.30 MiB     0.00 MiB        return a


Filename: D:\Mywork\MyProject\py\robot\trunk\common\memcheck.py

Line #    Mem usage    Increment   Line Contents
================================================
   158    27.30 MiB    27.30 MiB   @memory_profiler.profile(precision=2,stream=g_stream)
   159                             def testtt2():
   160    27.30 MiB     1.00 MiB        import numpy as np
   161    27.30 MiB     4.00 MiB        a = np.zeros((1024,1024*1024*4*8),dtype=np.uint8)
   162                                  if True:
   163    27.30 MiB     0.00 MiB                print("")
   164    27.30 MiB     0.00 MiB        return a"""
	_decode(s)
	show()
	
if __name__ == '__main__':
	MIN_MEMORY = 0.1
	testdecode()
	print("end testdecode")
	testtt()
	testtt2()
	testtt2()
	testtt()
	testtt2()
	autoShow()
	


