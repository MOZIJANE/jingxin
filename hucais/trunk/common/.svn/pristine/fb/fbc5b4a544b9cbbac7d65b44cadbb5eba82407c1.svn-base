# coding=utf-8
# ycat			2021-03-27	  create
# 跟踪接口 
import sys,os
import glob
import struct
import math
import time,datetime
import matplotlib.pyplot as plt
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__) 
import utility
import buffer
import enhance
import json_codec as json
import ui.pltUtil
import ui.pltTool
import log
import counter

#解析器，格式类型
#def decoder(buf)
g_decoders = {}

def addDecoder(type,func):
	global g_decoders
	g_decoders[type.__name__] = func
	
# mapDecoder(key,value)
mapDecoder = None

# alarmDecoder("key.instance")
alarmDecoder = None

def _toDatetime(v):
	return datetime.datetime.fromtimestamp(v)

class reader:
	def __init__(self):
		self.clear()
		#filter 
		self.starttime = None
		self.endtime   = None
		self.filter_alarms = None
		self.filter_events = None
		self.filter_keys = None
		self.filter_objs = None
		
		self.dataChanged = enhance.event()	#回调事件 dataChanged()
		self.selectChanged = enhance.event()	#回调事件 selectChanged(index)
		self.isInitEvent = False
		
		
	@property
	def count(self):
		return len(self.data)
	
	def clear(self):
		self.default_map = None #默认地图 
		self.maps = []	#当前地图 [(map,date),,,]
		self.data = []
		self.keys = set()	#数据key值集合 
		self.events = set()	#事件key值集合 
		self.alarms = set() #告警集合 
		self.objs = set()	#对象集合
		self.meta = {}
		self.axes = []		#画图生成的轴 
		self.timespan = datetime.timedelta(seconds=300)		#显示的时间跨度 
		self.currentTime = None	#当前坐标轴开始时间 
		self.selectIndex  = None #当前选择的索引 
		
	@property
	def map(self):
		if not self.maps:
			return self.default_map 
		t = self.selectTime
		if t is None:
			if len(self.data):
				t = self.data[0][1]
		if t is None:
			return self.default_map 
		for m in self.maps: 
			if t >= m[1]:
				return m[0]
		return self.default_map
		
	def getStat(self):
		s = {}
		s["values"] = sum(1 for _ in self.getIter(None,0))
		s["events"] = sum(1 for _ in self.getIter(None,1))
		s["alarms"] = sum(1 for _ in self.getIter(None,2))
		s["objects"] = len(self.objs)
		for o in self.objs:
			s[o] = 0
			
		for d in self.data:
			if d[3] != 3:
				continue 
			s[d[0]]+=1
		
		if self.minTime is not None and self.maxTime is not None :
			s["range"] = "[%s ~ %s]"%(utility.date2str(self.minTime),utility.date2str(self.maxTime))
		return s
		
	def load(self,dir_or_file):
		c = counter.counter()
		if os.path.isdir(dir_or_file):
			pp = glob.glob(os.path.join(dir_or_file,"*.data"))
			if not pp:
				log.info("load trace failed: can't find *.data in",dir_or_file)
				return 
			for f in pp:
				self._loadOne(f)
		else:
			self._loadOne(dir_or_file)
		self._update()
		log.info("load trace:",dir_or_file,", result=",self.getStat(),",used",c.get(),"ms")
		
	#取配置字典
	def getConf(self):
		if "_config" in self.meta:
			return self.meta["_config"]
		return {}
	 
		
	def _loadOne(self,filename):
		log.debug("trace load:",filename)
		f = open(filename,"rb")
		while self._readData(f):
			pass
		f.close()
		#self.data = self.data[1899895+40000:1899895+60000] #TODO
	
	
	#保存selectIndex上下count数据
	def saveByTimeRange(self,filename,minTime,maxTime): 
		m1 = 0
		if minTime is not None:
			for i in range(self.selectIndex,-1,-1):
				if self.data[i][1] < minTime:
					m1 = i
					break
				
		m2 = len(self.data)
		if maxTime is not None:
			for i in range(0,len(self.data)):
				if self.data[i][1] > maxTime:
					m2 = i
					break
		return self.saveByRange(filename,m1,m2)
	
	def saveByRange(self,filename,index1,index2):
		m1 = index1
		m2 = index2 
		if index2 == -1:
			index2 = len(self.data)
		import traceWriter
		c = counter.counter()
		t = traceWriter.writer()
		t.meta = utility.clone(self.meta)
		
		if self.map:
			t._mapId = self.map.mapId
			t._map = json.dump(self.map).encode("utf8")
			t._currentFileWriteMap = False 
		t.addConf(self.getConf())
		
		for i in range(index1,index2):
			d = self.data[i]
			#返回值： key, 时间, 值, 类型(int), 类型字串(f|i|d|e|a|c|o|l),数据索引
			if d[3] == 0:
				t.add(d[0],d[2],d[1].timestamp())
			elif d[3] == 1:
				t.addEvent(d[0],d[2],d[1].timestamp())
			elif d[3] == 2:
				if d[4] == "a":
					t.addAlarm(d[0],d[2],d[1].timestamp())
				else:
					t.clearAlarm(d[0],d[2],d[1].timestamp())
			elif d[3] == 3:
				if isinstance(d[2],bytes):
					d[2] = self._decodeObj(d[0],d[2])
					if d[2] is None:
						continue
					_,d[0] = d[0].split("@")
				t.addObj(d[0],d[2],d[1].timestamp())
			elif d[3] == 4:
				t.addLog(d[0],d[2],d[1].timestamp())
		if os.path.exists(filename):
			os.remove(filename)
		t.save(filename)
		log.info("traceReader save at",self.selectIndex,"from",index1,"to",index2)
				
		
	def getObjsIter(self,decode=True):
		for i,d in enumerate(self.data):
			if d[3] != 3:
				continue 
			t = d[1]
			if self.starttime is not None and t < self.starttime:
				continue
			if self.endtime is not None and t > self.endtime:
				continue	
			obj = d[2]
			if self.filter_objs and d[0] not in self.filter_objs:
				continue
			if decode and isinstance(d[2],bytes):
				d[2] = self._decodeObj(d[0],d[2])
			yield d[0],t,d[2],d[3],d[4],i
	
	
	#返回迭代器
	#keys可以是单个值，或者列表 
	#type=-1代表取出所有类型 
	#return: key,datetime,value,type
	
	#type取值： 0: value, 1: event, 2: alarm, 3: object, 4: log 
	#返回值： key, 时间, 值, 类型(int), 类型字串(f|i|d|e|a|c|o|l),数据索引
	def getIter(self,keys,type = -1):
		for i,d in enumerate(self.data):
			if type!=-1 and d[3] != type:
				continue
			if keys is not None and d[0] != keys and d[0] not in keys:
				continue
			if self.filter_keys is not None and d[3] == 0:
				if d[0] not in self.filter_keys:
					continue
			if self.filter_events is not None and d[3] == 1:
				if d[0] not in self.filter_events:
					continue
			if self.filter_alarms is not None and d[3] == 2:
				if d[0] not in self.filter_alarms:
					continue 
			t = d[1]
			#if self.starttime is not None:
			#	print(t,t < self.starttime ,t > self.endtime)
			if self.starttime is not None and t < self.starttime:
				continue
			if self.endtime is not None and t > self.endtime:
				continue
			yield d[0],t,d[2],d[3],d[4],i
			
	@property
	def minTime(self):
		if len(self.data):	
			return self.data[0][1]
		return None
		
	@property
	def maxTime(self):
		if len(self.data):	
			return self.data[-1][1]
		return None
		
	#def _onselect(self,xmin,xmax):
	#	if xmin == xmax:
	#		return
	#	if xmax == 1:
	#		return
	#	if xmin == 1:
	#		return
	#	self.starttime =  ui.pltUtil.num2date(xmin)
	#	self.endtime   =  ui.pltUtil.num2date(xmax)  
	#	self.redraw()
	#	for ax in self.axes:
	#		ax.set_xlim(xmin,xmax)
	#	if self.onselect is not None:
	#		self.onselect(xmin,xmax)
			
	def home(self):
		self.clearRange()
		self.timespan = datetime.timedelta(seconds=300)		#显示的时间跨度 
		self.currentTime = None	#当前时间 
		self.redraw()
		if self.onselect is not None:
			self.onselect(None,None)
		
	def _onclickHome(self,*params):
		self.home()
		
	def _onmousedown(self,event):
		if ui.pltTool.activeTools():
			return
		t = ui.pltUtil.num2date(event.xdata)
		self.selectByTime(t)
			
	#def _onmousemove(self,event):
	#	try:
	#		t = ui.pltUtil.num2date(event.xdata)
	#		for ax in self.axes:
	#			ax.current_label.set_text(str(t))
	#			ax.current_label.set_position((event.xdata,event.ydata))
	#			ax.current_line.set_xdata(event.xdata)
	#		plt.gcf().canvas.draw_idle()
	#	except:
	#		pass
	
	def selectByTime(self,dt):
		if self.count == 0:
			return -1
		# 二分查找 
		def binSearch(lists, left, right, x):
			if right >= left:
				mid = (left + (right - left) // 2)
				if mid >= len(lists):
					return len(lists) -1
				if lists[mid][1] == x:
					return mid
				elif lists[mid][1] > x:
					return binSearch(lists, left, mid - 1, x)
				else:
					return binSearch(lists, mid + 1, right, x)
			else:
				return left
				#r = lists[right]
				#l = lists[left]
				#if abs((r[1]-x).total_seconds()) < abs((l[1]-x).total_seconds()):
 				#	return right
				#return left
		index = binSearch(self.data,0,self.count,dt)
		self.setSelect(index)
		return index
	
	@property
	def selectTime(self):
		if self.selectIndex is None:
			return None
		if self.selectIndex < 0:
			return None
		if self.selectIndex >= self.count:
			return None
		return self.data[self.selectIndex][1]
		
	def setSelect(self,index):
		if self.selectIndex == index:
			return
		self.selectIndex = index
		self.selectChanged.emit(index)
		
		if index < 0:
			return
		if index >= self.count:
			return
		dt = self.data[index][1]
		for ax in self.axes:
			if not hasattr(ax,"current_label"):
				continue
			if not hasattr(ax,"current_line"):
				continue
			ax.current_label.set_text(str(dt))
			ax.current_label.set_position((dt,ax.get_ylim()[1]))
			ax.current_line.set_xdata(dt) 
		plt.gcf().canvas.draw()

		
	def draw(self):
		self._showValue()
		self._showEvent()
		self._showAlarm()
		#for ax in self.axes:
		#	ui.pltUtil.onselect(ax,self._onselect,keepSelect=True) 
		
		if not self.isInitEvent:
			ui.pltTool.onclick("home",self._onclickHome)
			self.isInitEvent = True
			ui.pltUtil.mouseDown(plt.gcf(),self._onmousedown)
			#ui.pltUtil.mouseMove(plt.gcf(),self._onmousemove)	
		
	def redraw(self):
		self.draw()
		ui.pltUtil.redraw() 
		
	def _getMeta(self,key):
		if key in self.meta:
			return self.meta[key]
		return None
		
	def _showOneValue(self,ax,key):
		import matplotlib.dates as mdates
		import matplotlib.ticker as ticker
		
		if self.count == 0:
			return
	
		xx = []
		yy = []
		for d in self.getIter(key,0):
			xx.append(d[1])
			yy.append(d[2])
		ax.set_ylabel(key)
		
		start = self.currentTime 
		end = None
		if start is None:
			start = self.minTime
			end   = self.maxTime
			if self.starttime:
				start = self.starttime
			if self.endtime:
				end   = self.endtime
		else:
			end = self.currentTime+self.timespan
		ax.set_xlim(start,end)
		ax.xaxis.set_major_formatter(ticker.FuncFormatter(mdates.DateFormatter('%H:%M:%S')))#时间格式 
#		ax.xaxis.set_major_locator(mdates.MinuteLocator(range(0,60,5)))						#5分钟显示刻度
			
		m = self._getMeta(key)
		if m:
			ax.set_ylim((m["min"],m["max"]))
		
		if len(xx) == 0:
			return   
		ax.plot(xx,yy,"o",linestyle=":")
		ax.current_label = plt.text(0,0,str(""),fontsize = 10) 
		ax.current_line = ax.axvline(x=xx[0], color='blue')
		 
	def _showValue(self):
		keys = self.filter_keys
		if not keys:
			return 
		
		plt.clf()
		#if len(keys) != len(self.axes):
		if len(keys) == 1:
			self.axes = [plt.gcf().gca(),]
		else:
			self.axes = plt.gcf().subplots(nrows=len(keys),sharex = True)
				
		for i,k in enumerate(keys):
			self.axes[i].clear()		
			self._showOneValue(self.axes[i],k)	
		
		plt.gcf().autofmt_xdate()  # 自动旋转日期标记
		
		#画选择画段 
		dt = self.selectTime
		if dt is None:
			return 
		for ax in self.axes:
			ax.current_label.set_text(str(dt))
			ax.current_label.set_position((dt,ax.get_ylim()[1]))
			ax.current_line.set_xdata(dt)

			
		
	def _showEvent(self): 
		ee = self.filter_events
		if not ee:
			return
			ee = self.events
			
		for e in self.getIter(ee,1):
			if e[4] == "l": #日志类型不显示 
				continue
			for ax in self.axes:
				ax.axvline(x=e[1],color="b")#nn[e[0]]) 
				ax.text(e[1], ax.get_ylim()[1], e[0])
			
	def _showAlarm(self):
		aa = {}
		ee = self.filter_alarms
		if not ee:
			return 
			
		for a in self.getIter(ee,2):
			if alarmDecoder:
				alarm = alarmDecoder(a[0])
			else:
				alarm = a[0]
			if a[4] == "a":
				for ax in self.axes:
					ax.axvline(x=a[1],color="r")
					ax.text(a[1], ax.get_ylim()[1], alarm)
				#aa[a[0]] = a[1]
			else:
				for ax in self.axes:
					ax.axvline(x=a[1],color="g")
					ax.text(a[1], ax.get_ylim()[1], "c."+alarm)
				#if a[0] in aa:
				#	start = aa[a[0]]
				#	end = a[1]
				#	for ax in self.axes:
				#		ax.axvspan(start,end, facecolor="red", alpha=0.5)
						
	
	def show(self):
		self.draw()
		plt.show()

	########### 设置过滤器 ###########
	def clearFilter(self):
		self.clearRange()
		self.filter_objs = None
		self.filter_alarms = None
		self.filter_events = None
		self.filter_keys =   None
		
		
	def clearRange(self):
		self.starttime = None
		self.endtime = None
		
	def setRange(self,starttime,endtime):
		self.starttime = starttime
		self.endtime   = endtime
		
	def setAlarmFilter(self,alarms):
		self.filter_alarms = alarms
		
	def setEventFilter(self,events):
		self.filter_events = events
		
	def setKeyFilter(self,keys):
		if keys is None:
			self.filter_keys = self.keys
			return
		if isinstance(keys,(list,tuple)):
			self.filter_keys = keys
		else:
			assert isinstance(keys,str)
			self.filter_keys = [keys,]
		
	#这个设置的是type类型列表 
	def setObjFilter(self,keys):
		if keys is None:
			self.filter_objs = self.keys
			return
		if isinstance(keys,(list,tuple)):
			self.filter_objs = keys
		else:
			self.filter_objs = [keys,]
	
		
	def __str__(self):
		#for ss in self.data:
		#	print(_toDatetime(ss[1]).microsecond)
		#	print(utility.str_datetime(_toDatetime(ss[1]),True),ss[0],"=",ss[2])
		return ""
			
	def _readData(self,f):
		def findHead():
			b = f.read(1)
			if len(b) == 0:
				return -1
			if b != b'\xAA':
				return 0
				
			b = f.read(1)
			if len(b) == 0:
				return -1
			if b != b'\xBB':
				return 0
				
			b = f.read(1)
			if len(b) == 0:
				return -1
			if b != b'\xCC':
				return 0
				
			b = f.read(1)
			if len(b) == 0:
				return -1
			if b != b'\xDD':
				return 0
			return 1
			
		r = findHead() 
		if r == -1:
			return False
		if r == 0:
			return True
	
		bb = f.read(4)
		if not bb:
			return False
		offset = struct.unpack("I",bb)[0]
		bb = f.read(offset)
		if bb[0] != ord('@') or bb[1] != ord('@'):
			log.error("wrong trace format,len=%d,wrong head:"%offset+str(bb[0:100]))
			return True
			#raise Exception("wrong trace format,wrong head:"+str(bb))
		t = chr(bb[2]) 
		if t == "m":
			self.meta.update(json.load(bb.decode("utf8")[4:]))
			return True
		#format : "@@d:time:key@@value" 
		if t != "o":
			try:
				ss = bb.decode("utf8")
			except Exception as e:
				print(e)
				return True
		else:
			indexVal = -1
			for i in range(2,len(bb) - 1):
				if bb[i] == ord('@') and bb[i+1] == ord('@'):
					indexVal = i
					break
			if indexVal == -1:
				raise Exception("wrong trace format,wrong spliter:"+str(ss))
			ss = bb[0:indexVal+2].decode("utf8")  #取出 @@d:time:key

		index = ss.find(":",4)
		dt = float(ss[4:index]) 
		keyIndex = ss.find("@@",index+1)
		key = ss[index+1:keyIndex]
		value = ss[keyIndex+2:]
		
		if t == "f" or t == "i":	#数据:浮点或整形  
			value = float(value) 
			self.data.append((key,_toDatetime(dt),value,0,t))
		elif t == "d":				#数据:字典
			value = json.load(value)
			for k in value:
				self.data.append((key+"."+k,_toDatetime(dt),value[k],0,t))
		elif t == "e": 				#事件 
			value = json.load(value)
			self.data.append((key,_toDatetime(dt),value,1,t))	
		elif t == "a" or t == "c": #告警或清除 
			value = json.load(value)
			self.data.append((key,_toDatetime(dt),value,2,t))
		elif t == "o":	#object对象 
			value = bb[indexVal+2:] 
			if value is not None:
				#key = key.replace("@",".")
				self.data.append([key,_toDatetime(dt),value,3,t])
		elif t == "l": 	#日志类型 
			value = json.load(value)
			self.data.append((key,_toDatetime(dt),value,4,t))
		elif t == "r": #地图raw
			if mapDecoder:
				if dt == 0 and self.default_map is not None: 
					log.info("traceReader: skip map:",key)
					return True #map的元数据，已经读过了 
				c = counter.counter()
				map = mapDecoder(key,value)
				if dt != 0:
					dt = _toDatetime(dt)
					self.maps.append((map,dt))
				else:
					dt = ""
					self.default_map = map
				log.info("traceReader: load map:",key,dt,",used",c.get(),"ms")
			else:
				log.error("traceReader: can't find mapDecoder")
		else:
			raise Exception("wrong trace format,unknow type=%s"%t)
		return True
		
		
	def _update(self):
		self.data.sort(key=lambda x:x[1])
		if self.maps:
			self.maps.sort(key=lambda x:x[1],reverse=True)
		self.keys.clear()
		for a in self.data:
			if a[3] == 0:
				if a[0] not in self.keys:
					self.keys.add(a[0])
			elif a[3] == 1:
				if a[0] not in self.events:
					self.events.add(a[0])
			elif a[3] == 2:
				if a[0] not in self.alarms:
					self.alarms.add(a[0])
			elif a[3] == 3:
				self.objs.add(a[0])
		self.filter_alarms = None 
		self.filter_events = None 
		self.filter_keys   = None 
		self.dataChanged.emit()
	
	def _decodeObj(self,key,data):
		try:
			global g_decoders
			type,key = key.split("@")
			if type == "dict":
				return json.load(data.decode("utf8"))
			if type not in g_decoders:
				raise Exception("can't find decoder for " + type)
			return g_decoders[type](data)
		except Exception as e:
			log.exception("traceReader:decode error:"+key,e) #wrong decoder version 
			return None

##################### Unit Test #############################	
def test_trace(): 
	import traceWriter
	traceWriter.test_trace()
	
def testbig():
	import traceReader
	import slam.smap
	import config 
	import slam.laser
	global mapDecoder
	mapDecoder = slam.smap.mapInfo.loadStr
	r = traceReader.reader()
	r.load("test/big.data")
	r.setSelect(1899895)
	r.save("test/big_snap.data",20000)
	r2 = traceReader.reader()
	r2.load("test/big_snap.data")
	r2.show()
	
	
if __name__ == '__main__':
	testbig()
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
