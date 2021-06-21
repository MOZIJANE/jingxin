# coding: utf-8
# author: ycat
# date: 2020-04-19
# desc: 零网络配置
#https://python-zeroconf.readthedocs.io/en/latest/api.html 
import os,sys
import socket
import zeroconf #pip install zeroconf
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import log

class serviceInfo:
	def __init__(self,s):
		self.params = {}
		#ServiceInfo(type='_robokitV2._tcp.local.', name='Robokit:SWX001._robokitV2._tcp.local.', addresses=[b'\xc0\xa8\xfc\xba'], port=1234, weight=0, priority=0, server='Robokit:SWX001._robokitV2._tcp.local.', properties={})
		self.typeName = s.type[1:-len("._tcp.local.")]
		self.name = s.name[0:s.name.find(".")]
		self.port = s.port
		if s.port is None:
			self.port = 0
		self.ip = socket.inet_ntoa(s.addresses[0])
		
		self.weight = s.weight
		self.priority = s.priority
		for p in s.properties:
			v = s.properties[p]
			if isinstance(v,bytes):
				v = v.decode("utf-8")
			self.params[p.decode("utf-8")] = v
		
	def __str__(self):
		return "zconf: type=%s, name=%s, addr=%s:%d, params="%(self.typeName,self.name,self.ip,self.port)+str(self.params)
		

g_zeroconf = zeroconf.Zeroconf()
	

def register(typeName,name,ip,port,params=None):
	info = _getServer(typeName,name,ip=ip,port=port,params=params)
	g_zeroconf.register_service(info)
	log.info("registering zeroconf service:",typeName+"."+name)
	
def unregister(typeName,name):
	info = _getServer(typeName,name,ip="0.0.0.0",port=0,params=None)
	g_zeroconf.unregister_service(info)
	log.info("unregister zeroconf service:",typeName+"."+name)
	
def unregister_all():
	g_zeroconf.unregister_all_services()
	log.info("unregister all zeroconf service")

#callback定义 callback(serviceInfo) 
def listen(typeName,addCallback=None,removeCallback=None):
	browser = zeroconf.ServiceBrowser(g_zeroconf,"_"+typeName+"._tcp.local.",_registerCallback(addCallback,removeCallback))
	
def _getServer(typeName,name,ip,port,params):
	t = "_%s._tcp.local."%typeName
	n = "%s.%s"%(name,t)
	pp = {}
	if params:
		for p in params:
			pp[p] = str(params[p])
	return zeroconf.ServiceInfo(t,n,
		addresses=[socket.inet_aton(ip)],
		properties = pp,
		port=port)
	
class _registerCallback:
	def __init__(self,addCallback,removeCallback):
		self.addCallback = addCallback
		self.removeCallback = removeCallback
		
	def remove_service(self, zeroconf, type, name):
		info = zeroconf.get_service_info(type, name)
		if info is None:
			log.info("remove zconf: can't find:",type,name)
			return
		s = serviceInfo(info)
		if self.removeCallback:
			self.removeCallback(s)
		log.info("remove",s)

	def add_service(self, zeroconf, type, name):
		info = zeroconf.get_service_info(type, name)
		if info is None:
			log.error("add zconf: can't find:",type,name)
			return
		s = serviceInfo(info)
		if self.addCallback:
			self.addCallback(s)
		log.info("add",s)



	
	
if __name__ == "__main__":
	import time
	register("ycatType","ycat_name2",ip="0.0.0.0",port=0,params={"y333":100,"b":"22"})
	listen("ycatType")
	while True:
		time.sleep(4)
		unregister("ycatType","ycat_name")
		break
	time.sleep(10)


