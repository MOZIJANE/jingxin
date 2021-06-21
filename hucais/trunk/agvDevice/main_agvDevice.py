import sys, os
import bottle
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import log
import webutility
import scadaUtility
import utility 
import jackMgr
import rotationMgr
import pgvMgr
import rollerMgr
import rollerPlusMgr
import audioMgr
 
# jack start
@scadaUtility.get('/api/agv/jackup')
def urlJackup():
	agvId= webutility.get_param("agv")
	timeout= webutility.get_param_int("timeoutSec",90)
	loc = webutility.get_param("loc")
	return jackMgr.jackUp(agvId=agvId, timeout=timeout,loc=loc)
	
@scadaUtility.get('/api/agv/jackdown')
def urlJackdown():
	agvId= webutility.get_param("agv")
	timeout= webutility.get_param_int("timeoutSec",90)
	loc = webutility.get_param("loc")
	return jackMgr.jackDown(agvId=agvId, timeout=timeout,loc=loc)

@scadaUtility.get('/api/agv/jackupstatus')
def urlJackUpStatus():
	agvId= webutility.get_param("agv")
	timeout= webutility.get_param_int("timeoutSec",90)
	return jackMgr.jackUpStatus(agvId=agvId, timeout=timeout)

@scadaUtility.get('/api/agv/jackdownstatus')
def urlJackDownStatus():
	agvId= webutility.get_param("agv")
	timeout= webutility.get_param_int("timeoutSec",90)
	return jackMgr.jackDownStatus(agvId=agvId, timeout=timeout)

@scadaUtility.get('/api/agv/jackstop')
def urlJackstop():
	agvId= webutility.get_param("agv")
	return jackMgr.jackStop(agvId=agvId)

@scadaUtility.get('/api/agv/jackdeviceinfo')
def urlJackDeviceInfo():
	agvId= webutility.get_param("agv")
	return jackMgr.jackDeviceInfo(agvId=agvId)

@scadaUtility.get('/api/agv/jackDistanceStatus')
def urlJackDistanceStatus():
	agvId= webutility.get_param("agv")
	return jackMgr.jackDistanceStatus(agvId=agvId)
# jack end
  
# rotation start
@scadaUtility.get('/api/agv/rotationreset')
def urlRotationreset():
	agvId = webutility.get_param("agv")
	timeout = webutility.get_param("timeoutSec")
	return rotationMgr.rotationReset(agvId,timeout)
	

@scadaUtility.get('/api/agv/rotationclear')
def urlRotationclear():
	agvId = webutility.get_param("agv")
	timeout = webutility.get_param("timeoutSec")
	return rotationMgr.rotationClear(agvId,timeout)
	 
@scadaUtility.get('/api/agv/rotationleft')
def urlRotationleft():
	agvId = webutility.get_param("agv")
	timeout = webutility.get_param("timeoutSec")
	target = webutility.get_param_int("target")
	return rotationMgr.rotationLeft(agvId,target,timeout)
	
@scadaUtility.get('/api/agv/rotationright')
def urlRotationright():
	agvId = webutility.get_param("agv")
	timeout = webutility.get_param("timeoutSec")
	target = webutility.get_param_int("target")
	return rotationMgr.rotationRight(agvId,target,timeout)
	
@scadaUtility.get('/api/agv/rotationstop')
def urlRotationstop():
	agvId = webutility.get_param("agv")
	return rotationMgr.rotationStop(agvId)
	
@scadaUtility.get('/api/agv/rotationdistancestatus')
def urlRotationdistanceStatus():
	agvId = webutility.get_param("agv")
	return rotationMgr.rotationDistanceStatus(agvId)
	
# rotation end

# pgv start
@scadaUtility.get("/api/agv/getpgv")
def urlGetPgv():
	agvId = webutility.get_param("agv")
	return pgvMgr.getPgv(agvId)
	
# pgv end
	

# roller start

@scadaUtility.get('/api/agv/rollerSetUnit')
def urlRollerSetUnit():
	agvId = webutility.get_param("agv")
	unitId = webutility.get_param("unitId")
	return rollerMgr.rollerSetUnit(agvId, unitId=unitId)


@scadaUtility.get('/api/agv/rollerClampOpen')
def rollerClampOpen():
	agvId = webutility.get_param("agv")
	dir = webutility.get_param("dir")
	return rollerMgr.rollerClampOpen(agvId, dir=dir)

@scadaUtility.get('/api/agv/rollerClampClose')
def rollerClampClose():
	agvId = webutility.get_param("agv")
	dir = webutility.get_param("dir")
	return rollerMgr.rollerClampClose(agvId, dir=dir)

@scadaUtility.get('/api/agv/rollerClampStatus')
def rollerClampStatus():
	dir = webutility.get_param("dir")
	agvId = webutility.get_param("agv")
	return rollerMgr.rollerClampStatus(agvId, dir=dir)


@scadaUtility.get('/api/agv/finishButtonStatus')
def finishButtonStatus():
	agvId = webutility.get_param("agv")
	return rollerMgr.finishButtonStatus(agvId)

@scadaUtility.get('/api/agv/rollerBackLoad')
def urlRollerBackLoad():
	agvId = webutility.get_param("agv")
	unitId = webutility.get_param("unitId")
	return rollerMgr.rollerBackLoad(agvId, unitId=unitId)


@scadaUtility.get('/api/agv/rollerBackUnload')
def urlRollerBackUnload():
	agvId = webutility.get_param("agv")
	unitId = webutility.get_param("unitId")
	return rollerMgr.rollerBackUnload(agvId, unitId=unitId)


@scadaUtility.get('/api/agv/rollerFrontLoad')
def urlRollerFrontLoad():
	agvId = webutility.get_param("agv")
	unitId = webutility.get_param("unitId")
	return rollerMgr.rollerFrontLoad(agvId, unitId=unitId)
	
@scadaUtility.get('/api/agv/rollerFrontUnload')
def urlRollerFrontUnload():
	agvId = webutility.get_param("agv")
	unitId = webutility.get_param("unitId")
	return rollerMgr.rollerFrontUnload(agvId, unitId=unitId)


@scadaUtility.get('/api/agv/rollerLoadStatus')
def urlrollerLoadStatus():
	agvId = webutility.get_param("agv")
	unitId = webutility.get_param("unitId")
	return rollerMgr.rollerLoadStatus(agvId, unitId)


@scadaUtility.get('/api/agv/rollerUnloadStatus')
def urlrollerUnloadStatus():
	agvId = webutility.get_param("agv")
	unitId = webutility.get_param("unitId")
	return rollerMgr.rollerUnloadStatus(agvId, unitId)

	

	
@scadaUtility.get('/api/agv/unitStatus')
def urlUnitStatus():
	agvId = webutility.get_param("agv")
	unitId = webutility.get_param("unitId")
	return rollerMgr.unitStatus(agvId, unitId=unitId)
	
@scadaUtility.get('/api/agv/rollerStop')
def urlRollerStop():
	agvId = webutility.get_param("agv")
	return rollerMgr.rollerStop(agvId)
	
@scadaUtility.get('/api/agv/rollerReset')
def urlRollerReset():
	agvId = webutility.get_param("agv")
	return rollerMgr.rollerReset(agvId)
	
@scadaUtility.get('/api/agv/rollerDeviceInfo')
def urlRollerDeviceInfo():
	agvId = webutility.get_param("agv")
	return rollerMgr.rollerDeviceInfo(agvId)
	
# roller end

# rollerPlus start
@scadaUtility.get('/api/agv/rollerSetInit')
def urlrollerSetInit():
	agvId = webutility.get_param("agv")
	return rollerPlusMgr.rollerSetInit(agvId)

@scadaUtility.get('/api/agv/rollerRobotLoad')
def urlrollerRobotLoad():
	agvId = webutility.get_param("agv")
	unitId = webutility.get_param("unitId")
	return rollerPlusMgr.rollerRobotLoad(agvId, unitId)

@scadaUtility.get('/api/agv/rollerRobotUnLoad')
def urlrollerRobotUnLoad():
	agvId = webutility.get_param("agv")
	unitId = webutility.get_param("unitId")
	return rollerPlusMgr.rollerRobotUnLoad(agvId, unitId)

@scadaUtility.get('/api/agv/checkUnitStatus')
def urlcheckUnitStatus():
	agvId = webutility.get_param("agv")
	unitId = webutility.get_param("unitId")
	return rollerPlusMgr.checkUnitStatus(agvId, unitId)

@scadaUtility.get('/api/agv/rollerRobotStop')
def urlrollerRobotStop():
	agvId = webutility.get_param("agv")
	return rollerPlusMgr.rollerRobotStop(agvId)


@scadaUtility.get('/api/agv/rollerRes')
def urlrollerRes():
	agvId = webutility.get_param("agv")
	return rollerPlusMgr.rollerRes(agvId)

@scadaUtility.get('/api/agv/rollerEmergency')
def urlrollerEmergency():
	agvId = webutility.get_param("agv")
	return rollerPlusMgr.rollerEmergency(agvId)

# rollerPlus end




# audio start
@scadaUtility.get('/api/agv/playaudio')
def urlPlayAudio():
	agvId = webutility.get_param("agv")
	name = webutility.get_param("name")
	loop = webutility.get_param_bool("loop")
	return audioMgr.playAudio(agvId, name, loop)


@scadaUtility.get('/api/agv/resumeaudio')
def urlResumeAudio():
	agvId = webutility.get_param("agv")
	return audioMgr.resumeAudio(agvId)


@scadaUtility.get('/api/agv/stopaudio')
def urlStopAudio():
	agvId = webutility.get_param("agv")
	return audioMgr.stopaudio(agvId)
#for uwsgi 
app = application = bottle.default_app()

if __name__ == '__main__': 
	webutility.run()
else:
	pass