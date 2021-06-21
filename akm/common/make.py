#coding=utf-8 
# ycat			 2017/09/27	  create
import os,sys,re,datetime
import compileall 
import shutil

buildDir = ""

def run_cmd(cmd):
	print(cmd)
	os.system(cmd)
	
def mkdir(path):
	if not os.path.exists(path):
		os.mkdir(path)	

def now_str():
	now = datetime.datetime.now()
	return datetime.datetime.strftime(now,'%Y%m%d_%H%M%S')

def write_version_info(): 
	path = buildDir+"/svn_info.txt"
	f = open(path,"wt")
	
	f.write(now_str()+"\n")
	f.close() 
	run_cmd("echo '======== svn info =========' >> "+path)
	run_cmd("svn info >> "+path)               
	run_cmd("echo '======== svn stat =========' >> "+path)
	run_cmd("svn stat >> "+path)             
	run_cmd("echo '======== svn diff =========' >> "+path)
	run_cmd("svn diff >> "+ path)
	f = open(buildDir+"/run.bat","w") 
	f.write("cd common\npython run_all.pyc")
	f.close()
	f = open(buildDir+"/run.sh","w")
	f.write("cd common\npython run_all.pyc")
	f.close()
	

def compile(path):
	compileall.compile_dir(path,quiet=True,force=True,legacy=True,rx=re.compile(r'/\.svn'))
	print("compile " + path + " finish")
	
	
def ignore(path):
	if len(path) >= 7 and path[2:7] == "build":
		return True
	if path.find("/.") != -1:
		return True
	if path.find("\.") != -1:
		return True	 
	return False
	
def copy(path):   
	for root, dirs, files in os.walk(path):
		if ignore(root):
			continue
		mkdir(buildDir+"/"+root) 
		for f in files:
			if os.path.splitext(root+f)[1] == ".zip" and root == ".":
				continue
			if os.path.splitext(root+f)[1] == ".py":
				continue
			if os.path.splitext(root+f)[1] == ".log":
				continue 
			if os.path.splitext(root+f)[1] == ".pyc":
				shutil.move(root+"/"+f,buildDir+"/"+root+"/")
			else:
				shutil.copy(root+"/"+f,buildDir+"/"+root+"/") 
	 
def make_archive(path):
	name = os.path.split(path)[1]
	base_name = path+"/"+name+"_"+now_str()
	shutil.make_archive(base_name=base_name,root_dir=path,base_dir="build",format="zip")
	print("create archive",base_name)
	 
	
def make():  
	global buildDir
	cur = os.path.abspath(os.path.dirname(__file__)+"/..") 
	buildDir = os.path.join(cur,"build")
	shutil.rmtree(buildDir,ignore_errors=True) 
	mkdir(buildDir)	 
	os.chdir(cur)
	
	write_version_info() 
	compile(".")
	copy(".")
	make_archive(cur) 
	
	

make()





