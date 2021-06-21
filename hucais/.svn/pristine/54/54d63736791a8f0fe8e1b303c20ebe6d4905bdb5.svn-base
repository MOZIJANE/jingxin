import os
import sys
import bottle
import datetime
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
	
import meta as m
import webutility
import scadaUtility
import mongodb as db
import runTask
import runTaskHucais
import feedMgr
import agvCtrl.mapMgr
import local

class mapSel(m.customSelect):
	def __init__(self):
		m.customSelect.__init__(self)
		
	def items(self, parentId):
		mapList = agvCtrl.mapMgr.getMapList()
		return [{"value": mapList[i]["id"], "label": mapList[i]["id"]} for i in range(len(mapList))]

@m.table("u_loc_info","工位信息",)
@m.field(id="_id",name="工位",unique=True, type=str, rules=[m.require()])
@m.field(id="floorId",name="地图", type=str, editCtrl=mapSel(), rules=[m.require()])
@m.field(id="location",name="点位", type=str, rules=[m.require()])
@m.field(id="location",name="前置点", type=str, rules=[m.require()])
@m.field(id="p_direction",name="方向", type=float, rules=[m.require()])
class seatManager(m.manager):
	def __init__(self):
		m.manager.__init__(self)

 
@scadaUtility.post('/api/agv/feed')
def urlFeed():
	proName = local.get("project","name")
	if proName=='hucais':
		param = {
			"source": webutility.get_param("source"),
			"target": webutility.get_param("target")
		}
		return {"taskId": runTaskHucais.feedTask(param)}
 
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
 
@scadaUtility.post('/api/agv/tasklist')
def scadaTaskList():
	return feedMgr.getTaskList()
	
@scadaUtility.get('/api/agv/seat')
def getSeat():
	return feedMgr.getSeat()

@scadaUtility.get('/api/scada/clearLoc')
def setLoc():
	locId = webutility.get_param("locId"),
	status = webutility.get_param("status"),
	return feedMgr.setLoc(locId,status)
	
#for uwsgi 
app = application = bottle.default_app()

if __name__ == '__main__':
	webutility.run()
else:
	pass