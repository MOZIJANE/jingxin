#coding=utf-8
# ycat			2017-07-27	  create
# 日志接口
import sys,os
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__) 
import logging
logging.addLevelName(35, "SUCC")
import traceback
import enhance
import logging.config
import _utility
import time
import utility

g_log = None

app_name = _utility.app_name
g_cur_log_file = ""

class _console_format(logging.Formatter):
	format_str = "[%(levelname)s]%(asctime)s: %(message)s"
	def __init__(self):
		super(_console_format,self).__init__(_console_format.format_str)
	
	def format(self,record): 
		r = super(_console_format,self).format(record) 
		if sys.platform == "win32":
			return r
		if record.levelno == 50:
			c = "\033[31;47m"	
		elif record.levelno == 20:
			c = "\033[36m"
		elif record.levelno == 30:
			c = "\033[33m"
		elif record.levelno == 35:
			c = "\033[32m"
		elif record.levelno == 40:
			c = "\033[31m"
		else:
			c = "\033[37m"
		return c + r + "\033[0m"

def copy_old_log(path,oldpath,name):
	if sys.platform == "win32":
		cmd = r"move /Y .\log\%s*.log .\log\oldLog\ "%name
		os.system(cmd)
		return
	myId = os.getpgid(0)
	for file in os.listdir(path):
		i = file.find(name+"_p")
		if i == -1:
			continue 
		i2 = file.find(".log")
		if i2 == -1:
			continue
		pid = file[len(name+"_p"):i2]
		if not str.isdigit(pid):
			continue
		try:
			if os.getpgid(int(pid)) == myId:
				continue
		except:
			pass  
		cmd = "mv -f %s/%s %s/ 2> /dev/null"%(path,file,oldpath) 
		os.system(cmd)
		
		
def _init_logger():
	import config
	global g_log
	global g_cur_log_file
	if g_log:
		return g_log
	name = app_name()
	g_log = logging.getLogger(name)
	set_level(config.getint("logger","level"))
		
	if (not sys.platform == "win32"):
		p = config.get("logger","logger_path")
		try:
			if _utility.is_python3():
				os.makedirs(p,exist_ok=True)
			else:
				os.makedirs(p)
		except OSError as e:
			if str(e).find("File exists") == -1:
				print("log.py:",e)
		
		#把日志移到old文件夹中 
		oldpath = os.path.join(p,"oldLog")
		
		try:
			if _utility.is_python3():
				os.makedirs(oldpath,exist_ok=True)
			else:
				os.makedirs(oldpath)
		except OSError as e:
			if str(e).find("File exists") == -1:
				print("log.py",e)
		
		copy_old_log(p,oldpath,name)
		
		#删除old文件夹的旧日志
		cmd = "find %s/*.log -mtime +30 -type f -exec rm -Rf {} \\; 2> /dev/null"%oldpath
		#print(cmd)
		os.system(cmd)
			
		name = name + "_p" + str(os.getpid()) + ".log"
		g_cur_log_file = os.path.join(p,name)
		timelog = logging.handlers.TimedRotatingFileHandler(g_cur_log_file,when='MIDNIGHT',interval=1,backupCount=30)
		timelog.suffix = "%Y%m%d.log" 
		timelog.formatter = logging.Formatter(_console_format.format_str)
		g_log.addHandler(timelog)
		write_console = config.getbool("logger","enable_console")
	else: 
		logDir = os.path.abspath("./log")
		if not os.path.exists(logDir):
			os.mkdir(logDir)
		if not os.path.exists(logDir+"/oldLog"):
			os.mkdir(logDir+"/oldLog")
		copy_old_log(logDir,logDir+"/oldLog/ ",name)
		g_cur_log_file = "./log/%s_p%s.log" %(app_name(),str(os.getpid()))
		write_console = True
		
	if write_console:
		if sys.platform == "win32":
			timelog = logging.handlers.TimedRotatingFileHandler(g_cur_log_file,when='MIDNIGHT',interval=1,backupCount=30)
			timelog.suffix = "%Y%m%d.log" 
			timelog.formatter = logging.Formatter(_console_format.format_str)
			g_log.addHandler(timelog) 
			import winConsole
			h = winConsole.winLoggerHander()	 
		else:
			h = logging.StreamHandler(sys.stdout)
			h.formatter = _console_format()
		g_log.addHandler(h) 
	errorLog = logging.FileHandler(g_cur_log_file+".error.log")
	errorLog.setLevel(50)
	errorLog.formatter = logging.Formatter(_console_format.format_str)
	g_log.addHandler(errorLog)
	
	def _write_exception_log(title,exception_obj):
		import threading
		pp = "\npid=%d, ppid=%d, tid=%d\n"%(os.getpid(),os.getppid(),threading.currentThread().ident)
		s = str(title) + " cause a error: " + str(exception_obj) + pp
		if not hasattr(exception_obj,"noprint"):
			try:
				s += traceback.format_exc()#chain=False)
				s += ""
			except Exception as e:
				pass
		g_log.critical(s)	
	g_log.exception = _write_exception_log
	g_log.info("log files at "+os.path.realpath("./log"))
	return g_log
 
def logger():
	if g_log:
		return g_log
	return _init_logger()

def logPath():
	if (not sys.platform == "win32"):
		return config.get("logger","logger_path")
	else:
		return "./log/"

g_enable_log = True

def disable_log():
	global g_enable_log
	g_enable_log = False
	
def enable_log(): 
	global g_enable_log
	g_enable_log = True
	set_level(-1)

##CRITICAL=50,ERROR=40,SUCCESS=35,WARNING=30,INFO=20,DEBUG=10,NOTSET=-1 	
def set_level(levelno): 
	logger().level = levelno	
	
def _makeMsg(*param):	 
	msg = ""
	for p in param:
		if isinstance(p,float):
			msg += "%0.3f "%p 
		else:
			msg += str(p) + " " 
	#msg = msg.encode("utf-8").decode("gbk")
	return msg.rstrip()
	
def debug(*param):	
	if not g_enable_log:
		return
	try:
		logger().debug(_makeMsg(*param))
		if utility.is_ros():
			import ros2.rosLog2
			ros2.rosLog2.debug(*param)
	except Exception as e:
		print("log:",e) 
	
def info(*param):
	if not g_enable_log:
		return	
	try:
		logger().info(_makeMsg(*param))
		if utility.is_ros():
			import ros2.rosLog2
			ros2.rosLog2.info(*param)
	except Exception as e:
		print("log:",e)  
	
def warning(*param):	
	if not g_enable_log:
		return
	try:
		logger().warning(_makeMsg(*param))
		if utility.is_ros():
			import ros2.rosLog2
			ros2.rosLog2.warning(*param)
	except Exception as e:
		print("log:",e) 

def error(*param):	
	if not g_enable_log:
		return
	try:
		logger().error(_makeMsg(*param))
		if utility.is_ros():
			import ros2.rosLog2
			ros2.rosLog2.error(*param)
	except Exception as e:
		print("log:",e) 
		 
def abort(*param):	
	if not g_enable_log:
		return
	try:
		logger().critical(_makeMsg(*param))	 
		if utility.is_ros():
			import ros2.rosLog2
			ros2.rosLog2.abort(*param)
	except Exception as e:
		print("log:",e)  
	os.sys.exit(0)

	
def showTrace(func=debug):
	func(enhance.getTrace())
	
def exception(*param,**params):
	if not g_enable_log:
		return
	try:
		ret = logger().exception(*param,**params)
	except Exception as e:
		print("log:",e)  
	
def success(*param):	
	if not g_enable_log:
		return
	try:
		logger().log(35,_makeMsg(*param))		
	except Exception as e:
		print("log:",e) 
	
##################### Unit Test #############################	
def test_logger(): 
	showTrace()
	debug("this is a test log ",1,"sss3") 
	for i in range(10):
		debug("this is a test log ",1+i,"sss3")
		info("this is a test log ",1+i,"sss2")
		warning("this is a test log ",1+i,"sss4")
		error("this is a test log ",1+i,"sss1")
		success("this is a Success test log ",1+i,"sss1")
	try:
		
		assert 0
	except Exception as e:
		exception("this is a test log",e)
		
	
def test_disable_log():
	#set_is_test(False)
	import math
	enable_log()
	error("test is a test",math.pi)
	disable_log()
	error("test is a test2, you dont see!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
	enable_log()
	error("test is a test3, you should see")
	#set_is_test(True) 	
	
if __name__ == '__main__':
	test_logger()
	test_disable_log()
