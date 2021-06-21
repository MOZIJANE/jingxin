#coding=utf-8 
# ycat			 2015/04/10      create
#自动生成ID的类 
import sys,os,random
import threading
import lock

class idmaker:
	def __init__(self,idName,startID=1000):
		self.startID = startID
		self.idName = "%s_%04d_%04d_"%(idName,os.getpid(),random.randint(1000,9999))
		self.lock = threading.RLock()
		
	def create(self):
		@lock.lock(self.lock)	
		def func(self):
			self.startID += 1
			return self.idName + str(self.startID)
		return func(self)
	
	def set_max(self,ID):
		@lock.lock(self.lock)
		def func(self):
			s = ID[-4:]
			if s.isdigit():
				self.startID = max(int(s),self.startID)
			return self.startID	
		return func(self)
	
#############################	unit test	###########################	
def test_id():
	a = "dfadfasf"
	ids = idmaker("dfadfasf",2000)
	b = ids.create()
	assert b[0:len(a)] == "dfadfasf"
	assert b[-4:] == "2001"
	b = ids.create()
	assert b[0:len(a)] == "dfadfasf"
	assert b[-4:] == "2002"
	b = ids.create()
	assert b[0:len(a)] == "dfadfasf"
	assert b[-4:] == "2003"
	
	assert ids.set_max("dfadfasf_2003") == 2003
	assert ids.set_max("dfadfasf_2014") == 2014
	assert ids.set_max("dfadfasf3_2314") == 2314
	assert ids.set_max("dfadf_fdfdf_fdfdfd_3014") == 3014
	
if __name__ == '__main__':
	import utility
	utility.run_tests()
		