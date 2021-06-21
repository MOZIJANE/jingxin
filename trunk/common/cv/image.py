#coding=utf-8
# ycat			2017-08-030	  create
# 图像操作 
import cv2
import numpy as np 
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import cv.cvUtility

def blackImg(width,height):
	return image(np.zeros((height,width,3), np.uint8))
	

class image:
	#cv2.IMREAD_COLOR : Loads a color image. Any transparency of image will be neglected. It is the default flag.
	#cv2.IMREAD_GRAYSCALE : Loads image in grayscale mode
	#cv2.IMREAD_UNCHANGED : Loads image as such including alpha channel
	def __init__(self,img,flag=cv2.IMREAD_COLOR):
		if isinstance(img,str):
			self.img = cv2.imread(img,flag) 
		else:
			self.img = img
			
	def clear(self,color=None):
		if color is None:
			color = (0,0,0)
		else:
			color = color[::-1]
		#BGR 
		self.img[::] = color
	
	#缩小 
	def pyrDown(self):
		return cv2.pyrDown(self.img)
	
	#放大 
	def pyrUp(self):
		return cv2.pyrUp(self.img)
	
	def clone(self):
		return image(self.img.copy())
	
	@property
	def size(self):
		return (self.width,self.height)
		
	@property
	def width(self):
		return self.img.shape[1]
		
	@property
	def height(self):
		return self.img.shape[0]
	
	@property
	def channel(self):
		if len(self.img.shape) <= 2:
			return 0
		return self.img.shape[2]
		
	@property
	def dtype(self):
		return self.img.dtype
	
	@property
	def shape(self):
		return self.img.shape
	
	#把两张图片合成一个图片
	#horizen是水平合并还是垂直合并 
	@staticmethod
	def join(img1,img2,horizen=True):
		if horizen:
			newImg = blackImg(img1.width+img2.width,max(img1.height,img2.height))
			newImg.draw(img1,(0,0))
			newImg.draw(img2,(img1.width,0))
		else:
			newImg = blackImg(max(img1.width,img2.width),img1.height+img2.height)
			newImg.draw(img1,(0,0))
			newImg.draw(img2,(0,img1.height))
		return newImg
	
	#分解成三通道的图像 
	def splitChannel(self):
		return [ image(x) for x in cv2.split(self.img) ]
		
	#把三通道合并成一个图像 
	@staticmethod
	def mergeChannel(self,b,g,r):
		return image(cv2.merge((b,g,r)))

	#扩大图像的画布 
	def padding(self,top, bottom, left, right,borderType=cv2.BORDER_CONSTANT,color=(0,0,0)):
		#cv2.BORDER_CONSTANT - Adds a constant colored border. The value should be given as next argument.
		#cv2.BORDER_REFLECT - Border will be mirror reflection of the border elements, like this : fedcba|abcdefgh|hgfedcb
		#cv2.BORDER_REFLECT_101 or cv2.BORDER_DEFAULT - Same as above, but with a slight change, like this : gfedcb|abcdefgh|gfedcba
		#cv2.BORDER_REPLICATE - Last element is replicated throughout, like this: aaaaaa|abcdefgh|hhhhhhh
		#cv2.BORDER_WRAP - Can’t explain, it will look like this : cdefgh|abcdefgh|abcdefg
		#color - Color of border if border type is cv2.BORDER_CONSTANT
		self.img = cv2.copyMakeBorder(self.img,top, bottom, left, right,borderType,value= color)
	
	#变成负片一样的效果 
	def inverse(self):
		cv2.bitwise_not(self.img,self.img)
		return self
	
	#转换成灰度图 
	def toGray(self):
		if len(self.img.shape) == 3 or len(self.img.shape) == 4:
			return image(cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY))
		else:
			return self
	
	#转换成RGB图像 
	def toRgb(self):
		return image(cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB))
	
	#区域剪切
	def roi(self,point,size):
		return image(self.img[int(point[1]):int(point[1]+size[1]),int(point[0]):int(point[0]+size[0])])
	
	#def add(self,img,alpha):
	#	self.img = cv2.addWeighted(self.img,1,img.img,alpha,0)
	
	#def inverse(self):
	#	return image(cv2.bitwise_and(self.img,self.img,mask = cv2.MASK_INV))
	 
	def resize(self,scaleX, scaleY):
		self.img = cv2.resize(self.img,None,fx=scaleX, fy=scaleY, interpolation = cv2.INTER_CUBIC)
	
	#图像大小不变，内容旋转 
	def rotation(self,angle):
		M = cv2.getRotationMatrix2D((self.height/2,self.width/2),angle,1)
		self.img = cv2.warpAffine(self.img,M,(self.height,self.width))
		
	#透视变换,也称作投影映射 
	def perspective(self,M):
		return image(cv2.warpPerspective(self.img, M, self.size, cv2.INTER_LINEAR))
	
	#######  绘图操作  #######
	def drawImg(self,img,point):
		self.img[point[1]:point[1]+img.height,point[0]:point[0]+img.width] = img.img 
	
	def line(self,pt1,pt2,color=(0,0,0),thickness = 1):
		cv2.line(self.img,(int(pt1[0]),int(pt1[1])),(int(pt2[0]),int(pt2[1])),color,thickness,cv2.LINE_AA)
	
	def lines(self,points,color=(0,0,0),isClosed=False,thickness = 1):
		pts = np.array(points, np.int32).reshape((-1,1,2)) 
		cv2.polylines(self.img,pts=[pts],isClosed=isClosed,color=color,thickness=thickness,lineType=cv2.LINE_AA)
	
	def arrow(self,pt1,pt2,color=(0,0,0),thickness = 1,tipLength=0.1):
		cv2.arrowedLine(self.img,pt1,pt2,color,thickness,cv2.LINE_AA,tipLength=tipLength) 
		
	def circle(self,point,radius,color=(0,0,0),thickness = 1):
		cv2.circle(self.img,point,radius,color,thickness,cv2.LINE_AA)
		
	def fillCircle(self,point,radius,color=(0,0,0)):
		return self.circle(point,radius,color,thickness = -1)
	
	def rect(self,point,size,color=(0,0,0),thickness = 1):
		cv2.rectangle(self.img,point,(point[0]+size[0],point[1]+size[1]),color,thickness,cv2.LINE_AA)
	
	#轮廓填充 drawContours
	#contours	All the input contours. Each contour is stored as a point vector.
	#contourIdx	Parameter indicating a contour to draw. If it is negative, all the contours are drawn.
	def fill(self,contours,contourIdx=-1,color=(255,255,255),thickness = 1):
		cv2.drawContours(self.img,contours=contours,contourIdx=contourIdx,color=color,thickness=thickness,lineType=cv2.LINE_AA)
		
	#def ellipse(self,pt1,pt2,color=(0,0,0),thickness = 1):
	#	cv2.ellipse(self.img,box=(0,0,100,100),color=color)#,thickness,cv2.LINE_AA)
		
	def marker(self,point,color=(0,0,0),markerType=cv2.MARKER_CROSS,markerSize = 20,thickness = 1):
		#cv.MARKER_CROSS: A crosshair marker shape.
		#cv.MARKER_TILTED_CROSS: A 45 degree tilted crosshair marker shape.
		#cv.MARKER_STAR: A star marker shape, combination of cross and tilted cross.
		#cv.MARKER_DIAMOND: A diamond marker shape.
		#cv.MARKER_SQUARE: A square marker shape.
		#cv.MARKER_TRIANGLE_UP : An upwards pointing triangle marker shape.
		#cv.MARKER_TRIANGLE_DOWN: A downwards pointing triangle marker shape.
		cv2.drawMarker(self.img, point, color, markerType=markerType,markerSize=markerSize,thickness=thickness,line_type=cv2.LINE_AA)

	
	#返回下一行信息 
	def text(self, strValue,point,color=(0,0,0),fontScale=1,thickness=1,align="left",bgColor=None):
		#转成左上角坐标 
		font = cv2.FONT_HERSHEY_SIMPLEX 
		strValue = str(strValue)
		size,baseLine = cv2.getTextSize(strValue,fontFace=font,fontScale=fontScale,thickness=thickness)
		if align == "left":
			x = point[0]
			y = point[1]+size[1]
		elif align == "center":
			x = point[0]-size[0]/2
			y = point[1]+size[1]
		elif align == "right":
			x = point[0]-size[0]
			y = point[1]+size[1]
		else:
			print("unkown align",align)
			assert 0  
		if bgColor is not None:
			#未实现...
			assert 0
		#	self.rect((point[0],point[1]+size[1]),size,color=bgColor,thickness = 1)
		cv2.putText(self.img, strValue,(int(x),int(y)),font,fontScale,color,thickness,cv2.LINE_AA)
		return point[1]+size[1]+baseLine
	
	#在point上画上立体的x,y,z轴
	def drawAxis(self,point,rvecs,tvecs,cameraMatrix,axisLen=1,style="line"):	
		if style == "line":
			axis = np.float32([[axisLen,0,0], [0,axisLen,0], [0,0,-axisLen]]).reshape(-1,3)
		else:
			axis = np.float32([[0,0,0], [0,axisLen,0], [axisLen,axisLen,0], [axisLen,0,0],
					[0,0,-axisLen],[0,axisLen,-axisLen],[axisLen,axisLen,-axisLen],[axisLen,0,-axisLen] ])
		#计算相机原点到世界坐标原点的距离
		rot_mat,jac = cv2.Rodrigues(rvecs)
		dist = cv2.norm(-rot_mat.T.dot(tvecs))
		# dist = cv.cvUtility.distance(tvecs,np.zeros(3))
		
		# project 3D points to image plane
		imgPts, jac = cv2.projectPoints(axis, rvecs, tvecs,cameraMatrix, np.array([]))
		if style == "line":
			self.line(point,tuple(imgPts[0].ravel()),color=(0,0,255),thickness = 3)
			self.line(point,tuple(imgPts[1].ravel()),color=(0,255,0),thickness = 3)
			self.line(point,tuple(imgPts[2].ravel()),color=(255,0,0),thickness = 3)
			self.text("dist:%0.2fcm"%dist,point,color=(0,0,255),align="center")
		elif style == "cube":
			imgPts = np.int32(imgPts).reshape(-1,2)
			# draw ground floor in green
			self.fill([imgPts[:4]],color=(0,255,0),thickness=-3)
			# draw pillars in blue color
			for i,j in zip(range(4),range(4,8)):
				self.line(tuple(imgPts[i]), tuple(imgPts[j]),color=(255),thickness=3)
			# draw top layer in red color
			self.fill([imgPts[4:]],color=(0,0,255),thickness=3) 
		else:
			print("unknow style",style)
			assert 0
		return self
	
	#######################
	def save(self,fileName):
		cv2.imwrite(fileName,self.img)
		
	def show(self,title="image",autoShow=True):
		cv2.imshow(title,self.img)
		if autoShow:
			cv.cvUtility.wait(0)
		
	
	def show2(self,plt=None,autoShow=True): 
		from matplotlib import pyplot as plt2
		if plt is None:
			plt = plt2
			autoShow = True
		plt.imshow(self.toRgb().img)
		plt.axis("off")
		if autoShow:
			plt.show()
	
	#显示直方图 
	def showHist(self,plt=None): 
		from matplotlib import pyplot as plt2
		if plt is None:
			plt = plt2
		plt.hist(self.img.ravel(),256,[0,256])
		plt.show()
	
	#显示三通道的直方图 
	def showHistChannel(self,plt=None): 
		from matplotlib import pyplot as plt2
		if plt is None:
			plt = plt2 
		color = ('b','g','r')
		for i,col in enumerate(color):
			histr = cv2.calcHist([self.img],[i],None,[256],[0,256])
			plt.plot(histr,color = col)
			plt.xlim([0,256])
		plt.show()
		
###################### unit test ######################
def testdraw():
	img = image("data/1.jpg")  
	assert img.width == 640
	assert img.height == 400
	assert img.channel == 3
	img.lines(points=[(10,3),(500,6),(70,100)],isClosed=True,thickness=1,color=(0,0,255)) 
	
	nextLine = img.text("hello ycat",(0,0),(255,0,0))
	img.text("hello ycat",(0,nextLine))
	img.circle((20,20),10,(0,255,0))
	img.arrow((0,0),(100,200),(0,0,255),1)
	img.line((100,200),(300,30),color=(255,0,0),thickness=10)
	img.rect((100,200),(30,30),color=(255,0,0),thickness=10)
	#img.ellipse(((100,200),(300,30)),color=(255,255,0),thickness=1)
	img.marker((100,200),color=(0,0,255))
	img.padding(10,10,10,10,color=(255,255,255))
	
	img2 = img.roi((0,0),(200,100))  
	assert img2.width == 200
	assert img2.height == 100
	img.drawImg(img2,(199,299))
	img.marker((400,400))    
	img.resize(0.5,0.5)
	img.inverse()
	img.show2()
	cv.cvUtility.wait()  
	 
def testjoin():
	img = image.join(image("data/1.jpg"),image("data/2.jpg"),False)
	img.toGray().show()  
	
def testtext():
	img = image("data/1.jpg")  
	img.marker(point=(200,100),color=(255,0,0))
	img.text("left text",point=(200,100),color=(255,0,0),align="left")
	img.marker(point=(200,200),color=(0,255,0))
	img.text("center text",point=(200,200),color=(0,255,0),align="center")
	img.marker(point=(200,300),color=(0,0,255))
	img.text("right text",point=(200,300),color=(0,0,255),align="right")#,bgColor=(255,255,255))
	img.show()
	
if __name__ == "__main__":
	testdraw()
	#testjoin()
	#testtext()	
	
	
	
