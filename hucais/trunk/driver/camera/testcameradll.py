#coding=utf-8
import os,sys
from PyQt5.QtCore import QCoreApplication
import ctypes
import numpy as np
import cv2

currentPath = os.path.dirname(__file__)
if __name__ == '__main__':
	os.chdir(currentPath)
	
	
def camtest():
	camera = ctypes.cdll.LoadLibrary(currentPath + "./dll/win32/cameradll.dll")
	#1.构造函数，创建全局相机对象
	camera.init()
	
	#2.连接相机
	rt = ctypes.c_bool(0)
	rt = camera.connectCam()
	print("camera.connectCam() ",rt)
	
	#3.打开相机
	rt = camera.open()
	print("camera.open() ",rt)
	
	#4.cfginit
	rt = camera.initDevandCfg()
	print("camera.initDevandCfg() ",rt)
	
	imgWidth = ctypes.c_int(0)
	imgHeight = ctypes.c_int(0)
	imgWidth = camera.getImgWidth()
	imgHeight = camera.getImgHeight()
	print("imgWidth, imgHeight: ",imgWidth,imgHeight)
	
	#5.设置曝光
	exposure = ctypes.c_int(2)
	rt = camera.setExposureGrad(exposure)
	print("camera.setExposureGrad(exposure) ",rt)
	
	#采集图像
	rt = camera.run()
	print("camera.run() ",rt)
	
	
	buflen = ctypes.c_int(imgWidth * imgHeight)
	imgData = (ctypes.c_ubyte * buflen.value)()
	
	actlen = camera.capture(imgData,buflen)
	print("capture actlen ",actlen)
	
	img = np.frombuffer(imgData,dtype=np.uint8)
	img = img.reshape(imgHeight,imgWidth)
	cv2.imwrite("timg.jpg",img)
	
	
	#关闭相机
	rt = camera.close()
	print("camera.close() ",rt)

if __name__=="__main__":
	camtest()