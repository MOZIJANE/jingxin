#coding=utf-8
#lizhenwei		2017-08-22		create
import os,sys,platform
import ctypes
import numpy as np
import cv2
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import utility

if utility.is_win32():
	g_camera = ctypes.cdll.LoadLibrary(os.path.dirname(__file__) + "/dll/win32/cameradll_32.dll")
elif utility.is_win64():
	g_camera = ctypes.cdll.LoadLibrary(os.path.dirname(__file__) + "/dll/win64/cameradll_64.dll")
	
assert(g_camera)
g_camera.init()
def finit():
	g_camera.finit()
	
def connectCam():
	global g_camera
	return g_camera.connectCam()

def openCam():
	global g_camera
	return g_camera.open()
	
def closeCam():
	global g_camera
	return g_camera.close()
	
def disConnectCam():
	global g_camera
	return g_camera.disConnect()
	
def runCam():
	global g_camera
	return g_camera.run()

def stopCam():
	global g_camera
	return g_camera.stop()

def setImgSize(width, height):
	global g_camera
	return g_camera.setImgSize(width, height)
	
def getImgSize():
	global g_camera
	imgWidth = g_camera.getImgWidth()
	imgHeight = g_camera.getImgHeight()
	return (imgWidth,imgHeight)
	
def setReverseX(isReverse = True):
	global g_camera
	isReverse = ctypes.c_bool(isReverse)
	return g_camera.setReverseX(isReverse)

def setCenterX(isCen = True):
	global g_camera
	isCen = ctypes.c_bool(isCen)
	return g_camera.setCenterX(isCen)
	
def setCenterY(isCen = True):
	global g_camera
	isCen = ctypes.c_bool(isCen)
	return g_camera.setCenterY(isCen)

def setExposureGrad(grad=2):
	global g_camera
	return g_camera.setExposureGrad(grad)

def setExposure(ms):
	global g_camera
	return g_camera.setExposure(ms)

def captureGray():
	global g_camera
	imgWidth, imgHeight = getImgSize()
	buflen = ctypes.c_int(imgWidth * imgHeight)
	imgData = (ctypes.c_ubyte * buflen.value)()
	actlen = g_camera.capture(imgData,buflen,1)
	img = np.frombuffer(imgData,dtype=np.uint8)
	img = img.reshape(imgHeight,imgWidth)
	return img

def captureOneGray():
	global g_camera
	imgWidth, imgHeight = getImgSize()
	buflen = ctypes.c_int(imgWidth * imgHeight)
	imgData = (ctypes.c_ubyte * buflen.value)()
	actlen = g_camera.captureOneImg(imgData,buflen,1)
	img = np.frombuffer(imgData,dtype=np.uint8)
	img = img.reshape(imgHeight,imgWidth)
	return img

def captureColor():
	'采集彩色图像'
	global g_camera
	imgWidth, imgHeight = getImgSize()
	buflen = ctypes.c_int(imgWidth * imgHeight * 3)
	imgData = (ctypes.c_ubyte * buflen.value)()
	actlen = g_camera.capture(imgData,buflen,3)
	img = np.frombuffer(imgData,dtype=np.uint8)
	img = img.reshape(imgHeight,imgWidth,3)
	return img
	
def captureOneColor():
	'采集一张彩色图像'
	global g_camera
	imgWidth, imgHeight = getImgSize()
	buflen = ctypes.c_int(imgWidth * imgHeight * 3)
	imgData = (ctypes.c_ubyte * buflen.value)()
	actlen = g_camera.captureOneImg(imgData,buflen,3)
	img = np.frombuffer(imgData,dtype=np.uint8)
	img = img.reshape(imgHeight,imgWidth,3)
	return img

def getError():
	'获取错误代码'
	global g_camera
	buflen = ctypes.c_int(500)
	buf = (ctypes.c_char * buflen.value)()
	code = g_camera.getError(buf, buflen)
	return code, buf.value.decode("utf8")

def isCamConnected():
	global g_camera
	return g_camera.isConnected()
	
def isCamOpened():
	global g_camera
	return g_camera.isOpened()
	
def isCamContinueCaptured():
	global g_camera
	return g_camera.isContinueCaptured()

def isCamRun():
	global g_camera
	return g_camera.isRun()
	
def isCamIdle():
	global g_camera
	return g_camera.isIdle()

def test_gray():
	if not connectCam():
		code,msg = getError()
		print(code,msg)
	assert isCamConnected()
	assert openCam()
	assert isCamOpened()
	assert setImgSize(640,480)
	w,h = getImgSize()
	assert (w,h)==(640,480)
	assert setExposure(20)
	img = captureOneGray()
	assert img.shape[:2] == (h,w)
	assert not isCamRun()
	assert not isCamContinueCaptured()
	assert isCamIdle()
	assert cv2.imwrite('onegray.jpg',img)
	assert runCam()
	assert isCamContinueCaptured()
	assert isCamRun()
	assert not isCamIdle()
	for i in range(2):
		img = captureGray()
		assert img is not None
		assert cv2.imwrite('continue_gray%d.jpg'%i, img)
	assert closeCam()
	assert disConnectCam()

def test_color():
	assert connectCam()
	assert openCam()
	assert setImgSize(640,480)
	w,h = getImgSize()
	assert setReverseX(False)
	assert setCenterX(False)
	assert setCenterY(False)
	assert setExposureGrad(2)
	img = captureOneColor()
	assert img.shape == (h,w,3)
	assert cv2.imwrite('onecolor.jpg',img)
	assert runCam()
	for i in range(2):
		img = captureColor()
		assert img is not None
		assert cv2.imwrite('continue_color%d.jpg'%i, img)
		
	assert closeCam()
	assert disConnectCam()
	
if __name__ == '__main__':
	test_gray()
	# test_color()
