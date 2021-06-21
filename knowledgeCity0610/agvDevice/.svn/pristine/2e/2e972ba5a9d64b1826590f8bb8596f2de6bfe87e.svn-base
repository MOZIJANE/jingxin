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




def forkLoad(agvId):
	agvCtrl.forkUpOpen(agvId)


def forkUnload(agvId):
	agvCtrl.forkDownOpen(agvId)


def forkUpStatus(agvId):
	return agvCtrl.forkUpStatus(agvId)


def forkDownStatus(agvId):
	return agvCtrl.forkDownStatus(agvId)

def forkReset(agvId):
	agvCtrl.forkUpClose(agvId)
	agvCtrl.forkDownClose(agvId)




