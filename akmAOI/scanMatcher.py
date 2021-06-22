# coding: utf-8
# author: ycat
# date: 2020-5-7
# TODO: 分数对里程计的考虑
# TODO: 分数对激光强度的考虑 
import os
import sys 
import math
import numpy as np
import numpy.linalg as lg
import matplotlib.pyplot as plt
import setup 
if __name__ == '__main__':
	setup.setCurPath(__file__) 
import log
import counter
import utility    
import slam.gridMap
import slam.laser
import slam.matrix
import kernel
import laserCache
import local 
import ui.pltUtil
import offsetInfo
import penalize

occupy_value = local.getint("scan_match","occupy_value",100)	

g_resolution = local.getfloat("scan_match","resolution",0.01)	#地图精度 

g_angle_resolution 		= local.getfloat("scan_match","angle_resolution",1)		 #粗查找角度分辨率(度)
g_angle_resolution 		= math.radians(g_angle_resolution)
g_fine_angle_resolution = local.getfloat("scan_match","fine_angle_resolution",0.5)	 #精查找角度分辨率(度)
g_fine_angle_resolution = math.radians(g_fine_angle_resolution)

g_fine_search_offset =local.getfloat("scan_match","fine_search_offset",0.05)	#精查找x,y的查找范围(+-)

g_fine_angle_offset = local.getfloat("scan_match","fine_angle_offset",2)		#精查找角度查找范围(+-)
#g_fine_angle_offset = math.radians(g_fine_angle_offset)

g_laser_sigma = local.getfloat("scan_match","laser_sigma",0.03)		#激光的误差范围
if local.getbool("scan_match","enable_skeleton",True):
	if g_laser_sigma < 0.05:
		log.warning("enable_skeleton is True, so laser_sigma change from %0.2f to 0.05"%g_laser_sigma)
		g_laser_sigma = 0.05

g_min_score = local.getfloat("scan_match","min_score",0.4)				#最小分值 
g_coarse_index_step = local.getint("scan_match","coarse_index_step",10)	#粗查找选取激光点步进 

g_fast_search_offset= local.getfloat("fast_match","fast_search_offset",1.0)		#快速粗查找x,y的查找范围(+-)
g_fast_index_step	= local.getint("fast_match","fast_index_step",10)		#快速粗查找选取激光点步进 	
g_fast_angle_offset = local.getfloat("fast_match","fast_angle_offset",60)	
#g_fast_angle_offset = math.radians(g_fast_angle_offset)
g_fast_min_score = local.getfloat("fast_match","fast_min_score",0.3)		#最小快速查找成功的分数

g_enable_fast_match = local.getbool("scan_match","enable_fast_match",True)		#快速定位，在分值恶化时退出定位 

g_reloc_min_coarse_score= local.getfloat("reloc","reloc_min_coarse_score",0.5)	#最小重定位粗定位分值 
g_low_confidence_alarm_threshold = local.getfloat("scan_match","low_confidence_alarm_threshold",0.7)
#g_reloc_success_score 	= local.getfloat("reloc","reloc_success_score",0.6)		#重定位成功的分值
g_reloc_success_score   = g_low_confidence_alarm_threshold
g_reloc_search_offset 	= local.getfloat("reloc","reloc_search_offset",1.0)		#重定位的偏移量

g_reloc_angle_offset 	= local.getfloat("reloc","reloc_angle_offset",20.0)		#重定位的角度偏移量

g_reloc_coarse_offset   = local.getfloat("reloc","reloc_coarse_offset",30.0)	#重定位粗定位取的偏移量
g_reloc_coarse_count	= local.getint("reloc","reloc_coarse_count",15)			#重定位粗定位取的激光点个数
g_reloc_coarse_step		= local.getint("reloc","reloc_coarse_step",5)			#重定位粗定位取的地图步进
g_reloc_angle_resolution_scale = local.getint("reloc","reloc_angle_resolution_scale",5)	#粗定位角分辨率的倍数
g_reloc_resolution_scale = local.getint("reloc","reloc_resolution_scale",10)			#粗定位分辨率的倍数


MAX_VARIANCE = 500			#最大协方差
ZERO_VALUE  = 1e-06			#极小值 
pos_str = slam.slamUtil.pos_str 

#激光查找匹配窗口 
class matcher:
	#x,y为预估位姿(里程计位姿) 
	def __init__(self,resolution=g_resolution,locationMode=False):
		#t = counter.counter()
		self.locationMode = locationMode
		if not locationMode:
			size = slam.laser.maxRange()*2+1
			self.map = slam.gridMap.baseMap(resolution=resolution,defaultValue=0,mapType=1) 
			self.map.init(size*2,size*2,value=0)
			self._init(resolution)
			self.enable_area_mask = False	#是否启用区域过滤功能 
		else:
			self.map = None
			self.enable_area_mask = local.getbool("scan_match","enable_area_mask",True)
		#分布式计算 
		self.worker_index = -1
		self.worker_total = 1
		self.map_margin = 0
		self.isExited = False
		#assert int(math.sqrt(self.worker_total))
		
	def set_dispatcher_num(self,index,total):
		self.worker_index = index
		self.worker_total = total
		
	def set_laser_sigma(self,value):
		global g_laser_sigma
		g_laser_sigma = value

		 
	def _init(self,resolution):
		size = slam.laser.maxRange()*2+1
		#高斯核 
		kmap = kernel._get(sigma=g_laser_sigma,resolution=resolution)
		
		#激光角度缓存地图 
		cacheSize = slam.laser.maxRange()*2 
		self.cache = laserCache.laserCache(size=cacheSize,angle_resolution=g_angle_resolution,map_resolution=self.resolution)
		
		#激光角度缓存地图(精定位)
		if g_angle_resolution == g_fine_angle_resolution:
			self.fineCache = self.cache
		else:
			self.fineCache = laserCache.laserCache(size=cacheSize,angle_resolution=g_fine_angle_resolution,map_resolution=self.resolution)
		#t.check()
		
		#存放匹配结果，主要用于显示 
		self.fastCoarsePos = None
		self.coarsePos = None
		self.finePos = None
		self.result_index = []
		self.reloc_result = None
		self.lastScan = None
		
	def loadMap(self,filename):
		map = slam.gridMap.load(filename)
		map.trim()
		if local.getbool("scan_match","enable_skeleton",True):
			map.skeleton()
		self.setMap(map)
		
	def setMap(self,map):
		assert self.locationMode
		self.map = map
		assert map.mapType == 0
		self.map_margin = g_reloc_search_offset+0.1
		self.map.expand(margin=self.map_margin,value=0)
		value = 100
		if map.mapType == 0:
			value = 255
		elif map.mapType == 1:
			value = occupy_value
		else:
			log.error("mapType error",map.mapType)
			assert 0
		self.map.mapType = 1
		self.map.grid = np.where(self.map.grid < value,0,occupy_value) #变成0或100
		self._init(self.resolution)
		if "has_kernel" not in self.map.property:
			kernel.update(self.map,sigma=g_laser_sigma,indexs=None)
			
		self.enable_area_mask = local.getbool("scan_match","enable_area_mask",True)
		if self.map.areaCount("LocConfigArea") == 0:
			self.enable_area_mask = False
		return self.map
		
	@property
	def hasMap(self):
		return self.map is not None
		
	@property
	def resolution(self):
		if self.map is None:
			return 0
		return self.map.resolution 
	
	#添加用于参考的激光数据 
	#返回激光索引index： [[y1,y2,y3...],[x1,x2,x3...]] 
	def addScan(self,laser):
		pp = laser.locPoints.T
		xx = np.round((pp[0] - self.map.startX)/self.resolution).astype(np.int)
		yy = np.round((pp[1] - self.map.startY)/self.resolution).astype(np.int)
		ii = np.where((xx >= 0) & (xx < self.map.shape[1]))
		xx = xx[ii]
		yy = yy[ii]
		ii = np.where((yy >= 0) & (yy < self.map.shape[0]))
		xx = xx[ii]
		yy = yy[ii]
		self.map._grid[yy,xx] = occupy_value	
		return xx,yy#np.vstack((yy,xx))
		
	#粗定位 
	def reloc_step1(self,scan,pos=None,offset=None):
		c = counter.counter()
		self.lastScan = scan
		assert self.map
		assert self.locationMode
	
		angle_resolution = g_angle_resolution*g_reloc_angle_resolution_scale	#粗定位角分辨率
		resolution = self.resolution*g_reloc_resolution_scale			#粗定位分辨率
		
		cache = laserCache.laserCache(size=slam.laser.maxRange()*2 ,angle_resolution=angle_resolution,map_resolution=resolution)
		count = g_reloc_coarse_count			#粗定位取的激光点个数 
		step = g_reloc_coarse_step				#循环步进的个数，step*resolution*10=0.5米 
		
		margin = round(self.map_margin/resolution)			#1.0是地图的margin可以跳过的 99行 self.map.expand(margin=1.0,value=0)
		cache.addScan(scan,r=0,angle_offset=math.pi,indexStep=round(scan.validCount/count))
		
		map = self.map.changeResolution(resolution=resolution)
		map.grid = np.where(map.grid < occupy_value,0,occupy_value)
		log.info("start relocation, seq=",scan.seq,",width=",self.map.width*self.map.resolution,
			",height=",self.map.height*self.map.resolution,",pos=",pos_str(pos))
		
		kernel.update(map,sigma=resolution*2.5,indexs=None)
		results = []	#x,y,r,score
		cache.setOffset(*map.index2Ptr(0,0),map,False) #设置左下角 
		
		startX 	= margin
		endX 	= map.width-margin
		startY  = margin
		endY 	= map.height-margin
			
		if pos is not None and offset is not None:
			x,y = map.ptr2Index(pos[0],pos[1])
			dx  = offset.offsetX/resolution
			dy  = offset.offsetY/resolution
			startX = round(max(x - dx,startX))
			endX   = round(min(x + dx,endX))
			startY = round(max(y - dy,startY))
			endY   = round(min(y + dy,endY))
		
		if self.worker_total > 1:
			#计算分布式的第几部分 
			p = int(math.sqrt(self.worker_total))
			partX = (endX - startX)/p
			partY = (endY - startY)/p
			ix = self.worker_index % p 
			iy = int(self.worker_index / p) 
			startX = startX + round(partX * ix)
			startY = startY + round(partY * iy)
			endX = min(round(startX + partX + step),endX)
			endY = min(round(startY + partY + step),endY)
			log.info(ix,iy,p,"relocation worker: id=",self.worker_index,",xrange (",startX,endX,"), yrange (",startY,endY,")")
		
		#显示覆盖区域
		#ui.pltUtil.rect2(startX,startY,endX,endY,alpha=0.3)
		#plt.text(startX,startY,self.worker_index,alpha=0.3)
		#map.show()
		
		#用射线法判断是否提前碰到障碍物 
		def isBlocked(map,x,y,indexs):
			error = 0
			max_error = int(len(indexs)*0.4)
			for i in indexs:
				ix = i[0] + x
				iy = i[1] + y
				if ix < 0 or ix >= map.width:
					continue
				if iy < 0 or iy >= map.height:
					continue
				if error >= max_error:
					return True
				nx,ny = map.findBlockPoint((x,y),(ix,iy),blockValue=occupy_value)
				if nx is None:
					#error+=1
					continue
				dis1 = slam.slamUtil.distance(nx,ny,x,y)
				dis2 = slam.slamUtil.distance(ix,iy,x,y)
				if dis1 < dis2*0.8:
					error+=1
					continue
			return error >= max_error
		
		max_score = 0
		
		for r in np.arange(-math.pi,math.pi,angle_resolution):
			r = slam.slamUtil.normAngle(r)
			m = cache.getMap(r)
			assert m
			indexs = m.property["points"]
			for x in range(startX,endX,step):
				for y in range(startY,endY,step):
					if self.isExited:
						return []
					s = 0
					for i in indexs:
						ix = i[0] + x
						iy = i[1] + y
						if ix < 0 or ix >= map.width:
							continue
						if iy < 0 or iy >= map.height:
							continue
						s += map._grid[iy,ix]
						assert map._grid[iy,ix]<=occupy_value
					if s == 0:
						continue
					if map.grid[y,x] == occupy_value:
						continue
					s = s/len(indexs)/occupy_value
					assert s <= 1.0
					if s >= g_reloc_min_coarse_score and s >= max_score-0.2:
						if isBlocked(map,x,y,indexs):
							continue
						max_score = max(s,max_score)
						results.append((*map.index2Ptr(x,y),r,s))
						if len(results) >= 2000:
							log.error("relocate step 1: found too many results,count",len(results))
							return []
		if self.worker_index > 0:
			log.info("relocate step 1: count:",len(results),",id:",self.worker_index,",used",c.get(),"ms")
		else:
			log.info("relocate step 1: count:",len(results),",used",c.get(),"ms")
		return results
		
	#过滤粗定位数据 
	def reloc_step2(self,results):
		c = counter.counter()
		results.sort(key=lambda x: x[3],reverse=True)
		results2 = []
		if len(results):
			min_score = results[0][3] - 0.2
			#过滤掉相近的点 
			for result in results:
				if result[3] <= min_score:
					break
				for r2 in results2:
					if slam.slamUtil.distance(r2[0],r2[1],result[0],result[1]) < g_reloc_search_offset -0.1:
						#合并相近点
						dr = abs(slam.slamUtil.normAngle(r2[2] - result[2]))
						if dr < math.radians(g_reloc_angle_offset):
							break
				else:
					results2.append(result)
		log.info("relocate step 2: filter count:",len(results2),", origin count=",len(results),",used",c.get(),"ms")
		return results2
		
	#fast match
	def reloc_step3(self,results):
		c = counter.counter()
		old_total  = self.worker_total
		self.worker_total = 1
		
		ret_results = []
		oldPos = self.lastScan.sensorPos
		dr = max(g_fast_angle_offset,g_reloc_angle_offset)
		offset = offsetInfo.create(g_reloc_search_offset,dr,mode="reloc_step3")
		for result in results:
			if self.isExited:
				return []
						
			#快速粗定位 
			self.lastScan.setSensorPos(*result[0:3])
			pos,score = self.match_step1(offset=offset,doPenalize=False)
			if pos is None:
				continue
			ret_results.append((*pos,score))
		self.lastScan.setSensorPos(*oldPos)
		log.info("reloc_step3: in count=",len(results),",out count=",len(ret_results),"used",c.get(),"ms")
		self.worker_total = old_total
		return ret_results
		
		
	#精重位
	def reloc_step4(self,results):
		if len(results) == 0:
			return None,0
			
		global g_min_score
		old_g_min_score = g_min_score
		old_total  = self.worker_total
		g_min_score = g_reloc_min_coarse_score
		self.worker_total = 1
		scan = self.lastScan
		assert self.lastScan is not None
		
		ret_score = 0
		ret_pos = None
		ret_results = []
		offset = offsetInfo.create(g_reloc_search_offset,g_reloc_angle_offset,mode="")
		if self.worker_index >= 0:
			offset.mode = "reloc_step4_%d"%(self.worker_index)
		else:
			offset.mode = "reloc_step4"
				
		for result in results:
			if self.isExited:
				return None,0
				
			scan.setSensorPos(*result[0:3])
			pos,score = self.localize(scan,offset=offset,fastMatch=False,doPenalize=False)
			#if score >= g_reloc_success_score:
			if pos is not None:
				ret_results.append((*pos,score))
			#if score > 0.9:
			#	break
				
		g_min_score = old_g_min_score
		self.worker_total = old_total
		if len(ret_results) == 0:
			return None,0
		ret_results.sort(key=lambda x: x[3],reverse=True)
		return ret_results[0][0:3],ret_results[0][3]
		
	def reloc_draw(self,results=None):
		if results is None:
			results = self.reloc_result
		if results is None:
			return
		#显示可选的点 
		for i,result in enumerate(results):
			slam.draw.drawPos(result[0],result[1],result[2],map=self.map,length=1,color="red",alpha=0.2)
			plt.text(*self.map.ptr2Index(result[0],result[1]),str(i))
		if not hasattr(self,"initEvent"):
			self.initEvent = True
			self.reloc_result = results
			ui.pltUtil.mouseDown(plt.gcf(),self.onclick)
		#self.map.show()
		
		
	#全局重定位 
	#返回pos和score 
	def reloc(self,scan,pos=None,offset=None,debug=0):
		def show():
			self.lastScan = scan
			self.results = results
			self.reloc_draw(results)
			self.show()
			
		oldPos = scan.sensorPos
		c = counter.counter()
		self.reloc_result = None
		
		results = self.reloc_step1(scan,pos=pos,offset=offset)
		if len(results) == 0:
			log.error("relocation failed, seq=",scan.seq,",no results, used",c.get(),"ms")
			scan.setSensorPos(*oldPos)
			return None,0
		
		if self.isExited:
			return None,0
			
		if debug == 1:
			show()

		count = 30
		results = self.reloc_step2(results)
		if len(results) > count:
			results = results[0:count]
		
		if debug == 2:
			show()
		
		if self.isExited:
			return None,0
			
		results = self.reloc_step3(results)
		results.sort(key=lambda x: x[3],reverse=True)
		count = 10
		if len(results) > count:
			results = results[0:count]
		self.reloc_result = results
		
		if debug == 2:
			show()
		
		if self.isExited:
			return None,0
			
		ret_pos,ret_score = self.reloc_step4(results)
		self.lastScan = None
		self.fastCoarsePos = None
		self.coarsePos = None
		self.finePos = None
		if ret_score == 0:
			log.error("relocation failed, seq=",scan.seq,",used",c.get(),"ms")
			scan.setSensorPos(*oldPos)
			return None,0
		log.success("finish relocation, seq=",scan.seq,",score=",ret_score,",pos=",pos_str(ret_pos),",used",c.get(),"ms")
		scan.setSensorPos(*oldPos)
		return ret_pos,ret_score
			
		
	#定位激光 
	def localize(self,scan,offset,fastMatch=False,doPenalize=True):
		assert self.locationMode
		assert self.map
		pos,score,_ = self.match(scan,[],offset=offset,fastMatch=fastMatch,doPenalize=doPenalize)
		return pos,score
	
	
	def _updateRefMap(self,pos,referLasers):
		#设置地图中心点为当前激光的base_link位置 
		#添加参考激光
		if "has_kernel" in self.map.property:
			self.map.property["has_kernel"] = False
		self.map.clear()
		x = pos[0] - self.map.width*self.resolution/2.
		y = pos[1] - self.map.height*self.resolution/2.
		self.map.setOrigin(x,y)
		xx = None
		yy = None
		for l in referLasers:
			x,y = self.addScan(l)
			if xx is None:
				xx = x
				yy = y
			else:
				xx = np.hstack((xx,x))
				yy = np.hstack((yy,y))
		indexs = np.vstack((yy,xx))
		kernel.update(self.map,sigma=g_laser_sigma,indexs=indexs)
		
		
	def match_step1(self,offset,doPenalize):
		t = counter.counter()
		laser = self.lastScan
		newOffset = offsetInfo.create(g_fast_search_offset,max(g_fast_angle_offset,offset.angle),mode=offset.mode)
		self.cache.addScan(laser,r=laser.sensorPos[2],angle_offset=newOffset.offsetR,indexStep=g_coarse_index_step) 

		if not self.locationMode:
			self.cache.setOffset(laser.sensorPos[0],laser.sensorPos[1],self.map,updateValidIndex=False)
		
		step = min(int(newOffset.offsetX/self.resolution),25)
		fastPos,fast_score,_ = self._matchScan(laser.sensorPos,laser,offset=newOffset,step=step,angle_resolution=2*g_angle_resolution,matchType=2,doPenalize=doPenalize)
		self.fastCoarsePos = fastPos
		if fastPos is None:
			log.warning(offset.mode,": fast coarsePos is None, seq:",laser.seq)
			return None,0
		
		if fast_score < g_fast_min_score:
			log.debug(offset.mode,": fast coarsePos is low: seq:",laser.seq,"score:",fast_score,",sensor pos:",pos_str(laser.sensorPos),",time used",t.get(),"ms")
			return None,0
		log.debug(offset.mode,": fast coarsePos seq:",laser.seq,"score:",fast_score,",pos:",pos_str(fastPos),",sensor_pos:",pos_str(laser.sensorPos),",time used",t.get(),"ms")
		return fastPos,fast_score
		
		
	def match_step2(self,pos,offset,doPenalize):
		t = counter.counter()
		laser = self.lastScan
		self.cache.addScan(laser,r=pos[2],angle_offset=offset.offsetR,indexStep=g_coarse_index_step)
		
		#粗定位 
		if not self.locationMode:
			self.cache.setOffset(pos[0],pos[1],self.map,updateValidIndex=False)
		step = min(int(g_fine_search_offset/self.resolution),4)
		
		coarsePos,coarse_score,results = self._matchScan(pos,laser,offset=offset,step=step,angle_resolution=g_angle_resolution,matchType=1,doPenalize=doPenalize)
#		assert len(results) != 0

		if coarsePos is None:
			log.warning(offset.mode,": coarse pos is None, seq:",laser.seq)
			return None,0,[]
		if len(results) == 0:
			log.warning(offset.mode,": coarse results is empty, seq:",laser.seq)
			return None,0,[]
		assert coarsePos is not None
		if coarse_score < g_min_score:
			log.warning(offset.mode,": coarse score is low",coarse_score,"seq:",laser.seq,",coarsePos: ",pos_str(coarsePos),",estimate pos: ",pos_str(pos),",time used",t.get(),"ms")
			return None,0,[]
		self.coarsePos = coarsePos
		log.debug(offset.mode,": seq:",laser.seq,",coarsePos: ",pos_str(coarsePos),",score:",coarse_score,",time used",t.get(),"ms")
		return coarsePos,coarse_score,results
		
	#精定位 
	def match_step3(self,coarsePos,mode,scale=1,doPenalize=True):
		t = counter.counter()
		laser = self.lastScan
		offset = offsetInfo.create(g_fine_search_offset*scale,g_fine_angle_offset*scale,mode=mode)
		if self.fineCache != self.cache:
			self.fineCache.addScan(laser,r=coarsePos[2],angle_offset=offset.offsetR,indexStep=1)
			if not self.locationMode:
				self.fineCache.setOffset(coarsePos[0],coarsePos[1],self.map,updateValidIndex=False)

		retPos,score,_ = self._matchScan(coarsePos,laser,offset=offset,step=1,angle_resolution=g_fine_angle_resolution,matchType=0,doPenalize=doPenalize)
		if score < g_min_score:
			log.warning(mode,": score is low",score,"seq:",laser.seq,",time used",t.get(),"ms")
			return None,0
		assert retPos is not None
		log.debug(mode,", seq:",laser.seq,",finePos:",pos_str(retPos),",score:",score,",time used",t.get(),"ms")
		self.finePos = retPos
		return retPos,score
	
	def setLastScan(self,scan):
		self.lastScan = scan
		
	#计算需要判断的激光数据 
	#laser为当前激光数据(其位置为预估位置)
	#referLasers为参考激光数据(位置已经校正过)
	#doRefineMatch:是否进行精定位 
	#search_offset粗查找x,y的查找范围(+-)
	#angle_offset粗查找角度的查找范围(+-)
	#doPenalize:是否考虑位姿偏差惩罚
	#返回base_link的位姿，分值和置信度   
	def match(self,laser,referLasers,offset,fastMatch=False,doPenalize=True,doCovariance=True):	
		if not referLasers and not self.locationMode:
			return None,-1,None
		t = counter.counter()
		self.lastScan = laser
		pos = laser.sensorPos
		
		if referLasers:
			self._updateRefMap(pos,referLasers)

		#快速粗定位 
		if fastMatch:
			pos,_ = self.match_step1(offset=offset,doPenalize=doPenalize)
			if pos is None:
				return None,0,None
				
		coarsePos,coarseScore,results = self.match_step2(pos=pos,offset=offset,doPenalize=doPenalize)
		if coarsePos is None:
			return None,0,None
		
		#精定位 
		retPos,score = self.match_step3(coarsePos=coarsePos,mode=offset.mode,doPenalize=doPenalize)
		if retPos is None:
			return None,0,None
		
		if self.locationMode:
			log.info(offset.mode,": match scan, seq:",laser.seq,", score:%0.2f"%score,", best pos:(%s)"%pos_str(retPos),", estimate pos:(%s)"%pos_str(laser.sensorPos)," using",t.get(),"ms")
			return retPos,score,None
		
		if not doCovariance:
			return retPos,score,None
			
		#计算协方差		
		M = self.computeCovariance(retPos,score,coarsePos,results,g_resolution,g_angle_resolution)
		log.info(offset.mode,": match scan, seq:",laser.seq,", score:%0.2f"%score,", best pos:(%s)"%pos_str(retPos),", estimate pos:(%s)"%pos_str(laser.sensorPos),"ref count:",len(referLasers),"variance(%0.6f,%0.6f)"%(M[0,0],M[1,1])," using",t.get(),"ms")
		return retPos,score,M
		
				
	#匹配激光 
	#laser：当前激光
	#search_offset：查找偏移量
	#search_angle_offset: 查找偏移角度
	#step：x,y步进
	#angle_resolution：角精度 
	#matchType:查找类型, 0：精查找，1为粗查找，2为快速粗查找
	def _matchScan(self,pos,laser,offset,step,angle_resolution,matchType,doPenalize):
		bestPos = None
		score = -1
		deltaX = round(offset.offsetX/self.resolution)
		deltaY = round(offset.offsetY/self.resolution)
		#建图时laser.sensorPos为地图中心点
		centerIndexX,centerIndexY = self.map.ptr2Index(pos[0],pos[1])	
		
		r = slam.slamUtil.normAngle(pos[2])
		results = []
		if matchType == 0:
			cache = self.fineCache
		else:
			cache = self.cache
		
		xranges = [(0,-deltaX-step,-step),] #左移
		xranges.append((step,deltaX+1,step)) #右移
		yranges = [(0,-deltaY-step,-step),] 	#上移
		yranges.append((step,deltaY+1,step)) #下移
		
		if self.locationMode:
			cache.setOffset(pos[0],pos[1],self.map,updateValidIndex=True,margin=self.map_margin)
			if self.worker_total > 1:
				assert 4 == self.worker_total or 2 == self.worker_total
				if 4 == self.worker_total:
					ix = self.worker_index % 2 
					iy = int(self.worker_index/2) 
					xranges = [xranges[ix],]
					yranges = [yranges[iy],]
				else:
					iy = int(self.worker_index%2) 
					yranges = [yranges[iy],]
		
		for x_range in xranges:
			last_score_x = 0
			for indexX in range(*x_range):
				maxYScore = 0
				for y_range in yranges:
					last_score_y = 0
					for indexY in range(*y_range):
						maxXYPos = self.matchAngle(cache=cache,centerIndexX=centerIndexX,centerIndexY=centerIndexY,indexX=indexX,indexY=indexY,r=r,search_angle_offset=offset.offsetR,angle_resolution=angle_resolution,scan=laser,doPenalize=doPenalize)
						if maxXYPos is None:
							if last_score_y != 0:
								break
							continue
						if matchType == 1:
							results.append(maxXYPos)
						maxXYScore = maxXYPos[3]
						if maxXYScore > score:
							bestPos = maxXYPos[0:3]
							score = maxXYScore
						if maxXYScore > last_score_y:
							last_score_y = maxXYScore
						elif maxXYScore < last_score_y - 0.2 and matchType != 0 and g_enable_fast_match:
							break
						maxYScore = max(maxYScore,last_score_y)
				if maxYScore > last_score_x:
					last_score_x = maxYScore
				elif maxYScore < last_score_x - 0.2 and matchType != 0 and g_enable_fast_match:
					break
		return bestPos,score,np.array(results)
		
		
	def matchAngle(self,cache,centerIndexX,centerIndexY,indexX,indexY,r,search_angle_offset,angle_resolution,scan,doPenalize=True):
		maxScore = 0	#x,y下的最大分值  
		maxPos = None
		for dr in np.arange(-search_angle_offset+r,search_angle_offset+angle_resolution+r-0.0001,angle_resolution): 
			m = cache.getMap(dr)
			if m is None:
				log.error("can't find angle cache",math.degrees(dr),"cache:",cache)
				#assert 0
				continue
			indexs = m.property["filter_points"]
			if len(indexs) == 0:
				continue
				
			#if self.locationMode and len(m.property["points"]) - len(indexs) > len(m.property["points"])*0.2:
			#	#20%的点超出地图范围，认为不可能  
			#	continue
				
			index_offset = np.array((indexX,indexY))
			indexs += index_offset - m.property["offset"]
			m.property["offset"] = index_offset
			
			s = self.matchIndexs(indexs,m.property["masks"])
			#里程计的偏差也要计算在内 
			#simple model (approximate Gaussian) to take odometry into account 
			if doPenalize:
				x,y = self.map.index2Ptr(indexX+centerIndexX,indexY+centerIndexY)
				s = penalize.calScore(scan.sensorPos,(x,y,m.property["r"]),s)
				
			if s > maxScore:
				#print(distancePenalty,anglePenalty,s)
				x,y = self.map.index2Ptr(indexX+centerIndexX,indexY+centerIndexY)
				maxScore = s
				maxPos = (x,y,m.property["r"],s)
		return maxPos	#返回 x,y,r,score 
	
	def matchIndexs(self,indexs,masks=None):
		assert len(indexs)
		if not self.enable_area_mask:
			pp = indexs.T
		else:
			ii = self.map.areaContainIndexs(indexs,"LocConfigArea")
			if len(ii):
				if masks is None:
					masks = np.ones(indexs.shape[0],dtype=bool)
				masks[ii] = 0
				pp = indexs[masks].T
				masks[ii] = 1
			else:
				pp = indexs.T
		ret = np.sum(self.map._grid[pp[1],pp[0]])
		ret = ret/pp.shape[1]/occupy_value
		if ret >= 1:
			return 1.0
		return ret 
		
		
	def draw(self):
		if self.map is None:
			log.error("no map, location=",self.locationMode)
			return
		if len(self.result_index):
			pp = self.result_index.T
			plt.scatter(pp[0],pp[1],marker=".",color="r",s=0.5)
		if self.fastCoarsePos is not None:
			ui.pltUtil.arrow(self.fastCoarsePos[0],self.fastCoarsePos[1],
					self.fastCoarsePos[2],width=1,head_width=0.2,color="red")
		if self.coarsePos is not None:
			ui.pltUtil.arrow(self.coarsePos[0],self.coarsePos[1],
					self.coarsePos[2],width=1,head_width=0.2,color="green")
		if self.finePos is not None:
			ui.pltUtil.arrow(self.finePos[0],self.finePos[1],
					self.finePos[2],width=1,head_width=0.2,color="blue")
		self.map.drawSlow()
		if self.lastScan:
			s = self.lastScan.clone()
			if self.finePos is not None:
				s.setSensorPos(*self.finePos)
			elif self.coarsePos is not None:
				s.setSensorPos(*self.coarsePos)
			s.draw()
			#pp = self.map.ptr2Indexs(s.locPoints).T
			#plt.scatter(pp[0],pp[1],marker=".",color="b")
		#x,y = self.map.ptr2Index(0,0)
		#plt.plot(x,y,"r+")
		
		self.reloc_draw()
	
	
	def show(self):
		self.draw()
		plt.show()
	
	
	#计算协方差矩阵 
	#results = [(x,y,r,score) ... ]
	def computeCovariance(self,bestPos,bestScore,searchCenter,results,resolution,angle_resolution):
		resolution = max(resolution,0.02)
		angle_resolution = max(angle_resolution,math.radians(2))
		
		M = np.identity(3) 
		if bestScore < ZERO_VALUE:
			M[0, 0] = MAX_VARIANCE
			M[1, 1] = MAX_VARIANCE
			M[2, 2] = 4 * angle_resolution*angle_resolution
			#assert lg.det(M) #行列式不能为0 
			return M
		if bestScore > 0.8:
			#高分没必要再算协议差了 
			M[0, 0] = M[1, 1] = 0.1*resolution*resolution
			M[2, 2] = angle_resolution*angle_resolution
			return M
		dx = bestPos[0]# - searchCenter[0]
		dy = bestPos[1]# - searchCenter[1]
		
		#response is not a low response 
		low_score = bestScore - 0.1 #min( bestScore - 0.1,0.6)
		data = results[results[:,3] > low_score].T 
		
		while data.shape[1] < 5:
			old = data.shape[1]
			low_score -= 0.1
			data = results[results[:,3] > low_score].T 
			log.warning("compute covariance: old=",old,",count=",data.shape[1])
		#else:
		#	log.debug("compute covariance: count=",data.shape[1])
		
		#data个数不能太少，太少产生的置信度g2o容易报错
		if len(data[0]) <= 1:
			M[0,0] = 0.1*resolution*resolution*(1.0 / bestScore)
			M[1,1] = 0.1*resolution*resolution*(1.0 / bestScore)
			M[2,2] = 4 * angle_resolution*angle_resolution
			return M
		sum_xx = np.sum(np.square(data[0] - bestPos[0])*data[3])
		sum_xy = np.sum((data[0] - bestPos[0])*(data[1] - bestPos[1])*data[3])
		sum_yy = np.sum(np.square(data[1] - bestPos[1])*data[3])
		sum_rr = np.sum(np.square(data[2] - bestPos[2])*data[3])
		sum_score = np.sum(data[3])
		
		#lower-bound variances so that they are not too small;
		#ensures that links are not too tight 
		min_variance = 0.1 * resolution * resolution
		
		#increase variance for poorer responses
		multiplier = 1.0 / bestScore
		#print(sum_xx,sum_xy,sum_yy,sum_rr,sum_score,"count=",len(data[3]),multiplier,bestScore)
		
		if sum_score > ZERO_VALUE:
			#lower-bound variances so that they are not too small
			variance_xx = max(sum_xx/sum_score,min_variance)*multiplier
			variance_xy = max(sum_xy/sum_score,min_variance)*multiplier#sum_xy/sum_score*multiplier
			variance_yy = max(sum_yy/sum_score,min_variance)*multiplier
			M[0,0] = variance_xx
			M[0,1] = variance_xy
			M[1,0] = variance_xy
			M[1,1] = variance_yy
		#if values are 0, set to MAX_VARIANCE
		#values might be 0 if points are too sparse and thus don't hit other points
		if abs(M[0,0]) < ZERO_VALUE:
			M[0,0] = MAX_VARIANCE
		if abs(M[1,1]) < ZERO_VALUE:
			M[0,0] = MAX_VARIANCE
			
		#计算角度协方差 
		if sum_score > ZERO_VALUE:
			if sum_rr < ZERO_VALUE:
				sum_rr = angle_resolution*angle_resolution
			sum_rr /= sum_score
		else:
			sum_rr = 1000 * angle_resolution*angle_resolution
		M[2,2] = sum_rr
		#if lg.det(M) == 0: #行列式不能为0 
		#	M[0,0] = 0.1 * resolution*resolution
		#	M[1,1] = 0.1 * resolution*resolution
		#	M[2,2] = angle_resolution*angle_resolution
		#	return M
		return M
		
	#打开rviz.map，配置成match_map的frameId
	def drawRos(self):
		return
		#m = self.map.toGrayMap()
		#for i in self.result_index:
		#	m.grid[i[1],i[0]] = 100
		#m.sendRos(frameId="match_map")
		
	def save(self,laser,referLasers,offset,fastMatch=False):	
		import json_codec
		import shutil
		log.warning("save scanMatcher data")
		shutil.rmtree("./matchData",ignore_errors=True)
		os.mkdir("./matchData")
		pp = {}
		pp["sensorPos"] = laser.sensorPos
		laser.save("matchData/scan.txt",pp)
		for i,r in enumerate(referLasers):
			pp = {}
			pp["sensorPos"] = r.sensorPos
			r.save("matchData/ref"+str(i)+".txt",pp)
		params = {}
		params["search_offset_x"] = offset.offsetX
		params["search_offset_y"] = offset.offsetY
		params["angle_offset_r"] = offset.angle
		params["mode"] = offset.mode
		params["fastMatch"] = fastMatch
		json_codec.dump_file("matchData/params.txt",params)

		
	def load(self,pathName="matchData",laserName="laser1"):
		import glob
		import json_codec
		log.warning("load scanMatcher data")
		params = json_codec.load_file(pathName+"/params.txt")
		x = params["search_offset_x"]
		y = params["search_offset_y"]
		r = params["angle_offset_r"] 
		m = params["mode"]
		del params["search_offset_x"]
		del params["search_offset_y"]
		del params["angle_offset_r"]
		del params["mode"]
		offset = offsetInfo.create(x,r,m)
		offset.offsetX = x
		offset.offsetY = y
		scan = slam.laser.laserInfo(laserName)
		pp = scan.load(pathName+"/scan.txt")
		scan.setSensorPos(*pp["sensorPos"])
		referLasers = []
		for f in glob.glob(pathName+"/ref*.txt"):
			s = slam.laser.laserInfo(laserName)
			pp = s.load(f)
			s.setSensorPos(*pp["sensorPos"])
			referLasers.append(s)
		params["fastMatch"] = bool(params["fastMatch"])
		return self.match(scan,referLasers,offset=offset,**params)
		
		
	def stop(self):
		self.isExited = True
			
			
	def onclick(self,event):
		if event.button == 3:
			#right mouse button
			plt.cla()
			self.draw()
			ui.pltUtil.redraw()
			return  
		if self.map is None:
			return
		x,y = event.xdata,event.ydata
		x,y = self.map.index2Ptr(x,y)
		max_dis = 2
		select = None
		for v in self.reloc_result:
			dis = slam.slamUtil.distance(v[0],v[1],x,y)
			if dis < max_dis:
				max_dis = dis
				select = v
				
		if select:
			self.lastScan.setSensorPos(select[0],select[1],select[2])
			map = self.map
			#显示重定位的地图点 
			#map = self.map.changeResolution(resolution=self.resolution*g_reloc_resolution_scale)
			#map.grid = np.where(map.grid < occupy_value,0,occupy_value)
			#kernel.update(map,sigma=map.resolution*2.5,indexs=None)
			#
			#x,y = map.ptr2Index(select[0],select[1])
			#
			#indexStep=round(self.lastScan.validCount/g_reloc_coarse_count)
			#pp = self.lastScan.locPoints[::indexStep]
			#pp = map.ptr2Indexs(pp)
			#plt.scatter(pp.T[0],pp.T[1])
			
			plt.text(x,y,"%0.2f"%select[3],color="red")
			print("reloc scan selected:",select)
			self.lastScan.draw(map)
			map.draw()
			ui.pltUtil.redraw()
		return  
		
	
############## unit test ##############
def testaddScan_single():
	sim = createSim(r"../robotSim/map/testmap2.json")
	sim.setPos(1,0,0)
	ll = []
	
	for i in range(10):
		sim.setPos(1.1,-0.1,math.pi/10*i)
		ll.append(sim.laserInfo)
		
	laser4 = sim.laserInfo
	
	good = (1.2,0,math.pi/2)
	sim.setPos(*good)		#real pose
	laser2 = sim.laserInfo.clone()
	laser3 = sim.laserInfo.clone()

	ptr = (1.1,0.1,math.pi/2-math.pi/10)			#wrong test pose
	laser3.setBaseLinkPos(*ptr)
	w = matcher(resolution=0.01)
	a,b,M = w.match(laser3,ll,offsetInfo.create(0.2,20,"test"))
	
	assert utility.near(a[0],laser2.sensorPos[0],0.02)
	assert utility.near(a[1],laser2.sensorPos[1],0.02)
	assert utility.near(a[2],laser2.sensorPos[2],0.02)
	if utility.is_ros():
		import time
		for i in range(100):
			w.drawRos()
			time.sleep(1)
			print("draw")
	#w.show()
	
def testcomputeCovariance():
	bestPos = (1,2,math.pi/5)
	bestScore = 0.8
	results = []
	w = matcher(resolution=0.01)
	results.append((1.1,2.1,math.pi/5,0.75))
	results.append((1.2,2.2,math.pi/5,0.76))
	results.append((0.1,2.3,math.pi/5,0.1 )) #low score
	results.append((0.9,2.3,math.pi/5,0.76))
	results.append((0.1,2.3,math.pi/5,0.1 ))#low score
	M = w.computeCovariance(bestPos,bestScore,bestPos,np.array(results),g_resolution,g_angle_resolution)
	#print(M)
	
	
def createSim(mapFile):
	if "../robotSim" not in sys.path:
		sys.path.append("../robotSim")
	if "../" not in sys.path:
		sys.path.append("../") 
	import robot,mapSim
	smap = mapSim.mapSim() 
	smap.load(mapFile)
	sim = robot.robotSim(smap)
	sim.setPos(0,0,0)
	sim.enable_error = True 
	return sim
	
	
def test_sim():
	sim = createSim(r"../robotSim/map/testmap2.json")
	sim.setPos(1,0,0)
	laser1 = sim.laserInfo
	
	sim.setPos(1.1,-0.1,0)
	laser4 = sim.laserInfo
	
	good = (1.2,0,0)
	sim.setPos(*good)		#real pose
	laser2 = sim.laserInfo.clone()
	laser3 = sim.laserInfo.clone()

	ptr = (1.1,0.1,math.pi/10)			#wrong test pose
	laser3.setBaseLinkPos(*ptr)
	
	w = matcher(resolution=0.01)
	a,b,M = w.match(laser=laser3,referLasers=[laser1,laser4],offset=offsetInfo.create(0.2,20,"test"))
	assert utility.near(a[0],laser2.sensorPos[0],0.01)
	assert utility.near(a[1],laser2.sensorPos[1],0.01)
	assert utility.near(a[2],laser2.sensorPos[2],0.01)
	#w.show()
	
	
#测试单次的match
def testmatch():
	w = matcher(resolution=0.01)
	scan1 = slam.laser.example_data1()
	scan1.seq = 10001
	scan1.setSensorPos(1,5,math.pi/6)
	
	scan2 = slam.laser.example_data1()
	scan2.seq = 10002
	scan2.setSensorPos(1.1,4.8,math.pi/5)
	a,b,M = w.match(laser=scan2,referLasers=[scan1,],offset=offsetInfo.create(0.2,20,"test"))
	assert utility.equal(a[0],scan1.sensorPos[0],0.001)
	assert utility.equal(a[1],scan1.sensorPos[1],0.001)
	assert utility.equal(a[2],scan1.sensorPos[2],0.5)
	assert b >= 0.95
	
	w.save(laser=scan2,referLasers=[scan1,],offset=offsetInfo.create(0.2,20,"test"))
	w2 = matcher(resolution=0.01)
	a,b,M = w2.load()
	assert utility.equal(a[0],scan1.sensorPos[0],0.001)
	assert utility.equal(a[1],scan1.sensorPos[1],0.001)
	assert utility.equal(a[2],scan1.sensorPos[2],0.5)
	assert b >= 0.95
	
	
#测试用matcher.save()保存的数据 
def testload_loopMatchData():
	w2 = matcher(resolution=0.01)
	ret = w2.load(pathName="loopMatchData",laserName="laser_oulei")
	#[INFO ] 2020-08-26 10:11:46.648: loopclose : match scan, seq: 384800 , score:0.42 , best pos:(-0.619,1.967,-1.426(-81.687)) , estimate pos:(-0.479,1.687,-1.358(-77.822)) ref count: 6 variance(0.003343,0.002514)  using 598 ms
	assert ret[1] > 0.4
	pos = (-0.619,1.967,-1.426)
	assert utility.equal(ret[0][0],pos[0],0.5)
	assert utility.equal(ret[0][1],pos[1],0.5)
	assert utility.equal(ret[0][2],pos[2],0.5)
	w2 = matcher(resolution=0.01)
	ret = w2.load(pathName="loopMatchData2",laserName="laser_oulei")
	#w2.show()
	#[INFO ] 2020-08-26 10:13:25.482: closeloop2 : match scan, seq: 6902 , score:0.78 , best pos:(0.254,-0.599,-0.309(-17.685)) , estimate pos:(-0.056,-0.969,-0.311(-17.821)) ref count: 8 variance(0.000513,0.001313)  using 250 ms
	assert ret[1] > 0.4
	pos = (0.254,-0.599,-0.309)
	assert utility.equal(ret[0][0],pos[0],0.05)
	assert utility.equal(ret[0][1],pos[1],0.05)
	assert utility.equal(ret[0][2],pos[2],0.5)
	#w2.show()
	
def testlocation_circle():
	import laserMgr
	def updateBaseLinkPos(preScan,scan):
		import random
		M = slam.matrix.createByPos(preScan.odomPos,preScan.basePos)
		pos = M.transform(scan.odomPos)
		pos2 = (pos[0],pos[1],slam.slamUtil.normAngle(pos[2]))
		#+random.random()*0.1-0.05 *0.1-0.05
		scan.setBaseLinkPos(*pos2)
	
	w2 = matcher(resolution=0.01,locationMode=True)
	ss = laserMgr.load("laser1/circle",laserName="laser1")
	w2.loadMap("test/circle.yaml")
	m = w2.map
	preScan = ss[0]
	
	for i,s in enumerate(ss):
		if i == 0:
			continue
		updateBaseLinkPos(preScan,s)
		s.seq = 1000+i
		pos,score = w2.localize(s,offset=offsetInfo.create(0.2,20,"test"))
		if score < 0.6:
			log.error(score,s.seq)
			w2.show()
		assert score > 0.6
		s.setSensorPos(*pos)
		preScan = s
	#test location wrong
	w2.localize(slam.laser.example_data1(),offset=offsetInfo.create(0.2,20,"test"))
	
	
def testlocation_5floor():
	import laserMgr
	def updateBaseLinkPos(preScan,scan):
		import random
		M = slam.matrix.createByPos(preScan.odomPos,preScan.basePos)
		pos = M.transform(scan.odomPos)
		pos2 = (pos[0],pos[1],slam.slamUtil.normAngle(pos[2]))
		#+random.random()*0.1-0.05 *0.1-0.05
		scan.setBaseLinkPos(*pos2)
	
	w2 = matcher(resolution=0.01,locationMode=True)
	
	m = slam.gridMap.load("test/5floor.yaml")
	m.trim() 
	ss = laserMgr.load("laser_oulei/round",laserName="laser_oulei")
	w2.setMap(m)
	m = w2.map
		
	#test single scan
	#s = ss[69]
	#s.setSensorPos(2.0135525500632303, 26.5041623789595, 2.8678015194336886)
	#pos,score = w2.localize(s,offset=offsetInfo.create(1,40,"test"),fastMatch=False)
	#s.setSensorPos(*pos)
	#s.draw(w2.map)
	#w2.show()
	#assert 0 #TODO
	
	preScan = ss[0]
	for i,s in enumerate(ss):
		if i == 0:
			continue
		updateBaseLinkPos(preScan,s)
		s.seq = 1000+i
		offset = offsetInfo.create(0.2,10,"test")
		if i == 1:
			offset.offsetX = 0.4
			offset.offsetY = 0.4
			pos,score = w2.localize(s,offset=offset,fastMatch=False)
		elif s.seq == 1069:
			offset.offsetX = 0.4
			offset.offsetY = 0.4
			pos,score = w2.localize(s,offset=offset,fastMatch=False)
		else:
			pos,score = w2.localize(s,offset=offset)
		#pos,score = w2.localize(s,offset=0.4)
		if score < 0.6:
			log.error(score,s.seq,s.sensorPos)
			#s.draw(w2.map)
			w2.show()
		assert score > 0.6
		s.setSensorPos(*pos)
		preScan = s
	#test location wrong
	w2.localize(slam.laser.example_data1(),offsetInfo.create(0.2,10,"test"))
	

def test_reloc_small():
	import laserMgr
	w2 = matcher(resolution=0.01,locationMode=True)
	m = slam.gridMap.load("test/circle.yaml")
	m.trim() 
	ss = laserMgr.load("laser1/circle",laserName="laser1")
	w2.setMap(m)
	m = w2.map
	
	#测试单个定位 
	#s = ss[30]
	## seq= 9238 ,score= 0.964 ,pos= 0.548,-3.491,-2.269(-130.00) 
	#pos,score = w2.reloc(s)
	#if score >0:
	#	s.setSensorPos(*pos[0:3])	
	##plt.plot(*m.ptr2Index(s.odomPos[0],s.odomPos[1]),"r+")
	#m.draw()
	#s.draw(m)
	#plt.show()
	
	for i in range(0,len(ss),10):
		s = ss[i]
		s.seq = 1000+i
		pos,score = w2.reloc(s)
		if score <= 0.8:
			print(s.seq,pos,score)
		assert score > 0.8 
	#test wrong scan 
	pos,score =w2.reloc(slam.laser.example_data1())
	assert score == 0
	 
def test_reloc_5floor():
	import laserMgr
	w2 = matcher(resolution=0.01,locationMode=True)
	m = slam.gridMap.load("test/5floor.yaml")
	m.trim() 
	ss = laserMgr.load("laser_oulei/round",laserName="laser_oulei")
	w2.setMap(m)
	m = w2.map
	
	#s = ss[80]
	#pos,score = w2.reloc(s)
	#if score >0:
	#	s.setSensorPos(*pos[0:3])	
	#s.draw(m)
	#w2.show()
	#plt.show()
	
	#test wrong scan 
	pos,score =w2.reloc(slam.laser.example_data1())
	assert score == 0
	
	#s = ss[10]
	#pos,score = w2.reloc(s)
	#if score >0:
	#	s.setSensorPos(*pos[0:3])	
	#else:
	#	s.setBaseLinkPos(*s.odomPos)	
	#m.draw()
	#s.draw(m)
	#plt.show()
	#
	for i in range(0,len(ss),10):
		s = ss[i]
		s.seq = 1000+i
		if i == 50:
			continue
		pos,score = w2.reloc(s)
		assert score > 0.7
		if score >0:
			s.setSensorPos(*pos[0:3])	
	#	m.draw()
	#	s.draw(m)
	#	plt.pause(0.1)
	#plt.show()
	
def test_wanji_5floor():
	import laserMgr
	w2 = matcher(resolution=0.01,locationMode=True)
	m = slam.gridMap.load("test/5floorfull.yaml")
	ss = laserMgr.load("laser_oulei/wall",laserName="laser_oulei")
	w2.setMap(m)
	m = w2.map
	ret = w2.reloc(ss[0])
	assert ret[0] is None
	#if ret[0]:
	#	ss[0].setSensorPos(*ret[0])
	#	ss[0].draw(w2.map,isColor=True)
	#w2.show()
	
def testbig_reloc():
	global g_laser_sigma,g_reloc_min_coarse_score
	g_laser_sigma = 0.1

	sim = createSim(r"./test/bigmap.yaml")
	goodPos = (166,22,math.pi/2) 
#	goodPos = (137,43,math.pi/2)
	sim.setPos(*goodPos)
	sim.enable_error = False
	s  = sim.laserInfo

	w = matcher(resolution=sim.map.resolution,locationMode=True)
	w.loadMap(r"./test/bigmap.yaml")
	m = w.map
	p = (goodPos[0]-20,goodPos[1]+8,goodPos[2])
	s.setSensorPos(*p)
	 
	pos,score = w.reloc(s,goodPos,offsetInfo.create(60,180,"test"))
	print(pos,score)
	#s.setSensorPos(*pos)
	#s.draw(m)
	#m.show()
	
	assert pos is not None
	assert utility.near(goodPos[0],pos[0],0.1)
	assert utility.near(goodPos[1],pos[1],1)
	assert utility.near(goodPos[2],pos[2],0.1)
	assert score > 0.8
	
	goodPos = (137,43,math.pi/2)
	sim.setPos(*goodPos)
	s  = sim.laserInfo
	p = (goodPos[0]-20,goodPos[1]+8,goodPos[2])
	s.setSensorPos(*p)
	
	pos,score = w.reloc(s,goodPos,offsetInfo.create(60,180,"test"))
	print(pos,score)
	assert pos is not None
	assert utility.near(goodPos[0],pos[0],0.1)
	assert utility.near(goodPos[1],pos[1],1)
	assert utility.near(goodPos[2],pos[2],0.1)
	assert score > 0.8
	 
	 
def testlocation2():
	import laserMgr
	w2 = matcher(resolution=0.01,locationMode=True)
	w2.loadMap("laser1/diniu4/active.yaml")

	#m = slam.gridMap.load("laser1/diniu4/active.yaml")
	#m.trim() 
	#m.skeleton() #TODO 
	ss = laserMgr.load("laser1/diniu4",laserName="laser1")
	#w2.setMap(m)
	m = w2.map
	
	s = ss[385]
	s.setSensorPos(-5.191,-2.861,0.280)
	pos,score = w2.localize(s,offsetInfo.default(),fastMatch=False)
	w2.show()
	
#[INFO ] 2020-11-13 10:28:25.455: default : match scan, seq: 1385 , score:0.64 , best pos:(-5.191,-2.861,0.280(16.04)) , estimate pos:(-5.431,-2.778,0.053(3.04))  using 201 ms
	



if __name__ == '__main__':  
	import utility
	import os,sys
	testlocation2()
	assert 0
	if utility.is_ros():
		import ros2.rosUtility
		ros2.rosUtility.init("testslam")
	utility.run_tests()
	
