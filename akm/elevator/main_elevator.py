import sys, os
import bottle
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import log
import utility
import webutility
import scadaUtility
import elevator.elevatorMgr as elevatorMgr
 
@scadaUtility.get('/api/elevator/go')
def urlElevatorgo():
	id= webutility.get_param("id")
	f= webutility.get_param("floor")
	elevatorInfo= elevatorMgr.getElevator(id)
	ret = elevatorInfo.gofloor(f)
	return ret


@scadaUtility.get('/api/elevator/status')
def urlElevatorstatus():
	id= webutility.get_param("id")
	elevatorInfo = elevatorMgr.getElevator(id)
	ret= elevatorInfo.status()
	return ret
 
@scadaUtility.get('/api/elevator/hold')
def urlElevatoropen():
	id= webutility.get_param("id")
	elevatorInfo = elevatorMgr.getElevator(id)
	ret = elevatorInfo.open()
	return ret

@scadaUtility.get('/api/elevator/unhold')
def urlElevatoropen():
	id= webutility.get_param("id")
	elevatorInfo = elevatorMgr.getElevator(id)
	ret = elevatorInfo.close()
	return ret

#for uwsgi 
app = application = bottle.default_app()

webutility.add_ignore('elevator/status')

if __name__ == '__main__':
	if webutility.is_bottle():
		utility.start()
	webutility.run()
else:
	pass