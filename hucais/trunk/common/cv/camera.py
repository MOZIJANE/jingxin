#coding=utf-8
# ycat			2017-08-030	  create
# 相机操作 
import sys,os,glob
import cv2
import time
import numpy as np 
import setup
if __name__ == "__main__":
	setup.setCurPath(__file__)
import cv.cvUtility as cvUtility
import cv.image as image
import utility

#列出所有相机的算法 
def listCameras():
	if utility.is_win():	
		import pygrabber.dshow_graph
		return pygrabber.dshow_graph.FilterGraph().get_input_devices()
	else:
		return glob.glob("/dev/video*")


#相机的相关参数配置  
#sensor.set_auto_gain(False)  # must turn this off to prevent image washout...
#sensor.set_auto_whitebal(False)  # must turn this off to prevent image washout...
 
class camera:
	def __init__(self,index,calibrateEnable=False):
		if os.path.exists("camera"+str(index)+".json"):
			import calibrate
			self.calibInfo = calibrate.load("camera"+str(index)+".json")
		else:
			self.calibInfo = None
		self.index = index
		self.calibrateEnable = calibrateEnable
		self.cap = cv2.VideoCapture(self.index)
	
	def __del__(self):
		self.cap.release()
	
	def read(self):
		if self.cap is None:
			self.cap = cv2.VideoCapture(self.index)
		ret,frame = self.cap.read()
		if not ret:
			raise IOError("Capture camera failed!")
		img =  image.image(frame)
		if self.calibrateEnable:
			assert self.calibInfo
			return self.calibInfo.rectify(img)
		else:
			return img
		
	def show(self,sendRos=False):
		while True:
			try:
				frame = self.read() 
			except IOError as e:
				self.cap = None
				time.sleep(1)
				continue
			if sendRos:
				name = "camera"+str(self.index)
				if self.calibInfo:
					self.calibInfo.sendRos(name+"/camera_info",name)
				frame.sendRos(name+"/image_raw",name) 
			else:	
				frame.text("Press q to quit",(0,10),fontScale=0.6,color=(0,0,255))
				frame.show(autoShow=False)
			if cvUtility.wait(millisec=1,key="q"):
				break
	
	@property
	def info(self):
		r = {}
		r["width"] = self.width
		r["height"] = self.height
		r["fps"] = self.fps
		r["brightness"] = self.cap.get(cv2.CAP_PROP_BRIGHTNESS)
		r["contrast"] = self.cap.get(cv2.CAP_PROP_CONTRAST)
		r["saturation"] = self.cap.get(cv2.CAP_PROP_SATURATION)
		r["hue"] = self.cap.get(cv2.CAP_PROP_HUE)
		r["exposure"] = self.cap.get(cv2.CAP_PROP_EXPOSURE)
		return r
	
	@property
	def width(self):
		return self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
		
	@property
	def height(self):
		return self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
	
	@property
	def fps(self):
		return self.cap.get(cv2.CAP_PROP_FPS)
	
	@property
	def size(self):
		return (self.width,self.height)
	
	#获取相机内参 
	@property
	def cameraMatrix(self):
		return self.calibInfo.cameraMatrix
			
	#畸变参数 
	@property
	def distCoefs(self):
		return self.calibInfo.distCoefs
	
	@property
	def isConnected(self):
		return self.cap is not None
		
	@property
	def name(self):
		return "camera"+str(self.index)
		
if __name__ == "__main__":	
	if utility.is_ros():
		import ros2.rosUtility
		ros2.rosUtility.init("test_camera")
	cc = listCameras()
	print("cameras:",cc)
	if utility.is_win():
		i = len(cc)-1
	else:
		i = 0
	c = camera(i)
	print(c.info)
	c.show(sendRos=utility.is_ros())  

	
	
	
	
