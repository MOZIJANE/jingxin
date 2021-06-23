import struct
from marshmallow import *
import time
import datetime

# 1000 robot_status_info_req 查询机器人信息
# 1002 robot_status_run_req 查询机器人的运行状态信息(如运行时间、里程等)
# 1003 robot_status_mode_req 查询机器人运行模式
# 1004 robot_status_loc_req 查询机器人位置
# 1005 robot_status_speed_req 查询机器人速度
# 1006 robot_status_block_req 查询机器人被阻挡状态

# 2000 robot_control_stop_req 停止运动
# 2001 robot_control_gyrocal_req 标定陀螺仪
# 2002 robot_control_reloc_req 重定位
# 2003 robot_control_comfirmloc_req 确认定位正确

# 3051 robot_task_gotarget_req 固定路径导航(根据地图上站点及固定路径导航)
# 3052 robot_task_patrol_req 巡检(设定路线进行固定路径导航)
# 3057 robot_task_gostart_req 去起始点
# 3058 robot_task_goend_req 去终止点
# 3059 robot_task_gowait_req 去待命点
# 3060 robot_task_charge_req 去充电

# =====port def=====

API_PORT_STATE = 19204
API_PORT_CTRL = 19205
API_PORT_TASK = 19206
API_PORT_CONFIG = 19207
API_PORT_KERNEL = 19208
API_PORT_OTHER = 19210

# =====for test=====
t1000 = {"id": "S001", "version": "v1.1.0", "model": "S1", "dsp_version": "v1.2.2", "map_version": "v1.0.0",
         "model_version": "v1.1.0", "netprotocol_version": "v1.2.0"}
t1002 = {"odo": 0, "time": 6.0, "total_time": 2.0, "controller_temp": 1.57, "controller_humi": 0.9,
         "controller_voltage": 0.9}
t1003 = {"mode": 0}
t1004 = {"x": 6.0, "y": 2.0, "angle": 1.57, "confidence": 0.9}
t1005 = {"vx": 6.0, "vy": 2.0, "w": 1.57}
t1006 = {"blocked": 6.0, "block_reason": 2.0, "block_x": 1.57, "block_y": 0.9, "block_di": 0.9,
         "block_ultrasonic_id": 0.9}


t1100 = {"odo": 0, "time": 6.0, "total_time": 2.0, "controller_temp": 1.57, "controller_humi": 0.9,
         "controller_voltage": 0.9,"mode": 0,"x": 6.0, "y": 2.0, "angle": 1.57,
         "confidence": 0.9,"vx": 6.0, "vy": 2.0, "w": 1.57, "task_status" : 0,"target_id":"LM1",
         "blocked": 6.0, "block_reason": 2.0, "block_x": 1.57, "block_y": 0.9, "block_di": 0.9,
         "block_ultrasonic_id": 0.9,"battery_level":0.94,"battery_temp":28,
         "charging":False,"voltage":48,"current":5.0}



f2002 = {"x": 10.0, "y": 3.0, "angle": 0}
f3051 = {"id": "S03", "x": 10.0, "y": 3.0, "max_speed": 0, "max_wspeed": 0, "max_acc": 0, "angle": 0, "max_wacc": 0}
f3052 = {"route": "route03", "loop": 10}

# =====code def=====
robot_status_info_req = 1000
robot_status_run_req = 1002
robot_status_mode_req = 1003
robot_status_loc_req = 1004
robot_status_speed_req = 1005
robot_status_area_req = 1011
robot_status_io_res = 1013
robot_status_task_req = 1020
robot_status_all1_req = 1100
robot_status_alarm_res = 1050
robot_status_map_res = 1300
robot_status_station_res = 1301

robot_control_reloc_req = 2002
robot_control_comfirmloc_req = 2003
robot_control_motion_req = 2010

robot_task_cancel_req = 3003
robot_task_gopoint_req = 3050
robot_task_gotarget_req = 3051
robot_task_translate_req = 3055
robot_task_turn_req = 3056
robot_task_gostart_req = 3057
robot_task_goend_req = 3058
robot_task_gowait_req = 3059
robot_task_gocharge_req = 3060

robot_daemon_ls_req = 5100
robot_daemon_scp_req = 5101
robot_daemon_rm_req = 5102

robot_other_setdo_req = 6001
robot_other_wait_req=6600
robot_other_robot01=6601
robot_other_robot02=6602
robot_other_robot03=6603
robot_other_robot04=6604


# =====status def======

TASK_STATUS_NONE=0
TASK_STATUS_WAITING=1
TASK_STATUS_RUNNING=2
TASK_STATUS_SUSPENDED=3
TASK_STATUS_COMPLETED=4
TASK_STATUS_FAILED=5
TASK_STATUS_CANCELED=6

class baseModel(object):
    def getdict(self):
        dict = {}
        dict.update(self.__dict__)
        return dict


class protocolHeader(baseModel):
    def __init__(self, m_sync, m_version, m_number, m_length, m_type, m_reserved, m_reserved2):
        self.m_sync = m_sync
        self.m_version = m_version
        self.m_number = m_number
        self.m_length = m_length
        self.m_type = m_type
        self.m_reserved = m_reserved
        self.m_reserved2 = m_reserved2

    def getsturct(self):
        structed = struct.pack('>BBHIHIH', self.m_sync, self.m_version, self.m_number, self.m_length, self.m_type,
                               self.m_reserved, self.m_reserved2)
        return structed


class baseResultData(baseModel):
    def __init__(self, ret_code, err_msg):
        self.ret_code = ret_code
        self.err_msg = err_msg


class taskItemInfo(Schema):
    label = fields.String()
    actionCode = fields.Number()
    params = fields.Method('getParams')
    type=fields.Method('getType')

    def getParams(self, obj):
        actionCode = obj['actionCode']
        command= commandMapping[actionCode]
        if command is None:
            return None
        paramsTemp= command['schema']
        if  paramsTemp is None:
            return obj['params']
        else:
            schema = paramsTemp()
            paramsObj = obj['params']
            data, result = schema.dump(paramsObj)
            if len(result) != 0:
                raise Exception("反序列化错误")
            return data
    
    
    def getType(self, obj):
        actionCode = obj['actionCode']
        command= commandMapping[actionCode]
        if command is None:
            return None
        return command['type']

class taskInfo(Schema):
    name = fields.String()
    tasks = fields.Nested(taskItemInfo, many=True)
    loop = fields.Boolean()


class locationInfo(Schema):
    x = fields.Number()
    y = fields.Number()
    angle = fields.Number()


class translateInfo(Schema):
    dist = fields.Number()
    vx = fields.Number()
    vy = fields.Number()


class turnInfo(Schema):
    angle = fields.Number()
    vw = fields.Number()


class doInfo(Schema):
    id = fields.Integer()
    status = fields.Boolean()

class waitInfo(Schema):
    duration = fields.Number()

class robot0XInfo(Schema):
    param1 = fields.Number()


class motionInfo(Schema):
    w = fields.Number()
    vx = fields.Number()
    vy = fields.Number()
    steer = fields.Number()

commandMapping={
    robot_control_reloc_req: {"schema": locationInfo, "type": API_PORT_CTRL},
    robot_control_comfirmloc_req: {"schema": None, "type": API_PORT_CTRL},
    robot_control_motion_req: {"schema": motionInfo, "type": API_PORT_CTRL},
    robot_task_gopoint_req: {"schema": locationInfo, "type": API_PORT_TASK},
    robot_task_gotarget_req: {"schema": None, "type": API_PORT_TASK},
    robot_task_translate_req: {"schema": translateInfo, "type": API_PORT_TASK},
    robot_task_turn_req: {"schema": turnInfo, "type": API_PORT_TASK},
    robot_task_gostart_req: {"schema": None, "type": API_PORT_TASK},
    robot_task_goend_req: {"schema": None, "type": API_PORT_TASK},
    robot_task_gowait_req: {"schema": None, "type": API_PORT_TASK},
    robot_task_gocharge_req: {"schema": None, "type": API_PORT_TASK},
    robot_other_setdo_req: {"schema": doInfo, "type": API_PORT_OTHER},
    robot_other_wait_req: {"schema": robot0XInfo, "type": API_PORT_OTHER},
    robot_other_robot01: {"schema": robot0XInfo, "type": API_PORT_OTHER},
    robot_other_robot02: {"schema": robot0XInfo, "type": API_PORT_OTHER},
    robot_other_robot03: {"schema": robot0XInfo, "type": API_PORT_OTHER},
    robot_other_robot04: {"schema": robot0XInfo, "type": API_PORT_OTHER},


}

# map
class mapPos(Schema):
    x = fields.Number()
    y = fields.Number()


class mapLine(Schema):
    startPos = fields.Nested(mapPos)
    endPos = fields.Nested(mapPos)


class mapHeader(Schema):
    mapType = fields.String()
    mapName = fields.String()
    minPos = fields.Nested(mapPos)
    maxPos = fields.Nested(mapPos)
    resolution = fields.Number()
    version = fields.String()


class advancedPoint(Schema):
    className = fields.String()
    instanceName = fields.String()
    pos = fields.Nested(mapPos)
    dir = fields.Number()


class advancedLine(Schema):
    className = fields.String()
    instanceName = fields.String()
    line = fields.Nested(mapLine)
    startPos = fields.Nested(mapPos)
    endPos = fields.Nested(mapPos)


class advancedCurve(Schema):
    className = fields.String()
    instanceName = fields.String()
    startPos = fields.Nested(advancedPoint)
    endPos = fields.Nested(advancedPoint)
    controlPos1 = fields.Nested(mapPos)
    controlPos2 = fields.Nested(mapPos)


class advancedArea(Schema):
    className = fields.String()
    instanceName = fields.String()
    posGroup = fields.Nested(mapPos, many=True)


class mapInfo(Schema):
    mapDirectory = fields.String()
    header = fields.Nested(mapHeader)
    normalPosList = fields.Nested(mapPos, many=True)
    normalLineList = fields.Nested(mapLine, many=True)
    advancedPointList = fields.Nested(advancedPoint, many=True)
    advancedLineList = fields.Nested(advancedLine, many=True)
    advancedCurveList = fields.Nested(advancedCurve, many=True)
    advancedAreaList = fields.Nested(advancedArea, many=True)

  
# status说明,-2失败,-1:尚未开始 ,0:完成,1:正在运行
class taskItem(baseModel):
    def __init__(self, sn, code, data, type, groupsn):
        self.sn = sn
        self.code = code
        self.data = data
        self.type=type
        self.createTime=datetime.datetime.now()
        self.finishTime=None
        self.startTime=None
        self.schema=None
        self.status=-1
        self.errorno=-1
        self.errormsg=''
        self.groupsn=groupsn
        

def test_marshmallow():
    origin = {"x": "6.0", "y": "2.0", "angle": "1.57", "confidence": "0.9"}
    schema = locationInfo()

    data, result = schema.dump(origin)
    assert isinstance(data["x"], float)
    assert isinstance(data["y"], float)
    assert isinstance(data["angle"], float)
    assert len(result) == 0
    pprint(result)




if __name__ == '__main__':
    test_marshmallow()
