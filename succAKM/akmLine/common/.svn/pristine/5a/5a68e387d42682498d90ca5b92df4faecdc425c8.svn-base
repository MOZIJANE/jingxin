#coding=utf-8
# ycat			2018-05-22	  create
# 自动生成web的编辑页面 
# 要求所有的主目录下面都要是main_开头 
import os,sys,glob
os.environ["runAll"] = "True"
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import webutility,utility,log,config


def findModule():
	p = os.path.abspath(os.path.dirname(__file__))
	p = os.path.join(p,"..")
	if p != "":
		parentDir = os.path.split(os.path.split(p)[0])[0]
		if parentDir not in sys.path:
			sys.path.append(parentDir)
		
		mm = []
		ll = glob.glob(p+"/*/main_*.py*") 
		for l in ll: 
			dirs,fileName = os.path.split(l)
			if not os.path.exists(os.path.join(dirs,"run.xml")):
				continue
			dirs2,lastDirName = os.path.split(dirs) 
			moudleName,ext = os.path.splitext(fileName)
			if ext != ".py" and ext != ".pyc":
				continue
			log.info("find module",lastDirName+"."+moudleName)
			sys.path.append(sys.path.append(os.path.join(parentDir,lastDirName)))
			mm.append((lastDirName,moudleName))
			
		for m in mm:
			utility.set_app_name(m[0])
			log.info("import "+m[0]+"."+m[1])
			try:
				__import__(m[1])
				utility.setModule(m[0])
			except Exception as e:
				msg = "import "+m[1]+" failed, path: " + m[0]
				log.exception(msg,e)
				log.abort(msg,",cause",str(e))
				raise e
			 
			
if __name__ == '__main__':
	import webutility,tcpServer
	port = webutility.readPort()
	if not tcpServer.checkPort("",port):
		print("error: tcp port %d is occupied, system quit!"%port)
		os.sys.exit(-1)
		
	utility.disableCloseButton()
	if webutility.is_bottle() or not config.getbool("bottle","reload"):
		findModule() 
		utility.start(True)    
	os.environ["port"] = str(port)
	webutility.run(port=port)
	
	