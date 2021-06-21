#coding=utf-8 
# ycat			 2019/01/10	  create
# 简单的画图脚本
# matplotlib的Path和patches是两个概念，patches有点象区域 
#https://matplotlib.org/api/patches_api.html
# https://matplotlib.org/gallery/shapes_and_collections/artist_reference.html#sphx-glr-gallery-shapes-and-collections-artist-reference-py
import sys,os
import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import matplotlib.patches as mpathes
import matplotlib.transforms
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import json_codec as json
import enhance
import utility
import ui.pltUtil
		

#注意这个类最好不要在线程中创建，要不然有可能会出现Segmentation fault (core dumped)
class drawScript:
	def __init__(self):
		self.paths = []
		self.items = []
		self.transforms = None
		
	def load(self,filename,key="draw"):
		import slam.matrix
		items = json.load_file(filename)[key]
		shapes = []
		for i in items:
			shapes.append(self._createShape(i))
		self.items = items
		self.paths = self._getPaths(shapes)
		
	@property
	def count(self):
		return len(self.paths)
		
	def draw(self,**param):
		for p in self.paths:
			plt.gca().add_patch(mpathes.PathPatch(p,**param))
		
	def show(self,**param):
		self.draw(**param)
		plt.gca().grid(True, which='major')
		ui.pltUtil.show()
	
	#有两个坐标
	def contains(self,x,y):
		for p in self.paths:
			if p.contains_point((x,y)):
				return True
		return False
		 
	#是否有点有交集，点的大小为radius
	def intersects(self,x,y,radius=0.01):
		c = mpath.Path.circle((x,y),radius)
		for p in self.paths:
			if c.intersects_path(p,filled=False):
				return True
		return False
	
	def _createShape(self,item):
		m,func = item["func"].split(".")
		p = enhance.invoke_func("matplotlib",m,func,**item["params"])
		return p
		
	
	#返回matplotlib.path.Path对象，注意不是self.shapes，这是matplotlib.patches列表
	def _getPaths(self,shapes):
		pp = []
		for p in shapes:
			t = p.get_patch_transform()
			p2 = p.get_path()
			p2 = t.transform_path(p2)
			if self.transforms is not None:
				p2 = self.transforms.transform_path(p2)
			pp.append(p2)
		return pp
		
	def reset(self):
		if self.transforms is None:
			return None
		t = self.transforms.inverted()
		pp = []
		for p in self.paths:
			pp.append(t.transform_path(p))
		self.paths = pp
		self.transforms = None
		return t
		
	def setScale(self,sx,sy):
		t = matplotlib.transforms.Affine2D()
		t.scale(sx,sy)
		self.transforms = t
		pp = []
		for p in self.paths:
			pp.append(t.transform_path(p))
		self.paths = pp
		return t
		
	def setRotation(self,r):
		import slam.matrix
		self.setTransform(slam.matrix.create(0,0,r))
		
	def setOffset(self,x,y):
		import slam.matrix
		self.setTransform(slam.matrix.create(x,y,0))
		
	def setTransform(self,M):
		import slam.matrix
		assert isinstance(M,slam.matrix.matrix2D)
		t = matplotlib.transforms.Affine2D(M.H)
		self.transforms = t
		pp = []
		for p in self.paths:
			pp.append(self.transforms.transform_path(p))
		self.paths = pp
		return t
			
	def drawBound(self,**params):
		ui.pltUtil.rect2(*self.bound(),edgecolor="black",facecolor="none",alpha=0.2,**params)
			
	#返回外接矩形：return x1,y1,x2,y2
	def bound(self):
		t = plt.gca().transData.inverted()
		rr = None
		for p in self.paths:
			bbox = p.get_extents()
			a1 = bbox.min
			a2 = bbox.max
			if rr is None:
				rr = a1
			else:
				rr = np.vstack((rr,a1))
			rr = np.vstack((rr,a2))
		return np.min(rr[:,0]),np.max(rr[:,1]),np.max(rr[:,0]),np.min(rr[:,1])
	
	#中心点
	def center(self):
		x1,y1,x2,y2 = self.bound()
		return x1 + (x2-x1)/2,y2 + (y1-y2)/2,
		
	#返回每个path的中心点 
	def centers(self):
		r = []
		for p in self.paths:
			bbox = p.get_extents()
			a1 = bbox.min
			a2 = bbox.max
			r.append((a1[0]+(a2[0]-a1[0])/2,a2[1]+(a1[1]-a2[1])/2))
		return r
		
	def clone(self):
		r = drawScript()
		for i in range(len(self.paths)):
			r.items.append(utility.clone(self.items[i]))
			r.paths.append(self.paths[i].deepcopy())
		return r
		
			
######### unit test #########
def testdrawpath():
	import ui.pltUtil
	if "../../" not in sys.path:
		sys.path.append("../../")
	
	import slam.matrix
	s = '{"func":"patches.Circle","params":{"xy":[0,0],"radius":0.3}}'
	s2 = '{"func":"patches.Rectangle","params":{"xy":[0,0],"width":1,"height":1,"angle":0,"color":"yellow"}}'
	sp = drawScript()
	item = sp._createShape(json.load(s))
	item2 = sp._createShape(json.load(s2))
	#sp.show()
	c = mpath.Path.circle((0.98,0.98),0.01)
	r = c.intersects_path(item2.get_path(),filled=False)
	
#	sp.draw()
	sp2 = drawScript()
	sp2.load("./draw.script")
	sp2.setTransform(slam.matrix.create(0,0,0))
	plt.plot(0,1.5,"g*")
#	assert sp2.intersects(0,1.5) 
#	assert not sp2.intersects(0.43,2.5) 
#	sp2.draw()
	#draw2()
	plt.plot(1.1,0.5,"r*")
	plt.plot(0,1.5,"g*")
	
	assert sp2.contains(1.1,0.5) 
	assert sp2.contains(1.9,0.8) 
	assert not sp2.contains(2,2) 
	
	sp2.setTransform(slam.matrix.create(10,1,0))
	sp2.draw()
	def click(event):
		r1 = sp2.contains(event.xdata,event.ydata)
		r2 =sp2.intersects(event.xdata,event.ydata,radius=0.1)
		print("contains",r1,", intersects:",r2,event.xdata,event.ydata)
	ui.pltUtil.mouseDown(plt.gcf(),click)
	ui.pltUtil.show()

def testdrawpath2():
	import ui.pltUtil
	if "../../" not in sys.path:
		sys.path.append("../../")
	import slam.matrix
	sp2 = drawScript()
	sp2.load("./draw.script")
	sp3 = sp2.clone()
	sp2.setTransform(slam.matrix.create(5,0,0))
	sp3.draw(color="red")
	sp2.draw(color="green")
	sp2.drawBound()
	plt.plot(*sp2.center(),"b+")
	for p in sp2.centers():
		plt.plot(*p,"r+")
	#ui.pltUtil.show()
	
	sp2.reset()
	sp2.setTransform(slam.matrix.create(0,6,0))
	sp2.setScale(1.5,1.5)
	sp2.drawBound()
	
	plt.plot(*sp2.center(),"r+")
	for p in sp2.centers():
		plt.plot(*p,"r+")
	sp2.show(color="yellow")
	
	
if __name__ == '__main__':  
	testdrawpath2()
	testdrawpath()
	assert 0
	
