#coding=utf-8
# ycat			2018-08-03	  create
# ros的消息解析 
import os,io
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import log
import re
import utility
import enhance
import datetime
import time
if utility.is_ros():
	import genpy.rostime
	import std_msgs.msg
	import ros2.rosUtility
import json_codec as json
import dict_obj

g_msgType = {}
g_srvType = {}

def emtpyMsg(msgType):
	m = getMsg(msgType)
	if utility.is_ros():
		return m.rosType()
	return m.empty()
	

def getMsg(msgType):
	global g_msgType
	init()
	return g_msgType[msgType]

	
def getSrv(srvType):
	global g_srvType  
	init()
	if srvType not in g_srvType:
		msg = getSrvInfo(srvType)
		s = decodeSrvMsg(srvType,msg)
		g_srvType[srvType] = s
	return g_srvType[srvType]
	 
	
def getMsgByRosObj(rosObj):
	ss = enhance.classname(rosObj).split(".")
	assert len(ss)
	msgType = ss[0]+"/"+ss[-1]
	return getMsg(msgType)

def getRosObs(msgType,dictObj):
	assert isinstance(dictObj,dict)
	return getMsg(msgType).toRos(dictObj)
	
def init():
	global g_srvType,g_msgType 
	if not g_msgType:
		loadMsgFile()
	if not g_srvType:
		loadSrvFile()
	
g_sn = -1
def _getSN():
	global g_sn
	g_sn += 1
	return g_sn
	
def header(frameId):
	if utility.is_ros():
		import rospy
		from std_msgs.msg import Header
		d = Header()
		d.stamp = rospy.Time.now() 
		d.frame_id = frameId
		d.seq = _getSN()
		return d
	else:
		return dict_obj.create(headerDict(frameId))

		
def headerDict(frameId):
	d = {}
	d["seq"] = _getSN()
	d["stamp"] = time.time()
	d["frame_id"] = frameId
	return d


def saveRos(obj,fileName,type="",indent=True,propertys=None):
	o = toDict(obj=obj,type=type,propertys=propertys)
	json.dump_file(fileName,o,indent=indent)
	
def toDict(obj,type="",propertys=None):
	if type == "":
		m = getMsgByRosObj(obj)
		type = m.type
		obj = m.toDict(obj)
	elif utility.is_ros():
		m = getMsg(type)
		obj = m.toDict(obj)
	elif isinstance(obj,dict_obj.dictObj):
		obj = obj.toDict()
		
	if propertys:
		for k in propertys:
			obj[k] = propertys[k]
	o = {"type":type,"data":obj}
	return o

def loadRos(fileName):
	data = json.load_file(fileName)
	return toRos(data)
		
def toRos(data):
	m = getMsg(data["type"])
	if utility.is_ros():
		return m.toRos(data["data"])
	else:
		#日期在写文件时，写成了字符串 
		ss = data["data"]["header"]["stamp"]
		if isinstance(ss,float):
			data["data"]["header"]["stamp"] = ss
		else:
			data["data"]["header"]["stamp"] = utility.str2date(ss).timestamp()
		return dict_obj.create(data["data"])
	
 
class msgInfo:
	def __init__(self,type,name,parent):
		self.fields = {}
		self.type = type.strip()
		self.name = name.strip()
		self.parent = parent
		self._rosType = None
		
	def add(self,type,name): 
		m = msgInfo(type,name,self)
		self.fields[name] = m
		return m
	
	def __str__(self):
		return self._getStr(0).strip("\n")
		
	def _getStr(self,level):
		if self.type:
			s = " " * 2 * level + self.type + " " + self.name+"\n"
			level += 1
		else:
			s = ""
		for m in self.fields.values():
			s += m._getStr(level)
		return s
	
	def __getitem__(self,name):
		return self.fields[name]
	
	@property
	def count(self):
		return len(self.fields)
		
	#返回ros消息的类型名 
	@property
	def rosType(self):
		assert utility.is_ros()
		if self._rosType:
			return self._rosType
		index = self.type.find("/") 
		if index == -1:
			lib = "std_msgs"
			msg = self.type
		else:
			lib = self.type[0:index]+".msg"
			msg = self.type[index+1:]
		aa = _isArray(msg)
		if aa[0]:
			msg = aa[1]
		module = __import__(lib) 
		m = getattr(module, "msg")
		self._rosType = getattr(m,msg) 
		return self._rosType
		
	def _getValue(self,data,field):
		if field in data: 
			return data[field]
		t = self.fields[field].type 
		if _isArray(t)[0]: 
			return []
		if not _isBaseType(t):
			return {} 
		if t == "string":
			return ""
		elif t == "time":
			return time.time()
		#elif t == "duration":
		#	return datetime.timedelta(seconds=0)
		return 0 
		
	#把字典转成ros字段 
	def toRos(self,data):	 
		obj = self.rosType()
		def _toRos(data,obj,msg): 
			for n in msg.fields: 
				item = msg._getValue(data,n) 
				if isinstance(item,list):
					rosItems = []
					field = msg.fields[n]
					for o in item:
						if _isBaseType(msg.fields[n].type):
							rosItems.append(o)
						else:
							rosObj = msg.fields[n].rosType()
							_toRos(o,rosObj,field)
							rosItems.append(rosObj) 
					setattr(obj,n,rosItems)
				elif _isBaseType(msg.fields[n].type):
					setattr(obj,n,_py2Ros(item,msg.fields[n].type))
				else: 
					_toRos(item,getattr(obj,n),msg.fields[n])
		_toRos(data,obj,self)
		return obj
	
	#把ros类型转成字典 
	def toDict(self,obj):
		data = {}
		def _toDict(data,obj,msg): 
			for n in msg.fields:
				objItem = getattr(obj,n)
				if _isBaseType(msg.fields[n].type):
					data[n] = _ros2py(objItem,msg.fields[n].type) 
				elif isinstance(objItem,list):
					data[n] = []
					field = msg.fields[n]
					for o in objItem:
						item = {}
						_toDict(item,o,field)
						data[n].append(item)
				else:
					data[n] = {} 
					_toDict(data[n],objItem,msg.fields[n])
		_toDict(data,obj,self)
		return data
		
	#创建一个空的dict_obj对象，用于在非ros系统上使用类似ros的对象 
	def empty(self): 
		data = {}
		def _toDict(data,msg): 
			for n in msg.fields:
				if _isBaseType(msg.fields[n].type):
					data[n] = _defaultValue(msg.fields[n].type)
				elif _isArray(msg.fields[n].type)[0]:
					data[n] = []
				else:
					data[n] = {} 
					_toDict(data[n],msg.fields[n])
		_toDict(data,self)
		return dict_obj.create(data)
		
	
	
class srvInfo:
	def __init__(self,msgType):
		self.type = msgType.strip()
		self.request = None
		self.response = None
		
	def __str__(self):
		s = str(self.request)
		s += "\n---\n"
		return s+str(self.response)
	
	@property
	def module(self):
		assert utility.is_ros()
		index = self.type.find("/") 
		if index == -1:
			log.error(self.type," format error")
			assert 0
		else:
			lib = self.type[0:index]+".srv" 
		module = __import__(lib)  
		return getattr(module, "srv") 
	
	@property
	def rosType(self):
		index = self.type.find("/") 
		return getattr(self.module,self.type[index+1:]) 
	
	@property
	def responseType(self):
		index = self.type.find("/") 
		return getattr(self.module,self.type[index+1:]+"Response") 
		
	@property
	def requestType(self):
		index = self.type.find("/") 
		return getattr(self.module,self.type[index+1:]+"Request") 
		

def _isBaseType(rosType):
	return rosType.find("/") == -1
	
	
def _isArray(rosType):	
	i = rosType.find("[")
	if i == -1:
		#非数组
		return False,rosType
	if i == len(rosType)-2:
		#可变数组
		return True,rosType[0:i]
	#固定数组 
	return True,rosType[0:i]

def _defaultValue(rosType):
	l,t = _isArray(rosType)
	if not l: 
		if rosType == "duration":
			return datetime.timedelta(seconds=0)
		elif rosType == "time":
			return time.time()
		elif rosType == "string":
			return ""
		else:
			return 0
	else:
		return []
		#if t == "time" or t == "duration":
		#	return [ _defaultValue(x,t) for x in value ]
		#return value
	
#ros基本类型转成py类型 	
#int8, int16, int32, int64 (plus uint*)
#float32, float64
#string
#time, duration
#other msg files
#variable-length array[] and fixed-length array[C]
def _ros2py(value,rosType):
	if rosType == "uint8[]":
		return value
	l,t = _isArray(rosType)
	if not l: 
		if rosType == "duration":
			return datetime.timedelta(seconds=value.to_sec())
		elif rosType == "time":
			return ros2.rosUtility.time2Py(value) 
		else:
			return value
	else:
		if t == "time" or t == "duration":
			return [ _ros2py(x,t) for x in value ]
		return value
	
	
#py基本类型转成ros类型 
def _py2Ros(value,rosType):
	if rosType == "uint8[]":
		return value
	l,t = _isArray(rosType)
	if not l: 
		if rosType == "duration":
			if isinstance(value,datetime.timedelta):
				return genpy.rostime.Duration(value.total_seconds())
			else:
				return genpy.rostime.Duration(value)
		elif rosType == "time":
			return ros2.rosUtility.time2Ros(value) 
		else:
			return value
	else:
		if t == "time" or t == "duration":
			return [ _py2Ros(x,t) for x in value ]
		return value
	
	
#返回msg列表
def getMsgList():
	assert utility.is_ros()
	import shell
	ret = shell.run_cmd2("rosmsg list")
	if not ret[1]:
		raise Exception("执行rosmsg list失败")
	return [ x for x in ret[0].split("\r\n") if x ]

	
def getMsgInfo(msgType):
	assert utility.is_ros()
	import shell
	ret = shell.run_cmd2("rosmsg info " + msgType)
	if not ret[1]:
		raise Exception("执行rosmsg info失败")
	return ret[0]
	
	
#返回srv列表
def getSrvList():
	assert utility.is_ros()
	import shell
	ret = shell.run_cmd2("rossrv list")
	if not ret[1]:
		raise Exception("执行rossrv list失败")
	return [ x for x in ret[0].split("\r\n") if x ]
	
	
def getSrvInfo(msgType):
	assert utility.is_ros()
	import shell
	#print("start get srv info ",msgType)
	ret = shell.run_cmd2("rossrv info " + msgType)
	if not ret[1]:
		raise Exception("执行rossrv info失败")
	return ret[0]
	
def _createFile(fileName,listFunc,infoFunc):
	file = open(fileName,"w+t")
	msgs = listFunc()
	print("found",len(msgs),"msgs")
	i = 0
	for m in msgs:
		i += 1
		desc = infoFunc(m)
		file.write("$")
		file.write(m+"\n")
		file.write(desc)
		print("get",m,"[%d/%d]"%(i,len(msgs)))
	file.close()
	
#生成消息描述信息，用于消息解析 
def createMsgFile():
	_createFile("./ros_msg.txt",getMsgList,getMsgInfo)

	
#生成消息描述信息，用于消息解析 
def createSrvFile():
	_createFile("./ros_srv.txt",getSrvList,getSrvInfo)
	
def _loadFile(fileName,decodeFunc):
	ret = {} 
	path = os.path.abspath(os.path.dirname(__file__)) + "/" + fileName
	assert os.path.exists(path)
	file = open(path,"r+t")
	msg,desc = "",""
	lines = file.readlines()
	errorMsg = {}
	for line in lines:
		if line[0] == "$": 
			if len(desc):
				if msg in errorMsg:
					continue
				try:
					m = decodeFunc(msg,desc)
					ret[m.type] = m 
				except (AttributeError,ImportError):
					errorMsg[msg] = True
					print("get %s ros msg failed"%msg)
					continue 
			msg = line[1:]
			desc = ""
		else:
			desc += line
	if len(desc):
		try:
			m = decodeFunc(msg,desc)
			ret[m.type] = m 
		except (AttributeError,ImportError):
			print("get %s ros msg failed"%str(msg))
	file.close()
	return ret

def loadMsgFile():
	global g_msgType
	g_msgType = _loadFile("ros_msg.txt",decodeMsg)
	 
def loadSrvFile():
	global g_srvType
	g_srvType = _loadFile("ros_srv.txt",decodeSrvMsg)
	
	
def _decodeEnum(line):
	ret = re.match("\s*(\S+)\s+(.+)=(.+)\s*",line)
	if ret is None:
		return None
	return ret.group(1),ret.group(2),ret.group(3)
	
	
def _decodeLine(line):
	ret = re.match("\s*(\S+)\s+(\S+)\s*",line)
	if ret is None:
		log.error("unknown line:",line)
	return ret.group(1),ret.group(2)
	
	
def _getLevel(line):
	if line[0] != " ":
		return 0
	for i in range(1,100): 
		if line[0:i] != " "*i:
			return (i-1)/2
	assert 0
	
 
def decodeMsg(msgType,text):
	global g_msgType
	msg = msgInfo(msgType,"",None)
	curLevel = -1
	curMsg = msg
	for line in text.splitlines(): 
		if len(line.strip()) == 0:
			continue
		if _decodeEnum(line) is not None:
			continue
		t,n = _decodeLine(line) 
		
		level = _getLevel(line) 
		if level == curLevel + 1:
			curMsg = curMsg.add(t,n)
			curLevel += 1
		elif level == curLevel: 
			curMsg = curMsg.parent.add(t,n)
		elif level < curLevel:
			for i in range(100):
				curLevel -= 1
				curMsg = curMsg.parent
				if level == curLevel:
					break
			else:
				assert 0
			curMsg = curMsg.parent.add(t,n)   
	return msg
	
def decodeSrvMsg(msgType,text):
	i = text.find("---")
	srv = srvInfo(msgType.strip()) 
	srv.request = decodeMsg("",text[0:i]) 
	if utility.is_ros():	
		srv.request._rosType = srv.requestType
		
	srv.response = decodeMsg("",text[i+3:])
	if utility.is_ros():	
		srv.response._rosType = srv.responseType
	return srv
		
########### unit test ###########
def testempty():
	msg = emtpyMsg("nav_msgs/OccupancyGrid")
	assert msg.header.frame_id == ""
	assert msg.header.seq == 0
	assert msg.info.resolution == 0
	assert msg.data == []
	
def testload(): 
	obj = loadRos("../test/laser_150130.txt")
	assert len(obj.ranges) == 1440
	assert len(obj.intensities) == 1440

	
def testgetMsgByRosObj():
	if not utility.is_ros():
		return
	import geometry_msgs.msg
	import std_msgs.msg
	import actionlib.msg
	p = geometry_msgs.msg.PoseStamped()
	p.header = header("2222")
	p.header.stamp.nsecs = 0
	p.pose.position.x = 1123.31
	p.pose.position.y = 5123.13
	p.pose.position.z = 0 
	p.pose.orientation.x = 123.31
	p.pose.orientation.y = 143.31
	p.pose.orientation.z = 113.31
	p.pose.orientation.w = 723.31  
	assert getMsgByRosObj(p).type == "geometry_msgs/PoseStamped"
	assert getMsgByRosObj(std_msgs.msg.Empty()).type == "std_msgs/Empty"
	assert getMsgByRosObj(actionlib.msg.TestActionGoal()).type == "actionlib/TestActionGoal"
	saveRos(p,"unittest.txt")
	pp = loadRos("unittest.txt") 
	assert pp == p 

	
def testdecodeSrvMsg():
	s = """---
nav_msgs/OccupancyGrid map
  std_msgs/Header header
    uint32 seq
    time stamp
    string frame_id
  nav_msgs/MapMetaData info
    time map_load_time
    float32 resolution
    uint32 width
    uint32 height
    geometry_msgs/Pose origin
      geometry_msgs/Point position
        float64 x
        float64 y
        float64 z
      geometry_msgs/Quaternion orientation
        float64 x
        float64 y
        float64 z
        float64 w
  int8[] data

"""
	srv = decodeSrvMsg("nav_msgs/GetMap",s)
	assert 0 == srv.request.count
	assert 1 == srv.response.count
	assert srv.response["map"].type == "nav_msgs/OccupancyGrid"
	assert srv.response["map"].count == 3
	if not utility.is_ros():
		return
	import nav_msgs.srv 
	assert srv.rosType == nav_msgs.srv.GetMap
	
	s = """float32 x
float32 y
float32 theta
string name
---
string name
""" 
	srv = decodeSrvMsg("turtlesim/Spawn",s) 
	assert 4 == srv.request.count
	assert 1 == srv.response.count
	assert srv.request["x"].type == "float32"
	assert srv.request["y"].type == "float32"
	assert srv.request["theta"].type == "float32"
	assert srv.request["name"].type == "string"
	assert srv.response["name"].type == "string" 
	import turtlesim.srv
	assert srv.rosType == turtlesim.srv.Spawn
	 
def testgetSrvList():
	if not utility.is_ros():
		return
	print(getSrvList())
	assert "tf2_msgs/FrameGraph" in getSrvList()
	
	
def test_isArray():
	assert (False,"float64")	== _isArray("float64")
	assert (True,"float64") == _isArray("float64[36]")
	assert (True,"int8") == _isArray("int8[]")
	assert (True,"sensor_msgs/PointField") == _isArray("sensor_msgs/PointField[]")
	assert not _isBaseType("sensor_msgs/PointField")
	assert _isBaseType("uint8")
	assert not _isBaseType("std_msgs/Char")
	
	
def testrosobj():
	init()
	import time
	if not utility.is_ros():
		return
	m = getMsg("std_msgs/Header")
	now = utility.now()
	msg = {}
	msg["seq"] = 110
	msg["stamp"] = now.timestamp()
	msg["frame_id"] = "ycat_test"
	r = m.toRos(msg) 
	g = m.toDict(r)
	assert g["seq"] == msg["seq"]
	assert g["stamp"] == now
	assert g["frame_id"] == msg["frame_id"] 
	

def test_decodeLine():
	ret = _decodeLine(" std_msgs/Header header ") 
	assert ret[0] == "std_msgs/Header"
	assert ret[1] == "header"
	ret = _decodeLine("geometry_msgs/Vector3 linear_acceleration") 
	assert ret[0] == "geometry_msgs/Vector3"
	assert ret[1] == "linear_acceleration"
	ret = _decodeLine("  float64 x") 
	assert ret[0] == "float64"
	assert ret[1] == "x"
	ret = _decodeLine("float64[9] angular_velocity_covariance") 
	assert ret[0] == "float64[9]"
	assert ret[1] == "angular_velocity_covariance"
	
	
def testisEnum():
	assert _decodeEnum("uint8 LINE_STRIP=4") == ("uint8","LINE_STRIP","4")
	assert not _decodeEnum("  float64 x")

	
def test_getLevel():
	assert _getLevel("float64 x") == 0
	assert _getLevel("    float64 x") == 2
	assert _getLevel("  float64 x") == 1
	assert _getLevel("      float64 x") == 3

	
def testdecodeMsg():
	sss = """geometry_msgs/Vector3 linear
  float64 x
  float64 y
  float64 z
geometry_msgs/Vector3 angular
  float64 x
  float64 y
  float64 z

"""
	msg = decodeMsg("geometry_msgs/Twist",sss) 
	assert msg.count == 2
	assert msg["linear"]["x"].type == "float64"
	assert msg["linear"]["y"].type == "float64"
	assert msg["linear"]["z"].type == "float64"
	assert msg["linear"].count == 3 
	assert msg["angular"].count == 3  
	assert msg["angular"]["x"].type == "float64"
	assert msg["angular"]["y"].type == "float64"
	assert msg["angular"]["z"].type == "float64" 
	
	sss = """std_msgs/Header header
  uint32 seq
  time stamp
  string frame_id
float32 angle_min
float32 angle_max
float32 angle_increment
float32 time_increment
float32 scan_time
float32 range_min
float32 range_max
float32[] ranges
float32[] intensities
	"""
	msg = decodeMsg("sensor_msgs/LaserScan",sss)
	sss = """std_msgs/Header header
  uint32 seq
  time stamp
  string frame_id
actionlib_msgs/GoalStatus status
  uint8 PENDING=0
  uint8 ACTIVE=1
  uint8 PREEMPTED=2
  uint8 SUCCEEDED=3
  uint8 ABORTED=4
  uint8 REJECTED=5
  uint8 PREEMPTING=6
  uint8 RECALLING=7
  uint8 RECALLED=8
  uint8 LOST=9
  actionlib_msgs/GoalID goal_id
    time stamp
    string id
  uint8 status
  string text
nav_msgs/GetMapResult result
  nav_msgs/OccupancyGrid map
    std_msgs/Header header
      uint32 seq
      time stamp
      string frame_id
    nav_msgs/MapMetaData info
      time map_load_time
      float32 resolution
      uint32 width
      uint32 height
      geometry_msgs/Pose origin
        geometry_msgs/Point position
          float64 x
          float64 y
          float64 z
        geometry_msgs/Quaternion orientation
          float64 x
          float64 y
          float64 z
          float64 w
    int8[] data

	"""
	msg = decodeMsg("nav_msgs/GetMapActionResult",sss)
	assert msg.count == 3
	assert msg["result"]["map"]["info"]["origin"]["orientation"].count == 4 
	
	
def testloadMsgFile():
	loadMsgFile()
	assert len(g_msgType) > 100
	if not utility.is_ros():
		return
	for m in g_msgType.values():
		#if m.type == "tf/tfMessage":
		#	continue
		print(m.rosType)
	
	
if __name__ == "__main__": 
	createSrvFile() 
	createMsgFile() 
	import utility
	utility.run_tests()

	
	
	
	
	
	
	
	
	
	
	
	
	
