#coding=utf-8 
# ycat			 2014/09/28      create
import bottle,json
import sys,os,io
import platform
import datetime
#import urllib.request 
import counter
import log
import time
import ConfigParser


def is_python3():
	return sys.version[0] == '3'

if is_python3():
	import urllib2
	urllib2.request 

def get_param(key):
	return bottle.request.params.getunicode(key,encoding="utf-8")

def escape(s):
	return cgi.escape(s)

def make_url(url,params,code):
	u = url
	if url.find("://") == -1:
		u = "http://"+u
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

def http_get(url,params,timeout=5,code="utf-8",writelog=True):
	u = make_url(url,params,code) 
	if writelog:
		log.debug("send http_get: " + u)
	
	f = urllib.request.urlopen(u,timeout=timeout)
	r = f.read().decode(code)
	if writelog:
		log.debug("http_get return: " + u + ", " + r)
	return r

def http_post(url,params,data,timeout=5,code="utf-8"):
	postdata = None
	if isinstance(data,dict):
		postdata = urllib.parse.urlencode(data).encode(code)
	elif isinstance(data,str):
		postdata = data.encode(code)
	u = make_url(url,params,code)
	log.debug("send http_post: " + u + str(data))
	
	f = urllib.request.urlopen(u,postdata,timeout=timeout)	
	r = f.read().decode(code)
	log.debug("http_post return: " + u + ", " + r)
	return r

def is_bottle():
	#if utility.is_win():
	#	server = config.get("bottle","service","wsgiref").lower()
	#	if server == "paste":
	#		#在linux下是多线程的，在win下是多进程 
	#		return True
	return "bottle" in os.environ

def check(value,errorCode,msg=None):
	if not value:
		if errorCode == 401 and not msg:
			msg = "用户未登陆" 
		bottle.abort(errorCode,msg)

def get_ip():
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
	if is_python3():
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
	if is_python3():
		return r
	else:
		return r.encode("utf-8")
 
g_ignoreNames = []

def add_ignore(name):
	global g_ignoreNames
	g_ignoreNames.append(name)
	
def is_get_log_request(url):
	global g_ignoreNames
	for n in g_ignoreNames:
		if url.find(n) != -1:
			return True
	if url[len(url) - 3:] == "log":
		return True
	if url[len(url) - 6:] == "logger":
		return True
	if url[len(url) - 3:] == "/ok":
		return True
	return False

def ticks():
	return int(time.time()*1000)

class bottleStat:
	def __init__(self):
		self.pending = {}
		self.stat = {}
		
	def start(self):
		self.pending[id(bottle.request)] = (bottle.request.method+":"+bottle.request.url,ticks())
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
		t = ticks() - self.pending[idd][1] 
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
	 

def run(port = 0):
	bottle.default_app().add_hook("before_request",before_request_hook)
	bottle.default_app().add_hook("after_request",after_request_hook)
	if is_bottle():
		log.warning("Local server start! version %s, path %s"%(platform.python_version(),os.getcwd()))
	
	fileName = './default.ini'
	if not os.path.exists(fileName):
		print('can not find default.ini file!')
		exit(1)
	config = ConfigParser.ConfigParser()
	config.read(fileName)
	isdebug = bool(config.get("bottle","debug"))
	if isdebug:
		bottle.debug(True)
	r = bool(config.get("bottle","reload"))
	if port == 0:
		port = int(config.get("bottle","port"))
	host = config.get("bottle","host","")
	
	ssl_cert = None #config.get("bottle","ssl_cert","")
	ssl_key = None #config.get("bottle","ssl_key","")
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

	if isdebug:
		bottle.run(host=host, port=port,reloader=r,server=server,debug=True)
	else:
		bottle.run(host=host, port=port,reloader=r,server=server,debug=False)


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

#decorator
def allow_cross_domain(fn):
	def _enable_cors(*args, **kwargs):
		#set cross headers
		bottle.response.headers['Access-Control-Allow-Origin'] = '*'
		bottle.response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,OPTIONS'
		allow_headers = 'Referer, Accept, Origin, User-Agent'
		bottle.response.headers['Access-Control-Allow-Headers'] = allow_headers
		if bottle.request.method != 'OPTIONS':
			# actual request; reply with the actual response
			return fn(*args, **kwargs)   
	return _enable_cors

def get(url):
	return _route(url,method="GET")

def post(url):
	return _route(url,method="POST")

def _route(url,method):
	def __call(func):
		ff = allow_cross_domain(_catch(func))
		return bottle.route(url, ["GET","POST"], callback=ff) 
	return __call	
	
#每个后端页面都需要返回的信息
def _addBackResult(errorno, errormsg, retDic = {}):
	retDic["errorno"] = errorno
	if errorno != 0:
		retDic["errormsg"] = errormsg
	#return json_codec.dump(retDic)
	return retDic
		
def _catch(func):
	def __call(*p,**pp):
		try:
			ret = func(*p,**pp)
			if ret is None:	
				return _addBackResult(0,"")
			assert isinstance(ret,dict) 
			return _addBackResult(0,"",ret)
		except Exception as e:
			log.exception("invoke "+str(func),e)
			return _addBackResult(-1, str(e))
	return __call


#############################	unit test	###########################

if __name__ == '__main__':
	pass

