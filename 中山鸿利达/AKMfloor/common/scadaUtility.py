# coding: utf-8
# author: ives
# date: 2017-10-24
# desc: 公共函数
import json_codec
import utility
import bottle
import webutility
import log

#用于wmqtt控制重联 
class WmqttException(Exception):
	def __init__(self,*p,**pp):
		super(WmqttException, self).__init__(*p,**pp)

class AuthException(Exception):
	def __init__(self,*p,**pp):
		super(AuthException, self).__init__(*p,**pp)

def get(url,cacheSecond=0):
	return _route(url,method=["GET","POST"],cacheSecond=cacheSecond)

def post(url):
	return _route(url,method=["GET","POST"]) 
	
def getNormal(url):
	return _route(url,method="GET")

	
#每个后端页面都需要返回的信息
def _addBackResult(errorno, errormsg, retDic = None):
	if retDic is None:
		retDic = {}
	retDic["errorno"] = errorno
	if errorno != 0:
		retDic["errormsg"] = errormsg
	else:
		assert not errormsg
		retDic["errormsg"] = ""
	return json_codec.dump(retDic)
		
def _catch(func):
	def __call(*p,**pp):
		try:
			ret = func(*p,**pp)
			if ret is None:	
				return _addBackResult(0,"")
			if not isinstance(ret,dict):
				print("type must be dict",type(ret),str(ret))
			assert isinstance(ret,dict) 
			return _addBackResult(0,"",ret)
		except AuthException as e1:
			log.error("auth failed! ",str(e1))
			return _addBackResult(-1000, str(e1))
		except WmqttException as e2:
			log.error("wmqtt failed! ",str(e2))
			return _addBackResult(-1001, str(e2))
		except Exception as e:
			if hasattr(e,"noprint"):
				log.error("catch Exception:",str(e))
			else:
				log.exception("invoke "+str(func),e)
			return _addBackResult(-1, str(type(e).__name__)+": "+str(e))
	__call.__name__ = func.__name__
	return __call
	
@webutility.allow_cross_domain
def _optionDefault():
	return "OK"
	
def _route(url,method,cacheSecond=0):
	def __call(func):
		f1 = func
		if cacheSecond:
			f1 = cacheFunc(func,cacheSecond)
		ff = webutility.allow_cross_domain(_catch(f1)) 
		ff = webutility.set_content_type(ff,'application/json;charset=utf-8') 
		bottle.route(url,"OPTIONS", _optionDefault)
		return bottle.route(url, method, callback=ff) 
	# __call.__name__ = func.__name__
	return __call	
 
def add(url,func,cacheSecond=0):
	f1 = func
	if cacheSecond:
		f1 = cacheFunc(func,cacheSecond)
	ff = webutility.allow_cross_domain(_catch(f1))
	ff = webutility.set_content_type(ff,'application/json;charset=utf-8') 
	bottle.route(url,"OPTIONS", _optionDefault)
	return bottle.route(url, ["GET","POST"], callback=ff) 
	
	
class cacheInfo:
	def __init__(self,cacheSecond):
		self.timeout = cacheSecond*1000
		self.data = None
		self.visitTicks = 0
		
g_cacheInfo = {}
		
def cacheFunc(func,cacheSecond):
	g_cacheInfo[func] = cacheInfo(cacheSecond)
	def __call(*p,**pp):
		if func in g_cacheInfo:
			c = g_cacheInfo[func]
			now = utility.ticks()
			if now - c.visitTicks > c.timeout:
				c.data = func(*p,**pp)
				c.visitTicks = now
			return c.data 
		else:
			return func(*p,**pp) 
	__call.__name__ = func.__name__
	return __call
 
#=================== unit test ======================
def test_addbackResult():
	import json,datetime
	
	dic1 = json.loads(_addBackResult(-1, "eefsdafas错误信息"))
	assert len(dic1) == 2 
	assert dic1["errorno"] == -1 
	assert dic1["errormsg"] == "eefsdafas错误信息" 

	dic2 = {}
	dic2["key1"] = 1
	dic2["key2"] = "string"
	dic2["date"] = datetime.datetime(1998,12,31,11,45,22)
	dic2["list"] = [1,2,3,4]
	dic2 = json.loads(_addBackResult(2, "aaa", dic2)) 
	assert len(dic2) == 6 
	assert dic2["errorno"] == 2 
	assert dic2["errormsg"] == "aaa" 
	assert dic2["key1"] == 1 
	assert dic2["key2"] == "string" 
	assert dic2["date"] == "1998-12-31 11:45:22" 
	assert dic2["list"] ==  [1,2,3,4] 

if __name__ == '__main__':
	utility.run_tests()



