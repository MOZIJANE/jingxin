#coding=utf-8
# ycat			2020-12-8	  create
# 文件锁封装  
import os,sys
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import utility

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
		#print(help(open))
		self.file = open(name+".lock","w+")
		if utility.is_win():
			self.hfile = win32file._get_osfhandle(self.file.fileno())
		else:
			self.hfile = self.file.fileno()

	def lock(self):
		if utility.is_win():
			win32file.LockFileEx(self.hfile, win32con.LOCKFILE_EXCLUSIVE_LOCK, 0, 0xffff0000, pywintypes.OVERLAPPED())
		else:
			fcntl.flock(self.hfile,fcntl.LOCK_EX)
		
	def unlock(self):
		if utility.is_win():
			win32file.UnlockFileEx(self.hfile, 0, 0xffff0000, pywintypes.OVERLAPPED())
		else:
			fcntl.flock(self.hfile,fcntl.LOCK_UN)
	

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
		l.lock()
		v = readInt()
		print(v)
		time.sleep(1)
		v += 1
		writeInt(v)
		l.unlock()
		

	
if __name__ == '__main__':
	#启多个进程，看数字会不会重复 
	test()
	
	
	