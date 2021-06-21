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
import utility

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

def handle_laser(msg):
	n = utility.now()
	t1 = msg.header.stamp
	t1 = ros2.rosUtility.time2Py(t1)
	print(n-t1)
	time.sleep(0.1)
	
if __name__ == "__main__": 	
	import ros2.rosUtility 
	ros2.rosUtility.init("test_laser") 
	ros2.topic.subscriber("/scan","sensor_msgs/LaserScan",	 	handle_laser,useRosType=True,queueSize=1) 
	ros2.rosUtility.wait()
	
	if "client" in sys.argv:
		startClient()
	else:
		startServer()
	  
	
	
	
	
	
	
	
