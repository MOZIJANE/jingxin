#coding=utf-8 
# ycat			 2019/01/10	  create
# plt.gcf().autofmt_xdate()  # 自动旋转日期标记
import sys,os
import math
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import matplotlib.patches as mpathes
import mpl_toolkits.mplot3d
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
	
#posList = [(x1,y1),(x2,y2)...]
def drawPaths(posList,**params):
	if len(posList):
		Path = mpath.Path
		path_data = []
		for p in posList:
			pp = (p[0],p[1])
			if len(path_data) == 0:
				path_data.append((Path.MOVETO,pp))
			else:
				path_data.append((Path.LINETO,pp))
		codes, verts = zip(*path_data)
		path = mpath.Path(verts, codes)
		patch = mpathes.PathPatch(path, facecolor='None', **params)
		plt.gca().add_patch(patch)
		
		
def autoscale():
	plt.axis("equal")
	plt.gca().autoscale_view() 
		
		
def fix(left=-10,right=10):   
	#ax.autoscale_view() 
	plt.gca().axis('square') #变方型  
	plt.xlim(left=left,right=right)
	plt.ylim(top=-left,bottom=-right)
	
#QT坐标系y轴是上面为负，和plot正好相反  
#把QT的路径转成matplotlib的路径 
def qt2path(qtPathObj,inverse=True,scale=1.):
	import PyQt5.QtGui
	if isinstance(qtPathObj,PyQt5.QtGui.QPainterPath):
		polygonList = qtPathObj.toSubpathPolygons(PyQt5.QtGui.QTransform())
	else:
		print(type(qtPathObj),qtPathObj)
		assert isinstance(qtPathObj,PyQt5.QtGui.QPolygonF)
		polygonList = [qtPathObj,] 
	paths = []
	s = 1
	if inverse:
		s = -1 
	for poly in polygonList:
		for i,p in  enumerate(poly):
			if i == 0:
				paths.append((mpath.Path.MOVETO, (p.x()*scale,s*p.y()*scale)))
			else:
				paths.append((mpath.Path.LINETO, (p.x()*scale,s*p.y()*scale)))
	if len(paths):
		codes, verts = zip(*paths) 
		return mpath.Path(verts, codes)
	else:
		return None
		
		
def addPath(qtPathObj,inverse=False,scale=1.,**param):
	p = qt2path(qtPathObj,inverse=inverse,scale=scale)
	if p is None:
		return
	return plt.gca().add_patch(mpathes.PathPatch(p, **param))
	

def drawLegend():
	from matplotlib.lines import Line2D
	custom_lines = [Line2D([0], [0], color="r", lw=4),
                Line2D([0], [0], color="g", lw=4),
                Line2D([0], [0], color="b", lw=4)]
	return plt.gca().legend(custom_lines, ['Cold', 'Medium', 'Hot'],loc='upper left')


def circle(x,y,r,**param):  
	return plt.gca().add_patch(mpathes.Circle((x,y),r,**param))

#x,y为左下角 
def rect(x,y,width,height,**param):
	return plt.gca().add_patch(mpathes.Rectangle((x,y),width,height,**param))

#x,y为左下角,x2,y2为右上角 
def rect2(x,y,x2,y2,**param):
	return plt.gca().add_patch(mpathes.Rectangle((x,y),(x2-x),(y2-y),**param))
	
def ellipse(x,y,r,width,height,**param):
	return plt.gca().add_patch(mpathes.Ellipse((x,y),width,height,angle=math.degrees(r),**param))

#画多边形，num为多少条边,r为半径 
def polygon(x,y,num,r,**param): 
	return plt.gca().add_patch(mpathes.RegularPolygon((x,y),num,r,**param))
	
#起点加角度
def arrow(x,y,r,width=1,head_width=0.2,**param):
	return plt.gca().arrow(x,y, math.cos(r)*width, 
			math.sin(r)*width, head_width=head_width, head_length=head_width, **param)
	
#点到点
def arrow2(x1,y1,x2,y2,head_width=0.2,**param):
	return plt.gca().arrow(x1,y1, x2-x1, y2-y1, head_width=head_width, head_length=head_width, **param)
			
#radius为半径,theta1和theta2是弧度
def ring(x,y,radius,theta1,theta2, width=None,**param):
	theta1 = math.degrees(theta1)
	theta2 = math.degrees(theta2)
	#https://matplotlib.org/api/_as_gen/matplotlib.patches.Wedge.html#matplotlib.patches.Wedge 
	return plt.gca().add_patch(mpathes.Wedge((x,y),r=radius,theta1=theta1,theta2=theta2,width=width, **param))


def line(x1,y1,x2,y2,**param):
	return plt.plot((x1,x2),(y1,y2),**param)
	

def text(x,y,text,**param):
	return plt.annotate(text,(x,y),**param)

############### 3D画图 ###############
g_ax_3d = None

def ax3d():
	global g_ax_3d
	if g_ax_3d is None:
		g_ax_3d = plt.figure().gca(projection='3d')
	return g_ax_3d
		
#https://matplotlib.org/api/_as_gen/mpl_toolkits.mplot3d.axes3d.Axes3D.html#mpl_toolkits.mplot3d.axes3d.Axes3D 
def fix3D(minValue=0,maxValue=10):   
	#plt.gca().axis('square') #变方型  
	ax = ax3d()
	ax.axis('square') #变方型  
	ax.set_xlim3d((minValue,maxValue))
	ax.set_ylim3d((minValue,maxValue))
	ax.set_zlim3d((minValue,maxValue))
	ax.view_init(20, 24)
	arrow3D(0,0,0,maxValue,0,0,arrow_length_ratio=0.05,color="r")
	arrow3D(0,0,0,0,maxValue,0,arrow_length_ratio=0.05,color="g")
	arrow3D(0,0,0,0,0,maxValue,arrow_length_ratio=0.05,color="b")
	text3D(maxValue+0.2, 0, 0, "X") 
	text3D(0, maxValue+0.2, 0, "Y") 
	text3D(0, 0, maxValue+0.2, "Z") 
	
#x1,x2为坐标上两个点
#quiver的x1,x2为相对x1的位移 
def arrow3D(x1,y1,z1,x2,y2,z2,arrow_length_ratio=0.2,**param):
	ax = ax3d()
	ax.quiver(x1,y1,z1,x2-x1,y2-y1,z2-z1,arrow_length_ratio=arrow_length_ratio,**param)

def line3D(x1,y1,z1,x2,y2,z2,**param):
	ax = ax3d()
	ax.plot([x1,x2],[y1,y2],[z1,z2],**param)

def text3D(x,y,z,text,**param):
	ax = ax3d()
	return ax.text(x,y,z,text,**param)
	
def mark3D(x,y,z,marker,**param):
	ax = ax3d() 
	ax.plot([x],[y],[z],marker,**param)
	
def axis3D(R,T):
	x,y,z = T[0],T[1],T[2]
	ax = ax3d()
	ax.quiver(x,y,z,R[0,0],R[0,1],R[0,2],color="r")
	ax.quiver(x,y,z,R[1,0],R[1,1],R[1,2],color="g")
	ax.quiver(x,y,z,R[2,0],R[2,1],R[2,2],color="b")
	
######################################

#def pause(sec):
#	plt.pause(sec)
	
def show():
	autoscale()
	plt.show()

def showTimeout(drawFunc=None,timeout=-1):
	if timeout != -1:
		plt.ion()
	if drawFunc:
		drawFunc()
	if timeout != -1:
		plt.pause(timeout)
	else:
		plt.show()
		
def showAnimation(drawFunc,timeout=-1):		
	while True:
		plt.clf()
		drawFunc()
		plt.pause(0.1)
	plt.show()

	
#鼠标键盘的事件处理  def callback(event) 
#event.xdata,event.ydata为坐标，event.x,event.y为像素坐标
#event.button=1为左键，3为右键 
#如果正在画图过程中，鼠标的x,y的值会有不准确的现象
#https://blog.csdn.net/guofei9987/article/details/78106492
def mouseUp(fig,callback):
	def _callback(event):
		if event.inaxes is not None:
			callback(event)
	if fig is None:
		fig = plt.gcf()
	fig.canvas.mpl_connect('button_release_event', _callback)
	
def mouseDown(fig,callback):
	def _callback(event): 
		if event.inaxes is not None: 
			callback(event)
	if fig is None:
		fig = plt.gcf()
	fig.canvas.mpl_connect('button_press_event', _callback)
	
def mouseMove(fig,callback):
	if fig is None:
		fig = plt.gcf()
	fig.canvas.mpl_connect('motion_notify_event', callback)
	
def keyDown(fig,callback):
	if fig is None:
		fig = plt.gcf()
	fig.canvas.mpl_connect('key_press_event', callback)
	
def keyUp(fig,callback):
	if fig is None:
		fig = plt.gcf()
	fig.canvas.mpl_connect('key_release_event', callback)
	 
def onClose(fig,callback):
	fig.canvas.mpl_connect('close_event', callback)
	 
def redraw(fig=None):
	if fig is None:
		fig = plt.gcf()
	fig.canvas.draw()

g_qt_app = None

def alert(msg):
	import qtutility
	import PyQt5.QtWidgets 
	global g_qt_app
	if g_qt_app is None:
		app = PyQt5.QtWidgets.QApplication(sys.argv)
	qtutility.alert(str(msg))
	
#https://www.it1352.com/1753776.html 
g_init_pause = False
	
def pause(interval):
	global g_init_pause
	if not g_init_pause:
		g_init_pause = True
		plt.ion()
		plt.show(block=False)

	backend = plt.rcParams['backend']
	if backend in matplotlib.rcsetup.interactive_bk:
		figManager = matplotlib._pylab_helpers.Gcf.get_active()
		if figManager is not None:
			canvas = figManager.canvas
			if canvas.figure.stale:
				canvas.draw()
			a = canvas.start_event_loop(interval)
			return

#总图加title plt.suptitle("ddd")

#fig.gca().autoscale_view()  

#ax.legend()
#ax.grid(True)
######### unit test #########
def testdrawpath():
	x = np.arange(0,2*math.pi+math.pi/10,math.pi/10)
	y = np.sin(x)
	drawPaths(np.vstack((x,y)).T)
	circle(0,0,1,color="red")
	rect(0,0,2,1,color="green")
	ellipse(0,0,math.pi/6,2,1,color="yellow")
	polygon(10.8,10.2,10,1,color='g')
	arrow(0,10,math.pi/2,1)
	arrow2(10,10,10,0,1,color="red")
	fix()
	plt.show()
 

 
if __name__ == '__main__':  
	#r = 0.5
	#ring(x=0,y=0,radius=r,theta1=-math.pi/2,theta2=math.pi/2,width=0.1)
	#arrow(0.01,r-0.05,math.pi,width=0.01)
	#fix()
	#plt.show()
	testdrawpath()
	
	
