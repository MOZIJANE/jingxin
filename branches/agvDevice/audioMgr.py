import os
import sys
import time

import setup
if __name__ == "__main__":
	setup.setCurPath(__file__)
	
import utility
import log
if utility.is_test(): 
	import driver.seerAgv.mockAgvCtrl as agvCtrl 
else:
	import driver.seerAgv.agvCtrl as agvCtrl
 
# 自研车体
def playAudio(agvId , name, loop):
	ret = agvCtrl.playAudio(agvId,name,loop)
	return ret

def pauseAudio(agvId):
	ret = agvCtrl.pauseAudio(agvId)
	return ret

def resumeAudio(agvId):
	ret = agvCtrl.resumeAudio(agvId)
	return ret