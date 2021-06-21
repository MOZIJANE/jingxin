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
	import remoteio.remoteioMgr_old as ioMgrOld


@scadaUtility.get('/api/remoteio/writeDO')
def urlwriteDO():
	id= webutility.get_param("id")
	index= webutility.get_param_int("index")
	value= webutility.get_param_int("value")
	return ioMgr.writeDO(id,index,value)

	
@scadaUtility.get('/api/remoteioOld/writeDO')
def urlwriteDO_old():
	id= webutility.get_param("id")
	index= webutility.get_param_int("index")
	value= webutility.get_param_int("value")
	return ioMgrOld.writeDO(id,index,value)

	
@scadaUtility.get('/api/remoteio/writeStatusDO')
def urlwriteStatusDO():
	id= webutility.get_param("id")
	index= webutility.get_param_int("index")
	value= webutility.get_param_int("value")
	return ioMgr.writeStatusDO(id,index,value)

@scadaUtility.get('/api/remoteio/writeStatusD100')
def urlwriteStatusD100():
	id= webutility.get_param("id")
	index= webutility.get_param_int("index")
	value= webutility.get_param_int("value")
	return ioMgr.writeStatusD100(id,index,value)

@scadaUtility.get('/api/remoteio/writeStatusD104')
def urlwriteStatusD104():
	id= webutility.get_param("id")
	index= webutility.get_param_int("index")
	value= webutility.get_param_int("value")
	return ioMgr.writeStatusD104(id,index,value)

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
	
@scadaUtility.get('/api/remoteio_old/readDI')
def urlReadDI_old():
	id= webutility.get_param("id")
	index= webutility.get_param_int("index")
	return ioMgrOld.readDI(id,index)

	
@scadaUtility.get('/api/remoteio/readDO')
def urlReadDO():
	id= webutility.get_param("id")
	index= webutility.get_param_int("index")
	return ioMgr.readDO(id,index)

@scadaUtility.get('/api/remoteio/readDIList')
def urlReadDIList():
	id= webutility.get_param("id")
	return ioMgr.readDIList(id)
	
	
@scadaUtility.get('/api/remoteio_old/readDIList')
def urlReadDIList_old():
	id= webutility.get_param("id")
	return ioMgrOld.readDIList(id)


@scadaUtility.get('/api/remoteio/readStatusList')
def urlreadStatusList():
	id= webutility.get_param("id")
	return ioMgr.readStatusList(id)

@scadaUtility.get('/api/remoteio/readStatusListD100')
def urlreadStatusListD100():
	id= webutility.get_param("id")
	return ioMgr.readStatusListD100(id)

@scadaUtility.get('/api/remoteio/readStatusListD104')
def urlreadStatusListD104():
	id= webutility.get_param("id")
	return ioMgr.readStatusListD104(id)

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


@scadaUtility.get('/api/remoteio/writeStatusDOList')
def urlwriteStatusDOList():
	id= webutility.get_param("id")
	value= webutility.get_param("value")
	return ioMgr.writeStatusDOList(id,value)
@scadaUtility.get('/api/remoteio/writeStatusD100List')
def urlwriteStatusD100List():
	id= webutility.get_param("id")
	value= webutility.get_param("value")
	return ioMgr.writeStatusD100List(id,value)

@scadaUtility.get('/api/remoteio/writeStatusD104List')
def urlwriteStatusD104List():
	id= webutility.get_param("id")
	value= webutility.get_param("value")
	return ioMgr.writeStatusD104List(id,value)
#for uwsgi 
app = application = bottle.default_app()
webutility.add_ignore('/api/remoteio/readStatusListD100')
webutility.add_ignore('/api/remoteio/readStatusListD104')
webutility.add_ignore('/api/remoteio/readDOList')

if __name__ == '__main__':
	webutility.run()
else:
	pass