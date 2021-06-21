#coding=utf-8
# ycat			2018-08-03	  create 
import time
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import shell,utility
import log 
import ros2.msg as msg
if utility.is_ros():
	import rospy
	import ros2.rosUtility as rosUtility

#返回topic列表
def getTopicList():
	assert utility.is_ros()
	ret = shell.run_cmd2("rostopic list")
	if not ret[1]:
		raise Exception("执行rostopic list失败")
	return [ x for x in ret[0].split("\r\n") if x ]
	

#取得topic的消息类型名 
def getTopicMsgType(topic):
	if topic == "odom" or topic == "/odom":
		return "nav_msgs/Odometry"
	elif topic == "scan" or topic == "/scan":
		return "sensor_msgs/LaserScan"
	elif topic == "map" or topic == "/map": 
		return "nav_msgs/OccupancyGrid"
	elif topic == "cmd_vel" or topic == "/cmd_vel":
		return "geometry_msgs/Twist"
	elif topic == "robot_pose" or topic == "/robot_pose":
		return "geometry_msgs/PoseStamped"
	assert utility.is_ros()
	ret = shell.run_cmd2("rostopic info "+topic)
	if not ret[1]:
		raise Exception("执行rostopic info失败")
	line = ret[0].splitlines()[0]
	return line[line.find("Type: ")+len("Type: "):]

g_isInited = False

#ROS的bug, 如果publisher在rospy.init_node之后初始化，第一个包也会丢
def _init():
	global g_isInited
	if g_isInited:
		return
	g_isInited = True
	import rosgraph_msgs.msg
	m = rosgraph_msgs.msg.Log()
	p = publisher("rosout","rosgraph_msgs/Log")
	p.send(m)
	time.sleep(0.5)
	p.send(m)


#rospy.Publisher
#@param name: resource name of topic, e.g. 'laser'. 
#@type  name: str
#@param data_class: message class for serialization
#@type  data_class: L{Message} class
#@param subscriber_listener: listener for subscription events. May be None. [监听连上来的客户端]
#@type  subscriber_listener: L{SubscribeListener}
#@param tcp_nodelay: If True, sets TCP_NODELAY on
#  publisher's socket (disables Nagle algorithm). This results
#  in lower latency publishing at the cost of efficiency.
#@type  tcp_nodelay: bool
#@param latch: If True, the last message published is
#'latched', meaning that any future subscribers will be sent
#that message immediately upon connection.
#@type  latch: bool
#@param headers: If not None, a dictionary with additional header
#key-values being used for future connections.
#@type  headers: dict
#@param queue_size: The queue size used for asynchronously
#publishing messages from different threads.  A size of zero
#means an infinite queue, which can be dangerous.  When the
#keyword is not being used or when None is passed all
#publishing will happen synchronously and a warning message
#will be printed.
#@type  queue_size: int
class publisher:
	def __init__(self,topic,msgType=None,queueSize=10,isLog=True): 
		assert utility.is_ros()
		assert rosUtility.isInited()
		assert topic
		self.topic = topic
		if msgType is None:	
			msgType = getTopicMsgType(topic)
		self.msgType = msgType 			  
		self._imp = rospy.Publisher(topic, msg.getMsg(self.msgType).rosType, queue_size=queueSize)
		if isLog:
			log.info("ros publisher:",topic,",msg type:",msgType)
		
	def send(self,data): 
		global g_isFirst
		if isinstance(data,dict):
			data = msg.getMsg(self.msgType).toRos(data)
		_init()
		self._imp.publish(data) 
		
	def connections(self):
		return self._imp.get_num_connections()
		
	def waitConnect(self,timeout=1,clientCount=1):
		for i in range(timeout*10):
			if self.connections() >= clientCount:
				return True
			time.sleep(0.1)
		return False
		
	def unregister(self):
		self._imp.unregister()
		

class subscriber:
	#callback原型： callback(data) 
	def __init__(self,topic,msgType,callback,useRosType=False,queueSize=10): 
		assert utility.is_ros()
		assert rosUtility.isInited()
		assert topic
		self.callback = callback
		self.useRosType = useRosType
		if msgType is None:	
			msgType = getTopicMsgType(topic)
		self.msgType = msgType  
		self.topic = topic
		self._imp = rospy.Subscriber(topic,msg.getMsg(self.msgType).rosType, self._callback,queue_size=queueSize)
		log.info("ros subscriber:",topic,"msg type:",msgType)
	
	def _callback(self,data):
		if self.useRosType:
			self.callback(data)
		else:
			self.callback(msg.getMsg(self.msgType).toDict(data))
		
	def unregister(self):
		log.info("ros unsubscriber:",self.topic,"msg type:",self.msgType)
		self._imp.unregister()
		
g_pubs = {}
g_subs = {}

def send(topic,data,msgType=None):
	global g_pubs
	if topic not in g_pubs:
		g_pubs[topic] = publisher(topic,msgType=msgType)
	g_pubs[topic].send(data)
	
	
def register(topic,callback,msgType=None):
	global g_subs
	if topic not in g_subs:
		g_subs[topic] = subscriber(topic,msgType=msgType,callback=callback,useRosType=utility.is_ros())

def unregister(topic):
	global g_subs
	if topic in g_subs:
		g_subs[topic].unregister()
		del g_subs[topic]

	
############ unit test ############
def testgetTopicList():
	ll = getTopicList()
	assert "" not in ll
	assert "/rosout" in ll 
	assert getTopicMsgType("/rosout")  == "rosgraph_msgs/Log"
	
def testpub(): 
	import enhance
	def callback(ret,data):
		assert data["data"] == "hello ros"
		ret["data"] = data["data"]
		
	p = publisher("/ycat_test","std_msgs/String")
	ret = {}
	s = subscriber("/ycat_test","std_msgs/String",enhance.bind(callback,ret))
	time.sleep(1)
	assert 1 == p.connections()
	p.send({"data":"hello ros"})
	time.sleep(0.01) 
	assert ret["data"] == "hello ros"

#def sendSim():
#	def callback(data):
#		print(data)
#	s2 = subscriber("/turtle1/color_sensor",None,callback)	
#	s = subscriber("/turtle1/pose",None,callback)
#	
#	p = publisher("/turtle1/cmd_vel")	
#	for i in range(100):
#		data = {}
#		data["linear"] = {"x":8,"y":0,"z":0}
#		data["angular"] =  {"x":0,"y":0,"z":0}
#		#p.send(data)
#		#p2.send({"r":255,"g":0,"b":0})
#		time.sleep(1)
	
if __name__ == "__main__":
	utility.start()
	rosUtility.init("ycattest")
	#sendSim()
	#rosUtility.wait()
	utility.run_tests()

	
	
	
	
	
	
	
	
	
	
	
	
	
