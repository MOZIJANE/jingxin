import math
import numpy as np
import matplotlib.pyplot as plt
import os
import PyQt5.QtGui 
import PyQt5.QtCore  
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import ui.pltUtil
import matplotlib.path as mpath
import matplotlib.patches as mpatches 

def _getBox(x,y,r,w,h):
	rr = PyQt5.QtGui.QTransform().rotateRadians(r)
	t = PyQt5.QtGui.QTransform().translate(x,y)
	p = PyQt5.QtGui.QPainterPath() 
	p.addRect(-h/2,-w/2,h,w)    
	return t.map(rr.map(p))
	

#Bezier转换成[(x1,y1),,,,]列表  
def bezier(p0,p1,p2,p3):
	global dataX,dataY
	dataX = []
	dataY = []
	ptrList,_ =  splitBezier(p0,p1,p2,p3)
	return ptrList 


def normAngle(angle):
	while angle > math.pi:
		angle -= 2.0 * math.pi 
	while angle < -math.pi:
		angle += 2.0 * math.pi 
	return angle


#沿着ptrList路线行走 
def strock(ptrList,width,height,x=None,y=None):
	last = None
	box = PyQt5.QtGui.QPainterPath() 
	box.setFillRule(1)
	dd = (height/3*2)**2
	index = 0 
	if x is not None:
		assert y is not None
		index = getIndex(x,y,ptrList)
	for i in range(index,len(ptrList)):
		p = ptrList[i] 
		if last is None:
			box.addPath(_getBox(p[0],p[1],p[2],width,height))
			last = p 
		else:
			if abs(normAngle(last[2] - p[2]) > math.radians(20)) or (last[0]-p[0])**2+(last[1]-p[1])**2 > dd:
				box.addPath(_getBox(p[0],p[1],p[2],width,height))
				last = p
	if len(ptrList):
		p = ptrList[-1]
		box.addPath(_getBox(p[0],p[1],p[2],width,height))
	#不能用 box.simplified()
	return box
	
	
#从r2旋转到r1的路径  
def rotate(x,y,r1,r2,width,height):
	#if r1 == 0 and (r2 == math.pi or r2 == math.pi*2):
	#	box = PyQt5.QtGui.QPainterPath() 
	#	h = max(width,height)
	#	box.addEllipse(x-h/2,y-h/2,h,h)
	#	return box
	a = 0 
	d = math.pi/18.
	box = _getBox(x,y,r1,width,height)
	box.setFillRule(1)
	dr = normAngle(r2 - r1)
	if abs(dr) < 0.01:
		return PyQt5.QtGui.QPainterPath() 
	if dr > 0:
		while a < normAngle(r2 - d - r1):
			a += d
			box.addPath(_getBox(x,y,a+r1,width,height))
	else:
		while a > normAngle(r2 + d - r1):
			a -= d
			box.addPath(_getBox(x,y,a+r1,width,height))
	box.addPath(_getBox(x,y,r2,width,height))
	return box.simplified()
	

#取最近点的索引  
def getIndex(x,y,ptrList):
	pp = np.array(ptrList).T
	cx = pp[0]
	cy = pp[1]
	cyaw = pp[2]
	dx = [x - icx for icx in cx]
	dy = [y - icy for icy in cy]
	dd = [idx ** 2 + idy ** 2 for (idx, idy) in zip(dx, dy)]
	distance = min(dd)	   
	return dd.index(distance) 

############## private func ##############

def BezierPoint(t,p0,p1,p2,p3):
	u = 1 - t
	tt = t * t
	uu = u * u
	uuu = uu * u
	ttt = tt * t
	
	p = [0,0]
	p[0] = uuu * p0[0]
	p[1] = uuu * p0[1]
	p[0] = p[0] + 3 * uu * t * p1[0]
	p[1] = p[1] + 3 * uu * t * p1[1]
	p[0] = p[0] + 3 * u * tt * p2[0]
	p[1] = p[1] + 3 * u * tt * p2[1]
	p[0] = p[0] + ttt * p3[0]
	p[1] = p[1] + ttt * p3[1]
	return p
 
	
#https://www.jianshu.com/p/73acea5fdac9
#I = p0*(1-e)^2 + p1*2*(1-e)e+p2*e^2
#H = p2*(1-e)+p3*e
#J = p1*(1-e)^2 + p2*2(1-e)*e+ p3*e^2
def getCurvature(num,p0,p1,p2,p3,dataX,dataY,fragmentLen,count):
	t1 = num / count
	t2 = (num+1) / count
	I = [0,0]
	J = [0,0]
	isVertical = False
	
	I[0] = p0[0]*(1-t1)*(1-t1)+p1[0]*2*(1-t1)*t1+p2[0]*t1*t1
	I[1] = p0[1]*(1-t1)*(1-t1)+p1[1]*2*(1-t1)*t1+p2[1]*t1*t1
	J[0] = p1[0]*(1-t1)*(1-t1)+p2[0]*2*(1-t1)*t1+p3[0]*t1*t1
	J[1] = p1[1]*(1-t1)*(1-t1)+p2[1]*2*(1-t1)*t1+p3[1]*t1*t1
	if J[0]==I[0]:
		k1 = (J[1]-I[1])/0.000001
		isVertical=True
	else:
		k1 = (J[1]-I[1])/(J[0]-I[0])
	I[0] = p0[0]*(1-t2)*(1-t2)+p1[0]*2*(1-t2)*t2+p2[0]*t2*t2
	I[1] = p0[1]*(1-t2)*(1-t2)+p1[1]*2*(1-t2)*t2+p2[1]*t2*t2
	J[0] = p1[0]*(1-t2)*(1-t2)+p2[0]*2*(1-t2)*t2+p3[0]*t2*t2
	J[1] = p1[1]*(1-t2)*(1-t2)+p2[1]*2*(1-t2)*t2+p3[1]*t2*t2
	if J[0]==I[0]:
		k2 = (J[1]-I[1])/0.000001
	else:
		k2 = (J[1]-I[1])/(J[0]-I[0])
	dr = math.atan((k2 - k1)/(1+k1*k2))
	r = math.atan(k1)
	if isVertical:#处理斜率不存在的情况
		#print("111111111",dataY[num+1],dataY[num])
		if dataY[num+1]<dataY[num]:
			rad = r
			#print("here2",math.degrees(r))
		else:
			#print("here1",math.degrees(r))
			rad = r #+ np.pi
	else:
		if math.degrees(math.atan(k1))==90:#处理角度为90度
			if dataY[num+1]<dataY[num]:
				rad = r + np.pi
			else:
				rad = r
		elif math.degrees(math.atan(k1))==0:#处理角度为0
			if dataX[num+1]<dataX[num]:
				rad = r + np.pi
			else:
				rad = r
		elif dataY[num+1]<dataY[num] and dataX[num+1]<dataX[num]:#处理角度处于第三象相
			rad = r + np.pi
		elif dataY[num+1]>dataY[num] and dataX[num+1]<dataX[num]:#处理角度处于第二象相
			rad = r + np.pi
		else:
			rad = r
	curvature = dr/fragmentLen[num+1]
	rad = normAngle(rad)
	list = [dataX[num],dataY[num],rad]#,None,None,curvature]
	return list
	
def splitBezier(p0,p1,p2,p3):
	ptrList = []
	dataX = []
	dataY = []
	fragmentLen = []
	ctrlList = [p0,p1,p2,p3]
	count = 0
	#拆分
	count = int(math.sqrt((p0[0]-p3[0])*(p0[0]-p3[0])+(p0[1]-p3[1])*(p0[1]-p3[1]))*10)*2
	lastPoint = BezierPoint(0.0 / count,p0,p1,p2,p3)

	for i in range(count+1):
		point = BezierPoint(i/count,p0,p1,p2,p3)
		dataX.append(point[0])
		dataY.append(point[1])
		len = math.sqrt((point[0]-lastPoint[0])*(point[0]-lastPoint[0])+(point[1]-lastPoint[1])*(point[1]-lastPoint[1]))
		fragmentLen.append(len)
		lastPoint = point
	for n in range(count):
		list = getCurvature(n,p0,p1,p2,p3,dataX,dataY,fragmentLen,count)
		ptrList.append(list)
	return ptrList,ctrlList
	
def show(posList,**params):
	if posList is None or len(posList) == 0:
		return
	Path = mpath.Path
	path_data = [] 
	for p in posList:
		if len(path_data) == 0:
			path_data.append((Path.MOVETO,p[0:2]))
		else:                                 
			path_data.append((Path.LINETO,p[0:2])) 
	path_data.append((Path.STOP,p[0:2]))
	codes, verts = zip(*path_data)
	path = mpath.Path(verts, codes)
	if "facecolor" not in params:
		params["facecolor"] = "None"
	patch = mpatches.PathPatch(path, **params)
	plt.gca().add_patch(patch) 
	
	plt.plot(*p0,"r*")
	plt.plot(*p1,"r*")
	plt.plot(*p2,"r*")
	plt.plot(*p3,"r*")
	plt.gca().axis('square') #变方型  
	plt.show()
	
	
def show2(p0,p1,p2,p3):
	from matplotlib import pyplot as plt
	import matplotlib.path as mpath  
	import matplotlib.patches as mpatches  
	linePath = mpatches.PathPatch(mpath.Path([p0, p1, p2, p3],
				[mpath.Path.MOVETO, mpath.Path.CURVE4, mpath.Path.CURVE4, mpath.Path.CURVE4 ]),
				fc="none",edgecolor="green",linewidth=2)  
	plt.plot(*p0,"r*")
	plt.plot(*p1,"r*")
	plt.plot(*p2,"r*")
	plt.plot(*p3,"r*")
	plt.gca().add_patch(linePath)   
	plt.gca().axis('square') #变方型  
	plt.show()

############ unit test ##########
def teststrock():
	b1 = _getBox(1.4965833333333336,3.1320000000000006, 0.0, 0.6, 1.2) 
	b2 = _getBox(1.7221966666666666, 3.132, 0.0, 0.6, 1.2)
	b3 = PyQt5.QtGui.QPainterPath() 
	b3.addPath(b1)
	b3.addPath(b2)
	ui.pltUtil.addPath(b1,inverse=False,facecolor="red",alpha=0.2)
	ui.pltUtil.addPath(b2,inverse=False,facecolor="g",alpha=0.2)
	ui.pltUtil.addPath(b3,inverse=False,facecolor="b",alpha=0.8)
	plt.gca().axis('square') #变方型  
	plt.show()
	

	
#+点和线段要相互重叠 
def testptrList():	
	pp = [[-89.557, 26.911, 0.0], [-89.51933494552968, 26.911, 0.0], [-89.48067336589033, 26.911000000000005, 0.0], 
	[-89.44103836401204, 26.911, 0.0], [-89.40045304282492, 26.910999999999998, 0.0], [-89.3589405052592, 26.911, 0.0],
	[-89.31652385424493, 26.910999999999998, 0.0], [-89.27322619271226, 26.911, 0.0], 
	[-89.22907062359127, 26.910999999999998, 0.0], [-89.18408024981217, 26.911, 0.0], [-89.13827817430503, 26.911, 0.0],
	[-89.0916875, 26.911, 0.0], [-89.04433132982719, 26.910999999999998, 0.0], [-88.99623276671677, 26.911000000000012, 0.0],
	[-88.9474149135988, 26.911000000000005, 0.0], [-88.89790087340347, 26.911000000000005, 0.0],
	[-88.84771374906086, 26.911, 0.0], [-88.79687664350112, 26.911, 0.0], [-88.74541265965439, 26.910999999999994, 0.0],
	[-88.69334490045077, 26.910999999999998, 0.0], [-88.64069646882041, 26.910999999999994, 0.0], 
	[-88.58749046769347, 26.911, 0.0], [-88.53375000000001, 26.911, 0.0], [-88.47949816867018, 26.911000000000005, 0.0], 
	[-88.4247580766341, 26.911, 0.0], [-88.36955282682194, 26.911, 0.0], [-88.3139055221638, 26.911, 0.0],
	[-88.25783926558978, 26.911, 0.0], [-88.20137716003005, 26.911, 0.0], [-88.14454230841474, 26.911, 0.0], 
	[-88.08735781367393, 26.911, 0.0], [-88.02984677873779, 26.911, 0.0], [-87.97203230653645, 26.911, 0.0], 
	[-87.9139375, 26.911, 0.0], [-87.8555854620586, 26.911, 0.0], [-87.7969992956424, 26.911000000000005, 0.0],
	[-87.73820210368145, 26.911, 0.0], [-87.67921698910595, 26.911, 0.0], [-87.62006705484599, 26.911, 0.0], 
	[-87.56077540383171, 26.911, 0.0], [-87.50136513899324, 26.911, 0.0], [-87.4418593632607, 26.911, 0.0], 
	[-87.38228117956425, 26.911, 0.0], [-87.32265369083396, 26.910999999999998, 0.0]]
	for p in pp:
		plt.plot(p[0],p[1],"g+")
	box = strock(pp,0.5,1)
	ui.pltUtil.addPath(box,inverse=False)
	ui.pltUtil.fix(-50,100)
	
	plt.xlim(left=-95,right=-85)
	plt.ylim(top=30,bottom=25)
	plt.show()

def test():
	
	pp = bezier(p0,p1,p2,p3)#((0,0),(1,2),(3,4),(0.1,4))
	import counter
	import utility
	c = counter.counter()
	c.check()
	t = utility.ticks()
	for i in range(100):
		path = strock(pp,0.5,1)
	c.check()
	ui.pltUtil.addPath(path,inverse=False)
	
	cc = rotate(10,10,-math.pi/2.,0,0.5,1.2)
	ui.pltUtil.addPath(cc,inverse=False)
	
	xx = np.arange(10,20,0.1)
	yy = np.repeat(10,len(xx))
	rr = np.zeros(len(xx))
	pp = np.vstack((xx,yy,rr)).T
	cc =  strock(pp,0.5,1.2)
	ui.pltUtil.addPath(cc,inverse=False)
	
	cc = rotate(12,12,-math.pi/2,-math.pi/180.*89,0.5,1.2)
	ui.pltUtil.addPath(cc,inverse=False)
	plt.plot(14.9,3,"b*") 
	
	cc = rotate(8,19,0,math.pi,0.5,2)
	ui.pltUtil.addPath(cc,inverse=False)
	plt.plot(8,19,"r*") 
	
	show(pp)
	plt.gca().axis('square') #变方型  
	plt.show()

if __name__ == '__main__': 	
	p0 = [0,0]
	p1 = [11,12]
	p2 = [-12,-41]
	p3 = [31,0]  
	test()
	testptrList()	
	
	
	
	
	
	
	
	