#-*- coding: utf-8 -*--
import sys,os
import time
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__) 
import psutil 

def sysInfo():
	r = {}
	r["cpu"] = cpu_rate()
	cc = cpu_rates()
	for i,c in enumerate(cc):
		r["cpu"+str(i)] = c
	r["mem"] = mem_rate()
	for dd in disk_rates():
		r["disk."+dd[0]] = dd[1]
	return r
	
	
#cpu利用率总数 
def cpu_rate():
    return psutil.cpu_percent()
	
#cpu每个核的利用率 
def cpu_rates():
    return psutil.cpu_percent(percpu=True)

#内存利用率 
def mem_rate():
    mem = psutil.virtual_memory()
    return mem.percent

#磁盘信息 
def disk_info():
    return psutil.disk_partitions()

#磁盘列表[(分区名,利用率)...]
def disk_rates():
	rr = []
	dd = disk_info()
	for d in dd:
		rr.append((d.mountpoint,psutil.disk_usage(d.mountpoint).percent))
	return rr

def disk_used_info(name):
    total = int(psutil.disk_usage(name).total/(1024*1024))
    used = int(psutil.disk_usage(name).used/(1024*1024))
    return total, used
 
 
################## unit test ##################
def testcpu():
	for i in range(1000):
		print(sysInfo())
		time.sleep(1)

if __name__ == '__main__':
	testcpu()
	
	
	
	
	
	
	
	
	
	
	
	
	
