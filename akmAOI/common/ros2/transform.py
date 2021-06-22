#coding=utf-8
# ycat			2018-10-03	  create 
import rospy
import genpy
import math
import tf
import threading
import time
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import utility
import log  

#对应关系 target=parent, src=child
# x=roll  y=pitch  z=yaw 
def quaternion_from_euler(x,y,z):
	return tf.transformations.quaternion_from_euler(x, y, z) 
	
def quaternion_from_yaw(z):
	return quaternion_from_euler(0, 0, z) 

def euler_from_quaternion(q):
	return tf.transformations.euler_from_quaternion(q)
	
def euler_from_quaternion2(x,y,z,w):
	q = [x,y,z,w]
	return euler_from_quaternion(q)
	
def yaw_from_quaternion(q):
	return euler_from_quaternion(q)[2]
	
g_publisher = None
g_static_publisher = None
g_listener = None
	
def _getPub():
	global g_publisher
	if g_publisher is None:
		g_publisher = publisher()
	return g_publisher
	
	
def _getStaticPub():
	global g_static_publisher
	if g_static_publisher is None:
		g_static_publisher = staticPublisher()
	return g_static_publisher	
	
	
def _getListen():
	global g_listener
	if g_listener  is None:
		g_listener = subscriber()
	return g_listener
	 
	
def send2D(x,y,r,child,parent,time=None):
	return _getPub().send2D(x,y,r,child=child,parent=parent,time=time)
	
#angles为欧拉角(rpy)或四元数(q1,q2,q3,q0) 
def send3D(pos,angles,child,parent,time=None):
	return _getPub().send3D(pos,angles,child=child,parent=parent,time=time)
	
def sendStatic2D(x,y,r,child,parent,hz=10):
	return _getStaticPub().send2D(x,y,r,child=child,parent=parent,hz=hz)

#angles为欧拉角(rpy)或四元数(q1,q2,q3,q0) 
def sendStatic3D(pos,angles,child,parent,hz=10):
	return _getStaticPub().send3D(pos,angles,child=child,parent=parent,hz=hz)
	
def lookup2D(child,parent, time=None):
	return _getListen().lookup2D(child=child,parent=parent,time=time)
	
#返回(x,y,z),(q1,q2,q3,q0) 
def lookup3D(child,parent, time=None):
	return _getListen().lookup3D(child=child,parent=parent,time=time)
	
#-1为无限等待 
def wait(child,parent,second=-1):
	return _getListen().wait(child=child,parent=parent,second=second)
	
def canTransform(child,parent, time=None):
	return _getListen().canTransform(child=child,parent=parent,time=time)
	
	
class publisher:
	def __init__(self):
		self.imp = None  
	
	# tf assumes that all transforms move from parent to child
	#发送2维的变换矩阵 
	#可以通过命令： rosrun tf tf_echo <parent> <child> 输出的是:child相对于parent的坐标 
	def send2D(self,x,y,r,child,parent,time=None):
		return self.send3D((x,y,0),(0,0,r),parent=parent,child=child,time=time)
		
	def send3D(self,pos,angles,child,parent,time=None):
		assert 3 == len(pos)
		if 4 == len(angles):
			#四元数 
			q = angles
		else:
			assert 3 == len(angles)
			q = quaternion_from_euler(*angles)
		import geometry_msgs
		if time is None:
			time = rospy.Time.now() 
		else: 
			assert isinstance(time,rospy.Time) or isinstance(time,genpy.rostime.Time)  
		if self.imp is None:
			self.imp = tf.TransformBroadcaster() 
		self.imp.sendTransform(pos, q, time=time, child=child, parent=parent)
		

class staticPublisher:
	def __init__(self,hz=10.):
		self.imp = None 
		self.thread = None
		self.timeout = 1./hz
		self.buffer = {}
		
	def send2D(self,x,y,r,child,parent,hz=10):
		return self.send3D((x,y,0),(0,0,r),parent=parent,child=child,hz=hz)
		
	def send3D(self,pos,angles,child,parent,hz=10):
		import geometry_msgs
		if self.imp is None:
			self.imp = publisher()
			self.thread = threading.Thread(target=self._threadFunc)
			self.thread.start()
			
		key = parent+"->"+child
		if key not in self.buffer:
			s = {}
			s["parent"] = parent
			s["child"] = child
			s["pos"] = pos
			s["angles"] = angles
			self.buffer[key] = s
			log.info("ros2.tf.sendStatic3D: %s->%s"%(child,parent),pos,angles)
		
	def _threadFunc(self):
		while not utility.is_exited():
			for s in self.buffer.values():
				self.imp.send3D(**s)
			time.sleep(self.timeout)
			
	
	
#TF还有些自动转换消息的函数未封装，可以把消息里的header.frame_id和当前的frame进行映射 
#'transformPoint', 'transformPointCloud', 'transformPose', 'transformQuaternion', 'transformVector3' 
class subscriber:
	def __init__(self):
		self.imp = tf.TransformListener()
		
	def canTransform(self,child, parent, time=None):
		if time is None:
			time = rospy.Time(0) 
		return self.imp.canTransform(target_frame=parent,source_frame=child,time=time) == 1
	
	#查找2维的变换，返回x,y,rad
	def lookup2D(self,child, parent, time=None):
		t,q = self.lookup3D(child,parent,time)
		if t is None:
			return None 
		return t[0],t[1],yaw_from_quaternion(q)
		
	#查找3维的变换，返回(x,y,z) (四元数)
	def lookup3D(self,child, parent, time=None):
		if time is None:
			# Providing rospy.Time(0) will just get us the latest available transform.  
			time = rospy.Time(0) 
		else: 
			assert isinstance(time,rospy.Time) or isinstance(time,genpy.rostime.Time)
		try:
			trans,q = self.imp.lookupTransform(target_frame=parent,source_frame=child,time=rospy.Time(0)) 
			return trans,q
		except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException) as e:
			log.warning("ros2.tf:lookup %s->%s failed: "%(child,parent),str(e))
		return None,None  
		
	def wait(self,child, parent, second=-1):
		if second == -1:
			while True:
				if self.canTransform(child,parent):
					return True
				log.info("ros2.tf: wait %s->%s failed"%(child,parent))
				time.sleep(1)
		else:
			for i in range(second):
				if self.canTransform(child,parent):
					return True
				log.info("ros2.tf: wait %s->%s failed"%(child,parent))
				time.sleep(1)
		return False
		
	
############ unit test ############
def teststatic():
	import time,math
	for i in range(10):
		#sendStatic(10,-0.2,math.pi/3.,"base_link","ycat") 
		send2D(10,-0.2,math.pi/3.,child="ycat",parent="world") 
		print("send tf")
		time.sleep(1)
	assert 0
		
	
def testclient():
	l = subscriber()
	b = publisher()
	
	t = utility.ticks()
	assert not l.wait("world","ycat",2)
	assert (utility.ticks() - t) > 1900
	
	for i in range(5):
		while True:
			b.send2D(5,10,3.14/4,"ycat","world")
			print("send 2d")
			time.sleep(0.4)
			if l.wait("ycat","world",1):
				break
		ret = l.lookup2D("ycat","world") 
		print(ret)
		assert ret
		assert utility.equal(ret[0],5.0,floatDiff=0.1)
		assert utility.equal(ret[1],10.0,floatDiff=0.1)
		assert utility.equal(ret[2],0.785,floatDiff=0.1) 
		 
		ret = l.lookup2D("world","ycat") 
		assert utility.equal(ret[0],-10.605,floatDiff=0.1)
		assert utility.equal(ret[1],-3.5397,floatDiff=0.1)
		assert utility.equal(ret[2],-0.785,floatDiff=0.1) 
		time.sleep(1)
		
	#读取旧的tf 
	#now = rospy.Time.now()
	#past = now - rospy.Duration(1.0) 
	#ret = l.lookup2D("ycat","world",past,now,"world")
	#assert utility.equal(ret[0],-10.605,floatDiff=0.1)
	#assert utility.equal(ret[1],-3.5397,floatDiff=0.1)
	#assert utility.equal(ret[2],-0.785,floatDiff=0.1) 
	sendStatic3D((1,2,0.4),(0,math.pi/4,0),child="ycat2",parent="world")
	assert wait("world","ycat2",10)
	assert wait("ycat2","world",10)
	t,q = lookup3D(child="ycat2",parent="world")
	print(t)
	assert t is not None
	assert q is not None
	a = euler_from_quaternion(q)
	print(a)
	assert t == [1,2,0.4]
	assert a[0] == 0
	assert a[2] == 0
	assert utility.near(a[1],math.pi/4,0.001)
	utility.finish()
	
	
def testtime():
	import time
	print(lookup2D(child="ycat",parent="map",time=now))
	send2D(x=0,y=0,r=0,child="ycat",parent="map")
	time.sleep(1)
	now = rospy.Time.now()
	print(now)
	time.sleep(1)
	send2D(x=10,y=0,r=0,child="ycat",parent="map")
	print(lookup2D(child="ycat",parent="map",time=now))
	
if __name__ == "__main__": 	
	import ros2.rosUtility
	
	utility.start() 
	ros2.rosUtility.init("ycattest2")
	testtime() 
#	teststatic()	
	
	
	
	
	
	
