import sys,os 
import time
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
	
import utility
import log
if utility.is_test(): 
	import driver.seerAgv.mockAgvCtrl as agvCtrl 
else:
	import driver.seerAgv.agvCtrl as agvCtrl
	
def getPgv(agvId):
	return {"tag_value": agvCtrl.statusPgv(agvId)["pgvs"][0]["tag_value"]}

if __name__ == '__main__':
	print (getPgv("AGV02"))
	while True:
		time.sleep(2)


