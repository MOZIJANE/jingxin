#coding=utf-8 
# ycat			 2014/06/29      create
import json
import sys,os,io
import utility
import enhance
import datetime
import codecs
from decimal import Decimal

_g_list_type = {}

#增加对于list,元组的序列化的模板 
#使用方法 @list_type("s",foo2())
#	  class foo2:
#		pass
#
#         class foo:
#	       def __init__(self):
#                 self.s = [] #foo2的数组 
def list_type(attr_name,template_class):
	def __call(cls):
		global _g_list_type
		if cls in _g_list_type:
			_g_list_type[cls].append((attr_name,template_class))
		else:
			_g_list_type[cls] = [(attr_name,template_class),]
		return cls
	return __call	

def _get_list_type(obj,attr_name):
	global _g_list_type
	if type(obj) in _g_list_type:
		tt = _g_list_type[type(obj)]
		for t in tt:
			if t[0] == attr_name:
				return utility.clone(t[1])
	return None


_class_name = "cls_name_xyz"
_g_ignore_set = set()
_g_ignore_obj = {}

#表示不需要序列化的修饰函数
#使用方法 @ignore_class()
#         class foo:
def ignore_class():
	def __call(cls):
		global _g_ignore_set
		_g_ignore_set.add(cls)
		return cls
	return __call

#表示不需要序列化的修饰函数
#使用方法 @ignore("s")
#         class foo:
#	       def __init__(self):
#                 self.s = "abc"
def ignore(attr_name):
	def __call(cls):
		global _g_ignore_obj
		if cls in _g_ignore_obj:
			_g_ignore_obj[cls].append(attr_name)
		else:
			_g_ignore_obj[cls] = [attr_name,]
		return cls
	return __call

def _is_ignore_class(obj):
	if hasattr(obj,"__call__"):
		return True
	global _g_ignore_set
	if type(obj) in _g_ignore_set:
		return True
	return False

def _is_ignore(obj,attr_name):
	assert len(attr_name)
	if attr_name[0] == "_":
		return True
	global _g_ignore_obj
	if type(obj) in _g_ignore_obj:
		return attr_name in _g_ignore_obj[type(obj)]
	return False

_g_rename = {}

def rename(old_name,new_name):
	def __call(cls):
		global _g_rename
		if cls in _g_rename:
			_g_rename[cls].append((old_name,new_name))
		else:
			_g_rename[cls] = [(old_name,new_name),]
		return cls
	return __call

def _get_name(obj,attr_name,index):
	global _g_rename
	if type(obj) not in _g_rename:
		return attr_name
	if index == 0:
		other_index = 1
	else:
		other_index = 0
		
	for n in _g_rename[type(obj)]:
		if n[index] == attr_name:
			return n[other_index]
	return 	attr_name


def _get_json_obj(obj,add_classname):
	if obj is None:
		return None
#	if isinstance(obj,str):
#		obj.decode("utf-8")
#		return obj
	if not utility.is_python3() and isinstance(obj,long):
		return obj
	if isinstance(obj,(str,bool,int,float)):
		return obj
	if isinstance(obj,Decimal):
		return str(obj)
	if isinstance(obj,datetime.datetime):
		s = utility.str_datetime(obj,False)
		if add_classname:
			return {_class_name:"d.datetime","value":s}
		else:
			return s
	if isinstance(obj,(list,tuple,set)):
		ret = []
		for o in obj:
			ret.append(_get_json_obj(o,add_classname))
		return ret
	
	if isinstance(obj,datetime.datetime):
		return utility.str_obj(obj)
		
	if isinstance(obj,datetime.date):
		return "%04d-%02d-%02d"%(obj.year,obj.month,obj.day) 
		
	if isinstance(obj,datetime.time):
		return "%02d:%02d:%02d"%(obj.hour,obj.minute,obj.second)

	if _is_ignore_class(obj):
		return {}

	if isinstance(obj,dict):
		d = {}
		for a in obj:
			o = obj[a]
			if _is_ignore_class(o):
				continue
			d[a] = _get_json_obj(o,add_classname)
		return d
	
	if hasattr(obj,"__call__"):
		print(obj,"is a function")
		assert 0
		return
	
	d = {}
	if not hasattr(obj,"__dict__"):
		return str(obj)
	for a in obj.__dict__:
		if _is_ignore(obj,a):
			continue
		o = getattr(obj,a)
		
		if _is_ignore_class(o):
			continue
		
		d[_get_name(obj,a,0)] = _get_json_obj(o,add_classname)

	if add_classname:
		assert _class_name not in d
		d["cls_name_xyz"] = enhance.classname(obj)
	return d


#如果是dict类型,dict的key值不管是什么都会变成str
#如果classname为True会自动加上"cls_name_xyz"字段，用于反映生成类 
def dump(obj,add_classname=False,indent=False):
	if indent:
		ii = 2
	else:
		ii = None
	return json.dumps(_get_json_obj(obj,add_classname),indent=ii,sort_keys=indent,ensure_ascii=False)

def load_obj(obj,tmpclass):
	if obj is None:
		return None
	if not utility.is_python3() and isinstance(obj,unicode):
		return obj.encode("utf-8")
	if not utility.is_python3() and  isinstance(obj,long):
		return obj
	if isinstance(obj,(str,bool,int,float,Decimal)):
		return obj
	if isinstance(obj,(list,tuple)):
		ret = []
		for o in obj:
			ret.append(load_obj(o,utility.clone(tmpclass))) 
		return ret
	
	if tmpclass is None:
		if isinstance(obj,dict) and _class_name not in obj:
			for a in obj:
				obj[a] = load_obj(obj[a],tmpclass)
			return obj
		c = obj[_class_name]
		if c == "d.datetime":
			return utility.str2date(obj["value"])
		o = enhance.create_obj(c)	
	else:
		o = tmpclass
	
	d = {}
	for a in obj:
		if a == _class_name:
			continue
		n = _get_name(o,a,1)
		tt = _get_list_type(o,a)
		setattr(o,n,load_obj(obj[a],tt))
	return o

def load(text,tmpclass=None):
	r = json.loads(text)
	return load_obj(r,tmpclass)

def load_file(filename,	tmpclass=None, codec = "utf-8"):
	try:
		f = codecs.open(filename,encoding=codec)
		s = f.read()
		f.close()  
		return load(s,tmpclass)
	except Exception as e:
		raise Exception("load json file: "+filename+" error:" + str(e))
	
def dump_file(filename,obj,add_classname=False, codec = "utf-8",indent=True):
	try:
		s = dump(obj,add_classname,indent=indent) 
		ss = s.encode(codec)
		f = open(filename,"wb")
		f.write(ss)
		f.close()
	except Exception as e:
		raise Exception("dump json file: "+filename+" error:" + str(e))
 
############# unit test ##############
def test_cn():
	a = {"aa":"中文","bb":11}
	dump_file("test_json2.json",a)
	
	bb = load_file("test_json2.json")
	assert bb["aa"] == "中文" 
	assert bb["bb"] == 11
	#os.remove("test_json.json")
	


@ignore_class()
class bbbb2:
	def __init__(self):
		self.ggg = 3

@rename("ggg","g")
@ignore("gsfsd")	
class bbbb:
	def __init__(self):
		self.ggg = 3
		self.gsfsd = "dfds"
		self._ddd = 34
		self.__d2dd = 34
		
@ignore("b")	
@rename("c","ccc")
@list_type("d",bbbb())
class aaaa4:
	def __init__(self):
		self.a = "sdfafs"
		self.b = 223.44
		self.c = 123.44
		self.e = bbbb2()
		self.d = []
		self._ddd = 34
		self.__d2dd = 34
			
def test_ignore():
	b = bbbb2()
	assert dump(b) == "{}"
	
	a = aaaa4()
	a.d.append(bbbb())
	a.d.append(bbbb())
	a.d.append(bbbb())
	a.d[2].ggg = 341
	rr = dump(a)
	assert len(rr) == len('{"a": "sdfafs", "d": [{"g": 3}, {"g": 3}, {"g": 341}], "ccc": 123.44}')
	cc = ['"a": "sdfafs"','"d": [{','{"g": 3}','{"g": 341}','"ccc": 123.44']
	for c in cc:
		assert rr.find(c) != -1
	
	a2 = aaaa4()
	a2 = load(dump(a),a2)
	print([id(x) for x in a2.d])
	assert utility.str_obj(a2) == utility.str_obj(a)
	
	a2 = aaaa4()
	a2.d.append(bbbb())
	a2.d[0].ggg = 16546
	assert utility.str_obj(load(dump([a,a2]),aaaa4())) == utility.str_obj([a,a2])
	
	a = aaaa4()
	a.a = "123468496"
	a.b = 2323
	a.c = 34434
	a2 = aaaa4()
	o = load(dump(a),a2)
	assert id(o) == id(a2)
	assert a2.a == "123468496"
	assert a2.b == 223.44
	assert isinstance(a2.e,bbbb2)
	assert a2.c == 34434
	

def test_json_load():
	def load1(obj,obj2=None):
		s = dump(obj)
		s2 = load(s)
		if obj2 is None:
			obj2 = obj
		print(s,s2,obj)
		print(type(obj),type(s2))
		assert utility.equal(s2,obj2)
		
	r = []
	r.append(None)
	r.append("dfsd姚fsd舜f65s4")
	r.append(232312)
	r.append("232312")
	r.append(True)
	r.append(False)
	r.append(128343.43)
	r.append([1,23,4,"434","sdfs您df好sfds"])
	r.append((1,23,4,"434","sdfsdfsfds"))
	
	for rr in r:
		load1(rr)

	r = []
	r.append({1,23,45})
	r.append((1,23,4,"434","sdfsdfsfds"))
	for rr in r:
		load1(rr,list(rr))
	load1({"afds":222, 2:"fdsfsdfsf", 4:[1,23,233,"sdafs姚df"]},{"afds":222, "2":"fdsfsdfsf", "4":[1,23,233,"sdafs姚df"]})	

class aaaa2:
	def __init__(self):
		self.a1 = 13343
		self.a2 = "fasdfa"
		self.a3 = 14342.2
			
class aaaa:
	def __init__(self):
		self.a1 = 1
		self.a2 = None
		self.a3 = 1.2
		self.a4 = True
		self.a5 = False
		self.a5 = False
		self.a6 = datetime.datetime(1998,12,31,11,45,22)
		self.aa6 = "aaa"
		self.aa6 = [aaaa2(),aaaa2()]
	@property	
	def p1(self):
		return self.a1 + self.a3
		
	def p2(self):
		return 1.1111
	
class aaaa3:
	def __init__(self):
		self.x = 1
		self.y = 2

@list_type("ccc",aaaa3())
class aaaa9:
	def __init__(self):
		self.ccc = aaaa3()

class aaaa10:
	def __init__(self):
		self.c1 = 11		
		
@list_type("ll",aaaa9())			
@list_type("mm",aaaa10())	
class aaaa5:
	def __init__(self):
		self.ll = []
		self.mm = None
	
def test_obj_in_obj(): 
	a = aaaa5()
	a.ll.append(aaaa9())
	a.ll[0].ccc.x = 1111
	a.ll[0].ccc.y = 1112
	a.ll.append(aaaa9())
	utility.print_obj(a)
	print()
	ss = dump(a)
	rr = load(ss,aaaa5())
	utility.print_obj(rr)
	assert rr.ll[0].ccc.x == 1111
	assert rr.ll[0].ccc.y == 1112
	assert rr.ll[1].ccc.x == 1
	assert rr.ll[1].ccc.y == 2
	
		
def test_json_dump():
	ccc = """{"a1": 1, "a3": 1.2, "a2": null, "a5": false, "a4": true, "a6": "1998-12-31 11:45:22", "aa6": [{"a1": 13343, "a3": 14342.2, "a2": "fasdfa"}, {"a1": 13343, "a3": 14342.2, "a2": "fasdfa"}]}"""
	cc = [ x.strip().replace("{","").replace("[","").replace("}","").replace("]","") for x in ccc.split(",") ]
	#print(cc)
	r = dump(aaaa())
	rr  = """{"aa6": [{"a2": "fasdfa", "a3": 14342.2, "a1": 13343}, {"a2": "fasdfa", "a3": 14342.2, "a1": 13343}], "a2": null, "a6": "1998-12-31 11:45:22", "a5": false, "a4": true, "a3": 1.2, "a1": 1}"""
	assert len(r) == len(rr)
	for c in cc:
		if c.find("aa6") != -1:
			assert r.find("aa6") != -1
			continue
		print("`%s`"%c,r.find(c))
		print(r)
		assert r.find(c) != -1

	
	assert dump(datetime.datetime(2015,2,12,16,21,23)) == '"2015-02-12 16:21:23"'
	
	d = datetime.datetime(2015,2,12,16,21,23)
	
	d1 = load("""{"cls_name_xyz":"d.datetime","value":"2015-02-12 16:21:23"}""")
	assert d1 == d

	a = aaaa()
	assert utility.equal(load(dump(a,True)),a,debug=True)
	
	d=datetime.datetime(2015,2,12,16,21,23)
	assert load(dump(d,True)) == d

def test_file():
	obj = "fdfdfsd"
	dump_file("test_json.json",obj)
	obj2 = load_file("test_json.json")
	assert obj2 == obj
	os.remove("test_json.json")
	 
@ignore("aaa")
@rename("a","aaa")
class yyy:
	def __init__(self):
		self.a = "a1111111"
		self.aaa = 0
			
def testrename(): 
	y = yyy()
	s = dump(y)
	print(s)
	y2 = load(s,yyy())
	print(y2.__dict__)
	assert  0
	 
if __name__ == '__main__':
	testrename()
	utility.run_tests()
	#test_obj_in_obj()
	
	
