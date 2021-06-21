#coding=utf-8
# ycat			2018-10-03	  create 
import os,sys
import rospy 
import rosnode
import genpy
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)  
import log
import datetime
import time
import utility
import numpy as np 
g_nodeName = None

def init(name,anonymous=False):
	import traceWriter
	global g_nodeName
	if g_nodeName:
		log.warning("repeat ros init, name=",g_nodeName,",name2",name)
		return 
	assert name.find(" ") == -1
	rospy.init_node(name, anonymous=anonymous)
	log.info("init ros node:",name)
	traceWriter.addEvent("startup",{"name":name,"pid":os.getpid()})
	rospy.on_shutdown(utility.finish)
	g_nodeName = name
	
def isInited():
	global g_nodeName
	return g_nodeName is not None
	
def wait():
	rospy.spin()
 
def isShutdown():
	return rospy.is_shutdown()
	
	
def shutdown(reason):
	rospy.signal_shutdown(reason)
	

def run(loopFunc,timeout):
	r = rospy.Rate(1.0/timeout)
	while not isShutdown():
		loopFunc()
		r.sleep()
		
#Ros参数查询
def getParam(key="/"):
	return rospy.get_param(key)
	
#Ros参数设置 
def setParam(key,value):
#	log.info("ros set param",key,"=",value)
	if isinstance(value,np.float64):
		value = float(value)
	rospy.set_param(key,value)
	
def delParam(key):
	log.info("ros del param",key)
	rospy.delete_param(key)

def hasParam(key):
	return rospy.has_param(key)
	
def sleep(secs):
	rospy.sleep(secs)
	
#如果use_sim_time设置为True，则时间不能和py的时间互换 
def time2Ros(t): 
	if isinstance(t,datetime.datetime):
		return rospy.Time(t.timestamp())
	elif isinstance(t,str):
		t = utility.str2date(t)
		return rospy.Time(t.timestamp())
	else:
		assert isinstance(t,float)
		return rospy.Time(t)
	
def time2Py(t):
	if isinstance(t,datetime.datetime):
		return t
	if isinstance(t,(rospy.Time,genpy.rostime.Time)):
		return datetime.datetime.fromtimestamp(t.to_time())
	assert isinstance(t,(int,float))
	return datetime.datetime.fromtimestamp(t)
		
def now():
	return rospy.Time.now()


def getNodes():
	return rosnode.get_node_names()

def kill(nodes):
	if isinstance(nodes,str):
		rosnode.kill_nodes([nodes,])
	else:
		rosnode.kill_nodes(nodes)
		

def ping(node):
	return rosnode.rosnode_ping(node,max_count=1,verbose=False)
	
	
#返回例子 (['/rostopic', '/rosout'], []) 
def pingAll():
	return rosnode.rosnode_ping_all()
		 
		 

########## unit test ########## 

	
def testgetnodes():
	nn = getNodes()
	assert len(nn) >= 1
	print(nn)
	
	
def testparam():
	assert "rosversion" in getParam()
	#assert True == getParam("use_sim_time")
	setParam("background_b",155)
	assert 155 == getParam("background_b")
	assert hasParam("background_b")
	delParam("background_b")
	assert  hasParam("background_b")

def testtime():
	n = datetime.datetime.now()
	t = time2Ros(n)
	assert time2Py(t) == n
	assert time2Ros(n.timestamp()) == t
	print(n,t,time2Py(t))

def testping():
	import time
	for i in range(100):
		x = ping("alarmNode")
		print(x,type(x))
		time.sleep(1)

if __name__ == "__main__": 
	testping()
	testgetnodes()
	testparam()
	testtime()
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	

	
	
	
	
	
	
	
	
	
	
	
	
	
