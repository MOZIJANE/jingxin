# coding: utf-8
# author: pengshuqin
# date: 2020-08-07
# desc: roslog

import os
import rospy 
import time


import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
	
import ros2.rosUtility
import ros2.topic
	
g_enable_log = True
g_publisher = None
# std_msgs/Header header
  # uint32 seq
  # time stamp
  # string frame_id
# byte level #DEBUG=1 INFO=2 WARN=4 ERROR=8 FATAL=16
# ----string name 节点
# ----string msg  
# string file
# ----string function  debug/info/warn/error/fatal
# uint32 line
# string[] topics
def _makeMsg(*param):	 
	msg = ""
	for p in param:
		msg += str(p) + " " 
	msg = msg.rstrip()
	return msg
		
def sendRos(level,msg):
	if not ros2.rosUtility.isInited():
		return
	import rosgraph_msgs.msg
	global g_publisher
	if g_publisher is None:
		g_publisher = ros2.topic.publisher("robot/rosLog","rosgraph_msgs/Log",isLog=False)
	rosmsg = rosgraph_msgs.msg.Log()
	rosmsg.name = ros2.rosUtility.g_nodeName
	rosmsg.function = level
	rosmsg.msg = msg
	g_publisher.send(rosmsg)
			
	
def debug(*param):	
	if not g_enable_log:
		return
	try:
		sendRos("debug",_makeMsg(*param))
	except Exception as e:
		print("roslog:",e) 
	
def info(*param):
	if not g_enable_log:
		return	
	try:
		sendRos("info",_makeMsg(*param))
	except Exception as e:
		print("roslog:",e)  
	
def warning(*param):	
	if not g_enable_log:
		return
	try:
		sendRos("warn",_makeMsg(*param))
	except Exception as e:
		print("roslog:",e) 
		 

def error(*param):	
	if not g_enable_log:
		return
	try:
		sendRos("error",_makeMsg(*param))
	except Exception as e:
		print("roslog:",e) 
		 
def abort(*param):	
	if not g_enable_log:
		return
	try:
		sendRos("fatal",_makeMsg(*param))	 
	except Exception as e:
		print("roslog:",e)  
	# os.sys.exit(0)
		
		

########## unit test ##########
def testlog():
	import time
	ros2.rosUtility.init("testlog")
	while True:
		debug("this is a debug msg",1,2,3)
		time.sleep(1)
		info("this is a info msg",1,2,3)
		time.sleep(1)
		warning("this is a warning msg",1,2,3)
		time.sleep(1)
		error("this is a error msg",1,2,3)
		time.sleep(1)
		abort("this is a abort msg",1,2,3)
		time.sleep(1)
	

if __name__ == "__main__":
	testlog() 