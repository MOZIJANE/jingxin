import os
import sys
import time

import setup
if __name__ == "__main__":
    setup.setCurPath(__file__)
    
import utility
import alarm.alarmApi
import log
if utility.is_test(): 
    import driver.seerAgv.mockAgvCtrl as agvCtrl 
else:
    import driver.seerAgv.agvCtrl as agvCtrl

import local 
import json 



def _loadAgvList():
    proName = local.get("project","name")
    if utility.is_test():
        proName = 'test'
    file = "/../agvCtrl/projects/"+proName+"/" + local.get("project","agvcfg")  
    with open(os.path.abspath(os.path.dirname(__file__) + file), 'r') as f:        
        agvList = {}
        aa = json.load(f)
        for a in aa:
            if aa[a]["enable"].lower() == "false":
                continue
            agvList[a] = aa[a]
        return agvList
g_agvList = _loadAgvList()

def _getAgvType(agvId):
    type_ = g_agvList[agvId]["type"]
    return g_agvType[type_]

def _loadAgvType():
    proName = local.get("project","name") 
    if utility.is_test():
        proName = 'test'
    file = "/../agvCtrl/projects/"+proName+"/" + local.get("project","agvType")  
    with open(os.path.abspath(os.path.dirname(__file__) + file), 'r') as f:        
        agvTypeDict = {}
        aa = json.load(f)
        for a in aa:
            agvTypeDict[a] = aa[a]
        return agvTypeDict
g_agvType = _loadAgvType()

# 自研车体
def rotationReset(agvId , timeout):
    ret = agvCtrl.rotationReset(agvId)
    return _rotation(agvId=agvId,target=None, timeout=timeout,action="reset")
     
def rotationLeft(agvId , target, timeout):
    ret = agvCtrl.rotationLeft(agvId,target=target)
    return _rotation(agvId=agvId, target=target, timeout=timeout,action="left")
    
def rotationRight(agvId , target, timeout):
    agvCtrl.rotationRight(agvId,target=target)
    return _rotation(agvId=agvId, target=target, timeout=timeout,action="right")
     
def rotationStop(agvId):
    agvCtrl.rotationStop(agvId)
    return {}
    
def rotationDistanceStatus(agvId):
    return agvCtrl.rotationDistanceStatus(agvId)
    
def rotationResetStatus(agvId):
    return agvCtrl.rotationResetStatus(agvId)
    

def rotationClear(agvId,timeout):
    count = 0
    if _getAgvType(agvId)['jackType'].lower()=="io": 
        timeout = 10
        
        while count<5:
            agvCtrl.rotationClear(agvId)
            ret = _rotation(agvId=agvId,target=None,timeout=timeout,action="clear")
            count += 1
            if ret=={}:
                return ret
            
    else:
        agvCtrl.rotationClear(agvId)
        return _rotation(agvId=agvId,target=None, timeout=timeout,action="clear")



def _rotation(agvId,target,timeout,action):
    for i in range(int(timeout)):
        time.sleep(1)
        status = None
        
        if action == "left" :
            status = agvCtrl.rotationLeftStatus(agvId, target)
        elif action == "right":
            status = agvCtrl.rotationRightStatus(agvId, target)
        elif action == "reset":
            status = agvCtrl.rotationResetStatus(agvId)
        elif action == "clear":
            status = agvCtrl.rotationClearStatus(agvId)
        ios = agvCtrl.readIOs(agvId)
        log.info('_rotation in rotationMgr:', agvId, target, ios['DO'])
        if status != None :
            if "isRotationALarm" in status and status["isRotationALarm"] != 0:
                msg = "rotation device has alarm"
                alarm.alarmApi.alarm(moid=agvId, typeId=49995, desc=msg, domain="agv")
                raise Exception(msg+",action:"+action)
            else:
                alarm.alarmApi.clear(moid=agvId, typeId=49995, domain="agv")
            if "status" in status and status["status"]:
                log.info(agvId,"rotation %s status:"%action, status["status"])
                return {}
    else:
        # agvCtrl.cancelTask(agvId) # 自研车体不需要
        error = agvId + "rotation" + " action：" + action + ",timeout=" + timeout 
        raise Exception(error) 
