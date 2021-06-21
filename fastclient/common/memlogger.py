#coding=utf-8 
# ycat			 2015/04/02      create
# 因为sae的日志显示很不及时，所以用内存来存放日志 
import sys,os
import datetime
import utility
import logging
import datetime
import memcache
from string import Template

class mem_logger_hander(logging.Handler):
	_count_name = "memlogger.hander.counter"
	def __init__(self,max_size = 10240):
		self.max_size = max_size
		logging.Handler.__init__(self)

	def emit(self,record):
		record.datetime = utility.now_str(True)
		record.pid = os.getpid()
		record.msg = record.getMessage()
		index = memcache.get(mem_logger_hander._count_name,1)
		key = "memlogger.record.%d"%(index)
		memcache.set(key,record)
		memcache.set(mem_logger_hander._count_name,index+1)
		
	@staticmethod
	def logs():
		#TODO:可优化为多返回接口 
		index = memcache.get(mem_logger_hander._count_name)
		ret = []
		if index:
			start = index - 1000
			if start < 0:
				start = 0
			for i in range(start,index):
				key = "memlogger.record.%d"%(i)
				v = memcache.get(key)
				if v:
					v.index = i
					ret.append(v)
		return ret
	
	@staticmethod
	def start():
		memcache.delete(mem_logger_hander._count_name)

#############################	unit test	###########################	
def test_write_log():
	h = mem_logger_hander(8)
	logger = logging.getLogger()
	logger.addHandler(h)
	logger.setLevel(logging.NOTSET)
	
	for x in range(100):
		logger.debug("lala11")
		logger.info("lala12")
		logger.warning("lala13")
		logger.error("lala14")
		logger.critical("lala15")

	
if __name__ == '__main__':
	utility.run_tests()
		