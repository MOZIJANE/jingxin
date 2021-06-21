#coding=utf-8 
# ycat	  2015/06/18      create
# https://www.jb51.net/article/107718.htm
import sys,os
import utility

def create(dictValue):
	obj = dictObj(dictValue)
	for k in dictValue:
		if isinstance(dictValue[k],dict):
			obj[k] = create(dictValue[k])
	return obj
		

#能把dict转换成obj.xxx的形式访问
class dictObj:
	def __init__(self,dictValue={}):
		assert isinstance(dictValue,dict) 
		self.__dict__.update(dictValue)
	
	def __contains__(self,key):
		return key in self.__dict__
	
	def __getitem__(self,key):
		return self.__dict__[key]
	
	def __iter__(self):
		for k in self.__dict__:
			yield k
	
	def __setitem__(self,key,value):
		self.__dict__[key] = value
		
	def __delitem__(self,key):
		del self.__dict__
		
	def __str__(self):
		return utility.str_obj(self.__dict__)
		
	def __len__(self):
		return len(self.__dict__)
	

########################## unit test ############################
def testcreate():
	d = {}
	d["111"] = 1123
	d["222"] = 345
	d["a33"] = {"c":333,"a":"11"}
	o = create(d)
	assert o.a33.c == 333
	assert o.a33.a == "11"
	
def test1():
	d =dictObj()
	d.aaa = dictObj()
	d.aaa.bb = 1999
	d.aaa["cc"] = 222
	assert 1 == len(d)
	assert d["aaa"]["bb"] == 1999
	assert d["aaa"].cc == 222
	assert 2 == len(d["aaa"])
	del d["aaa"]["bb"]
	assert "aaa" in d
	assert "bb" not in d["aaa"]
	assert "aaa"  in d
	d = dictObj()
	d[1] =111
	d[2.1] = 3343
	d["ggg"] = "xx"
	assert 3 == len(d)
	for k in d:
		assert k in [1,2.1,"ggg"]
	
	
def test_dict_obj():
	d = {}
	d["a1"] = "abc"
	d["a343s"] = "3452342sdd"
	d["b34"]=None
	o = dictObj(d)
	#assert o.has("a343s")
	#assert o.has("b34")
	#assert o.has("a343s")
	#assert not o.has("343s2")
	
	assert o.a343s == "3452342sdd"
	assert o.a1 == "abc"
	assert o.b34 == None
	
	assert o["a343s"] == "3452342sdd"
	assert o["a1"] == "abc"
	assert o["b34"] == None
	
	o.a1 = "13245646dee"
	assert o.a1 == "13245646dee"
	
	try:
		bb = o.no_exist
		assert 0
	except AttributeError as e:
		print(e)
		
	o._dict_obj_ = d
	print(o)
	
if __name__ == '__main__':
	test1()
	utility.run_tests()
	
