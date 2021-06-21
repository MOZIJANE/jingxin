
import os
import sys
import time
import json
import threading

import setup
if __name__ == "__main__":
    setup.setCurPath(__file__)
    
import log
import taskApi as taskApi
import agvApi
import agvDevice.jackApi as jackApi
import agvDevice.rollerPlusApi as rollerPlusApi
import agvDevice.audioApi as audioApi
import enhance
import mongodb as db
import lock as lockImp
import socket
import elevatorMgr
import local 
import utility
import agvList

if utility.is_test(): 
    import driver.seerAgv.mockAgvCtrl as agvCtrl 
else:
    import driver.seerAgv.agvCtrl as agvCtrl

# http://127.0.0.1:5550/api/agv/feed?source=tailor&target=product

# 1. 叫料
# /api/agv/feed
# source : tailor 裁剪 product 产线 buffer 缓冲区
# target

# 2. 查询
# /api/agv/tasklist
# (同兴森)

# 3.删除
#       
# （同兴森）

# 4.设置工位
# /api/scada/clearLoc
# locId
# status： 0 无货架 1货架空 2货架满

# 5. 查询工位
# /api/agv/seat
# Status： 0 无货架 1货架空 2货架满
# （同兴森）

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

finishEvent = enhance.event()
g_lockPrepoint = {}
g_lockp = lockImp.create("PDA runTask.g_lock")

g_init = None 
def _init():
    global g_init 
    if g_init is None:
        g_init = 'feed'
        agvApi.init("scadaTask")

def feedTask(param):
    _init()
    t_task = feed(param)
    t_task.run()
    log.info('Got a task from feed Hucais %s:s %s'%(t_task.taskId, t_task))
    return t_task.taskId 

def formatLoc(mapId, loc):
    if mapId and loc.find(".") == -1:
        return mapId + '.' + loc 
    return loc 

g_workPlaceNone = []
g_workPlaceEmpty = []
g_workPlaceFull = []

class feed:
    def __init__(self, param):
        param["taskType"] = "feed"
        self.m_lock = threading.RLock()
        self.param = param
        self.status = 0 
        self.restartN = 0 
        self.isRunning = False 
        self.s_lock = lockImp.create("feed.s_lock")
        self.s_info = None 
        self.t_info = None 
        # g_workPlaceNone = []
        # g_workPlaceEmpty = []
        # g_workPlaceFull = []
        self.param["sourceID"]=None
        self.param["targetID"]=None
        self.taskStep = "waiting"

        self._load(param)
        self.param["taskName"] = "从%s 运送货架到 %s"%(self.param["seat1"],self.param["seat2"])
        self.taskId = taskApi.add(taskName=self.param["taskName"], taskType="feed",msg="创建任务：%s" % self.param["taskName"])
        taskApi.update(self.taskId, taskName=param["taskName"])
        
        self._taskThread = threading.Thread(target=self._taskFunc)

        
    @lockImp.lock(g_lockp)
    def islocAvailable(self,floorId,loc):
        return formatLoc(floorId,loc) not in g_lockPrepoint
    
    @lockImp.lock(g_lockp)
    def lockLoc(self,taskId,floorId,loc):
        key = formatLoc(floorId,loc)
        if key not in g_lockPrepoint:
            log.info("task: prepoint locked ",self.taskId,key)
            g_lockPrepoint[key] = taskId
            return True
        else:
            if g_lockPrepoint[key] == taskId:
                log.info("task: same prepoint",self.taskId,key)
                return True
            log.warning("task: prepoint locked",self.taskId,key,"failed, lock by",g_lockPrepoint[key])
            return False
            
    @lockImp.lock(g_lockp)
    def unlockLoc(self,floorId,loc): 
        key = formatLoc(floorId,loc)
        if key in g_lockPrepoint :
            log.info("task: prepoint released ",self.taskId,key)
            del g_lockPrepoint[key]
        
    @lockImp.lock(g_lockp)
    def clearLoc(self):
        rr = []
        for key in g_lockPrepoint:
            if g_lockPrepoint[key] == self.taskId:
                log.info("task: prepoint released2 ",self.taskId,key)
                rr.append(key)
        for k in rr:
            del g_lockPrepoint[k]

    def _load(self,param):
        ds = db.find("u_loc_info",{"_id": {"$in": [param["seat1"],param["seat2"]]}})
        while ds.next():
            if ds["_id"] == param["seat1"]:
                self.s_info = {
                        "prepoint": ds["prepoint"],
                        "location": ds["location"],
                        "floorId": ds["floorId"],
                        "direction": ds["direction"],
                        "WorkPlace": ds["WorkPlace"],
                        "payloadId": ds["payloadId"],
                        "p_direction": ds["p_direction"]
                    }
            elif ds["_id"] == param["seat2"]:
                self.t_info = {
                        "prepoint": ds["prepoint"],
                        "location": ds["location"],
                        "floorId": ds["floorId"],
                        "direction": ds["direction"],
                        "WorkPlace": ds["WorkPlace"],
                        "payloadId": ds["payloadId"],
                        "p_direction": ds["p_direction"]
                    }
        if self.s_info is None and self.t_info is None:
            raise Exception("can't find source-%s and target-%s info"%(param["source"],param["target"]))
        elif self.s_info is None:
            raise Exception("can't find source-%s info"%param["source"])
        elif self.t_info is None:
            raise Exception("can't find target-%s info"%(param["target"]))
    
    def run(self):
        if not self.isRunning:
            self.restartN = 0 
            self.isRunning = True
            self._taskThread.start()
    
    def _taskFunc(self):
        self.count = 0
        self.msg = ''
        while self.isRunning:
            try:
                if self.taskStep == "fail":
                    taskApi.fail(self.taskId, self.msg)
                    self.status = 2
                    self.updataStaus()
                    self._release()
                    break
                elif self.taskStep == "finish":
                    log.info("taskStepfinishfinishfinishfinishfinishfinish")
                    taskApi.finish(self.taskId, msg="任务成功")
                    self._release()
                    break
                elif not self.handle():
                    log.info(str(self),self.taskStep,"error")
                    time.sleep(2)
                    continue 
            except (ConnectionResetError,ConnectionAbortedError,socket.timeout,IOError) as e:
                log.exception("taskFunc:"+str(self),e)
                time.sleep(2)
                continue
            except Exception as e:
                log.exception("taskFunc2:"+str(self),e)
                taskApi.update(self.taskId, step=self.taskStep, msg=e)
                break
            time.sleep(1)
        # self._release()
        # self._goHome()
        self.isRunning = False
        log.info("task: stop",self)
    
    def handle(self):
        if self.taskStep == "waiting":

            self.taskStep = 'waitForAgv'
            self.param["location"] = self.s_info["location"]
            self.param["floorId"] = self.s_info["floorId"]
            # self.param["floorId"] = self.s_info["WorkPlace"]
            taskApi.update(self.taskId, step=self.taskStep, msg="等待分配小车")
            return True
        elif self.taskStep == 'waitForAgv':
            if not self._callAgv():
                return False
            self.status = 1
            self.taskStep = 'goSource'
            self.param["taskId"] = self.taskId + "_1"
            self.param["location"] = self.s_info['location']
            taskApi.update(self.taskId, step=self.taskStep, msg="前往上料工位")
            self.param["agvId"] = self.agvId
            self.updataStaus()
            # taskApi.update(self.taskId, step=self.taskStep, msg="检测下降")
            return True

        elif self.taskStep == "goSource":
            if not self._moveAgv():
                return False
            taskApi.update(self.taskId, step=self.taskStep, msg="等待上料确认")
            self.taskStep = "goSourceMoving"
            return True
        elif self.taskStep == "jackUpWP":
            if not self._audioPlay(name = 'arriveUp'):
                time.sleep(2)
                return False
            taskApi.update(self.taskId, step=self.taskStep, msg="播放语音")
            self.taskStep = "audioPlayUp"
            return True
        elif self.taskStep == "audioPlayUp":
            if not self.getUnitLoadStatus(self.agvId,1):
                if self.count > 300:
                    self.step = "fail"
                    self.msg = "检查小车上料超时"
                self.count += 1
                return False
            self.canReleaseAgv = True
            self.taskStep ="waitDestPreLoc"
            taskApi.update(self.taskId, step=self.taskStep, msg="等待目标位置%s前置点锁"%self.t_info["prepoint"])
            return True
        elif self.taskStep == "waitDestPreLoc":
            self._stopAudio()
            self.taskStep = "goTarget"
            self.param["floorId"] = self.t_info["floorId"]
            self.param["taskId"] = self.taskId + "_2"
            self.param["location"] = self.t_info["location"]
            taskApi.update(self.taskId, step=self.taskStep, msg="前往下料点")
            return True 
        elif self.taskStep == "goTarget":
            if not self._moveAgv():
                return False
            taskApi.update(self.taskId, step=self.taskStep, msg="等待下料确认")
            self.taskStep = "goTargetMoving"
            return True
        elif self.taskStep == "jackDown":
            if not self._audioPlay(name = 'arriveDown'):
                time.sleep(2)
                return False
            taskApi.update(self.taskId, step=self.taskStep, msg="等待下料确认")
            self.taskStep = "audioPlayDown"
            return True
        elif self.taskStep == "audioPlayDown":
            if not self.getUnitLoadStatus(self.agvId, 1):
                if self.count > 300:
                    self.step = "fail"
                    self.msg = "检查小车下料超时"
                self.count += 1
                return False
            self.taskStep = "stopPlayDown"
            taskApi.update(self.taskId, step=self.taskStep, msg="完成下料")
            self.status = 0
            self.updataStaus()
            self.canReleaseAgv = True
            # self.isRunning = False
            # self._release()
            return True
        elif self.taskStep == "stopPlayDown":
            self._stopAudio()
            self.taskStep = "finish"
            return True


        else:
            return True
    
    def updateDB(self):
        db.update_one("u_loc_info",{"_id": self.param["seat1"]},{"status":0})
        db.update_one("u_loc_info",{"_id": self.param["seat2"]},{"status":2})

    def updataStaus(self):
        db.update_one("u_agv_task", {"_id": db.ObjectId(self.taskId)}, {"status":self.status})

    @lockImp.lock(None)
    def onFinish(self,obj):
        log.info("task: move finish callback",self)
        if not obj["result"]:
            self.needRelease = True
            taskApi.update(self.taskId, step=self.taskStep, msg=obj["resultDesc"])
            return
        if self.taskStep == "goSourceMoving" or self.taskStep == "goSource":
            time.sleep(1)
            self.taskStep = "jackUpWP"
            taskApi.update(self.taskId, step=self.taskStep, msg="到达上料点")
            return  
        elif self.taskStep == "goTargetMoving" or self.taskStep == "goTarget":
            time.sleep(1)
            self.taskStep = "jackDown"
            taskApi.update(self.taskId, step=self.taskStep, msg="到达下料点")
            return


    def _callAgv(self,timeOut=300):
        msg = None
        for i in range(1,timeOut+1):
            try:
                self.agvId = agvApi.apply(taskId=self.taskId,mapId=self.param["floorId"],loc=self.param["location"])
                taskApi.update(self.taskId, agvId=self.agvId, msg="成功分配小车%s"%self.agvId)
                return self.agvId
            except Exception as e:
                time.sleep(1)
                msg = e
                log.warning("taskId[%s] apply agv %s failed: %s"%(self.taskId,i,str(e)))
        if str(msg) == "":
            msg = Exception("taskId[%s] apply agv failed"%self.taskId)
        taskApi.fail(self.taskId,msg=str(msg))
        raise msg
            
    def _moveAgv(self, timeOut=86400):
        try:    
            self.param["timeoutSec"] = timeOut
            if "seer_jackup" in self.param:
                del self.param["seer_jackup"]
            agvApi.move(self.agvId, self.param["floorId"]+'.'+self.param["location"], self.onFinish, self.param)
            return True
        except (ConnectionResetError,ConnectionAbortedError,socket.timeout,IOError) as e:
            # self._deal(str(e))
            raise e
    
    def _moveJackup(self, timeOut=86400):
        try:    
            self.param["timeoutSec"] = timeOut
            agvApi.moveJackup(self.agvId, self.param["floorId"]+'.'+self.param["location"], self.onFinish, self.param, use_pgv=False)
            return True
        except (ConnectionResetError,ConnectionAbortedError,socket.timeout,IOError) as e:
            # self._deal(str(e))
            raise e
            
    def _moveJackdown(self, timeOut=86400):
        try:    
            self.param["timeoutSec"] = timeOut
            agvApi.moveJackdown(self.agvId, self.param["floorId"]+'.'+self.param["location"], self.onFinish, self.param)
            return True
        except (ConnectionResetError,ConnectionAbortedError,socket.timeout,IOError) as e:
            # self._deal(str(e))
            raise e

    
    def _jackUpOld(self,timeOut=5, delLoc=None):
        try:
            jackApi.jackUpOld(self.agvId, timeOut)
            return
        except (ConnectionResetError,ConnectionAbortedError,socket.timeout,IOError) as e:
            # self._deal(str(e))
            raise e

    def getUnitLoadStatus(self, agvId, unitId):
        try:
            return rollerPlusApi.checkUnitloadStatus(agvId, unitId)["status"]
        except Exception as e:
            log.exception(self.taskId + "getUnitLoadStatus", e)
            return None

    def _audioPlay(self,name):
        try:
            ret = audioApi.playAudio(self.agvId, name, False)
            print("playAudio",name)
            if ret["errorno"] == 0:
                return True
            else:
                return False
        except Exception as e:
            log.exception(self.taskId + " playAudio", e)
            raise

    def _stopAudio(self):
        try:
            ret = audioApi.stopAudio(self.agvId)
        except Exception as e:
            log.exception(self.taskId + " stopAudio", e)
            raise

    @property
    def sPrepoint(self):
        return formatLoc(self.s_info["floorId"], self.s_info["prepoint"])

    @property
    def tPrepoint(self):
        return formatLoc(self.t_info["floorId"], self.t_info["prepoint"])
    def _goHome(self):
        #TODO
        # self._jackDown(self.param)
        agvApi.goHome(self.agvId,force=False,timeout=0)
        
    def _release(self):
        try:
            if self.agvId:
                log.info(self, self.agvId, "release task, release agv", self.canReleaseAgv)
                if self.canReleaseAgv:
                    agvApi.release(self.agvId, self.taskId, force=False)
                    # g_relese_agvs.add(self.agvId)
                    if agvApi.isLocked(self.agvId, self.taskId):
                        log.info(self, "let", self.agvId, "gohome")
                        agvApi.goHome(self.agvId, force=False, timeout=60 * 60 * 3)
                    self.agvId = ""
        except Exception as e:
            log.exception(str(self) + "task release", e)
        # self.clearLoc()

    def _jackUp(self,timeOut=1800):
        try:    
            # agvInfo = agvList.getAgv(self.agvId)
            ret = jackApi.jackUpCattle(self.agvId)
            # if ret["ret_code"] == 0:
            #     time.sleep(2)
            #     return True
            # else:
            #     return False
            return True
        except (ConnectionResetError,ConnectionAbortedError,socket.timeout,IOError) as e:
            # self._deal(str(e))
            raise e
        
    def _jackDown(self, timeOut=1800):
        try:    
            # agvInfo = agvList.getAgv(self.agvId)
            ret = jackApi.jackDownCattle(self.agvId)
            # if ret["ret_code"] == 0:
            #     time.sleep(5)
            #     return True
            # else:
            #     return False
            return True
        except (ConnectionResetError,ConnectionAbortedError,socket.timeout,IOError) as e:
            # self._deal(str(e))
            raise e
    def _jackClear(self, timeOut=1800):
        try:
            # agvInfo = agvList.getAgv(self.agvId)
            ret = jackApi.jackClearCattle(self.agvId)
            # if ret["ret_code"] == 0:
            #     return True
            # else:
            #     return False
            return True
        except (ConnectionResetError,ConnectionAbortedError,socket.timeout,IOError) as e:
            # self._deal(str(e))
            raise e
    def _deal(self,msg):
        taskApi.fail(self.taskId,msg=msg)
        self.isRunning = False
        
    def _deal2(self,msg):
        taskApi.fail(self.taskId,msg=msg)
        self._release()
        self.isRunning = False
        
    def _dealEx2(self,msg):
        taskApi.fail(self.taskId,msg=msg)
        self.isRunning = False

