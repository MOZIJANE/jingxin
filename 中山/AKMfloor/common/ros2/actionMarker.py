#coding=utf-8
# ycat			2018-08-03	  create 
# http://wiki.ros.org/rviz/Tutorials/Interactive%20Markers%3A%20Basic%20Controls 
import rospy
import time
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import shell,utility
import log
import ros2.msg  
import ros2.rosUtility   
import interactive_markers.interactive_marker_server as interactive
import visualization_msgs.msg as m
import interactive_markers.menu_handler as m2
from geometry_msgs.msg import Point

def defaultActionCallback(action,position,orientation):
	print(action.name + " is at ",position,orientation)
	

class actionMarker:
	def __init__(self,frameId,name,desc="",position=(0,0,0),scale=1,callback=defaultActionCallback):
		self._marker = m.InteractiveMarker()
		self._marker.header.frame_id = frameId
		self._marker.pose.position = Point(*position)
		self._marker.scale = scale 
		self._marker.name = name
		self._marker.description = desc
		self._server = None
		self.callback = callback
		self.hasMarker = False 
	
	#可以通过ros2.draw.xxx(activeMarker=True)来生成
	#例如：　
	#	srv = ros2.actionMarker.server("mockRobot")
	#	robot = ros2.actionMarker.actionMarker(frameId="map",name="robot",position=(1,0,0),callback=robotCallback) 
	#	robot.moveXY(fixed=True) 
	#	robot.rotateZ(fixed=True) 
	#	robot.add(ros2.draw.cylinder(activeMarker=True))
	#	srv.add(robot)
	def add(self,marker): 
		assert isinstance(marker,m.Marker)
		marker.pose.position.x += self._marker.pose.position.x
		marker.pose.position.y += self._marker.pose.position.y
		marker.pose.position.z += self._marker.pose.position.z
		self.hasMarker = True
		control =  m.InteractiveMarkerControl()
		control.always_visible = True
		control.markers.append(marker)
		control.interaction_mode = m.InteractiveMarkerControl.NONE
		self._marker.controls.append(control)
	
	@property
	def name(self):
		return self._marker.name
	
	def _callback(self,feedback):
		p = feedback.pose.position
		c = feedback.pose.orientation
		self.callback(self,(p.x,p.y,p.z),(c.x,c.y,c.z)) 
		
	def addDefaultBox(self):
		box = m.Marker()
		box.type = m.Marker.CUBE
		box.scale.x = 0.45
		box.scale.y = 0.45
		box.scale.z = 0.45
		box.color.r = 0.0
		box.color.g = 0.5
		box.color.b = 0.5
		box.color.a = 1.0 
		control =  m.InteractiveMarkerControl()
		control.always_visible = True
		control.markers.append(box)
		control.interaction_mode = m.InteractiveMarkerControl.NONE
		self._marker.controls.append(control)
	
	def button(self): 
		self._marker.controls[0].interaction_mode = m.InteractiveMarkerControl.BUTTON
	
	def moveX(self,fixed):
		self._move(fixed,"move_x")
		
	def moveY(self,fixed):
		self._move(fixed,"move_y")
		
	def moveZ(self,fixed):
		self._move(fixed,"move_z")
		
	def moveXY(self,fixed):
		c = self._move(fixed,"move2d_z") 
		c.interaction_mode = m.InteractiveMarkerControl.MOVE_PLANE
		
	def moveYZ(self,fixed):
		c = self._move(fixed,"move2d_x") 
		c.interaction_mode = m.InteractiveMarkerControl.MOVE_PLANE
		
	def moveXZ(self,fixed):
		c = self._move(fixed,"move2d_y") 
		c.interaction_mode = m.InteractiveMarkerControl.MOVE_PLANE
		
	def rotateX(self,fixed):
		self._rotate(fixed,"rotate_x")
		
	def rotateY(self,fixed):
		self._rotate(fixed,"rotate_y")
		
	def rotateZ(self,fixed):
		self._rotate(fixed,"rotate_z")
		
	def rotate3D(self,fixed):
		self._marker.controls[0].interaction_mode = m.InteractiveMarkerControl.ROTATE_3D
	
	def move3D(self,fixed):
		self._marker.controls[0].interaction_mode = m.InteractiveMarkerControl.MOVE_3D
	
	def moveRotate3D(self,fixed):
		self._marker.controls[0].interaction_mode = m.InteractiveMarkerControl.MOVE_ROTATE_3D 
		self.rotateX(fixed)
		self.rotateY(fixed)
		self.rotateZ(fixed)  
		self.moveX(fixed)
		self.moveY(fixed)
		self.moveZ(fixed)
	
	def _rotate(self,fixed,name):
		c = self._move(fixed,name)
		c.interaction_mode = m.InteractiveMarkerControl.ROTATE_AXIS
		
	def _move(self,fixed,name):
		control = m.InteractiveMarkerControl()
		control.orientation.w = 1
		if name[-1] == "x":
			control.orientation.x = 1
			control.orientation.y = 0
			control.orientation.z = 0
		elif name[-1] == "y":
			control.orientation.x = 0
			control.orientation.y = 0
			control.orientation.z = 1
		elif name[-1] == "z":
			control.orientation.x = 0
			control.orientation.y = 1
			control.orientation.z = 0
		else:
			assert 0
		control.name = name
		control.interaction_mode = m.InteractiveMarkerControl.MOVE_AXIS
		if fixed:
			control.orientation_mode = m.InteractiveMarkerControl.FIXED
		self._marker.controls.append(control)
		return control
		
		
def defaultMenuCallback(name, menu):
	if menu.checked is None:
		log.info("Action:",name,"clicked:",menu.name)
	else:
		log.info("Action:",name,"clicked:",menu.name,"checked:",menu.checked)
	
	 
class menuItem:
	def __init__(self,name,callback,checked,menuHandle):
		self.name = name
		self.callback = callback
		if callback is None:
			self.callback = defaultMenuCallback
		self.checked = checked
		self._handle = menuHandle
		self._menu = None	#其实是个int 
		self._visible = True
	
	def add(self,name,callback=None,checked=None):
		self._handle._addItem(name=name,parent=self,callback=callback,checked=checked)
	
	@property
	def visible(self):
		return self._visible
	
	@visible.setter
	def visible(self,value):
		if self._handle and value != self._visible:
			self._handle._imp.setVisible(self._menu,value)
			self._handle._apply()
		self._visible = value

	def toggle(self):
		self.setCheck(not self.checked)
	
	def setCheck(self,value):
		self.checked = value
		if self._handle:
			if value:	
				state = m2.MenuHandler.CHECKED
			else:
				state = m2.MenuHandler.UNCHECKED
			self._handle._imp.setCheckState(self._menu, state)
			self._handle._apply() 
	
	@property
	def itemHandle(self):	
		return self._menu
	

class menu:
	def __init__(self):
		self._imp = m2.MenuHandler() 
		self._server = None
		self._items = {}
		
	def add(self,name,callback=None,checked=None):
		return self._addItem(name = name,parent=None,callback=callback,checked=checked)
		
	def attach(self,marker):
		assert isinstance(marker,actionMarker)  
		if marker._server is None:
			raise Exception("Must add actionMarker to server first")
		if self._server is None:
			self._server = marker._server
		else:
			assert self._server == marker._server 
		self._imp.apply(marker._server._imp,marker.name)
		marker._server.apply()
		
	def _addItem(self,name,parent,callback,checked):
		item = menuItem(name,callback,checked,self)
		p = None
		if parent:
			p = parent._menu
		item._menu = self._imp.insert(name,p,callback=self._callback) 
		self._items[item._menu] = item 
		if checked is not None:
			item.setCheck(checked)
		return item 
		
	def _callback(self,msg):
		item = self._items[msg.menu_entry_id]
		if item.callback:
			item.callback(msg.marker_name,item)
	
	def _apply(self):
		if self._server:
			self._imp.reApply( self._server._imp ) 
			self._server.apply()
		
		
# 注意: 
# 1. 需要在rviz添加InteractiveMarker层
# 2. 在InteractiveMarker的Update Topic填上 /<name>/update
# server接收,rviz发送： /<name>/feedback
# server发送,rviz接收： /<name>/update
class server:
	def __init__(self,name):
		self._imp = interactive.InteractiveMarkerServer(name)
		self.isModified = False
		self.actions = {}
	
	def add(self,marker):
		assert isinstance(marker,actionMarker) #or isinstance(marker,menu)
		self._imp.insert(marker._marker, marker._callback)  
		marker._server = self
		self.actions[marker.name] = marker
		self.isModified = True
	
	def __getitem__(self,name):
		return self.actions[name] 
	
	def apply(self):
		for marker in self.actions.values():
			if not marker.hasMarker:
				marker.addDefaultBox()
		self._imp.applyChanges()
	
	def run(self):
		if self.isModified:	
			self.isModified = False
			self.apply()
		ros2.rosUtility.wait()
		
############ unit test ############
def testclient():
	s = server("ycat_test")
	m1 = actionMarker("base_link","ycat")
	m1.moveRotate3D(fixed=True) 
	s.add(m1)
	
	m2 = actionMarker("base_link","ycat2",position=(0,5,0))
	m2.moveXY(fixed=True) 
	s.add(m2)
	
	m3 = actionMarker("base_link","ycat3",position=(0,7,0))
	m3.button() 
	s.add(m3)
	
	mm = menu()
	mm.add("ycat1") 
	mm.add("ycat2") 
	i1 = mm.add("ycat3")  
	i1.add("ycat3.1",checked=False)
	i1.add("ycat3.2",checked=True)
	mm.attach(m2) 
	mm.attach(m1) 
	
	assert s["ycat"].name == "ycat" 
	s.run()
	
if __name__ == "__main__": 
	utility.start()
	ros2.msg.init()
	ros2.rosUtility.init("ycattest2")
	testclient() 

	
	
	
	
	
	
	
	
	
	
	
	
	
