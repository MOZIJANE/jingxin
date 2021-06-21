# coding=utf-8
# ycat			2017-08-07	  create
# 配置每个文件的 
import sys, os

if "../../common" not in sys.path:
	sys.path.append("../../common")

if "../../" not in sys.path:
	sys.path.append("../../")

if "../../factory" not in sys.path:
	sys.path.append("../../factory")


def setCurPath(filename):
	currentPath = os.path.dirname(filename)
	if currentPath != "":
		os.chdir(currentPath)


if __name__ == '__main__':
	pass
