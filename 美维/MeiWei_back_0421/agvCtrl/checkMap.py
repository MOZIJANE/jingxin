#coding=utf-8 
# ycat			2019-11-03	  create
# 检查不合理的地图点位 
import os,sys
import math
import PyQt5   
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__) 
import agvList
import mapMgr
import utility 
import enhance
import counter 
import shelveInfo
import bezierPath
from matplotlib import pyplot as plt
import matplotlib.path as mpath  
import matplotlib.patches as mpatches
import ui.pltUtil
import log

agvs = agvList._loadAgvList() 
g_maps = {}

def getMapInfo():
	mm = mapMgr.getMapList()
	def getMap(mapId): 
		ww = [a.width for a in agvs.values() if a.mapId == mapId or a.mapId is None]
		w = shelveInfo.maxWidth()
		if ww:
			w = max(w,max(ww))
			
		hh = [a.height for a in agvs.values() if a.mapId == mapId or a.mapId is None]
		h = shelveInfo.maxHeight()
		if hh:
			h = max(h,max(hh))
		return w,h 
		
	for m in mm:
		print("find map",m["id"])
		c = counter.counter()
		g_maps[m["id"]] = enhance.empty_class()
		w,h = getMap(m["id"])
		g_maps[m["id"]].width = w
		g_maps[m["id"]].height = h
		g_maps[m["id"]].map = mapMgr.getMap(m["id"])
		c.check()
	return g_maps
		
		
def getRect(x,y,r,w,h):
	rr = PyQt5.QtGui.QTransform().rotateRadians(r)
	t = PyQt5.QtGui.QTransform().translate(x,y)
	p = PyQt5.QtGui.QPainterPath() 
	p.addRect(-h/2,-w/2,h,w)  
	return t.map(rr.map(p))
		
		
def getPoints(mapId):
	w = g_maps[mapId].width
	h = g_maps[mapId].height
	rr = []
	m = g_maps[mapId]
	for p in m.map.positions:
		if not p.preLines:
			continue
		box = PyQt5.QtGui.QPainterPath() 
		if p.rotation: 
			box.addPath(bezierPath.rotate(p.x,p.y,0,math.pi,w,h))
		else:
			box.addPath(getRect(p.x,p.y,p.preLines[0].r,w,h)) #判断进去角度
		box.pos = p
		rr.append(box)
	return rr
	
	
def drawMap(mapId): 
	pp = getPoints(mapId)
	g_maps[mapId].map.draw(showPoint=True, showText=True)
	count = 0
	total = len(pp)
	for p in pp:
		c = "green"
		#if p.pos.preLines[0].isDeadend:
		#	continue
		#	
		for k in pp:
			if k == p:
				continue
			if p.intersects(k):
				count += 1
				c = "red"
				break
		plt.gca().add_patch(mpatches.PathPatch(ui.pltUtil.qt2path(p,inverse=False),edgecolor="none", facecolor=c,alpha=0.2,zorder=100))	
	log.success(mapId,"total",total,"conflict",count)

 

#m = mapMgr.getMap("fp-neiwei")  
#p1 = m.getPos("LM39")
#p2 = m.getPos("LM40")
#cc = p1.distance(p2.x,p2.y)
#print(cc)
#aa = m.getPos("AP32")
#print(aa.hasRotation())
#assert 0  0.8600000000000001

getMapInfo()

for m in g_maps:
	drawMap(m) 
plt.show()









