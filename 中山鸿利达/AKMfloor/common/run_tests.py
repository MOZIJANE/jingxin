#coding=utf-8 
# ycat       2015/06/05      create
#运行所有的单元测试 
import sys,os,re,pytest
	
_exclude_dir = []
_exclude_files = []
_start_file = ""

def add_exclude_file(f):
	global _exclude_files
	_exclude_files.append(f)
	
def add_exclude_dir(d):
	global _exclude_dir
	_exclude_dir.append(d)	
	
def start_at(file):
	global _start_file
	_start_file = file
	
def _is_exclude_dir(root):
	global _exclude_dir
	for d in os.path.split(root):
		if d in _exclude_dir:
			return True
	return False	

def _get_test_files():
	global _exclude_dir,_exclude_files,_start_file
	result = []
	for root,dirs,files in os.walk("."):
		for filespath in files:
			if filespath in _exclude_files:
				continue
			find = False
			
			for e in _exclude_files:
				if filespath.find(e) != -1:
					find = True
					break
			if find:
				continue
				
			if _is_exclude_dir(root):
				continue
			name,ext = os.path.splitext(filespath)
			if ext != ".py":
				continue
			f = os.path.join(root,filespath)
			if _has_test_file(f):
				result.append(f)
	if _start_file != "" and _start_file in result:
		i = result.index(_start_file)
		return result[i:]
	return result			

def _has_test_func(s):
	return re.match('\s*def\s*test\S+\(.*\)\s*:\s*',s) is not None

def _has_test_file(file):
	try:
		with open(file,"r",encoding="utf-8") as f:
			lines = f.readlines()
			for l in lines:
				if _has_test_func(l):
					return True
		return False
	except Exception as e:
		#print(e)
		return False


########## unit test ###################

assert _has_test_func("def test1(a,b,c):")
assert _has_test_func(" \t  def     \t   test_fsdfsdf1()  :  \t  ")
assert not _has_test_func("def t1est1(a,b,c):")
assert not _has_test_func("def Test1(a,b,c):")
assert not _has_test_func("class test1(a,b,c):")
assert not _has_test_func("class test1:")
assert not _has_test_func("#def test1(a,b,c):")

assert _has_test_file("utility.py")
assert _has_test_file("wx/wx_mgr.py")
assert not _has_test_file("wrong.py")
assert not _has_test_file("idmaker.pyc")
assert not _has_test_file("memcache.py")

########## get test result ###################
def run_all():
	utility.set_is_test(True)
	add_exclude_dir("sae")
	add_exclude_dir("__pycache__")
	add_exclude_file("wx_mock.py")
	add_exclude_file("dblogger.py")
	
	if utility.is_win():
		add_exclude_file("mongodb.py")

	#start_at(".\\wx\\push.py") #可以设置从某个文件开始跑 	
	result = _get_test_files()
	print("collect tests files: \n\t"+"\n\t".join(result))

	cmd = "-x " + " ".join(result)
	cmd = cmd.replace("\\","\\\\")
	pytest.main(cmd)

def run_single(file):
	pytest.main(" -x " + file)


def main_func():
	import coverage
	cov = coverage.coverage()
	cov.start()
	
	#run_single("comm/cmd.py comm/ntf.py")
	run_all()

	cov.stop()
	cov.save()
	cov.exclude("\s*def\s*test\S+\(.*\)\s*:\s*")
	cov.exclude("\s*import.*")
	cov.exclude("\s*__all__.*")
	cov.exclude(".*'__main__'.*")
	cov.exclude(".*sys.path.append.*")
	
	# pragma: no cover
	omit_list=["__init__.py"]
	omit_list.append(r"wx\__init__.py")
	omit_list.append(r"comm\__init__.py")
	omit_list.append(r"run_tests.py")
	omit_list.append(r"C:\Program Files\ActiveState Komodo IDE 8\lib\support\dbgp\bin\py3_dbgp.py")
	omit_list.append(r"C:\Program Files\ActiveState Komodo IDE 8\lib\support\dbgp\python3lib\dbgp\client.py")
		
	cov.html_report(omit=omit_list,directory='../reports/common/')
	
	
if __name__ == '__main__':
	import utility
	if utility.is_win():
		os.chdir(os.path.dirname(__file__))
	main_func()
