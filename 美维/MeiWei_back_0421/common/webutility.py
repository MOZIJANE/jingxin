#coding=utf-8 
# ycat			 2014/09/28      create
import bottle,json
import sys,os,io
import utility
import platform
import config
import datetime
import cgi,urllib.request
import counter,json_codec
import http.client as client
import log
import re
if not utility.is_python3():
	import urllib2
	
g_test_param = {}
def get_param_int(key,default=None):
	v = get_param(key,default)
	if v is None:
		return None
	if isinstance(v,str) and v.isdigit():
		return int(v)
	else:
		return float(v)

def get_param_bool(key,default=None):
	v = get_param(key,default)
	if v == 0 or v is None:
		return False
	elif v == 1:
		return True
	elif v.lower() == "true":
		return True
	else:
		return False
	
def get_param_float(key,default=None):
	return get_param_int(key,default)
	
def get_param(key,default=None):
	global g_test_param
	if key in g_test_param:
		return g_test_param[key]
	if not is_bottle():
		return default
	ret = bottle.request.params.getunicode(key,encoding="utf-8")
	if ret:
		return ret
	if hasattr(bottle.request,"myParam"):
		if key in bottle.request.myParam:
				return bottle.request.myParam[key]
		else:
			return default
	payload = bottle.request.body.read().decode('utf-8')
	if len(payload):
		try:
			params =  json_codec.load(payload)
			bottle.request.myParam = params
			if key in params:
				return params[key]
		except Exception as e:
			bottle.request.myParam = {} 
			pass
	return default

def set_test_param(key,value):
	global g_test_param
	g_test_param[key] = value

def escape(s):
	return cgi.escape(s)

def make_url(url,params,code):
	u = url
	if url.find("://") == -1:
		u = "http://"+u
	# u = u.replace("127.0.0.1","localhost") 
	if not params:
		return u
	sortkey = list(params.keys())
	sortkey.sort()
	first = True
	for k in sortkey:
		if first:
			u+= "?"
		else:
			u+= "&"
		s = str(params[k])
		if len(s):
			u += k + "=" + urllib.parse.quote(s.encode(code))
		else:
			u += k
		first = False
	return u

def http_get(url,params,timeout=15,code="utf-8",writelog=True):
	u = make_url(url,params,code)   #拼成完整的http连接
	if writelog:
		ticks = utility.ticks()
		log.debug("send http_get: " + u)
	try:
		f = urllib.request.urlopen(u,timeout=timeout)
	except Exception as e:
		raise Exception("http get",url,params,"error:",str(e))

	try:  # 添加了try语句
		buffer = f.read()
	except client.IncompleteRead as e:
		buffer = e.partial
	r = buffer.decode(code)

	if writelog:
		log.debug("[return] use %d ms,http_get: "%(utility.ticks() - ticks) + u)# + ", " + r)
	return r

def http_post(url,params,data,timeout=15,code="utf-8"):
	postdata = None
	if isinstance(data,dict):
		postdata = urllib.parse.urlencode(data).encode(code)
	elif isinstance(data,str):
		postdata = data.encode(code)
	u = make_url(url,params,code)
	ticks = utility.ticks()
	log.debug("send http_post: " + u + str(data))
	
	try:
		f = urllib.request.urlopen(u,postdata,timeout=timeout)	
	except Exception as e:
		raise Exception("http post",url,params,"error:",str(e))
		
	r = f.read().decode(code)
	log.debug("[return] post use %d ms : "%(utility.ticks() - ticks) + u + ", " + r)
	return r
	
def is_uwsgi():
	return "UWSGI_ORIGINAL_PROC_NAME" in os.environ
	
def is_bottle():
	if is_uwsgi():
		return True
	return "bottle" in os.environ
	#if utility.is_win():
	#	os.environ['bottle']="True"
	#	server = config.get("bottle","service","wsgiref").lower()
	#	if server == "paste":
	#		#在linux下是多线程的，在win下是多进程
	#		return True
	#return "bottle" in os.environ

def check(value,errorCode,msg=None):
	if not value:
		if errorCode == 401 and not msg:
			msg = "用户未登陆" 
		bottle.abort(errorCode,msg)

def get_ip():
	if utility.is_test():
		return "unittest"
	return bottle.request.remote_addr

#处理web上传的文件 
def get_request_file(param_name):
	mem = io.BytesIO()
	upload = bottle.request.files.get(param_name)
	mem.write(upload.file.read())
	mem.seek(0)
	return mem

#直接保存web上传的文件到local中 
def save_request_file(param_name,local):
	upload = bottle.request.files.get(param_name)
	f = open(local,"w+b")
	f.write(upload.file.read())
	f.close()

def __read_file(filename):
	if utility.is_python3():
		with open(filename,"r",encoding='utf-8') as f:
			return f.read()
	else:
		import codecs
		with codecs.open(filename,encoding='utf-8') as f:
			return f.read().encode("utf-8")


def load_file(filename,keyword):
	s = __read_file(filename)
	tpl = bottle.SimpleTemplate(s,encoding='utf8')
	r = tpl.render(keyword)
	if utility.is_python3():
		return r
	else:
		return r.encode("utf-8")
 
g_ignoreNames = []

def add_ignore(name):
	global g_ignoreNames
	g_ignoreNames.append(name.lower())
	
def is_get_log_request(url):
	global g_ignoreNames
	if url[len(url) - 3:] == "log":
		return True
	if url[len(url) - 6:] == "logger":
		return True
	if url[len(url) - 3:] == "/ok":
		return True
	for n in g_ignoreNames:
		if url.lower().find(n) != -1:
			return True
	return False

class bottleStat:
	def __init__(self):
		self.pending = {}
		self.stat = {}
		
	def start(self):
		self.pending[id(bottle.request)] = (bottle.request.method+":"+bottle.request.url,utility.ticks())
		if is_get_log_request(bottle.request.url):
			return	
		log.debug(bottle.request.method+": "+bottle.request.url+" addr: "+bottle.request.remote_addr)
		
	def finish(self):
		idd = id(bottle.request)
		if idd not in self.pending:
			return
		u = bottle.request.method+":"+bottle.request.url
		index = u.find("?") 
		if index != -1:	
			u = u[0:index]
		t = utility.ticks() - self.pending[idd][1] 
		del self.pending[idd]
		if u not in self.stat:
			b = counter.bucket()
			b.add(t)
			self.stat[u] = b
		else:
			self.stat[u].add(t)
			
		if is_get_log_request(bottle.request.url):
			return
		printFunc = log.debug
		if bottle.response._status_code != 200:
			printFunc = log.warning
		printFunc("used "+str(t)+"ms",str(bottle.response.status) + " " + bottle.response.content_type+", " +bottle.request.method+": "+bottle.request.url)

g_bottleStat = bottleStat() 

def before_request_hook():
	global g_bottleStat
	g_bottleStat.start()

def after_request_hook():
	global g_bottleStat
	g_bottleStat.finish()
	
#读取run_all的端口，或者是nginx的端口 
def readPort():
	if utility.is_run_all():
		return config.getint("bottle","port",9000)
	return _get_port()
	 
	
def _get_port():
	import inspect 
	s = inspect.stack()[2:]   
	name = s[0][1]     
	p = os.path.abspath(os.path.dirname(name))+"/run.xml"
	log.info("**********************执行配置文件的路径是：",p)
	if not os.path.exists(p): #如果port为0，必需要配置这个文件 
		log.error("Can't find run.xml",p)
		raise Exception("Can't find run.xml,path:"+p)
	f = open(p,"r+t")
	xml = f.read()
	f.close()
	mm = re.search('<root.*port\s*=\s*"(\d+)">',xml,re.M|re.S)
	if not mm:
		return 0
	return int(mm.group(1))

def run(port = 0): 
	bottle.default_app().add_hook("before_request",before_request_hook)
	bottle.default_app().add_hook("after_request",after_request_hook)
	if is_bottle():
		log.warning("Local server start! version %s, path %s, pid %d"%(platform.python_version(),os.getcwd(),os.getpid()))
	
	ss = config.get("bottle","ignore").split(";")
	for s in ss:
		log.info('add_ignore:', s)
		add_ignore(s)
	
	isdebug = config.getbool("bottle","debug",False)	
	if isdebug:
		bottle.debug(True)
	r = config.getbool("bottle","reload",False)
	if port == 0:
		port = _get_port() #config.getint("bottle","port",80)
	host = config.get("bottle","host","")
	
	ssl_cert = config.get("bottle","ssl_cert","")
	ssl_key = config.get("bottle","ssl_key","")
	server = config.get("bottle","service","wsgiref")
	os.environ["bottle"] = "True"
	if server == "":
		server = "wsgiref"
		
	if ssl_cert:
		#to use https
		#python -m pip install cherrypy
		#python -m pip install cherrypy???????
		from cherrypy import wsgiserver
		from cherrypy.wsgiserver.ssl_builtin import BuiltinSSLAdapter
		wsgiserver.CherryPyWSGIServer.ssl_adapter = BuiltinSSLAdapter(ssl_cert,ssl_key,None)
	os.environ["port"] = str(port)
	if isdebug:
		bottle.run(host=host, port=port,reloader=r,server=server,debug=True,quiet=False)
	else:
		bottle.run(host=host, port=port,reloader=r,server=server,debug=False,quiet=True)


#自动处理异常的修饰符
#用法 @catch 
def catch(func):
	def __call(*p):
		try:
			return func(*p)
		except bottle.HTTPResponse as httperror:
			log.info(httperror)
			raise
		except Exception as e:
			log.exception("invoke "+str(func),e)
			return "invoke "+str(func) + str(e)
	return __call

#获得外网ip 
def get_public_ip():
	import re
	ips = []
	ips.append(("http://city.ip138.com/ip2city.asp","\d+\.\d+\.\d+\.\d+","gb2312"))
	ips.append(("http://www.ip.cn/","\d+\.\d+\.\d+\.\d+","utf-8"))
	ips.append(("http://www.whereismyip.com/","\d+\.\d+\.\d+\.\d+","utf-8"))
	for u in ips:
		try:
			ret = http_get(u[0],None,code=u[2])
			r = re.search(u[1],ret)
			if r:
				return r.group(0)
		except Exception as e:
			log.exception("get_public_ip failed",e)
	log.error("get_public_ip failed, return 0.0.0.0")
	return "0.0.0.0"

#获得外网时间 
def get_public_date():
	try:
		content =http_get("http://www.beijing-time.org/time15.asp",None,timeout=3,code="gbk",writelog=False)
		#返回示例： t0=new Date().getTime(); nyear=2016; nmonth=3; nday=24; nwday=4; nhrs=9; nmin=6; nsec=40;
		import re
		result = re.search("nyear=(\d+);\s+nmonth=(\d+);\s+nday=(\d+);\s+nwday=\d+;\s+nhrs=(\d+);\s+nmin=(\d+);\s+nsec=(\d+);",content)
		if result:
			r = result.group
			return datetime.datetime(int(r(1)),int(r(2)),int(r(3)),int(r(4)),int(r(5)),int(r(6)))
		else:
			return None
	except Exception as e:
		return None


def gethostname():
	import socket  
	return socket.gethostname()  

@bottle.route("/"+utility.app_name()+'/ok')
def url_check():
	import mac
	t = utility.running_time()
	d = {"seconds":t.total_seconds(),"pid":os.getpid(),"hostname":gethostname(),"mac":mac.system_mac().to_str()}
	return json.dumps(d)
	
def _load_table_file(name,tables):
	f = os.path.dirname(__file__)+"/table.tpl"
	f = os.path.realpath(f)
	return load_file(f,{"name":name,"tables":tables})

@bottle.route("/"+utility.app_name()+'/stat/bottle')
def url_bottle_stat():
	global g_bottleStat
	pending = {}
	pending["name"] = "Pending统计"
	pending["titles"] = ["地址","时长(ms)"]
	data = []
	now = utility.ticks()
	for p in g_bottleStat.pending:
		pp = g_bottleStat.pending[p]
		d = [pp[0],now-pp[1]]
		data.append(d)
	pending["data"] = data
	
	stat = {}
	stat["name"] = log.app_name()+",Url统计"
	stat["titles"] = ["URL","总时长(ms)","次数","平均时长(ms)"] + counter.bucket.titles()
	data = []
	for s in g_bottleStat.stat:
		b = g_bottleStat.stat[s]
		row = []
		row.append(s)
		row.append(b.total)
		row.append(b.count)
		row.append("%0.2f"%b.average)
		row += b.counts
		data.append(row)
	stat["data"]= data
	return _load_table_file(stat["name"],[pending,stat])
	
@bottle.route("/"+utility.app_name()+'/stat/count')
def url_count_stat():
	import counter 
	stat = {}
	stat["name"] = log.app_name()+", 性能统计"
	stat["titles"] = ["函数","总时长(ms)","次数","平均时长(ms)"] + counter.bucket.titles()

	data = []
	for s in counter.g_stat:
		b = counter.g_stat[s]
		row = [] 
		row.append(s)
		row.append(b.total)
		row.append(b.count)
		row.append("%0.2f"%b.average)
		row += b.counts
		data.append(row)
	stat["data"]= data 
	return _load_table_file(stat["name"],[stat])
	
@bottle.route("/"+utility.app_name()+'/stat/mongo')
def url_mongo_stat():
	import mongodb 
	stat = {}
	stat["name"] = log.app_name()+", Mongodb统计"  
	stat["titles"] = ["操作","成功次数","失败次数","使用索引","检查文档","检查Key","返回文档","总时长(ms)","平均时长(ms)"] + counter.bucket.titles()
	data = []
	for s in mongodb._get_mongodb().stat.stat:
		v = mongodb._get_mongodb().stat.stat[s]
		row = [] 
		row.append(s)
		row.append(v.successCount)
		row.append(v.failCount)
		row.append(v.indexCount)
		row.append(v.totalExamDoc)
		row.append(v.totalKeyExamDoc)
		row.append(v.totalRetDoc)
		row.append(v.bucket.total)
		row.append("%0.2f"%v.bucket.average)
		row += v.bucket.counts
		data.append(row) 
	stat["data"]= data 
	return _load_table_file(stat["name"],[stat])


def set_content_type(fn,content_type):
	def _enable_cors(*args, **kwargs): 
		bottle.response.content_type = content_type
		return fn(*args, **kwargs)   
	return _enable_cors


#decorator
def allow_cross_domain(fn):
	def _enable_cors(*args, **kwargs):
		#set cross headers
		bottle.response.headers['Access-Control-Allow-Origin'] = '*'
		bottle.response.headers['Access-Control-Allow-Methods'] = 'GET, HEAD, POST, OPTIONS, PUT, PATCH, DELETE'
		#bottle.response.headers['Access-Control-Allow-Headers'] = "*" 
		bottle.response.headers['Access-Control-Allow-Headers'] = "content-type, location, session"
		bottle.response.headers['Access-Control-Max-Age'] = 86400 
		bottle.response.content_type = "application/json;charset=utf-8"
		if bottle.request.method != 'OPTIONS':
			# actual request; reply with the actual response
			return fn(*args, **kwargs)   
	return _enable_cors
 	
#############################	unit test	###########################
def test_gethostname():
	a = gethostname()
	assert a != ""
	
def test_public_date():
	r = get_public_date()
	if r is None:
		r = utility.now()
	import lock
	lock.sleep(2)
	tmp = utility.now()
	r2 = get_public_date()
	if r2 is None:
		r2 = tmp
	assert utility.equal(r2,utility.now(),dateDiffSecond=300,debug=True) #和本地时间不能相差5分钟
	assert utility.equal(r2,r,dateDiffSecond=3,debug=True)  

def test_get_public_ip():
	assert "0.0.0.0" != get_public_ip() or "0.0.0.0" == get_public_ip()
	
def test_catch():
	@catch
	def test1():
		raise NotImplementedError("lalalal")
	assert test1().find("lalalal") != -1
	
	@catch
	def test2(a1,a2,a3,a4):
		raise NotImplementedError("lalalal")
	assert test2(1,2,3,4).find("lalalal") != -1
	
def test_load_file():
	s = """<span>这是中文1</span>
<input type="hidden" id="session" value="{{session1}}" />
<input type="hidden" id="session" value="{{session2}}" />
<input type="hidden" id="session" value="{{session3}}" />
<span>这是中文2</span>"""
	assert s == __read_file("testwebutility.tpl")
	
	d = {"session1":"ycat1","session2":"ycat2","session3":"中文"}
	a = load_file("testwebutility.tpl",d)
	s = """<span>这是中文1</span>
<input type="hidden" id="session" value="ycat1" />
<input type="hidden" id="session" value="ycat2" />
<input type="hidden" id="session" value="中文" />
<span>这是中文2</span>"""
	assert s == a

def test_escape():
	assert escape("<dfsd' \">") == '&lt;dfsd\' "&gt;'
	assert escape("abbb发bbbbdfdsfasf12321321") == "abbb发bbbbdfdsfasf12321321"
	assert escape("") == ""

def test_make_url():
	assert make_url("https://api.weixin.qq.com/cgi-bin/abced",None,code="utf-8") == "https://api.weixin.qq.com/cgi-bin/abced"
	d = {"aaaa":"bbbb"}
	assert make_url("https://api.weixin.qq.com/cgi-bin/abced",d,code="utf-8") == "https://api.weixin.qq.com/cgi-bin/abced?aaaa=bbbb"
	d["ccc"] = "eeee"
	assert make_url("https://api.weixin.qq.com/cgi-bin/abced",d,code="utf-8") == "https://api.weixin.qq.com/cgi-bin/abced?aaaa=bbbb&ccc=eeee"
	d["c1cc"] = "ee1ee"
	assert make_url("https://api.weixin.qq.com/cgi-bin/abced",d,code="utf-8") == "https://api.weixin.qq.com/cgi-bin/abced?aaaa=bbbb&c1cc=ee1ee&ccc=eeee"
	d["dddd"] = ""
	assert make_url("https://api.weixin.qq.com/cgi-bin/abced",d,code="utf-8") == "https://api.weixin.qq.com/cgi-bin/abced?aaaa=bbbb&c1cc=ee1ee&ccc=eeee&dddd"

def t1est_timeout():
	import datetime
	a = datetime.datetime.now()
	try:
		http_get("http://www.facebook.com",{},timeout=5)
	except Exception as e:
		print(datetime.datetime.now() - a,e)
		d = datetime.datetime.now() - a
		assert d.total_seconds() >= 5
		assert d.total_seconds() < 10
	
	a = datetime.datetime.now()	
	try:
		http_post("http://www.facebook.com",{},None,timeout=6)
	except Exception as e:
		print(datetime.datetime.now() - a,e)
		assert d.total_seconds() >= 6
		assert d.total_seconds() < 12

if __name__ == '__main__':
	utility.run_tests()

