import sys, os
import bottle
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import log
import utility
import webutility
import scadaUtility
if utility.is_test():
	import remoteio.mockRemoteioApi as ioMgr
else:
	import remoteio.remoteioMgr as ioMgr


@scadaUtility.get('/api/remoteio/writeDO')
def urlwriteDO():
	id= webutility.get_param("id")
	index= webutility.get_param_int("index")
	value= webutility.get_param_int("value")
	return ioMgr.writeDO(id,index,value)

@scadaUtility.get('/api/remoteio/writeDOList')
def urlwriteDOList():
	id= webutility.get_param("id")
	value= webutility.get_param("value")
	return ioMgr.writeDOList(id,value)

@scadaUtility.get('/api/remoteio/readDI')
def urlReadDI():
	id= webutility.get_param("id")
	index= webutility.get_param_int("index")
	return ioMgr.readDI(id,index)

@scadaUtility.get('/api/remoteio/readDO')
def urlReadDO():
	id= webutility.get_param("id")
	index= webutility.get_param_int("index")
	return ioMgr.readDO(id,index)

@scadaUtility.get('/api/remoteio/readDIList')
def urlReadDIList():
	id= webutility.get_param("id")
	return ioMgr.readDIList(id)

@scadaUtility.get('/api/remoteio/readDOList')
def urlReadDOList():
	id= webutility.get_param("id")
	return ioMgr.readDOList(id)

#测试用
@scadaUtility.get('/api/remoteio/writeDI')
def urlwriteDI():
	id= webutility.get_param("id")
	index= webutility.get_param_int("index")
	value= webutility.get_param_int("value")
	return ioMgr.writeDI(id,index,value)

@scadaUtility.get('/api/remoteio/writeDIList')
def urlwriteDIList():
	id= webutility.get_param("id")
	value= webutility.get_param("value")
	return ioMgr.writeDIList(id,value)

#for uwsgi 
app = application = bottle.default_app()

if __name__ == '__main__':
	webutility.run()
else:
	pass