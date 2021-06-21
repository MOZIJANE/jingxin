#coding=utf-8
# ycat			2017-08-07	  create
import sys,os
 
if "../../common" not in sys.path:
			sys.path.append("../../common")	
if "../../" not in sys.path:
			sys.path.append("../../") 
	
def setCurPath(filename):
	currentPath = os.path.dirname(filename)
	if currentPath != "":
		os.chdir(currentPath)
		
if __name__ == '__main__':
	pass
