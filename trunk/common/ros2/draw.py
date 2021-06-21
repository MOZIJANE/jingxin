#coding=utf-8
# ycat			2018-10-03	  create 
# 默认rviz不会显示,要增加marker层
# 点击Add按键，然后选择Markers层
# No tf data.  Actual error: Fixed Frame [map] does not exist
# 把Global Options的FixedFrame设置为map
# 
# 注意：不同进程间的ns不能相同，要不然会导致marker显示时闪烁的问题 
import rospy   
import time
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import utility
import ros2.msg   
import ros2.topic 
import ros2.transform
import threading
import lock as lockImp
#具体参数可见： http://wiki.ros.org/rviz/DisplayTypes/Marker 

g_sn = 0
g_currentFrame = "/map"


def getFrame():
	global g_currentFrame
	return g_currentFrame
	

def setFrame(frame):
	global g_currentFrame
	g_currentFrame = frame
	

def sphere(position=(0,0,0),orientation=(0,0,0),size=(1,1,1),color=(255,255,255),
		transparent=1.0,id=None,ns=None,lifetime=0,frame=None,activeMarker=False):
	return _drawSimpleMarker(id,2,position,orientation,size,color,transparent,lifetime,frame,ns,activeMarker=activeMarker)
	
	
def spheres(points,size=(1,1,1),color=(255,255,255),transparent=1.0,id=None,ns=None,lifetime=0,frame=None):
	return _drawListMarker(typeId=7,pointList=points,size=size,color=color,
		transparent=transparent,id=id,ns=ns,lifetime=lifetime,frame=frame)
	
def cylinder(position=(0,0,0),orientation=(0,0,0),size=(1,1,1),color=(255,255,255),
	transparent=1.0,id=None,ns=None,lifetime=0,frame=None,activeMarker=False):
	return _drawSimpleMarker(id,3,position,orientation,size,color,transparent,lifetime,frame,ns,activeMarker=activeMarker)
		
	
def cube(position=(0,0,0),orientation=(0,0,0),size=(1,1,1),color=(255,255,255),transparent=1.0,
	id=None,ns=None,lifetime=0,frame=None,activeMarker=False):
	return _drawSimpleMarker(id,1,position,orientation,size,color,transparent,lifetime,frame,ns,activeMarker=activeMarker)
	

def cubes(points,size=(1,1,1),color=(255,255,255),transparent=1.0,id=None,ns=None,lifetime=0,frame=None):
	return _drawListMarker(typeId=6,pointList=points,size=size,color=color,
		transparent=transparent,id=id,ns=ns,lifetime=lifetime,frame=frame)
	

def arrow(startPoint=(0,0,0),endPoint=(1,1,0),
			shaftDiameter=0.1,headDiameter=0.3,headLength=0.3,color=(255,255,255),
			transparent=1.0,id=None,ns=None,lifetime=0,frame=None,activeMarker=False):  
	data = _getData(id,0,(0,0,0),(0,0,0),(shaftDiameter,headDiameter,headLength),color,transparent,lifetime,frame,ns)
	data["points"] = []
	data["points"].append({"x":startPoint[0],"y":startPoint[1],"z":startPoint[2]})
	data["points"].append({"x":endPoint[0],"y":endPoint[1],"z":endPoint[2]}) 
	return _send(data,activeMarker=activeMarker) 
	

def arrow2(position=(0,0,0),orientation=(0,0,0),
			arrowLength=1.0,arrowWidth=0.1,arrowHeight=0.1,color=(255,255,255),
			transparent=1.0,id=None,ns=None,lifetime=0,frame=None,activeMarker=False):
	data = _getData(id,0,position,orientation,(arrowLength,arrowWidth,arrowHeight),color,transparent,lifetime,frame,ns) 
	return _send(data,activeMarker=activeMarker) 
	

def line(startPoint=(0,0,0),endPoint=(1,1,0),width=0.1,color=(255,255,255),
			transparent=1.0,id=None,ns=None,lifetime=0,frame=None):
	return lines(points=[startPoint,endPoint],color=color,width=width,transparent=transparent,id=id,lifetime=lifetime,frame=frame,ns=ns) 
	
	
def lines(points,color=(255,255,255),width=0.1,transparent=1.0,id=None,ns=None,lifetime=0,frame=None):
	return _drawListMarker(typeId=4,pointList=points,size=(width,0,0),color=color,
		transparent=transparent,id=id,ns=ns,lifetime=lifetime,frame=frame)
	

def point(position=(0,0,0),color=(255,255,255),width=0.1,height=0.1,transparent=1.0,
	id=None,ns=None,lifetime=0,frame=None):
	return points([position,],color=color,width=width,height=height,transparent=transparent,id=id,lifetime=lifetime,frame=frame,ns=ns) 
	

def points(pts=[],color=(255,255,255),size=0.1,transparent=1.0,
	id=None,ns=None,lifetime=0,frame=None):
	return _drawListMarker(typeId=8,pointList=pts,size=(size,size,0),color=color,
		transparent=transparent,id=id,ns=ns,lifetime=lifetime,frame=frame)
	 
	
def text(strValue,position=(0,0,0),color=(255,255,255),height=0.3,transparent=1.0,
	id=None,ns=None,lifetime=0,frame=None,activeMarker=False):
	orientation=(0,0,0)
	data = _getData(id,9,position,orientation,(0,0,height),color,transparent,lifetime,frame,ns)
	data["text"] = strValue
	return _send(data,activeMarker=activeMarker) 
	
	
def delete(id):
	data = {}
	data["header"] = ros2.msg.headerDict(getFrame()) 
	data["ns"],data["id"] = _splitId(id)
	data["type"] =  0
	data["action"] = 2 #delete  
	_send(data,activeMarker=False)

#TODO：未实现 	
#Line List (LINE_LIST=5) 
#Triangle List (TRIANGLE_LIST=11) [1.1+]
#Mesh Resource (MESH_RESOURCE=10) [1.1+]

	
def clear():
	data = {}
	data["header"] = ros2.msg.headerDict(getFrame()) 
	data["ns"] = ""
	data["id"] = 0
	data["type"] =  0
	data["action"] = 3 #delete all  
	_send(data,activeMarker=False)
	
	
def _drawSimpleMarker(id,type,position,orientation,size,color,transparent,lifetime,frame,ns,activeMarker=False):
	data = _getData(id,type,position,orientation,size,color,transparent,lifetime,frame,ns)
	return _send(data,activeMarker) 
	   

def _drawListMarker(typeId,pointList,size,color,transparent,id,ns,lifetime,frame):
	orientation=(0,0,0)
	data = _getData(id,typeId,(0,0,0),orientation,size,color,transparent,lifetime,frame,ns)
	data["points"] = []
	for p in pointList:
		if len(p) == 3:
			data["points"].append({"x":p[0],"y":p[1],"z":p[2]}) 
		else:
			data["points"].append({"x":p[0],"y":p[1],"z":0}) 
	_send(data,activeMarker=False) 
	return data["ns"] + "." + str(data["id"])
	
def _getData(id,type,position,orientation,size,color,transparent,lifetime,frame,ns):
	data = {}
	if frame is None:
		data["header"] = ros2.msg.headerDict(getFrame()) 
	else:
		data["header"] = ros2.msg.headerDict(frame) 
	if id is None:
		if ns:
			data["ns"] = ns
		else:
			data["ns"] = utility.app_name()
		data["id"] = _getSn()
	else: 
		if id.find(".") != -1:
			data["ns"],data["id"] = _splitId(id)
		else:
			data["ns"] = ns
			data["id"] = id
		if ns: 
			assert data["ns"] == ns #id有值时，ns不能和id不能冲突 
			
	data["type"] =  type
	data["action"] = 0 #ADD  
	
	data["pose"] = {"position":{}}
	data["pose"]["position"]["x"] = position[0]
	data["pose"]["position"]["y"] = position[1]
	if len(position) == 3:
		data["pose"]["position"]["z"] = position[2]
	else:
		data["pose"]["position"]["z"] = 0
	data["pose"]["orientation"] = {}
	
	o = ros2.transform.quaternion_from_euler(*orientation)
	data["pose"]["orientation"]["x"] = o[0]
	data["pose"]["orientation"]["y"] = o[1]
	data["pose"]["orientation"]["z"] = o[2]
	data["pose"]["orientation"]["w"] = o[3]
	
	data["scale"] = {}
	data["scale"]["x"] = size[0]
	data["scale"]["y"] = size[1]
	data["scale"]["z"] = size[2]
	
	data["color"] = {}
	data["color"]["a"] = transparent
	data["color"]["r"] = color[0]/255.0
	data["color"]["g"] = color[1]/255.0 
	data["color"]["b"] = color[2]/255.0
	if lifetime:
		data["lifetime"] = lifetime
	data["frame_locked"] = True 
	return data
	
	
def _getSn():
	global g_sn
	g_sn += 1
	return g_sn

	
def _splitId(idValue):
	i = idValue.find(".")
	assert i != -1
	return idValue[0:i],int(idValue[i+1:])
	

g_makers = {}
g_visualization_marker = None
g_thread = None
g_lock = lockImp.create("ros.draw")

@lockImp.lock(g_lock)
def _send(data,activeMarker=False):
	if activeMarker:
		return ros2.msg.getRosObs("visualization_msgs/Marker",data)
		
	global g_makers
	global g_visualization_marker
	global g_thread
	if g_visualization_marker is None:
		g_visualization_marker = ros2.topic.publisher("visualization_marker","visualization_msgs/Marker",queueSize=1000)
		g_thread = threading.Thread(target=_autoSendMarker)
		g_thread.start()
		
	assert data
	frameId = data["header"]["frame_id"]
	key = data["id"]#data["ns"] + "." + str(data["id"])
	action = data["action"]
	if frameId not in g_makers or action == 3: #delete all  
		g_makers[frameId] = {} 
	if action == 2: #delete
		if key in g_makers:
			del g_makers[frameId][key]
	elif action == 0: #ADD  
		g_makers[frameId][key] = data 
	lockImp.release(g_lock)
	g_visualization_marker.send(data)
	return data["ns"] + "." + str(data["id"])

#只有不停发送界面才能收到数据  
def _autoSendMarker():
	while not utility.is_exited():
		lockImp.acquire(g_lock)
		for frame in g_makers.values():
			for data in frame.values(): 
				g_visualization_marker.send(data)
				time.sleep(0)
		lockImp.release(g_lock)
		time.sleep(3) 
	
	
############ unit test ############
def testclient(): 
	#sphere(position=(4,1,0),size=(1,1,1))
	cylinder(position=(4,4,0))
	#arrow()
	#line((0,0,0),(1,10,0),color=(0,255,0))
	#lines([(0,0,0),(1,8,0),(4,3,0)],color=(0,255,255))
	points([(0,0,0),(1,8,0),(4,3,0)],color=(0,255,255))
	
	cubes([(0,0,0),(1,8,0),(4,3,0)],color=(255,0,255))
	
	#for i in range(100):
	#	point((0+i*0.1,12.4,0),color=(255,0,0))
	points([(0+x*0.1,x,0) for x in range(100)])
	text("HELLO WORLD")
	arrow2()
	
def testfollowTf():
	setFrame("ycat")
	text("HELLO WORLD")
	spheres([(0,0,0),(1,8,0),(4,3,0)],color=(0,255,255))
	
if __name__ == "__main__": 	
	import ros2.rosUtility 
	ros2.rosUtility.init("ycattest2") 
	#testclient()
	testfollowTf()
	
	import time
	import ros2.transform
	i = 0
	while True:
		ros2.transform.send2D(i,0,0,parent="map",child="ycat")
		time.sleep(1)
		i += 0.1
	  
	
	
	
	
	
	
	
