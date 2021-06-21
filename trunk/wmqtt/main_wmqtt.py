#-*- coding: utf-8 -*--
import json
import platform  
import sys,os
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)  
import scadaUtility
import mqttQueue
import webutility
import utility
import bottle
import log

#创建一个mqtt队列
#maxsize 代表保存多少数据，比如1只保存最后一条数据，1000保存最新1000条数据 
#timeSec:代表多少秒没有访问，自动清除session 
@scadaUtility.get('/api/wmqtt/create') 	
def create():
	s = webutility.get_param("session")
	c = webutility.get_param("maxSize")
	t = webutility.get_param("timeSec")
	mqttQueue.create(s,int(c),int(t))
	
#	订阅者的Topic name 
@scadaUtility.get('/api/wmqtt/register') 	
def register():
	s = webutility.get_param("session")
	t = webutility.get_param("topic")
	mqttQueue.subscribe(s,t)
	
@scadaUtility.get('/api/wmqtt/send')
def send(topic,data,qos=0):
	t = webutility.get_param("topic")
	d = webutility.get_param("data")
	mqttQueue.send(t,d)
	
#返回topic为None，表示没有收到数据，则应该休眠后调用 
#否则收到数据，这时应该继续调用
@scadaUtility.get('/api/wmqtt/get')
def get():
	try:
		s = webutility.get_param("session")
		ret = mqttQueue.get(s)
		if ret is None:
			return {"topic":None,"data":None}
		return {"topic":ret[0],"data":ret[1]}
	except Exception as e:
		log.exception("wmqtt get",e)
		raise scadaUtility.WmqttException(str(e))

	
#for uwsgi 
app = application = bottle.default_app()

webutility.add_ignore('/api/wmqtt/get')

if __name__ == '__main__':
	webutility.add_ignore("api/wmqtt/get")
	if webutility.is_bottle():
		utility.start() 
	webutility.run()
else:
	pass




