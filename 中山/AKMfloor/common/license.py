#coding=utf-8 
# ycat			 2016/3/22      create
import sys,os
import utility
import webutility
import mytimer
import mac
import json
import config
import datetime
if "../licmaker" not in sys.path:
	sys.path.append("../licmaker")
import lic_code

#用于检查某些操作权限，例如op_portal_ad,op_marketing_analyze等等 
def check(op_code):
	if is_expire():
		return False
		
	if op_code in g_license_data:
		return g_license_data[op_code] != 0
	else:
		return False
	
#用于检查数量类型，例如ap_count和sta_count 
def check_count(op_code,number):
	if is_expire():
		return False
	
	if op_code in g_license_data:
		if g_license_data[op_code] == 0: #不限制  
			return True
		utility.logger().debug("license %s,%d,%d"%(op_code,number,g_license_data[op_code]))
		return number <= g_license_data[op_code]
	else:
		return False
		
_test_machine_code = None

def is_expire():
	global g_license_data
	_load()
	if "expire_date" in g_license_data: 
		if _get_datetime() > g_license_data["expire_date"]:
			return True
	return False

def machine_code():
	if _test_machine_code:
		return _test_machine_code
	return utility.md5(mac.system_mac().to_str()).lower()[-8:]

def get_path():
	if utility.is_win() and not utility.is_test():
		return "./"
	return config.get("license","path")

def get_desc(data,has_append=True):
	if not data:
		_load()
		data = g_license_data
	r = []
	if "sta_count" in data:
		if data["sta_count"] == 0:
			r.append(("用户个数", "不限"))
		else:
			r.append(("用户个数", str(data["sta_count"]) + "个"))
			
	if "ap_count" in data:
		if data["ap_count"] == 0:
			r.append(("AP个数", "不限"))
		else:
			r.append(("AP个数",str(data["ap_count"]) + "个"))	
				
	for x in data:
		if x in lic_code.op_map:
			if data[x]:
				r.append((lic_code.op_map[x], "已授权"))
			else:
				r.append((lic_code.op_map[x], "未授权"))
	
	if "expire_date" in data:
		r.append(("过期时间", utility.date2str(data["expire_date"])))
		if _get_datetime() > data["expire_date"]:
			r.append(("是否过期","是"));
		else:
			r.append(("是否过期","否"));
		
	if "append_mode" in data and has_append:
		if data["append_mode"]:
			r.append(("追加模式", "是"))
		else:
			r.append(("追加模式", "否"))			
	return r

g_last_check_ticks = 0
g_license_data = {}
is_first = True

g_datetime_tick = 0
g_datetime = None
def _get_datetime():
	global g_datetime,g_datetime_tick
	if g_datetime is None:
		g_datetime_tick = mytimer.ticks()
		g_datetime = webutility.get_public_date()
		if g_datetime is None:
			g_datetime = utility.now()
			return g_datetime
		else:
			return g_datetime
	else:
		return g_datetime + datetime.timedelta(milliseconds = (mytimer.ticks() - g_datetime_tick))

def _load():
	global g_last_check_ticks,g_license_data
	if g_last_check_ticks and mytimer.ticks() - g_last_check_ticks < 3600:
		return
	g_last_check_ticks = mytimer.ticks()
	g_license_data = {}
	files = _search_file()
	
	results = []
	for f in files:
		d = _read_file(f)
		if not d:
			continue
		results.append(d)
	
	results.sort(key=lambda x : x["create_date"])
	for d in results:
		if int(d["append_mode"]) == 0:
			g_license_data = utility.clone(d)
		else:
			_append_data(g_license_data,d)
			
	
def _append_data(data,d):
	#license可以为追加模式或者为覆盖模式，在追加模式下，
	#有效期以最大值为准，最大ap和sta数为两者相加，操作权限为并集。
	for x in d:
		if x == "expire_date":
			if x in data:
				data[x] = max(d[x],data[x])
			else:
				data[x] = d[x]
			continue
		if x == "create_date":
			data[x] = d[x]
			continue		
		if x in data:
			if x == "machine_code" or x == "append_mode" or x == "checksum":
				continue
			data[x] += d[x]
		else:
			data[x] = d[x]
	
def _check_file(strdata,filename):
	try:
		if isinstance(strdata,bytes):
			strdata = str(strdata, encoding = "utf-8")    
		d = json.loads(strdata)
		checksum = d["checksum"]
		d["checksum"] = ""
		
		keys = d.keys()
		keys = sorted(keys)
		sd = [ (k,d[k]) for k in keys ]
		s = json.dumps(sd)
		#utility.logger().debug('license info: %s',s)
		checksum2 = utility.md5(s+machine_code()+"ycat")
		if checksum != checksum2:
			return None
		if "expire_date" in d:
			d["expire_date"] = datetime.datetime.strptime(d["expire_date"],'%Y-%m-%d')
		
		d["create_date"] = _get_lic_datetime(d,filename)
		return d
	except Exception as e:
		#utility.logger().exception("check file error " + filename,e)
		return None

def _read_file(filename):
	try:
		global is_first
		with open(filename) as f:
			return _check_file(f.read(),filename)
	except Exception as e:
		if is_first:
			utility.logger().exception("read file "+filename,e)
			is_first = False
		return None
	
def _search_file():
	r = []
	p = get_path()
	for filename in os.listdir(p):
		fp = os.path.join(p, filename)
		if os.path.isfile(fp) and os.path.splitext(fp)[1] == ".lic":
			r.append(fp)
	return sorted(r)

def _get_lic_datetime(d,filename):
	if "create_date" in d:
		return utility.str2date(d["create_date"])
	#老格式,无create_date
	i = filename.find("_")
	b = filename.rfind(".")
	return datetime.datetime.strptime(filename[i+1:b],'%Y%m%d%H%M%S')
	

#############################	unit test	###########################
def test_load2():
	global g_last_check_ticks
	global g_license_data
	g_last_check_ticks = 0
	global _test_machine_code
	_test_machine_code = "90100f99"
	config.set("license","path",os.path.dirname(__file__)+"/test/lic2")
	_load()
	d = g_license_data
	assert d["append_mode"] == 0
	assert d["sta_count"] == 8
	assert d["op_marketing_analyze"] == 0
	assert d["expire_date"] == datetime.datetime(2021,12,31,0,0,0)
	assert d["ap_count"] == 1
	assert d["op_portal_ad"] == 1
	assert d["create_date"] == datetime.datetime(2016,5,5,9,9,5)
	
	
def test_get_lic_datetime():
	assert _get_lic_datetime({"create_date":"2016-05-04 14:48:55"},"") == datetime.datetime(2016,5,4,14,48,55)
	assert _get_lic_datetime({"create_date2":"2016-05-04 14:48:55"},"license_20160324142155.lic") == datetime.datetime(2016,3,24,14,21,55)

'''	
def test_is_expire():
	global g_license_data
	g_license_data = _read_file("test/expire_20160324142114.txt")
	assert g_license_data["expire_date"] == datetime.datetime(2016,4,26,0,0,0)
	assert is_expire()
	g_license_data["expire_date"] = datetime.datetime(2018,1,1,0,0,0)
	assert not is_expire()
'''	
def test_machine_code():
	assert len(machine_code()) == 8
	print(machine_code())
	
def test_read_file():
	global _test_machine_code
	_test_machine_code = "90100f99"
	d = _read_file(os.path.dirname(__file__)+"/test/license_20160324142111.lic")
	assert d
	assert d["checksum"] == ""
	assert d["append_mode"] == 1
	assert d["sta_count"] == 5000
	assert d["op_marketing_analyze"] == 1
	assert d["expire_date"] == datetime.datetime(2018,1,1,0,0,0)
	assert d["ap_count"] == 1000
	#assert d["machine_code"] == "90100f99"
	assert d["op_portal_ad"] == 0
	
	d = _read_file(os.path.dirname(__file__)+"/test/wrong.lic")
	assert not d
	
def test_search_file():
	config.set("license","path",os.path.dirname(__file__)+"/test")
	r = _search_file()
	assert 3 == len(r)
	rr = ["license_20160324142111.lic","license_20160324142155.lic","wrong.lic"]
	for i in range(len(rr)):
		print(i,rr[i],r[i])
		assert os.path.join(os.path.dirname(__file__)+"/test" ,rr[i]) == r[i]
	
def test_append_data():
	global _test_machine_code
	_test_machine_code = "90100f99"
	
	d1 = _read_file(os.path.dirname(__file__)+"/test/license_20160324142111.lic")
	d2 = _read_file(os.path.dirname(__file__)+"/test/license_20160324142155.lic")
	d = {}
	_append_data(d,d1)
	assert utility.equal(d,d1,debug=True)
	d = {}
	_append_data(d,d2)
	assert utility.equal(d,d2)
	_append_data(d,d1)
	assert d["checksum"] == ""
	assert d["append_mode"] == 1
	assert d["sta_count"] == 7000
	assert d["op_marketing_analyze"] == 1
	assert d["expire_date"] == datetime.datetime(2018, 12, 31, 0, 0)
	assert d["ap_count"] == 2000
	#assert d["machine_code"] == "90100f99"
	assert d["op_portal_ad"] == 1
	
def test_load():
	global _test_machine_code
	_test_machine_code = "90100f99"
	
	global g_last_check_ticks
	global g_license_data
	global is_first
	g_last_check_ticks = 0
	g_license_data = {}
	is_first = True
	_load()
	d = g_license_data
	assert d["checksum"] == ""
	assert d["append_mode"] == 1
	assert d["sta_count"] == 7000
	assert d["op_marketing_analyze"] == 1
	assert d["expire_date"] == datetime.datetime(2018, 12, 31, 0, 0)
	assert d["ap_count"] == 2000
	#assert d["machine_code"] == "90100f99"
	assert d["op_portal_ad"] == 1
	assert g_last_check_ticks != 0
	
	assert check("op_portal_ad")
	assert check("op_marketing_analyze")
	assert check_count("sta_count",7000)
	assert check_count("ap_count",2000)
	assert not check_count("sta_count",7001)
	assert not check_count("ap_count",2001)

	g_license_data["expire_date"] = datetime.datetime(2012, 12, 31, 0, 0)
	assert not check("op_portal_ad")
	assert not check("op_marketing_analyze")
	assert not check_count("sta_count",1)
	assert not check_count("ap_count",1)	

def test_get_desc():
	d1 = _read_file(os.path.dirname(__file__)+"/test/license_20160324142111.lic")
	print(get_desc(d1))
	assert 7 == len(get_desc(d1))

def test_get_datetime():
	
	d = _get_datetime()
	import common.lock
	 
	common.lock.sleep(3) 
	d2 = _get_datetime()
	tt =  d2 - d
	print(tt)
	assert tt.total_seconds() > 2.8
	assert tt.total_seconds() < 3.1
	
	common.lock.sleep(1) 
	d3 = _get_datetime()
	tt =  d3 - d2
	print(tt)
	assert tt.total_seconds() > 0.8
	assert tt.total_seconds() < 1.1
	common.lock.sleep(1) 

if __name__ == '__main__':
	old = config.get("license","path")
	utility.run_tests()
	config.set("license","path",old)
	
