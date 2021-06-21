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


def rollerSetUnit(agvId, unitId):
	agvCtrl.rollerSetUnit(agvId, unitId=unitId)


def rollerClampOpen(agvId, dir):
	agvCtrl.clampOpen(agvId, direction=dir)


def rollerClampClose(agvId, dir):
	agvCtrl.clampClose(agvId, direction=dir)


def finishButtonStatus(agvId):
	return agvCtrl.finishButtonStatus(agvId)

def rollerClampStatus(agvId, dir):
	return agvCtrl.clampStatus(agvId, direction=dir)


def rollerBackLoad(agvId, unitId):
	agvCtrl.rollerSetUnit(agvId, unitId=unitId)
	agvCtrl.rollerBackLoad(agvId)


def rollerBackUnload(agvId, unitId):
	agvCtrl.rollerSetUnit(agvId, unitId=unitId)
	agvCtrl.rollerBackUnload(agvId)


def rollerFrontLoad(agvId, unitId):
	agvCtrl.rollerSetUnit(agvId, unitId=unitId)
	agvCtrl.rollerFrontLoad(agvId)


def rollerFrontUnload(agvId, unitId):
	agvCtrl.rollerSetUnit(agvId, unitId=unitId)
	agvCtrl.rollerFrontUnload(agvId)


def rollerLoadStatus(agvId, unitId):
	return agvCtrl.rollerLoadStatus(agvId, unitId=unitId)


def rollerUnloadStatus(agvId, unitId):
	return agvCtrl.rollerUnloadStatus(agvId, unitId=unitId)


def unitStatus(agvId, unitId):
	return agvCtrl.unitStatus(agvId, unitId=unitId)


def rollerStop(agvId):
	agvCtrl.rollerStop(agvId)


def rollerReset(agvId):
	agvCtrl.rollerReset(agvId)


def rollerDeviceInfo(agvId):
	return agvCtrl.rollerDeviceInfo(agvId)
