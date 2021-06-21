#coding=utf-8 
# ycat   2018/5/13	  create
# Web取时间控件的对应后台 
import sys,os 
import setup
import utility  
import webutility 
import datetime
import math,uuid
import log
	
def _parseTime(timeStr):
	return datetime.datetime.strptime(timeStr.split(".")[0],'%Y-%m-%dT%H:%M:%S')
	
#时间范围的回传参数 
#dateRangeType: date
#dateRangeStart: 2018-06-19T00:00:00.000Z
#dateRangeEnd: 2018-06-19T23:59:59.999Z
	
#最近时间的回传参数
#dateRangeRecent：以秒为单位的最近时间
#dateRangeRequestId: 增量请求的ID 
 
#取过滤时间的条件 
#datetimeField：数据库的时间字段名
def getFilter(datetimeField,filter={}):
	if not datetimeField:
		return filter
	
	if getIncreaseFilter(datetimeField,filter):
		return filter
	
	s,e = getTimeRange()
	if not s:
		return filter 
	#时间条件不能再出现在filter，否则会冲突 
	assert datetimeField not in filter
	filter[datetimeField] = {"$gte": s,"$lt":e}
	return filter

	
def getType():
	return webutility.get_param("dateRangeType")
	
def getGroupOp(datetimeField):
	if datetimeField[0] != "$":
		datetimeField = "$" + datetimeField
	dateType = getType()
	assert dateType
	if dateType == "date": #天为间隔
		return {"$hour":datetimeField}
	elif dateType == "week":
		return {"$dayOfWeek":datetimeField}
	elif dateType == "month":
		return {"$dayOfMonth":datetimeField}
	elif dateType == "year":
		return {"$month":datetimeField}
	elif dateType == "dates": #自定义 
		#return "$dayOfYear"
		return {"$dateToString": {"format": "%Y-%m-%d", "date": datetimeField}}
	else:
		print("unknow dateRangeType "+dateType)
		assert 0
		
def getEmptyData(noGroup=False):
	s,e = getTimeRange()
	dateType = getType()
	if dateType is None:
		return getTimeRecentEmpty()
	
	if noGroup:
		diff = e-s
		d = getNoGroupDiff()
		return [None]*(int(diff.total_seconds()/d)+1)
		
		
	if dateType == "date": #天为间隔
		return [None]*24
	elif dateType == "week":
		return [None]*7
	elif dateType == "month":
		return [None]*((e - s).days)
	elif dateType == "year":
		return [None]*12
	elif dateType == "dates": #自定义 
		days = int((e - s).days) + 1 
		return [None]*days
	else:
		print("unknow dateRangeType "+dateType)
		assert 0
		

def getNoGroupDiff():
	dateType = getType()
	if dateType == "date":
		return 60
	elif dateType == "week":
		return 60*60
	elif dateType == "month":
		return 60*60
	elif dateType == "year":
		return 24*3600
	elif dateType == "dates": #自定义 
		return 24*3600
			
		
#noGroup:是否进行分组 
def getAxisData(noGroup=False): 
	s,e = getTimeRange()
	dateType = getType()
	if dateType is None:
		return getTimeRecentAxisData()
		
	if noGroup:
		i = s 
		d = datetime.timedelta(seconds=getNoGroupDiff())
		r = []
		while i<=e:
			r.append(str(i))
			i += d 
		assert len(r) == len(getEmptyData(noGroup))
		return r
		
	if dateType == "date": #天为间隔
		return [ i for i in range(0,24) ]
	elif dateType == "week":
		return ["周一","周二","周三","周四","周五","周六","周日"]
	elif dateType == "month":
		return [ i for i in range(1,(e - s).days+1) ]
	elif dateType == "year":
		return ["1月","2月","3月","4月","5月","6月","7月","8月","9月","10月","11月","12月"]
	elif dateType == "dates": #自定义 
		i = s.date()
		ee = e.date()
		oneday = datetime.timedelta(days=1)
		r = []
		while i<=ee:
			r.append(str(i))
			i += oneday
		assert len(r) == len(getEmptyData())
		return r
	else:
		print("unknow dateRangeType "+dateType)
		assert 0
		return r
	
def getTimeRange():
	#根据类型取结束时间 
	startTime = webutility.get_param("dateRangeStart")
	if startTime is None:
		#实时图表的时间范围 
		return getTimeRecentRange()
	startTime = _parseTime(startTime)
	dateType = getType()
	date = startTime.date()
	assert dateType
	if dateType == "date": #天为间隔 
		d = date + datetime.timedelta(days=1)
		return (datetime.datetime(date.year,date.month,date.day,0,0,0),datetime.datetime(d.year,d.month,d.day,0,0,0))
	elif dateType == "week":
		d = date + datetime.timedelta(days=8)
		return (datetime.datetime(date.year,date.month,date.day,0,0,0),datetime.datetime(d.year,d.month,d.day,0,0,0))
	elif dateType == "month":
		m = date.month + 1
		y = date.year
		if m > 12:
			m = 1
			y += 1
		return (datetime.datetime(date.year,date.month,date.day,0,0,0),datetime.datetime(y,m,date.day,0,0,0))
	elif dateType == "year":
		return (datetime.datetime(date.year,date.month,date.day,0,0,0),datetime.datetime(startTime.year+1,startTime.month,startTime.day,0,0,0))
	elif dateType == "dates": #自定义 
		endTime = webutility.get_param("dateRangeEnd")
		return (startTime,_parseTime(endTime))
	else:
		print("unknow dateRangeType "+dateType)
		assert 0
		
def getIndex(dtValue,xData,noGroup=False):
	dateType = getType()
	if dateType is None:
		return getTimeRecentIndex(dtValue,xData)
	if noGroup:	
		diff = getNoGroupDiff()
		startTime = _parseTime(webutility.get_param("dateRangeStart"))
		return int((dtValue - startTime).total_seconds()/diff)
	if dateType == "dates":
		d = datetime.datetime.strptime(dtValue,'%Y-%m-%d').date()
		startTime = _parseTime(webutility.get_param("dateRangeStart"))
		return (d - startTime.date()).days
	elif dateType == "week":
		return ["周一","周二","周三","周四","周五","周六","周日"].index(dtValue)
	elif dateType == "month":
		assert isinstance(dtValue,int)
		return dtValue - 1
	elif dateType == "year":
		assert isinstance(dtValue,int)
		return dtValue - 1
	else:
		assert isinstance(dtValue,int)
		return dtValue
	
##### 实现实时图表 #####
def getTimeRecentIndex(dtValue,xData):
	seconds = webutility.get_param("dateRangeLastSec")
	if seconds is None:
		return -1
	assert xData is not None
	#n = datetime.datetime(dtValue.year,dtValue.month,dtValue.day,dtValue.hour,dtValue.minute,dtValue.second)
	index = int((dtValue - xData[0]).total_seconds())
	if index < len(xData):
		return index
	return -1
			
def getTimeRecentEmpty():
	r = getTimeRecentRange()
	if r is None:
		assert 0 
	return [None]*int((r[1] - r[0]).total_seconds()) 
 
def getTimeRecentAxisData():
	r = getTimeRecentRange()
	if r is None:
		return None
	s = datetime.timedelta(seconds=1)
	start = r[0]
	if r[0] > r[1]:
		log.error(r[0],r[1],"wrong time logical")
		assert 0 
	x = []  
	while start < r[1]:
		x.append(start)
		start += s
	return x
		
def getRefreshSec(refreshSec):
	seconds = webutility.get_param("dateRangeLastSec")
	if seconds is None:
		return refreshSec
	seconds = int(seconds)
	if seconds <= 60:
		return max(refreshSec,8)
	if seconds <= 300:
		return max(refreshSec,15)
	if seconds <= 3600:
		return max(refreshSec,120)
	return max(refreshSec,600)

#dateRangeRequestId: 增量请求的ID 
g_lastRequestSet = {}

def getIncreaseFilter(datetimeField,filter):
	r = getTimeRecentRange()
	if r[0] is None:
		return False 
	#时间条件不能再出现在filter，否则会冲突 
	assert datetimeField not in filter 
	filter[datetimeField] = {"$gte": r[0],"$lt":r[1]} 
	return True
	
def isIncrease():
	if webutility.get_param("dateRangeRequestId"):
		return True
	else:
		return False 
		
		
#判断这个series之前是否出现过，没出现过则不显示 
def hasSeries(name):
	global g_lastRequestSet
	requestId = webutility.get_param("dateRangeRequestId") 
	if not requestId:
		return True
	if requestId not in g_lastRequestSet:
		return True
	ss = g_lastRequestSet[requestId][1]
	if not ss:
		#为空也不判断 
		return True
	return name in ss
	

#设置上次查询的时间，同时删除过期的数据 	
def setRequestId(series):
	requestId = webutility.get_param("dateRangeRequestId") 
	if not requestId:
		requestId = str(uuid.uuid1())
	global g_lastRequestSet
	now = utility.now()
	if requestId in g_lastRequestSet and g_lastRequestSet[requestId][1]:
		#旧的留下，这个serie会固定 
		g_lastRequestSet[requestId] = (now,g_lastRequestSet[requestId][1])
	else:
		g_lastRequestSet[requestId] = (now,series)
		
	if len(g_lastRequestSet) < 5000:
		return requestId
	#删除一天后的数据 
	d = utility.now() - datetime.timedelta(days=1)
	remove = []
	for g in g_lastRequestSet:
		if g_lastRequestSet[g][0] < d:
			remove.append(g)
	for g in remove:
		del g_lastRequestSet[g]
	return requestId
		
		
def getTimeRecentRange(): 
	now = utility.now()
	now = datetime.datetime(now.year,now.month,now.day,now.hour,now.minute,now.second) #去掉毫秒 
	seconds = webutility.get_param("dateRangeLastSec")
	if seconds is None:
		return None,None
	seconds = int(seconds) 
	requestId = webutility.get_param("dateRangeRequestId") 
	if requestId is None or requestId not in g_lastRequestSet: 
		return (now - datetime.timedelta(seconds=seconds),now)   
	#max解决刷新频率大于整体时间范围的情况 
	s =  min(int((now -g_lastRequestSet[requestId][0]).total_seconds()),seconds)
	return (now - datetime.timedelta(seconds=s),now)   
		 
		
################### unit test 	###################
def testgetIncreaseFilter():
	n = datetime.datetime(2018,6,19,23,59,59)
	n2 = datetime.datetime(2018,6,19,23,54,59)
	utility.set_now(n)
	filter = {}
	webutility.set_test_param("dateRangeLastSec","300") 
	getIncreaseFilter("ycat",filter)
	assert filter["ycat"] == {"$gte": n2,"$lt":n}
	
	#request不存在 
	filter = {}
	webutility.set_test_param("dateRangeLastSec","300")
	webutility.set_test_param("dateRangeRequestId","10086")
	getIncreaseFilter("ycat",filter)
	assert filter["ycat"] == {"$gte": n2,"$lt":n}
	setRequestId([])
	
	#request存在 
	filter = {}
	utility.set_now(n + datetime.timedelta(seconds=60))
	webutility.set_test_param("dateRangeRequestId","10086")
	getIncreaseFilter("ycat",filter)
	assert filter["ycat"] == {"$gte": n,"$lt":n+ datetime.timedelta(seconds=60)}
	setRequestId([])
	
	#间隔很大
	filter = {}
	utility.set_now(n + datetime.timedelta(seconds=600))
	getIncreaseFilter("ycat",filter)
	assert filter["ycat"] == {"$gte": n+ datetime.timedelta(seconds=300),"$lt":n+ datetime.timedelta(seconds=600)}
	n = n + datetime.timedelta(seconds=600)
	setRequestId("10081")
	utility.set_now(n + datetime.timedelta(seconds=100))
	filter = {}
	getIncreaseFilter("ycat",filter)
	assert filter["ycat"] == {"$gte": n,"$lt":n+ datetime.timedelta(seconds=100)}
	#test del timeout 
	for i in range(10000):
		webutility.set_test_param("dateRangeRequestId","10081" + str(i))
		setRequestId([])
		 
	global g_lastRequestSet
	utility.set_now(n + datetime.timedelta(hours=25))
	webutility.set_test_param("dateRangeRequestId","51000")
	setRequestId([])
	assert "51000" in g_lastRequestSet
	assert len(g_lastRequestSet) == 1
	utility.set_now(None)
	
def testgetTimeRecentAxisData():
	n = datetime.datetime(2018,6,19,23,59,59) 
	utility.set_now(n)
	n2 = n - datetime.timedelta(seconds=300)
	n = n - datetime.timedelta(seconds=1)
	
	webutility.set_test_param("dateRangeLastSec","300")
	webutility.set_test_param("dateRangeRequestId","")
	r = getTimeRecentAxisData()
	assert len(r) == 300 
	assert r[0] == n2 
	assert r[299] == n 
	utility.set_now(None)
	
def testgetTimeRecentRange():
	n = datetime.datetime(2018,6,19,23,59,59)
	n2 = datetime.datetime(2018,6,19,23,54,59)
	utility.set_now(n)
	webutility.set_test_param("dateRangeLastSec","300")
	assert getTimeRecentRange() == (n2,n)
	utility.set_now(None)
	
#部份单元测试在dbQuery.query.py里
def testgetMatch():
	a = _parseTime("2018-06-19T00:00:00.000Z")
	b = _parseTime("2018-06-19T23:59:59.999Z")
	assert a == datetime.datetime(2018,6,19,0,0,0)
	assert b == datetime.datetime(2018,6,19,23,59,59)

def testgetindex():
	webutility.g_test_param.clear()
	webutility.set_test_param("dateRangeStart","2017-12-29T00:00:00.000Z")
	webutility.set_test_param("dateRangeEnd","2018-01-27T23:59:59.000Z")
	webutility.set_test_param("dateRangeType","dates")
	assert getIndex("2017-12-29",[]) == 0
	assert getIndex("2017-12-30",[]) == 1
	assert getIndex("2017-12-31",[]) == 2
	assert getIndex("2018-01-27",[]) == 29

def testgetTimeRange():
	webutility.set_test_param("dateRangeStart","2018-06-19T23:59:59.999Z")
	webutility.set_test_param("dateRangeEnd","2018-06-27T23:59:49.999Z")
	webutility.set_test_param("dateRangeType","dates")
	assert datetime.datetime(2018,6,27,23,59,49) == getTimeRange()[1]
	assert datetime.datetime(2018,6,19,23,59,59) == getTimeRange()[0]
	
	webutility.set_test_param("dateRangeType","date")
	assert datetime.datetime(2018,6,20,0,0,0) == getTimeRange()[1]
	assert datetime.datetime(2018,6,19,0,0,0) == getTimeRange()[0]
	
	webutility.set_test_param("dateRangeType","week")
	assert datetime.datetime(2018,6,27,0,0,0) == getTimeRange()[1]
	assert datetime.datetime(2018,6,19,0,0,0) == getTimeRange()[0]
	
	webutility.set_test_param("dateRangeType","month")
	assert datetime.datetime(2018,7,19,0,0,0) == getTimeRange()[1]
	assert datetime.datetime(2018,6,19,0,0,0) == getTimeRange()[0]
	
	webutility.set_test_param("dateRangeStart","2018-12-22T23:59:59.999Z")
	assert datetime.datetime(2019,1,22,0,0,0)== getTimeRange()[1]
	assert datetime.datetime(2018,12,22,0,0,0) == getTimeRange()[0]
	
	webutility.set_test_param("dateRangeType","year")
	assert datetime.datetime(2019,12,22,0,0,0)== getTimeRange()[1]
	assert datetime.datetime(2018,12,22,0,0,0)== getTimeRange()[0]
	
	
def testgetEmptyData():
	#dateRangeType: date
#dateRangeStart: 2018-06-19T00:00:00.000Z
#dateRangeEnd: 2018-06-19T23:59:59.999Z
	webutility.set_test_param("dateRangeStart","2018-06-19T23:59:59.999Z")
	webutility.set_test_param("dateRangeEnd","2018-06-20T23:59:59.999Z")
	webutility.set_test_param("dateRangeType","date")
	assert 24 == len(getEmptyData())
	webutility.set_test_param("dateRangeType","dates")
	assert 2 == len(getEmptyData())
	assert getAxisData() == ["2018-06-19","2018-06-20"]
	webutility.set_test_param("dateRangeStart","2018-06-20T10:59:59.999Z")
	webutility.set_test_param("dateRangeEnd","2018-06-20T23:59:59.999Z")
	assert 1 == len(getEmptyData())
	assert getAxisData() == ["2018-06-20"]
	webutility.set_test_param("dateRangeType","month")
	webutility.set_test_param("dateRangeStart","2018-02-01T10:59:59.999Z")
	webutility.set_test_param("dateRangeEnd","2018-02-30T23:59:59.999Z")
	assert 28 == len(getEmptyData())
	webutility.set_test_param("dateRangeType","month")
	webutility.set_test_param("dateRangeStart","2018-06-01T10:59:59.999Z")
	webutility.set_test_param("dateRangeEnd","2018-07-30T23:59:59.999Z")
	assert 30 == len(getEmptyData())
	
if __name__ == '__main__':
	utility.run_tests() 
	
	
	
def _getKey(year,value):
	return year*1000+value

def getDayOfYear(d):
	s = datetime.datetime(d.year,1,1)
	e = datetime.datetime(d.year,d.month,d.day)
	i = 1
	oneday = datetime.timedelta(days=1)
	while s < e:
		s += oneday
		i+=1
	return i

#返回XAxis的值和groupId的操作符 
def getGroup(datetimeField):
	startTime = webutility.get_param("dateRangeStart")
	endTime = webutility.get_param("dateRangeEnd")
	dateType = webutility.get_param("dateRangeType")
	if startTime is None:
		return 
	assert endTime
	assert dateType
	
	s = _parseTime(startTime)
	e = _parseTime(endTime)
	r = {}
	groupOp = ""
	begin = 0
	if dateType == "date": #天为间隔
		k = "$hour"
		begin = 0
		for i in range(24):
			r[_getKey(s.year,i)] = 0
	elif dateType == "week":
		k = "$dayOfWeek"
		for i in range(7):
			r[_getKey(s.year,i+1)] = 0
	elif dateType == "month":
		k = "$dayOfMonth"
		for i in range(31):
			r[_getKey(s.year,i+1)] = 0
	elif dateType == "year":
		ll = 12
		k = "$month"
		for i in range(12):
			r[_getKey(s.year,i+1)] = 0
	elif dateType == "dates": #自定义 
		#"dateStr": {"$dateToString": {"format": "@type@", "date": "$productTime"}}, 
		ll = 12
		k = "$dayOfYear"
		begin = 1
		i = utility.clone(s)
		oneday = datetime.timedelta(days=1)
		while i<e:
			r[_getKey(i.year,getDayOfYear(i))] = 0
			i += oneday
	else:
		assert 0
	#elif dateType == "年月":
	#	ll = 12
	#	k = "$month"
	#	a = s.month
	#	i = datetime.datetime(s.year,s.month,1)
	#	while i<e:
	#		r[_getKey(i.year,i.month)] = 0
	#		i = datetime.datetime(s.year+int(a/12),int(a%12)+1,1)
	#		a += 1
	rr= sorted(r.items(), key=lambda d:d[0], reverse = False)
	return r,{"_id":{"year":{"$year":datetimeField},"datetime":{k:datetimeField}}} 

	
class sta_count:
	def GET(self):
		data = web.input()
		m = get_match(data,"_id.apmac",[data.mac],"_id.dt")
		r,k = get_data(data)
		g = {"$group": {"_id":{"year":{"$year":"$_id.dt"},"dt":{k:"$_id.dt"}},"value": { "$sum": "$value.result"}}} 
		ds = mongodb.aggregate("r_sta_count",[m,g])
		while ds.next():
			r[_getKey(ds["_id"]["year"],ds["_id"]["dt"])] = ds["value"]
		sta= sorted(r.items(), key=lambda d:d[0], reverse = False)
		return json.dumps([x[1] for x in sta])
	
class sta_count_day:
	def GET(self):
		data = web.input()
		s = datetime.datetime.strptime(data.start,'%Y-%m-%d')
		e = datetime.datetime.strptime(data.end,'%Y-%m-%d')
		a = data.mac
		m = {"$match":{"$and":[{"apmac":a},{"startime" : {"$gte": s }},{ "startime" : {"$lt": e}}]}}
		if web.ctx.session.roleid == webmgr_obj_globals.g_admin:
			m = {"$match":{"$and":[{"domainid" : web.ctx.session.domainid},{"apmac":a},{"startime" : {"$gte": s }},{ "startime" : {"$lt": e}}]}}
		elif web.ctx.session.roleid == webmgr_obj_globals.g_user:
			m = {"$match":{"$and":[{"domainid" : web.ctx.session.domainid},{"accountid" : web.ctx.session.accountid},{"apmac":a},{"startime" : {"$gte": s }},{ "startime" : {"$lt": e}}]}}
		r,k = get_data(data)
		g = {"$group": {"_id":{"year":{"$year":"$startime"},"dt":{k:"$startime"}},
			"value": { "$sum": 1}}}
		ds = mongodb.aggregate("r_sta_running",[m,g])
		while ds.next():
			r[_getKey(ds["_id"]["year"],ds["_id"]["dt"])] = ds["value"]
		
		ds = mongodb.aggregate("r_sta_connection",[m,g])
		while ds.next():
			if _getKey(ds["_id"]["year"],ds["_id"]["dt"]) in r.keys():
				r[_getKey(ds["_id"]["year"],ds["_id"]["dt"])] += ds["value"]
			else:
				r[_getKey(ds["_id"]["year"],ds["_id"]["dt"])] = ds["value"]
		
		return json.dumps([x for x in r.values()])
	
class ap_traffic:
	def GET(self):
		data = web.input() 
		m = get_match(data,"devid",[data.devid],"statime")
		r1,k = get_data(data)
		r2 = utility.clone(r1)
		g = {"$group": {"_id":{"year":{"$year":"$statime"},"dt":{k:"$statime"}},
			"up": { "$sum": "$txbytes"},
			"down": { "$sum": "$rxbytes"}}}
		ds = mongodb.aggregate("r_ssid_stat",[m,g])
			
		aa = []	
		while ds.next():
			r1[_getKey(ds["_id"]["year"],ds["_id"]["dt"])] = ds["up"]
			r2[_getKey(ds["_id"]["year"],ds["_id"]["dt"])] = ds["down"]
		up= sorted(r1.items(), key=lambda d:d[0], reverse = False)
		down= sorted(r2.items(), key=lambda d:d[0], reverse = False)
		return json.dumps({"up":["%0.1f"%(x[1]/1024/1024) for x in up],"down":["%0.1f"%(x[1]/1024/1024) for x in down]})
	
class ap_traffic_day:
	def GET(self):
		data = web.input()
		s = datetime.datetime.strptime(data.start,'%Y-%m-%d')
		e = datetime.datetime.strptime(data.end,'%Y-%m-%d')
		d = data.devid
		
		m = {"$match":{"$and":[{"devid":d},{"statime" : {"$gte": s }},{ "statime" : {"$lt": e}}]}}
		r1,k = get_data(data)
		r2 = utility.clone(r1)
		g = {"$group": {"_id":{"year":{"$year":"$statime"},"dt":{k:"$statime"}},
			"up": { "$sum": "$txbytes"},
			"down": { "$sum": "$rxbytes"}}}
		ds = mongodb.aggregate("r_ssid_stat",[m,g])
			
		while ds.next():
			r1[_getKey(ds["_id"]["year"],ds["_id"]["dt"])] = ds["up"]
			r2[_getKey(ds["_id"]["year"],ds["_id"]["dt"])] = ds["down"]
		return json.dumps({"up":["%0.1f"%(x/1024/1024) for x in r1.values()],"down":["%0.1f"%(x/1024/1024) for x in r2.values()]})
	
class ap_app:
	def GET(self):
		data = web.input()
		m1 = get_match(data,"apmac",[data.mac],"timestamp")
		u = {"$unwind":"$app"}
		m2 = {"$match":{"app" : {"$ne":None}}}
		g1 = {"$group":{"_id":"$app","value":{'$sum': 1}}}
		ds = mongodb.aggregate("r_sta_logs",[m1,u,m2,g1,{"$sort":{"value":-1}}, {"$limit" : 10 }])
		d = {}
		while ds.next():
			d[ds["_id"]] = {"_id":ds["_id"],"value":ds["value"]}
		return json.dumps(d)
	
class ap_app_day:
	def GET(self):
		data = web.input()
		s = datetime.datetime.strptime(data.start,'%Y-%m-%d')
		e = datetime.datetime.strptime(data.end,'%Y-%m-%d')
		a = data.mac
		m1 = {"$match":{"$and":[{"apmac":a},{"timestamp" : {"$gte": s }},{ "timestamp" : {"$lt": e}}]}}
		if web.ctx.session.roleid == webmgr_obj_globals.g_admin:
			m1 = {"$match":{"$and":[{"domainid" : web.ctx.session.domainid},{"apmac":a},{"timestamp" : {"$gte": s }},{ "timestamp" : {"$lt": e}}]}}
		elif web.ctx.session.roleid == webmgr_obj_globals.g_user:
			m1 = {"$match":{"$and":[{"domainid" : web.ctx.session.domainid},{"accountid" : web.ctx.session.accountid},{"apmac":a},{"timestamp" : {"$gte": s }},{ "timestamp" : {"$lt": e}}]}}
		u = {"$unwind":"$app"}
		m2 = {"$match":{"app" : {"$ne":None}}}
		g1 = {"$group":{"_id":"$app","value":{'$sum': 1}}}
		ds = mongodb.aggregate("r_sta_logs",[m1,u,m2,g1,{"$sort":{"value":-1}}, {"$limit" : 10 }])
		d = {}
		while ds.next():
			d[ds["_id"]] = {"_id":ds["_id"],"value":ds["value"]}
		return json.dumps(d)

class sta_phonetype:
	mapper = """function (){
		var find = false;
		var keys = [%s];var values=[%s];
		for(var k in this.value.result){
			if(!this.value.result[k].name)
			{
				emit('其它',this.value.result[k].cnt);
				continue;
			}	
			var kkk = this.value.result[k].name.toString();
			for(var i in keys){
				if(kkk.indexOf(keys[i]) != -1){
					find = true;
					emit(values[i],this.value.result[k].cnt);
				}
			}
			if(!find){
				emit('其它',this.value.result[k].cnt);
			}
		}
	}"""
	
	reduce = """function(key,cnt){
		return Array.sum(cnt);
	}"""
	
	def GET(self):
		data = web.input() 
		query = get_match(data,"_id.apmac",[data.mac],"_id.dt")
		
		ds = mongodb.find("c_phone")
		keys = []
		values = []
		while ds.next():
			keys.append("'"+ds["_id"]+"'")
			values.append("'"+ds["value"]+"'")
		
		m = sta_phonetype.mapper % (",".join(keys),",".join(values))
		ds = mongodb.map_reduce("r_sta_phone",m,sta_phonetype.reduce,query=query["$match"])
		ds.sort(key=lambda x : x["value"],reverse=True)
		return json.dumps(ds)
	
class sta_phonetype_day:
	def GET(self):
		data = web.input()
		s = datetime.datetime.strptime(data.start,'%Y-%m-%d')
		e = datetime.datetime.strptime(data.end,'%Y-%m-%d')
		a = data.mac
		m = {"$match":{"$and":[{"apmac":a},{"startime" : {"$gte": s }},{ "startime" : {"$lt": e}}]}}
		if web.ctx.session.roleid == webmgr_obj_globals.g_admin:
			m = {"$match":{"$and":[{"domainid" : web.ctx.session.domainid},{"apmac":a},{"startime" : {"$gte": s }},{ "startime" : {"$lt": e}}]}}
		elif web.ctx.session.roleid == webmgr_obj_globals.g_user:
			m = {"$match":{"$and":[{"domainid" : web.ctx.session.domainid},{"accountid" : web.ctx.session.accountid},{"apmac":a},{"startime" : {"$gte": s }},{ "startime" : {"$lt": e}}]}}
		g1 = {"$group":{"_id":"$terminal_type","value":{'$sum': 1}}}
		d = {}
		ds = mongodb.aggregate("r_sta_running",[m,g1,{"$sort":{"value":-1}}, {"$limit" : 10 }])
		while ds.next():
			d[ds["_id"]] = {"_id":ds["_id"],"value":ds["value"]}
		ds = mongodb.aggregate("r_sta_connection",[m,g1,{"$sort":{"value":-1}}, {"$limit" : 10 }])
		while ds.next():
			if ds["_id"] in d.keys():
				values = d[ds["_id"]]['value']+ ds["value"]
				d[ds["_id"]] = {"_id":ds["_id"],"value":values}
			else:
				d[ds["_id"]] = {"_id":ds["_id"],"value":ds["value"]}
		return json.dumps(d)

class sta_auth:
	def GET(self):
		data = web.input() 

		m = get_match(data,"apmac",[data.mac],"startime")
		r,k = get_data(data) 
		g = {"$group": {"_id":{"dt":{"year":{"$year":"$startime"},"dt":{k:"$startime"}},"auth":"$authtype"},
			"value": { "$sum": 1}}}
		
		names = {}
		names["wechat"] = "微信认证"
		names["portal"] = "密码认证"
		names["sms"] = "短信认证"
		names["mac"] = "MAC认证"
		names["fast"] = "快速认证"
		names["noauth"] = "免认证"
		names["sms"] = "短信认证"
		names["wx2wifi"] = "微信连WIFI认证"
		dd = {}
		for n in names:
			dd[n] = utility.clone(r)
			
		#计算当前表 
		ds = mongodb.aggregate("r_sta_running",[m,g])
		while ds.next():
			a = ds["_id"]["auth"]
			t = _getKey(ds["_id"]["dt"]["year"],ds["_id"]["dt"]["dt"])
			dd[a][t] = ds["value"] 
		
		
		m = get_match(data,"_id.apmac",[data.mac],"_id.dt")
		u = {"$unwind" : "$value.result"}
		g = {"$group": {"_id":{"dt":{"year":{"$year":"$_id.dt"},"dt":{k:"$_id.dt"}},"auth":"$value.result.name"},
			"value": { "$sum": "$value.result.cnt"}}}
		
		authcnt = 0
		assoccnt = 0
		s = datetime.datetime.strptime(data.start,'%Y-%m-%d')
		e = datetime.datetime.strptime(data.end,'%Y-%m-%d')
		nowtime = datetime.datetime.today()
		today = datetime.datetime(nowtime.year,nowtime.month,nowtime.day)
		if e > today:
			e = today
		a = data.mac
		request = {"apmac":a,"startime" : {"$gte": s,"$lt": e}}
		authcnt = mongodb.find("r_auth_counting",request).count
		
		request2 = {"apmac":a,"date" : {"$gte": s.strftime("%Y-%m-%d"), "$lt": e.strftime("%Y-%m-%d")}}
		ds_assoc = mongodb.find("r_assoc_counting",request2)
		while ds_assoc.next():
			assoccnt += ds_assoc['assoc_count']
		
		ds = mongodb.aggregate("r_rule_connected",[m,u,g])
		while ds.next():
			a = ds["_id"]["auth"]
			t = _getKey(ds["_id"]["dt"]["year"],ds["_id"]["dt"]["dt"])
			dd[a][t] = ds["value"]
		
		ret = []
		for d in dd:
			if sum(dd[d].values()) == 0:
				continue
			g = {}
			g["type"] = d
			g["name"] = names[d]
			auth= sorted(dd[d].items(), key=lambda a:a[0], reverse = False)
			g["data"] = [x[1] for x in auth]
			ret.append(g)
		times =  config.get("associate","times")
		return json.dumps({"legend":[x for x in names.values()],"data":ret,"authcnt":authcnt,"assoccnt":assoccnt,"times":times})
	
class sta_auth_day:
	def GET(self):
		data = web.input() 
		s = datetime.datetime.strptime(data.start,'%Y-%m-%d')
		e = datetime.datetime.strptime(data.end,'%Y-%m-%d')
		a = data.mac
		m = {"$match":{"$and":[{"apmac":a},{"startime" : {"$gte": s }},{ "startime" : {"$lt": e}}]}}
		if web.ctx.session.roleid == webmgr_obj_globals.g_admin:
			m = {"$match":{"$and":[{"domainid" : web.ctx.session.domainid},{"apmac":a},{"startime" : {"$gte": s }},{ "startime" : {"$lt": e}}]}}
		elif web.ctx.session.roleid == webmgr_obj_globals.g_user:
			m = {"$match":{"$and":[{"domainid" : web.ctx.session.domainid},{"accountid" : web.ctx.session.accountid},{"apmac":a},{"startime" : {"$gte": s }},{ "startime" : {"$lt": e}}]}}
		r,k = get_data(data) 
		g = {"$group": {"_id":{"dt":{"year":{"$year":"$startime"},"dt":{k:"$startime"}},"auth":"$authtype"},
			"value": { "$sum": 1}}}
		
		request = {"apmac":a,"startime" : {"$gte": s ,"$lt": e}}
		authcnt = mongodb.find("r_auth_counting",request).count
		
		request2 = {"apmac":a,"date" : {"$gte": s.strftime("%Y-%m-%d"), "$lt": e.strftime("%Y-%m-%d")}}
		ds_assoc = mongodb.find("r_assoc_counting",request2)
		assoccnt = 0
		while ds_assoc.next():
			assoccnt += ds_assoc['assoc_count']
		
		names = {}
		names["wechat"] = "微信认证"
		names["portal"] = "密码认证"
		names["sms"] = "短信认证"
		names["mac"] = "MAC认证"
		names["fast"] = "快速认证"
		names["noauth"] = "免认证"
		names["sms"] = "短信认证"
		names["wx2wifi"] = "微信连WIFI认证"
		dd = {}
		for n in names:
			dd[n] = utility.clone(r)
			
		ds = mongodb.aggregate("r_sta_running",[m,g])
		while ds.next():
			a = ds["_id"]["auth"]
			t = _getKey(ds["_id"]["dt"]["year"],ds["_id"]["dt"]["dt"])
			dd[a][t] = ds["value"]
		ds = mongodb.aggregate("r_sta_connection",[m,g])
		while ds.next():
			a = ds["_id"]["auth"]
			t = _getKey(ds["_id"]["dt"]["year"],ds["_id"]["dt"]["dt"])
			if a in dd.keys():
				if t in dd[a]:
					dd[a][t] += ds["value"]
				else:
					dd[a][t] = ds["value"]
			else:
				dd[a][t] = ds["value"]
		
		ret = []
		for d in dd:
			if sum(dd[d].values()) == 0:
				continue
			g = {}
			g["type"] = d
			g["name"] = names[d]
			g["data"] = [x for x in dd[d].values()]
			ret.append(g)
		times =  config.get("associate","times")
		return json.dumps({"legend":[x for x in names.values()],"data":ret,"authcnt":authcnt,"assoccnt":assoccnt,"times":times})

class ap_list:
	def GET(self):
		aplist = []
		domainid = web.ctx.session.domainid
		accountid = web.ctx.session.accountid
		roleid = web.ctx.session.roleid
		cond = {}
		if roleid == webmgr_obj_globals.g_supper:
			pass
		elif roleid == webmgr_obj_globals.g_admin:
			cond = {"domainid":domainid}
		else:
			cond = {"domainid":domainid,"accountid":accountid}
		ds = mongodb.find("r_ap_running_info",cond).leftjoin("_id","u_ap_info","_id")
		while ds.next():
			a = {}
			a["name"] = ds["u_ap_info.name"]
			a["devid"] = ds["_id"]
			a["mac"] = mac.from_deviceid(ds["_id"])[2].to_str()
			aplist.append(a)
		return json.dumps(aplist)

class sta_list:
	def GET(self):
		data = web.input(devid="")
		devid = data.devid
		s = datetime.datetime.strptime(data.start,'%Y-%m-%d')
		e = datetime.datetime.strptime(data.end,'%Y-%m-%d')
		nowtime = datetime.datetime.today()
		today = datetime.datetime(nowtime.year,nowtime.month,nowtime.day)
		if e > today:
			e = today
		ret = {}
		m = {"devid":devid,"startime":{"$lte":s}}
		n = utility.now()
			
		m = {"devid":devid,"lastime":{"$gt":s},"startime":{"$lt":e}}
		ds = mongodb.find("r_sta_connection",m)
		while ds.next():
			mac = ds["stamac"]
			if mac in ret:
				r = ret[mac]
			else:
				r = {}
				r["userid"] = ds["userid"]
				r["stamac"] = mac
				r["staip"] = ds["staip"] 
				r["authcount"] = 0
				r["duration"] = 0
				r["curtx"] = 0
				r["currx"] = 0
				r["online"] = False
				ret[mac] = r
			r["authcount"] += 1	
			t = ds["lastime"] - ds["startime"]
			r["duration"] += t.total_seconds()
			r["curtx"] += ds["txbytes"]
			r["currx"] += ds["rxbytes"]
		
		ll = []	
		for r in ret.values():
			r["durationtext"] = str(datetime.timedelta(seconds=int(r["duration"]))).replace("days","天").replace("day","天")
			r["curtx"] = "%0.02f"%(r["curtx"]/1024/1024)
			r["currx"] = "%0.02f"%(r["currx"]/1024/1024)
			ll.append(r);
		return json.dumps(sorted(ll,key=lambda r:r["duration"],reverse=True))
	

class sta_list_day:
	def GET(self):
		data = web.input(devid="")
		devid = data.devid
		s = datetime.datetime.strptime(data.start,'%Y-%m-%d')
		e = datetime.datetime.strptime(data.end,'%Y-%m-%d')
		ret = {}
		m = {"devid":devid,"startime":{"$lte":s}}
		ds = mongodb.find("r_sta_running",m) #小于开始时间，说明sta这个时间在线
		n = utility.now()
		
		while ds.next():
			mac = ds["stamac"]
			if mac in ret:
				r = ret[mac]
			else:
				r = {}
				r["userid"] = ds["userid"]
				r["stamac"] = mac
				r["staip"] = ds["staip"]
				r["authcount"] = 0
				r["duration"] = 0
				r["curtx"] = 0
				r["currx"] = 0
				ret[mac] = r
			t = n - ds["startime"]
			r["authcount"] += 1
			r["duration"] += t.total_seconds()
			r["curtx"] += ds["curtx"]+ds["pretx"]
			r["currx"] += ds["currx"]+ds["prerx"]
			r["online"] = True

			
		m = {"devid":devid,"lastime":{"$gt":s},"startime":{"$lt":e}}
		ds = mongodb.find("r_sta_connection",m)
		while ds.next():
			mac = ds["stamac"]
			if mac in ret:
				r = ret[mac]
			else:
				r = {}
				r["userid"] = ds["userid"]
				r["stamac"] = mac
				r["staip"] = ds["staip"] 
				r["authcount"] = 0
				r["duration"] = 0
				r["curtx"] = 0
				r["currx"] = 0
				r["online"] = False
				ret[mac] = r
			r["authcount"] += 1	
			t = ds["lastime"] - ds["startime"]
			r["duration"] += t.total_seconds()
			r["curtx"] += ds["txbytes"]
			r["currx"] += ds["rxbytes"]
		
		ll = []	
		for r in ret.values():
			r["durationtext"] = str(datetime.timedelta(seconds=int(r["duration"]))).replace("days","天").replace("day","天")
			r["curtx"] = "%0.02f"%(r["curtx"]/1024/1024)
			r["currx"] = "%0.02f"%(r["currx"]/1024/1024)
			ll.append(r);
		return json.dumps(sorted(ll,key=lambda r:r["duration"],reverse=True))
	




