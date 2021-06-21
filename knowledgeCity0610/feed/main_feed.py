import os
import sys,time
import bottle
import utility
import datetime
import feed.setup
if __name__ == '__main__':
	feed.setup.setCurPath(__file__)
	
import meta as m
import webutility
import log
import scadaUtility
import mongodb as db
import runTask
from feed import feedMgr
import agvCtrl.agvApi as agvApi
import agvDevice.jackApi as jackApi
# import agvCtrl.mapMgr

# class mapSel(m.customSelect):
	# def __init__(self):
		# m.customSelect.__init__(self)
		
	# def items(self, parentId):
		# mapList = agvCtrl.mapMgr.getMapList()
		# return [{"value": mapList[i]["id"], "label": mapList[i]["id"]} for i in range(len(mapList))]

# @m.table("u_loc_info","工位信息",)
# @m.field(id="_id",name="工位",unique=True, type=str, rules=[m.require()])
# @m.field(id="floorId",name="地图", type=str, editCtrl=mapSel(), rules=[m.require()])
# @m.field(id="location",name="点位", type=str, rules=[m.require()])
# @m.field(id="location",name="前置点", type=str, rules=[m.require()])
# @m.field(id="p_direction",name="方向", type=float, rules=[m.require()])
# class seatManager(m.manager):
	# def __init__(self):
		# m.manager.__init__(self)

 
@scadaUtility.post('/api/manual/feed')
def urlFeed():
	param = {
		"seat1": webutility.get_param("seat1"),
		"location1": webutility.get_param("location1"),
		"floorId1": webutility.get_param("floorId1"),
		"direction1": webutility.get_param("direction1"),
		"seat2": webutility.get_param("seat2"),
		"location2": webutility.get_param("location2"),
		"floorId2": webutility.get_param("floorId2"),
		"direction2": webutility.get_param("direction2")
	}
	# if param["floorId1"] != param["floorId2"]:
	# 	raise Exception("工位不在同一地图上")
	param["floorId"] = param["floorId1"]
	return {"taskId": runTask.feedTask(param)}
 
@scadaUtility.post('/api/manual/tasklist')
def scadaTaskList():
	return feedMgr.getTaskList()
	
@scadaUtility.get('/api/manual/seat')
def getSeat():
	return feedMgr.getSeat()










#for uwsgi 
app = application = bottle.default_app()

if __name__ == '__main__':
	webutility.run()
else:
	pass