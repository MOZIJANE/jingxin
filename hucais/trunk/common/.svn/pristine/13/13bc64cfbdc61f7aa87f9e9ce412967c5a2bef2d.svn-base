#coding=utf-8
# ycat			2017-08-030	  create
# 计算相机内参 
#https://blog.csdn.net/u010128736/article/details/52875137
#https://blog.csdn.net/shadow_guo/article/details/44193993
import os,sys
import numpy as np
import cv2
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)

import cv.image as image
import cv.camera as camera
import cv.cvUtility as cvUtility
import utility
import json_codec as json
import slam.pose


# class chessboard:
# 	def __init__(self):
# 		self.cornerWidthNum = 8
# 		self.cornerHeightNum = 6
# 		self.squareSize = 0.02
		
# g_chessboard = chessboard()

def load(filename):
	info = json.load_file(filename)
	r = caliInfo()
	r.cornerWidthNum = info["cornerWidthNum"] 
	r.cornerHeightNum = info["cornerHeightNum"]  
	r.squareSize = info["squareSize"] 
	r.cameraMatrix = np.array(info["cameraMatrix"])
	r.distCoefs = np.array(info["distCoefs"])
	r.imageWidth = info["imageWidth"]  
	r.imageHeight = info["imageHeight"]  
	r.error = info["error"]  
	r.rms = info["rms"]
	# g_chessboard.cornerHeightNum = r.cornerHeightNum
	# g_chessboard.cornerWidthNum = r.cornerWidthNum
	# g_chessboard.squareSize = r.squareSize
	return r

#校正结果类 
class caliInfo:
	def __init__(self):
		self.cornerWidthNum = 0
		self.cornerHeightNum = 0
		self.squareSize = 1
		
		#https://blog.csdn.net/yangdashi888/article/details/51356385/ 
		#相机的内参数是六个分别为：1/dx、1/dy、r、u0、v0、f。		#opencv1里的说内参数是4个其为fx、fy、u0、v0。实际其fx=F*Sx，其中的F就是焦距上面的f,Sx是像素/没毫米即上面的dx，
		#其是最后面图里的后两个矩阵进行先相乘，得出的，则把它看成整体，就相当于4个内参。其是把r等于零，实际上也是六个。		#dx和dy表示：x方向和y方向的一个像素分别占多少长度单位，即一个像素代表的实际物理值的大小，其是实现图像物理坐标系与像素坐标系转换的关键。
		#u0，v0表示图像的中心像素坐标和图像原点像素坐标之间相差的横向和纵向像素数。
		self.cameraMatrix = None
		self.distCoefs = None 
		self.imageWidth = None
		self.imageHeight = None
		self.error = 0
		self.rms = 0
		
		self.mapx = None
		self.mapy = None
		self.newcameramtx = None
		self.roi = None
		
	def save(self,filename):
		info = {}
		info["cornerWidthNum"] = self.cornerWidthNum
		info["cornerHeightNum"] = self.cornerHeightNum
		info["squareSize"] = self.squareSize
		info["cameraMatrix"] = self.cameraMatrix.tolist()
		info["distCoefs"] = self.distCoefs.tolist()
		info["imageWidth"] = self.imageWidth
		info["imageHeight"] = self.imageHeight
		info["error"] = self.error
		info["rms"] = self.rms
		json.dump_file(filename,info)
		
	def _initMap(self):
		if self.mapx is None:
			w,h = self.imageWidth,self.imageHeight
			self.newcameramtx, self.roi = cv2.getOptimalNewCameraMatrix(self.cameraMatrix, self.distCoefs, (w, h), alpha=0, newImgSize=(w, h)) 
			self.mapx,self.mapy = cv2.initUndistortRectifyMap(self.cameraMatrix, self.distCoefs, None,self.newcameramtx,(w, h), cv2.CV_16SC2) 
		
	#对图像进行校准 
	def rectify(self,img):  
		self._initMap()
		return image.image(cv2.remap(img.img, self.mapx,self.mapy, cv2.INTER_LINEAR) )

	#对图像进行校准，在多图情况下，这个效率比remap低
	#因为畸变坐标映射矩阵mapx和mapy只需要计算一次就足够了，而重复调用UndistortImage()只会重复计算mapx和mapy，严重影响程序效率 
	def rectify2(self,img): 
		h, w = img.img.shape[:2] 	 
		self.newcameramtx, self.roi = cv2.getOptimalNewCameraMatrix(self.cameraMatrix, self.distCoefs, (w, h), alpha=0, newImgSize=(w, h)) 
		dst = cv2.undistort(img.img, self.cameraMatrix, self.distCoefs, None, newcameramtx)
		return image.image(dst)
		
	#x焦距(像素)
	@property
	def fx(self):
		return self.cameraMatrix[0][0]
		
	#y焦距(像素)
	@property
	def fy(self):
		return self.cameraMatrix[1][1]
		
	def getPos(self,img):
		rvecs, tvecs, corners = self.solvePnPRansac(img)
		if rvecs is None:
			return None
		if corners.shape[0] != self.cornerWidthNum * self.cornerHeightNum:
			return None
		p = slam.pose.pose3D(frameId="camera",parentId="chessboard")
		p.setPos(tvecs[0],tvecs[1],tvecs[2])
		p.matrix.rvecs = rvecs
		return p

	def solvePnPRansac(self,img):
		corner = self._findCorners(img)
		if corner is None:
			return None,None,None
		#https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_calib3d/py_pose/py_pose.html#pose-estimation 
		pattern_size = (self.cornerWidthNum, self.cornerHeightNum)
		objp = np.zeros((np.prod(pattern_size), 3), np.float32)
		objp[:, :2] = np.indices(pattern_size).T.reshape(-1, 2) 
		#objp[:, :2] = np.indices(pattern_size).T[::-1].reshape(-1, 2)   #左下角第一点为原点  
		objp *= self.squareSize
		# Find the rotation and translation vectors.
		# ret,rvecs, tvecs, inliers = cv2.solvePnPRansac(objp, corner, self.cameraMatrix, self.distCoefs)
		ret,rvecs, tvecs = cv2.solvePnP(objp, corner, self.cameraMatrix, self.distCoefs,flags=cv2.SOLVEPNP_ITERATIVE)
		if not ret:
			return None,None,None
		return rvecs, tvecs, corner

	def drawCorners(self, img, corners):
		if len(img.img.shape) == 2:  # if gray image
			img = img.toRgb()
		cv2.drawChessboardCorners(img.img, (self.cornerWidthNum, self.cornerHeightNum), corners, True)
		return image.image(img.img)

	def sendRos(self,topic,frameId):
		#用ros的camera还不行，不知道为什么 
		import ros2.topic
		import sensor_msgs.msg
		c = sensor_msgs.msg.CameraInfo()
		c.header = ros2.msg.header(frameId)
		c.height = self.imageHeight
		c.width = self.imageWidth
		c.distortion_model = "plumb_bob"
		c.D = self.distCoefs[0]
		c.K = self.cameraMatrix.reshape(-1)
		ros2.topic.send(topic,c,"sensor_msgs/CameraInfo")

	def _findCorners(self, img):
		found, corners = cv2.findChessboardCorners(img.img, (self.cornerWidthNum, self.cornerHeightNum))
		# found, corners = cv2.findChessboardCorners(img.img, (self.cornerWidthNum, self.cornerHeightNum),
		# 										   flags=cv2.CALIB_CB_ADAPTIVE_THRESH
		# 												 + cv2.CALIB_CB_NORMALIZE_IMAGE
		# 												 + cv2.CALIB_CB_FILTER_QUADS
		# 												 + cv2.CALIB_CB_FAST_CHECK
		# 										   )
		# found, corners = cv2.findChessboardCornersSB(img.img, (self.cornerWidthNum, self.cornerHeightNum),
		# 											 flags=cv2.CALIB_CB_NORMALIZE_IMAGE
		# 												   + cv2.CALIB_CB_EXHAUSTIVE
		# 												   + cv2.CALIB_CB_LARGER
		# 												   + cv2.CALIB_CB_MARKER
		# 												   cv2.CALIB_CB_ACCURACY
		# 											 )
		if not found:
			return None

		#Refines the corner locations.
		term = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT, 30, 0.1)
		#用cornerSubPix()函数将角点定位到子像素，从而取得亚像素级别的角点检测效果。
		cv2.cornerSubPix(img.toGray().img, corners, (11, 11), (-1, -1), term)
		return corners
		
		
#在img上画上棋盘的信息
#img:图像
#corners: findCorners返回的结果
def _drawCorners(img,corners):
	if len(img.img.shape) == 2:  # if gray image
		retImg = cv2.cvtColor(img.img, cv2.COLOR_GRAY2BGR)
	cv2.drawChessboardCorners(retImg, (g_chessboard.cornerWidthNum, g_chessboard.cornerHeightNum), corners, True)
	return image.image(retImg)


def _compute(imgList):
	'''extract corners and calibrate camera intrinsic and distortion
	:param imgList: list of images to be calibrated
	:return: caliInfo
	'''
	assert len(imgList) == 10
	pattern_size = (g_chessboard.cornerWidthNum, g_chessboard.cornerHeightNum)
	pattern_points = np.zeros((np.prod(pattern_size), 3), np.float32)
	pattern_points[:, :2] = np.indices(pattern_size).T.reshape(-1, 2)
	pattern_points *= g_chessboard.squareSize
	
	obj_points = []
	img_points = []
	for img in imgList:
		c = _findCorners(img)
		if c is None:
			img.show()
			assert 0
	chessboards = [_findCorners(fn) for fn in imgList] 
	chessboards = [x.reshape(-1, 2) for x in chessboards if x is not None]
	for corners  in chessboards:
		img_points.append(corners)
		obj_points.append(pattern_points)
	assert len(img_points)>= 10
	assert len(obj_points) >= 10
	assert len(imgList)>=10 
	# calculate camera distortion 
	#cameraMatrix: 内参矩阵
	#distCoeffs: 畸变矩阵 (默认获得5个即便参数k1,k2,p1,p2,k3
	#rvecs: 外参：旋转向量
	#tvecs: 外参：平移向量
	rms, cameraMatrix, distCoefs, rvecs, tvecs = cv2.calibrateCamera(obj_points, img_points, imgList[0].size, None, None)
	info = caliInfo() 
	info.cornerWidthNum = g_chessboard.cornerWidthNum
	info.cornerHeightNum = g_chessboard.cornerHeightNum
	info.squareSize = g_chessboard.squareSize
	info.cameraMatrix = cameraMatrix
	info.distCoefs = distCoefs 
	info.imageWidth = imgList[0].width
	info.imageHeight = imgList[0].height
	info.rms = rms
	info.error = _reprojectError(obj_points,img_points,cameraMatrix,distCoefs,rvecs,tvecs)
	return info 

#计算重投影误差,越逼近0越好 
def _reprojectError(obj_points, img_points,cameraMatrix,distCoefs,rvecs,tvecs):
	total_error = 0
	for i in range(len(obj_points)):
		img_points2, _ = cv2.projectPoints(obj_points[i], rvecs[i], tvecs[i], cameraMatrix, distCoefs)
		s = img_points[i].shape
		error = cv2.norm(img_points[i].reshape([s[0],1,s[1]]),img_points2, cv2.NORM_L2)/len(img_points2)
		total_error += error
	return total_error/len(obj_points) 
	
def _drawAxis(img,info):
	rvecs, tvecs, corner = info.solvePnPRansac(img)
	if rvecs is None:
		return
	print(info.getPos(img))
	#p = corner[-info.cornerWidthNum].ravel()
	p = corner[0].ravel()	#左下角第一点为原点  
	img.drawAxis(tuple(p),rvecs, tvecs,info.cameraMatrix,axisLen=3*info.squareSize,style="line")
	
	
		
#对机相进行校准对话框   
#cameraIndex: 相机索引  
def showConfigDlg(cameraIndex):
	'''calibration APP'''
	import camera
	print("<ESC>, 'q' - quit the program") 
	print("'s' - switch undistortion on/off")
	print("'space' - to capture image")
	
	c = camera.camera(cameraIndex,calibrateEnable=False)
	mode = False
	imgList = []
	lastTakeTick = utility.ticks()
	showUndistort = True
	info = None 
	corner = None
	while True:
		img = c.read()  
		if len(imgList) < 10:
			corner = _findCorners(img)
			if corner is None:
				img.text("no chessboard found!",(0,0),color=(0,0,255),fontScale=0.8)
			else:
				newImg = img.clone()
				grayImg = img.toGray()
				img = _drawCorners(grayImg,corner)
				img.text("press space to capture: %d/10"%len(imgList),(0,0),color=(0,255,0),fontScale=0.8)
		elif len(imgList) >= 10:
			#for i,img in enumerate(imgList):
			#	img.save("./img/%d.jpg"%i)
			if info is None:
				info = _compute(imgList) 
				info.save("./camera"+str(cameraIndex)+".json")
			if showUndistort:
				img = info.rectify(img)
				img.text("undistort error=%f,rms=%f"%(info.error,info.rms),(10,10),color=(0,255,0),fontScale=0.8)
			else:
				img.text("original",(10,10),color=(0,0,255),fontScale=0.8)
			_drawAxis(img,info)
			
		key = cv2.waitKey(1)
		if key == 32:
			imgList.append(newImg)
			
		img.show(title="calibrate dlg",autoShow=False)
		if key &0xFF == ord('s'):
			if showUndistort:
				showUndistort = False
			else:
				showUndistort = True 
		if key &0xFF == ord('q'):
			break
		if key == 27:
			break
	cvUtility.quit()


#显示相机校正结果，如有棋盘还显示坐标轴 
def showDlg(cameraIndex):
	import camera 
	print("<ESC>, 'q' - quit the program") 
	print("'s' - switch undistortion on/off") 
	c = camera.camera(cameraIndex,calibrateEnable=True)
	while True:
		img = c.read()  
		if c.calibrateEnable:
			img.text("undistort error=%f,rms=%f"%(c.calibInfo.error,c.calibInfo.rms),(10,10),color=(0,255,0),fontScale=0.8)
		else:
			img.text("original",(10,10),color=(0,0,255),fontScale=0.8)
		_drawAxis(img,c.calibInfo)
		img.show(title="show result",autoShow=False) 
		key = cv2.waitKey(1)
		if key &0xFF == ord('s'):
			if c.calibrateEnable:
				c.calibrateEnable = False
			else:
				c.calibrateEnable = True 
		if key &0xFF == ord('q'):
			break
		if key == 27:
			break
	cvUtility.quit() 
	 
	
if __name__ == '__main__':
	cc = camera.listCameras()
	print("cameras:",cc)
	if utility.is_win():
		index = len(cc)-1
	else:
		index = 0
	if "cfg" in sys.argv:
		showConfigDlg(index) 
	else:
		showDlg(index) 

	
	
	
	
	
	
	
	
	
