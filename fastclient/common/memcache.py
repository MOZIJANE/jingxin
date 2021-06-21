#coding=utf-8 
# ycat	  2015/04/03      create
# 分布式的对象存储 
import sys,os
import datetime
import utility

mc = None

class _mock_mem_cache:
	def __init__(self):
		self.data = {}
	
	def get(self,key):
		return None
		#TODO:
		if key in self.data:
			return self.data[key]
		return None
		
	def set(self,key,value):
		#TODO
		pass
		#self.data[key] = value
	
	def incr(self,key,delta=1):
		v = self.get(key)
		if v is not None:
			self.set(key,int(v)+delta)
	
	def decr(self,key,delta=1):
		v = self.get(key)
		if v is not None:
			self.set(key,int(v)-delta)
	
	def delete(self,key):
		if self.check_key(key):
			del self.data[key]

	def check_key(self, key):
		return key in self.data
	
	def clear(self):
		self.data = {}

if utility.is_sae():
	import pylibmc as memcache
	mc = memcache.Client()
else:
	mc = _mock_mem_cache()

def set(key,value):
	global mc
	mc.set(key,value)
	
#missing_func为找不到的处理函数，也可以是固定值 	
def get(key,missing_func = None):
	global mc
	v = mc.get(key)
	if v is not None:
		return v
		
	if missing_func is not None:
		v = missing_func
		if callable(missing_func):
			v = missing_func(key)
		if v is not None:
			mc.set(key,v)
			return v
	return None	

def incr(key,delta=1):
	global mc
	mc.incr(key,delta)

def decr(key,delta=1):
	global mc
	mc.decr(key,delta)
	
def delete(key):
	global mc
	mc.delete(key)

def check_key(key):
	global mc
	mc.check_key(key)
	

