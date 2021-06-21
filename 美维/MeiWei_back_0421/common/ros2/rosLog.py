#coding=utf-8
# ycat			2019-7-25	  create 
import os
import rospy   
		
g_enable_log = True

def _makeMsg(*param):	 
	msg = ""
	for p in param:
		msg += str(p) + " " 
	return msg.rstrip()
	
def debug(*param):	
	if not g_enable_log:
		return
	try:
		rospy.logdebug(_makeMsg(*param))
	except Exception as e:
		print("roslog:",e) 
	
def info(*param):
	if not g_enable_log:
		return	
	try:
		rospy.loginfo(_makeMsg(*param))
	except Exception as e:
		print("roslog:",e)  
	
def warning(*param):	
	if not g_enable_log:
		return
	try:
		rospy.logwarn(_makeMsg(*param))
	except Exception as e:
		print("roslog:",e) 
		 

def error(*param):	
	if not g_enable_log:
		return
	try:
		rospy.logerr(_makeMsg(*param))
	except Exception as e:
		print("roslog:",e) 
		 
def abort(*param):	
	if not g_enable_log:
		return
	try:
		rospy.logfatal(_makeMsg(*param))	 
	except Exception as e:
		print("roslog:",e)  
	os.sys.exit(0)
		
		 

########## unit test ##########
def testlog():
	import rosUtility
	rosUtility.init("testlog")
	debug("this is a debug msg",1,2,3)
	info("this is a info msg",1,2,3)
	warning("this is a warning msg",1,2,3)
	error("this is a error msg",1,2,3)
	abort("this is a abort msg",1,2,3)

	 

if __name__ == "__main__":
	testlog() 
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	

	
	
	
	
	
	
	
	
	
	
	
	
	
