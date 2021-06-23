import os, os.path
import json
import shutil
import time
import hashlib

pagefoldername = 'pages'
webfoldername = "vue/src"


def getallfiles(basepath):
	allfile = []
	allfilelist = os.listdir(basepath)
	for file in allfilelist:
		if file == webfoldername:
			continue
		filepath = os.path.join(basepath, file)

		if os.path.isdir(filepath):
			allfile.append(filepath)
	return allfile


def copyfiles(allfile, basepath):
	webpagepath = os.path.join(basepath, webfoldername, pagefoldername)
	if not os.path.exists(webpagepath):
		os.makedirs(webpagepath)
	for file in allfile:
		modulepath = os.path.join(file, pagefoldername)
		if os.path.isdir(modulepath):
			subname = os.path.split(file)[1]
			disdir = os.path.join(webpagepath, subname)
			if not os.path.exists(disdir):
				os.makedirs(disdir)
			merge(modulepath, disdir)
			print(modulepath, " done")


def GetFileMd5(filename):
	if not os.path.isfile(filename):
		return
	myhash = hashlib.md5()
	f = open(filename, 'rd')
	while True:
		b = f.read(8096)
		if not b:
			break
		myhash.update(b)
	f.close()
	return myhash.hexdigest()


def isModify(A_file, B_file):
	# return GetFileMd5(A_file) != GetFileMd5(B_file)
	return True


def stamp2Time(Stamp):
	timeArray = time.localtime(Stamp)
	Time = time.strftime("%y%m%d%H%M%S", timeArray)
	return Time


def merge(patha, pathb):
	pathsb = os.listdir(pathb)
	for fp in os.listdir(patha):
		newpatha = os.path.join(patha, fp)
		newpathb = os.path.join(pathb, fp)

		if os.path.isdir(newpatha):
			if os.path.exists(newpathb):
				merge(newpatha, newpathb)
			else:

				shutil.copytree(newpatha, newpathb)

		elif os.path.isfile(newpatha):
			if os.path.exists(newpathb):
				s = os.stat(newpathb)
				if isModify(newpatha, newpathb) == True:
					# suffix = newpathb.split('.')[-1]
					# temppathb = newpathb[:-len(suffix) - 1] + "(%s)." % (stamp2Time(s.st_mtime)) + suffix
					# shutil.copy2(newpathb, temppathb)
					shutil.copy2(newpatha, newpathb)
			else:
				shutil.copy2(newpatha, newpathb)


def testgetallfiles():
	path = "../"
	allfile = getallfiles(path)
	assert (allfile)


def testcopyfiles():
	# "../"
	path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
	allfile = getallfiles(path)
	assert (allfile)
	copyfiles(allfile, path)
	webpagepath = os.path.join(path, webfoldername, pagefoldername)
	allfilelist = os.listdir(webpagepath)
	assert (allfilelist)


if __name__ == '__main__':
	# testgetallfiles()
	testcopyfiles()
