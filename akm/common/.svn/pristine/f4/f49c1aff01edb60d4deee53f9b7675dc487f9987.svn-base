#coding=utf-8
# ycat			2020-12-8	  create
# 文件锁封装  
import os,sys
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import utility
import lock as lockimp

if utility.is_win():
	import win32con
	import pywintypes
	import win32file
	#LOCK_EX = win32con.LOCKFILE_EXCLUSIVE_LOCK
	#LOCK_SH = 0  # The default value
	#LOCK_NB = win32con.LOCKFILE_FAIL_IMMEDIATELY
else:
	#https://blog.csdn.net/whatday/article/details/108901054
	import fcntl

class processorLock:
	def __init__(self,name):
		self.thread_lock = lockimp.create("processor_lock"+name)
		if utility.is_win():
			p = os.path.dirname(__file__)
		else:
			p = "/tmp"
		self.file = open(p +"/"+name+"_processor.lock","w+")
		
		if utility.is_win():
			self.hfile = win32file._get_osfhandle(self.file.fileno())
		else:
			self.hfile = self.file.fileno()

	def lock(self):
		lockimp.acquire(self.thread_lock)
		if utility.is_win():
			win32file.LockFileEx(self.hfile, win32con.LOCKFILE_EXCLUSIVE_LOCK, 0, 0xffff0000, pywintypes.OVERLAPPED())
		else:
			fcntl.flock(self.hfile,fcntl.LOCK_EX)
		
	def lock_share(self):
		lockimp.acquire(self.thread_lock)
		if utility.is_win():
			win32file.LockFileEx(self.hfile, 0, 0, 0xffff0000, pywintypes.OVERLAPPED())
		else:
			fcntl.flock(self.hfile,fcntl.LOCK_SH)
		
	def unlock(self):
		if utility.is_win():
			win32file.UnlockFileEx(self.hfile, 0, 0xffff0000, pywintypes.OVERLAPPED())
		else:
			fcntl.flock(self.hfile,fcntl.LOCK_UN)
		lockimp.release(self.thread_lock)

############### unit test ###############
	
def test():
	import time
	import mmap,struct
	f = open("testlock222.lock","w+")
	m = mmap.mmap(-1, 10, tagname="testlock", access=mmap.ACCESS_DEFAULT)
	
	def readInt():
		m.seek(0)
		ss = m.read(4)
		return struct.unpack("i",ss)[0]
		
	def writeInt(value):
		m.seek(0)
		m.write(struct.pack("i",value))
	
	l = processorLock("test/ycat")
	for i in range(1000):
		l.lock_share()
		print("get share lock")
		v = readInt()
		print(v)
		time.sleep(1)
		l.unlock() 
		 
		v += 1
		l.lock()
		print("get lock")
		writeInt(v)
		time.sleep(1)
		l.unlock()
		print("unlock")
		
		
def test2():
	import time
	import mmap,struct
	f = open("testlock222.lock","w+") 
	l = processorLock("ycat")
	for i in range(1000):
		l.lock_share()
		print("get share lock")
		time.sleep(1)
		l.unlock() 
		  
		l.lock()
		print("get lock")
		time.sleep(1)
		l.unlock()
		print("unlock")

	
if __name__ == '__main__':
	#启多个进程，看数字会不会重复 
	if utility.is_win():
		test()
	else:
		test2()
	
	
	