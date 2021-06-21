#coding=utf-8
# ycat			2017-10-20	  create
# AGV的控制 
import sys,os 
import json
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import utility
import enhance	
import threading
import time
import log
import re
import lock
import json_codec
import driver.agv.hdcAgvApi as api
g_threads =[]
g_carts = None
g_point = None
g_lock = threading.RLock()
locationEvent = enhance.event()
api.locationEvent.connect(locationEvent.emit)

@utility.init()
def init():
	if utility.is_test():
		return
	api.init()
	time.sleep(3)

def wait():
	global g_threads
	for t in g_threads:
		t.join()
	g_threads.clear()
	
@utility.fini()
def fini():
	if utility.is_test():
		return
	api.fini()
	wait()

g_stockLock = {}

def getStockA(loc):
	if loc[0:6] != "stockA":
			return None
	m = re.search("stockA_row(\d+)_col(\d+).*",loc)
	if m is None:
		return None
	row = int(m.group(1))
	col = int(m.group(2))
	if row is None:
		return
	if row%2 != 1:
		row -= 1
	return row*1000+col
	
@lock.lock(g_lock)	
def checkTimeout(index,agvId,loc):
	global g_stockLock
	if index in g_stockLock:
		if utility.ticks() - g_stockLock[index] > 10*60*1000:
			unlockStockA(agvId,loc)
			log.warning("delete timeout locked",index)
			
	
#解决在StockA两个车头对撞的问题 
def lockStockA(agvId,loc):
	global g_stockLock
	index = getStockA(loc)
	if index is None:
		return
	if index in g_stockLock:
		checkTimeout(index,agvId,loc)
		log.warning(agvId,loc,"is locked, wait for unlock")
		for i in range(60*5):
			if index not in g_stockLock:
				break
			time.sleep(1)
		log.info(agvId,loc,"wait for unlock success")
	global g_lock
	log.debug(agvId,"lock",loc,index)
	g_lock.acquire()
	g_stockLock[index] = utility.ticks()
	g_lock.release()

@lock.lock(g_lock)	
def unlockStockA(agvId,loc):
	global g_stockLock
	index = getStockA(loc)
	if index in g_stockLock:
		log.debug(agvId,"unlock",loc,index)
		del g_stockLock[index]

@lock.lock(g_lock)
def getPoint(originPoint):
	global g_point
	loadPoint()
	if g_point[originPoint] is not None:
		return g_point[originPoint]

	return originPoint


@lock.lock(g_lock)
def getOriginPoint(point):
	global g_point
	loadPoint()
	for itemIndex in g_point:
		if g_point[itemIndex] == point:
			return itemIndex
	return point

@lock.lock(g_lock)
def loadPoint():
	global g_point
	filePath = os.path.dirname(__file__)
	fileName = "point.cfg"
	if filePath:
		fileName = filePath + "/" + fileName
	g_point = json_codec.load_file(fileName)


@lock.lock(g_lock)	
def checkCart(cartId,scanId):
	scanId = scanId.strip()
	def loadCart():
		global g_carts
		p = os.path.dirname(__file__)
		pp = "cart.cfg"
		if p:
			pp = p+"/"+pp 
		g_carts = json_codec.load_file(pp)
		
	def saveCart():
		global g_carts
		p = os.path.dirname(__file__)
		pp = "cart.cfg"
		if p:
			pp = p+"/"+pp 
		json_codec.dump_file(pp,g_carts)
		
	def findCart(scanId):
		global g_carts
		for c in g_carts:
			if g_carts[c] == scanId:
				return c
		return "unknown"
		
	global g_carts
	if g_carts is None:
		loadCart()
	if cartId in g_carts:
		if scanId != g_carts[cartId]:
			log.error("货架ID不正确，期望货架:"+cartId+", 实际货架:"+findCart(scanId))
			raise Exception("货架ID不正确，期望货架:"+cartId+", 实际货架:"+findCart(scanId))
	else:
		g_carts[cartId] = scanId
		saveCart()
	
#finishCallback参数： finishCallback(obj)
#obj会自动带上下面三个参数 
#obj["agv"] = agvId
#obj["result"] = 0
#obj["resultDesc"] = "success"
	
def _run(func,args,callback,obj):
	def threadFunc(func,args,callback,obj):
		hasCallback = False
		try:
			func(*args)
			if utility.is_exited():
				return
			hasCallback = True
			callback(obj)
		except Exception as e:
			obj["result"] = -1
			obj["resultDesc"] = str(e)
			log.exception("agvCtrl:",e)
			if "agv" in obj:
				agvId= obj["agv"]
				log.debug("小车："+agvId+"，出现未经处理的异常，正在返航 ")
				restAgv(agvId)
				freeAgv(agvId)
			if not hasCallback:
				callback(obj)
	t = threading.Thread(target=threadFunc,args=(func,args,callback,obj))
	global g_threads
	t.start()
	g_threads.append(t)
	
def _initObj(obj,agvId):
	obj["agv"] = agvId
	obj["result"] = 0
	obj["resultDesc"] = "success"
	
def _call(agvId,locId):
	if api.isCartLoc(locId):
		api.move(agvId,locId+".1")
		lockStockA(agvId,locId)
		try:
			api.mission(agvId,1) #旋转——》钻入货架——》扫码——》返回货架id号码  
		except Exception as e:
			unlockStockA(agvId,locId)
			raise e
	else:
		api.move(agvId,locId)

def apply(locId):
	locId=getOriginPoint(locId)

	return api.apply(locId+'.1')
	
def call(agvId,locId,finishCallback,obj):
	_initObj(obj,agvId)
	locId=getOriginPoint(locId)
	try:

		_run(func=_call,args=(agvId,locId),callback=finishCallback,obj=obj)
	except Exception as e:
		restAgv(agvId)
		freeAgv(agvId)
		raise e
	return agvId
	 
def _moveCart(agvId,srcLoc,locId,cartId):
	try:
		c = api.mission(agvId,2) #顶升任务，这个也会返回货架ID  
		if c:
			checkCart(cartId,c)
		api.move(agvId,srcLoc+".2") 
	except Exception as e:
		#TODO:ycat api.move(agvId,srcLoc+".2")
		#TODO:ycat raise e
		pass
	finally:
		unlockStockA(agvId,srcLoc)
	
	loc,type = api.getMissionType("get","",srcLoc)
	api.mission(agvId,type) #3随动使小车和货架向右随动,4随动使小车和货架向左随动
	
	loc,type = api.getMissionType("put",srcLoc,locId)
	api.move(agvId,loc+".3")
	api.mission(agvId,type) #3随动使小车和货架向右随动,4随动使小车和货架向左随动
	lockStockA(agvId,locId)
	try:
		api.move(agvId,locId+".4")
		api.mission(agvId,5) #放下货架 
		api.move(agvId,locId+".5") #返航 
	finally:
		unlockStockA(agvId,locId)
	freeAgv(agvId)
	 
#带货架运输 
def moveCart(agvId,cartId,srcLoc,locId,finishCallback,obj):	 
	_initObj(obj,agvId)
	assert api.isCartLoc(cartId)
	#移动货架前，一定是locked状态 
	#assert api.isLocked(agvId)
	srcLoc = getOriginPoint(srcLoc)
	locId = getOriginPoint(locId)
	try:
		_run(func=_moveCart,args=(agvId,srcLoc,locId,cartId),callback=finishCallback,obj=obj)  
	except Exception as e:
		restAgv(agvId)
		freeAgv(agvId)
		raise e
			 
			
#不带货架运输 
def move(agvId,locId,finishCallback,obj):
	_initObj(obj,agvId)		
	#移动前，一定是locked状态 
	#assert api.isLocked(agvId)
	try:
		locId=getOriginPoint(locId)
		_run(func=api.move,args=(agvId,locId),callback=finishCallback,obj=obj)  
	except Exception as e:
		freeAgv(agvId)
		raise e
	
#释放对agv的占用 
def freeAgv(agvId): 
	try:
		api.unlock(agvId)
	except Exception as e:
		log.exception("freeAgv",e)
	
#回归转盘
def restAgv(agvId):
	agvId2 = api.getAgvId(agvId)
	api.reset(agvId2)


def Init():
	import interface.dashboard.dashboardApi
	locationEvent.connect(interface.dashboard.dashboardApi.reportAgvLoc)
	time.sleep(3)
################# unit test ################# 
def testgetPoint():
	resulta= getPoint("StockA_row7_col4")
	assert resulta== "begin_1"
	resultb= getPoint("StockA_row8_col4")
	assert resultb == "begin_2"


def testgetOrginPoint():
	resulta= getOriginPoint("begin_1")
	assert resulta== "StockA_row7_col4"
	resultb= getOriginPoint("begin_2")
	assert 	resultb == "StockA_row8_col4"
	resultc = getOriginPoint("hhahahaa")

	assert resultc == "hhahahaa"


def testgetStockA():
	assert getStockA("stockA_row10_col3") == 9003
	assert getStockA("stockA_row10_col4") == 9004
	assert getStockA("stockA_row1_col1") == 1001
	assert getStockA("stockA_row2_col2") == 1002
	assert getStockA("stockA_row3_col2") == 3002
	assert getStockA("stockA_row4_col2") == 3002
	assert getStockA("stockA_row4_col2.1") == 3002
	assert getStockA("stockB_row4_col2.1") == None
	assert getStockA("begin_1") == None
	assert getStockA("seat_1") == None

def testcheckCart():
	global g_carts
	g_carts = None
	checkCart("CART9001","591")
	checkCart("CART9002","592")
	gg = json_codec.load_file("cart.cfg")
	assert "CART9001" in gg
	assert "CART9002" in gg
	assert gg["CART9001"] == "591"
	assert gg["CART9002"] == "592"
	checkCart("CART9002","592")
	checkCart("CART9001","591")
	try:
		checkCart("CART9002","591")
		assert 0
	except Exception as e:
		s = str(e)
		assert s.find("货架ID不正确，期望货架:CART9002, 实际货架:CART9001") != -1
		
import counter
@counter.count
def move_cart(cartId,srcLoc,destLoc,agvId=None):
	print(cartId,srcLoc,destLoc)
	counter.setPrint(True)
	def callback1(obj):
		if obj["result"] == -1: 
			print("error, system exit")
			obj["finish"] = True
			sys.exit(-1) 
		else:
			log.warning(obj["agv"],"start move from",obj["loc1"],"to",obj["loc2"]) 
			moveCart(obj["agv"],obj["cart"],obj["loc1"],obj["loc2"],callback2,obj)
	
	def callback2(obj):
		if obj["result"] == -1: 
			print("error, system exit")
			obj["finish"] = True
			sys.exit(-1) 
		else:
			log.warning(obj["agv"],"arrived",obj["loc2"])
		obj["finish"] = True
			
	obj = {}
	obj["loc1"] = srcLoc
	obj["loc2"] = destLoc
	obj["cart"] = cartId
	print("call ",srcLoc)
	if agvId is None:
		agvId = apply(srcLoc)

	call(agvId,srcLoc,callback1,obj)
	while not utility.is_exited():
		if "finish" in obj:
			break
		time.sleep(0.2)
	print("------ move ",srcLoc," to ",destLoc," finish ------")
	
	
#def func1(start,stock1,stock2):
#	print("-------------------- start thread ------------------------")
#	time.sleep(1) 
#	cartId = "CART9009"
#	move_cart(cartId,start,stock1)
#	next = stock1
#	for s in seats:
#		move_cart(cartId,next,"seat"+str(s)+"_1")
#		if next == stock1:
#			next = stock2
#		else:
#			next = stock1
#		move_cart(cartId,"seat"+str(s)+"_1",next)
#		# move_cart(cartId, s, next)
#	print("=======================================")
#	print("finish func1")
#	print("=======================================")

def func2(stock1,stock2):
	print("-------------------- start thread ------------------------",stock1,stock2)
	time.sleep(1) 
	cartId = "CART9009"
	for i in range(20):
		print("current loop is - ",i.__str__())
		move_cart(cartId,stock1,stock2)
		move_cart(cartId,stock2,stock1) 
		print("current loop end - ",i.__str__())
	print("=======================================")
	print("finish func2")
	print("=======================================")	

def func3(times,starts,seats):
	current=starts
	cartId = "CART9009"
	time.sleep(1)
	for loop in range(0,times-1):
		# current=starts
		tip1="currentLoop is "+loop.__str__()+" currentStart is "+current
		print(tip1)
		for i in range(0,len(seats)):
			next = str(seats[i])
			tip2= "currentLoop is "+loop.__str__()+"currentOrigin is "+ current	+ "currentNext is " + next +" seatIndex is "+i.__str__()
			print(tip2)
			print("excuting")
			move_cart(cartId,current,next)
			current = next
def testPageAgvControl(jsonstr):
	jsonData = json.loads(jsonstr)
	result = False
	if len(jsonData)==0:
		result=False
	else:
		for currentJson in jsonData:
			start = currentJson["start"]
			seat = currentJson["seat"]
			loop=int(currentJson["loop"])
			seats = str.split(seat, ',')
			durabilityTestTask1 = threading.Thread(target=func3, args=[loop, start, seats])
			durabilityTestTask1.start()
		result=True

	return result

def testtestPageAgvControl(jsonstr):
	jsonData = json.loads(jsonstr)
	result = False
	if len(jsonData) == 0:
		result = False
	else:
		for currentJson in jsonData:
			start = currentJson["start"]
			print(start)
			time.sleep(3)
			seat = currentJson["seat"]
			seats = str.split(seat, ',')
			print(seat)
			time.sleep(3)
			for	currentseat in seats:
				print(currentseat)
				time.sleep(3)
			time.sleep(10)
		result = True

	return result

def testPageUnloockAll():
	api.unlockAll();

def testProcess(jsonData):
	utility.start()
	testPageAgvControl(jsonData)
	utility.finish()



def test1():
	Init()
	
	durabilityTestTask1= threading.Thread(target=func3,args=[20,"stockA_row1_col3",["stockA_row1_col2","stockA_row1_col4"]])
	durabilityTestTask1.start()

	durabilityTestTask2= threading.Thread(target=func3,args=[20,"stockA_row1_col2",["seat2_1","stockA_row4_col2"]])
	# durabilityTestTask2.start()

	durabilityTestTask3= threading.Thread(target=func3,args=[20,"stockA_row5_col3",["seat16_1","stockA_row5_col2"]])
	# durabilityTestTask3.start()

	durabilityTestTask4= threading.Thread(target=func3,args=[20,"stockA_row6_col3",["seat12_1","stockA_row6_col2"]])
	# durabilityTestTask4.start()

	durabilityTestTask1.join()

	
	#t1.join()	
	print("===============ALL FINISH ========================")




if __name__ == '__main__':
	# utility.run_tests()
	if sys.argv is not None and len(sys.argv)>0:
		if "process" in sys.argv:
			log.info("run at testPage mode")
			args=""
			with open('/agvscada/driver/args.txt', 'r', encoding='utf-8') as f:
				args=f.read()
			api.init()
			time.sleep(3)
			testPageAgvControl(args)
		elif "unlock" in sys.argv:
			testPageUnloockAll()
		elif "test" in sys.argv:
			utility.start()
			test1()
			utility.finish()



	else:
		utility.start()
		testgetPoint()
		utility.finish()
	# test3()
	
	
	
	
