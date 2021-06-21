#coding=utf-8
# ycat			2018-08-03	  create 
import rospy
import time
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import shell,utility
import log
import ros2.msg  
import ros2.rosUtility  
import traceWriter

#返回提供服务的实例 
def getSrvList():
	assert utility.is_ros()
	ret = shell.run_cmd2("rosservice list")
	if not ret[1]:
		raise Exception("执行rosservice list失败") 
	return [ x for x in ret[0].split("\r\n") if x ]
	
#返回消息类型 
def getSrvMsgType(srvName):
	assert utility.is_ros()
	ret = shell.run_cmd2("rosservice info "+srvName)
	if not ret[1]:
		raise Exception("执行rosservice info失败") 
	line = ret[0].splitlines()
	if len(line) < 3:
		raise Exception("执行rosservice info失败2") 
	line = line[2]
	return line[line.find("Type: ")+len("Type: "):]


#根据Request类型，返回Response类型
def getResponse(msg):
	m = __import__(msg.__module__)
	m = getattr(m,"srv")
	name = type(msg).__name__
	index = -len("Request") 
	assert name[index:] == "Request"
	return getattr(m,name[:index]+"Response")()
	
def getCaller(request):
	#{'callerid': '/rosservice_15958_1603682173451', 'md5sum': '04af24139a49a00f4c578ef63795a508', 'service': '/ss/Reloc'}
	if "callerid" in request._connection_header:
		return request._connection_header["callerid"]
	return "unknown"

#自动处理返回值为code和message的类型 
def catch(func):
	def __call(*p):
		assert len(p) > 0
		assert len(p) <= 2
		import log 
		try:
			r = func(*p) 
			if r is None:
				return getResponse(p[-1])
			else:
				return r
		except Exception as e:
			log.exception("invoke "+str(func),e)
			ret = getResponse(p[-1])		
			assert hasattr(ret,"code")
			assert hasattr(ret,"message")
			ret.code = -1
			ret.message = str(e)
			return ret
	__call.__name__ = func.__name__
	return __call
	

	
class service:
	def __init__(self,serviceType,serviceName,callback,useRosType=False):
		assert ros2.rosUtility.isInited()
		self.type = serviceType
		self.name = serviceName
		self.callback = callback
		if useRosType:
			h = self._handleRos
		else:
			h = self._handleDict
		if isinstance(serviceType,str):
			t = ros2.msg.getSrv(serviceType).rosType
		else:
			t = serviceType
			assert useRosType
		log.info("start ros service, name="+serviceName + ", type="+serviceType) #{'callerid': '/rosservice_15386_1603682094284', 'md5sum': '04af24139a49a00f4c578ef63795a508', 'service': '/ss/Reloc'}
		self.imp = rospy.Service(serviceName, t, h)  
		
		
	def _handleDict(self,request):
		msg = ros2.msg.getSrv(self.type)
		data = msg.request.toDict(request)
		traceWriter.addEvent("rossrv.%s.%s"%(self.type,self.name),data)
		try:
			response = self.callback(data)
			return msg.response.toRos(response)
		except Exception as e:
			log.exception("handle "+self.type,e)
		return None
		
	def _handleRos(self,request): 
		msg = ros2.msg.getSrv(self.type)
		data = msg.request.toDict(request)
		traceWriter.addEvent("rossrv.%s.%s"%(self.type,self.name),data)
		try:
			return self.callback(request)
		except Exception as e:
			log.exception("handle "+self.type,e)
		return None
		

		
#getSrvMsgType(serviceName) 
class client:
	def __init__(self,serviceType,serviceName,useRosType=False):
		self.name = serviceName
		if serviceType is None:
			self.type = getSrvMsgType(serviceName)
		else:
			self.type = serviceType
		self.useRosType = useRosType
		self.imp = rospy.ServiceProxy(serviceName, ros2.msg.getSrv(self.type).rosType)
		
		
	def __call__(self,*param,**params):
		msg = ros2.msg.getSrv(self.type)
		try:
			if len(param) == 1 and isinstance(param[0],dict) and len(params) == 0:
				#直接传字典的运行方法 
				response = self.imp(msg.request.toRos(param[0]))  
			else:
				response = self.imp(*param,**params)  
			if self.useRosType:
				return response
			else:
				return msg.response.toDict(response)
		except rospy.ServiceException as e:
			log.exception("Service call failed:"+self.type,e)
			raise
		
	def wait(self,timeout):
		rospy.wait_for_service(self.name,timeout=timeout)
	
	def invoke(self,*param,**params):
		return self(*param,**params)
		
		
#返回值为字典 
def invoke(serviceType,serviceName,*params):
	return client(serviceType,serviceName)(*params)
		


g_services = {}

def startService(serviceType,serviceName,callback):
	global g_services
	if serviceName not in g_services:
		g_services[serviceName] = service(serviceType,serviceName,callback,utility.is_ros())
	

#def stopService():
#	global g_services
#	if serviceName in g_services:
#		del g_services[serviceName]
#	
	
############ unit test ############ 
def testgetResponse():
	import std_srvs.srv as s
	a = s.SetBoolRequest()
	b = getResponse(a)
	assert isinstance(b,s.SetBoolResponse)
	
def testclient1():
	ret = invoke("roscpp/SetLoggerLevel","/rosout/set_logger_level","/rosout","ERROR")
	print(ret)

	c = client(None,"/rosout/get_loggers")()
	ll = c["loggers"]
	find = False
	for r in ll:
		if r["name"] == "/rosout":
			assert r["level"] == "error"
			find = True
	assert find 
	
def testserver():
	def handle_reloc(msg):
		print("caller is",getCaller(msg))
		
	startService("robot_msg/Reloc","ss/Reloc",		handle_reloc)
	ros2.rosUtility.wait()
	
if __name__ == "__main__": 
	#要先执行 rosrun turtlesim turtlesim_node
	utility.start()
	ros2.msg.init()
	ros2.rosUtility.init("ycattest2")
	testgetResponse()
	testclient1() 
	
	testserver()
	

	
	
	
	
	
	
	
	
	
	
	
	
	
