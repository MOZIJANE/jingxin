#coding=utf-8
# ycat			2020-12-2	  create 
# python 3.8可以使用SharedMemory类，这样更方便 
# 共享内存里的数据不会自动清空
# https://docs.python.org/zh-cn/3.6/library/multiprocessing.html#module-multiprocessing.sharedctypes 
# https://docs.python.org/zh-cn/3/library/multiprocessing.shared_memory.html
import sys,os
import time
from ctypes import *
import mmap
import struct
import time 
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import utility,log
import fileLock

MAX_ITEM_COUNT 	= 2000		#最多支持多少个key值
KEY_SIZE 		= 64		#一个key的大小 
ITEM_SIZE 		= 255		#一个item的大小 


class key_c(Structure):
	_fields_  = [("key",c_char*KEY_SIZE),("index",c_int)] 

class items_c(Structure):
	_fields_  = [("type",c_char),("value",c_char*ITEM_SIZE)] 

def _createFile(filename,size):
	if os.path.exists(filename):
		s = os.path.getsize(filename)
		if s >= size:
			return open(filename,"r+")
		f = open(filename,"a+")
		f.write(" "*(size-s))
		f.flush()
		return f
	f = open(filename,"w+")
	f.seek(size - 1)
	f.write('\x00')
	f.flush()
	return f
		

class dictionary:
	def __init__(self,name,size=MAX_ITEM_COUNT):
		self.name = name
		self.size = size
		self.keysMap = {}
		self.lock = fileLock.processorLock(name)
		k1 = name+"_keys"
		k2 = name+"_values"
		n1 = sizeof(key_c)*self.size
		n2 = sizeof(items_c)*self.size
		if utility.is_win():
			self.keys_mem   = mmap.mmap(-1, n1, tagname=k1,access=mmap.ACCESS_DEFAULT)
			self.values_mem = mmap.mmap(-1, n2, tagname=k2,access=mmap.ACCESS_DEFAULT)
		else:
			f = _createFile("/tmp/"+k1+".sharemem",n1)
			#print(os.path.getsize("/tmp/"+k1+".sharemem"),n1)
			self.keys_mem   = mmap.mmap(f.fileno(),n1,flags=mmap.MAP_SHARED,prot=mmap.PROT_WRITE | mmap.PROT_READ,access=mmap.ACCESS_WRITE)
			f.close()
			
			f = _createFile("/tmp/"+k2+".sharemem",n2)
			self.values_mem = mmap.mmap(f.fileno(),n2,flags=mmap.MAP_SHARED,prot=mmap.PROT_WRITE | mmap.PROT_READ,access=mmap.ACCESS_WRITE)
			f.close()
			
	def getIndex(self,key,insertFlag):
		if key in self.keysMap:
			return self.keysMap[key]
		count = self._readInt(self.keys_mem,0)
		for i in range(count):
			k = self._readKeyStr(self.keys_mem,4+KEY_SIZE*i)
			self.keysMap[k] = i
			if key == k:
				return i
		if not insertFlag:
			return -1
		if count >= self.size:
			raise Exception("shareMem: "+self.name+" is full")
		self._writeInt(self.keys_mem,0,count+1)
		self._writeStr(self.keys_mem,4+KEY_SIZE*count,key,KEY_SIZE)
		self.keysMap[key] = count
		return count
		
	@property
	def count(self):
		return self._readInt(self.keys_mem,0)
		
	def __len__(self):
		return self.count
		
	def __setitem__(self,key,value):
		return self.set(key,value)
		
	def __getitem__(self,key):
		return self.get(key)
	
	def get(self,key,ignoreError=False,ignoreType=False):
		self.lock.lock_share()
		try:
			index = self.getIndex(key,insertFlag=False)
			if index == -1:
				if ignoreError:
					return None
				raise KeyError("shareMem: "+self.name+" can't find key:"+key)
			return self._readValueStr(self.values_mem,sizeof(items_c)*index,ignoreType=ignoreType)
		finally:
			self.lock.unlock()
	
	
	def set(self,key,value):
		self.lock.lock()
		try:
			index = self.getIndex(key,insertFlag=True)
			t = None
			if isinstance(value,int):
				t = "i"
			elif isinstance(value,float):
				t = "f"
			elif isinstance(value,bool):
				t = "b"
			elif isinstance(value,str):
				t = "s"
			else:
				raise TypeError("shareDict unknow value type:"+str(type(value)))
			self._writeStr(self.values_mem,sizeof(items_c)*index,t,KEY_SIZE)
			self._writeStr(self.values_mem,sizeof(items_c)*index+1,str(value),ITEM_SIZE)
		finally:
			self.lock.unlock()
		
	def close(self):
		self.keys_mem.close()
		self.values_mem.close()
		#if not utility.is_win():
		#	self.file1.close()
		#	self.file2.close()
	
	def _readInt(self,mem,index):
		mem.seek(index)
		ss = mem.read(4)
		return struct.unpack("i",ss)[0]
		
	def _trim(self,ss):
		for i in range(len(ss)):
			if ss[i] == 0:
				return ss[0:i].decode("utf-8")
		return ss.decode("utf-8")
		
	def _readKeyStr(self,mem,index):
		mem.seek(index)
		ss = mem.read(KEY_SIZE)
		return self._trim(ss)
		
	def _readValueStr(self,mem,index,ignoreType):
		mem.seek(index)
		t = mem.read(1).decode("utf-8")
		ss = mem.read(ITEM_SIZE)
		ss = self._trim(ss)
		if ignoreType:
			return ss
		if t == "s":
			return ss
		elif t == "i":
			return float(ss)
		elif t == "f":
			return float(ss)
		elif t == "b":
			return bool(ss)
		else:
			raise TypeError("shareDict unknow type str:"+t)
		
	def _writeInt(self,mem,index,value):
		mem.seek(index)
		mem.write(struct.pack("i",value))
		
	def _writeStr(self,mem,index,value,maxLen):
		mem.seek(index)
		ss = value.encode("utf-8") + b'\x00' + b'\x00'+ b'\x00'+ b'\x00'+ b'\x00'+ b'\x00'+ b'\x00'+ b'\x00'+ b'\x00'+ b'\x00'
		assert len(ss) <= maxLen
		mem.write(ss)	
		
	def show(self):
		self._updateKeys()
		print("shareDict: name =",self.name,",count =",self.count)
		for k in self.keysMap:
			print(k,"\t:",self[k])
		print()
		
	def _updateKeys(self):
		c = self.count
		if len(self.keysMap) != c:
			kk = {}
			for i in range(c):
				k = self._readKeyStr(self.keys_mem,4+KEY_SIZE*i)
				if len(k) == 0:
					continue
				kk[k] = i
			self.keysMap = kk
	
	def getAll(self):
		self._updateKeys()
		data = {}
		for k in self.keysMap:
			try:
				data[k] = self.get(k,ignoreType=True)
			except Exception as e:
				log.error("shareDict:",self.name,"get key error",k,e)
				raise e
		return data
		
############## unit test ##############

def test_server():
	import time
	d = dictionary("ycat")
	assert d._trim(b'\x39\x39\x00\x39\x00\x00\x00\x00\x00\x00\x00\x00') == "99"
	assert d._trim(b'\x39\x39\x41') == "99A"
	assert d._trim(b'\x39\x39\x41\x00\x39\x41\x00\x00\x00\x00\x00') == "99A"
	s = d._trim(b'\x00\x00\x00\x00\x00\x00')
	assert d._trim(b'\x00\x00\x00\x00\x00\x00') == ""
	ee =b'\x39\x39\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
	#print(len(d._trim(ee)))
	#assert 0
	assert 0
	d["aaa"] = 1000
	d["ccc"] = 2323
	d["ggg"] = "eefefefe" 
	print("start test set")
	a = str(utility.ticks())
	a = a[len(a)-1]
	print(a)
	for i in range(100):
		d["test"] = a*100
		time.sleep(1)
	d.close()
	
def test_client():
	d = dictionary("ycat")
	d.show()
	assert d["aaa"] == 1000
	assert d["ccc"] == 2323
	assert d["ggg"] == "eefefefe"
	while True:
		print(d["test"])
		time.sleep(1)
	d.close()
	print("finish test")
	
#测试内存分配和释放
def testfree():
	global MAX_ITEM_COUNT
	MAX_ITEM_COUNT*=10000
	d = dictionary("ycat2")
	time.sleep(10)
	d.close()
	
def test_createFile():
	for i in range(3):
		try:
			os.remove("test.txt")
		except Exception as e:
			#print(e)
			pass
		f = _createFile("test.txt",100)
		assert f
		f.close()
		assert 100 == os.path.getsize("test.txt")
		f = _createFile("test.txt",100)
		f.close()
		assert 100 == os.path.getsize("test.txt")
		f = _createFile("test.txt",100*1024*1024)
		f.close()
		assert 100*1024*1024 == os.path.getsize("test.txt")
		os.remove("test.txt")
	

if __name__ == '__main__':
	#test_createFile()
	##testfree()
	#assert 0
	if utility.is_test():
		test_server()
	else:
		test_client()
		
		
		
