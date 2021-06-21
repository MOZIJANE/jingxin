import rospy   
import os,sys
import time
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import utility
import ros2.msg   
import ros2.topic 
import ros2.srv
import ros2.transform
import threading
import lock as lockImp
import counter

@ros2.srv.catch
def handle(msg):
	print(msg)
	return

def startServer():
	print("start server")
	ros2.rosUtility.init("test_server") 
	ros2.srv.startService("robot_msg/RobotCmd","robot/Alarm",handle) 
	ros2.rosUtility.wait()
	
def startClient():
	print("start client")
	ros2.rosUtility.init("test_client") 
	c = counter.counter()
	while True:
		param = {}
		param["cmd_type"] = 4001
		param["cmd_value"] = "ycat"
		try:
			ros2.srv.invoke("robot_msg/RobotCmd","robot/Alarm",param)
		except Exception as e:
			print("raise alarm failed",str(e))
		c.check()


	
if __name__ == "__main__": 	
	import ros2.rosUtility 
	
	if "client" in sys.argv:
		startClient()
	else:
		startServer()
	  
	
	
	
	
	
	
	
