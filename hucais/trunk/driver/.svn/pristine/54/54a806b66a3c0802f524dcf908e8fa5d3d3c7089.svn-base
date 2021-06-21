# coding: utf-8
# author: ives
# date: 2018-02-26
# desc: SAP

import sys
import os
import pysap

#--sap返回的字段说明--
#aufnr: 订单编码
#plnbez: 物料号
#plntxt: 物料描述
#gltrp: 基本完成日期
#gstrp: 基本开始日期
#gamng: 订单数量总计
#gmein: 基本计量单位(对应 gamng)
#vornr: 操作号
#ltxa1: 工序短文本
#meinh: 用于显示的计量单位(对应 bmsch)
#bmsch: 基本数量
#wunit: 标准值计量单位(对应 wtime)
#wtime: 标准值
#vge01: 标准值计量单位(对应 vgw01)
#vgw01: 机器使用时
#vge02: 标准值计量单位(对应 vgw02)
#vgw02: 直接人工工
#vge03: 标准值计量单位(对应 vgw03)
#vgw03: 间接人工工
#vge04: 标准值计量单位(对应 vgw04)
#vgw04: 直接制造费
#vge05: 标准值计量单位(对应 vgw05)
#vgw05: 间接制造费

def loadFromSap(jobId):
    try:
        name1 = '装配'.decode("utf8").encode("gb2312")
        name2 = '组装'.decode("utf8").encode("gb2312")
        pysap.setSystemCodePage('8400')
        #conn = pysap.Rfc_connection(conn_file='sapconn.ini',conn_name='my_connection')
        conn = pysap.Rfc_connection('LCHECK=1 ASHOST=192.168.0.80 CLIENT=600 SYSNR=00 USER=COMBAMES PASSWD=C3B6E9F3')
        conn.open()
        func = conn.get_interface('ZMES_PRODUCEORDER_WORKTIME')
        func['IM_AUFNR'] = jobId
        rc = func('IM_AUFNR', 'WT_TIME')
        lt = func['WT_TIME'].to_list()
        for idx in range(len(lt)):
            if 'ltxa1' in lt[idx]:
                if lt[idx]['ltxa1'] == name1 or lt[idx]['ltxa1'] == name2:
                    if 'wtime' in lt[idx]:
                        return int(lt[idx]['wtime'])
    except Exception as e:
        print(e)
    return 10
    
    
if __name__ == '__main__':
    mins = loadFromSap('200035492')
    print mins


