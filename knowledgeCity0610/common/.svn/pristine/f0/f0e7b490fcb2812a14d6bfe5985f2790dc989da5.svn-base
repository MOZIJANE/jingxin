# coding=utf-8
# linzhongxiaosheng
import os, sys, re, datetime
import compileall
import pyminizip
import shutil
import zipfile
import threading
password="znzz"

def run_cmd(cmd):
	print(cmd)
	os.system(cmd)


def mkdir(path):
	if not os.path.exists(path):
		os.mkdir(path)


def now_str():
	now = datetime.datetime.now()
	return datetime.datetime.strftime(now, '%Y%m%d_%H%M%S')


def compile(path):
	compileall.compile_dir(path, quiet=False, force=True, legacy=True, rx=re.compile(r'/\(\.svn\)\(build.py\)'))
	print("compile " + path + " finish")


def ignore(path):
	if len(path) >= 7 and path[2:7] == "build":
		return True
	if path.find("/.") != -1:
		return True
	if path.find("\.") != -1:
		return True
	return False


def copy(path, extension):
	targetPath = os.path.join(os.path.dirname(path), "temp000")
	mkdir(targetPath)
	for root, dirs, files in os.walk(path):
		if ignore(root):
			continue

		for f in files:
			if f == "build"+extension:
				continue
			if os.path.splitext(root + f)[1] == extension:
				shutil.copy(os.path.join(root,f), targetPath)


def remove(path, extension):
	for root, dirs, files in os.walk(path):
		for f in files:
			if f == "build.py":
				continue
			if os.path.splitext(os.path.join(root,f))[1] == extension:
				os.remove(os.path.join(root,f))

def make_archive_single(zipName):
	compression_level = 5  # 1-9
	pyminizip.compress(zipName, "encrypted"+zipName, password, compression_level)

def make_archive(path):
	global password
	name = os.path.split(path)[1]
	base_name = os.path.join(path,name + "_" + now_str())
	base_dir = os.path.abspath("./")
	root_dir = os.path.join(os.path.dirname(path), "temp000")
	os.chdir(root_dir)
	zip_filename = base_name + ".zip"
	archive_dir = os.path.dirname(base_name)

	if archive_dir and not os.path.exists(archive_dir):
		os.makedirs(archive_dir)

	with zipfile.ZipFile(zip_filename, "w",
	                     compression=zipfile.ZIP_DEFLATED) as zf:
		zf.setpassword(password.encode())
		path = os.path.normpath(base_dir)
		if path != os.curdir:
			zf.write(path, path)

		for dirpath, dirnames, filenames in os.walk(base_dir):
			for name in sorted(dirnames):
				path = os.path.normpath(os.path.join(dirpath, name))
				zf.write(path, path)

			for name in filenames:
				path = os.path.normpath(os.path.join(dirpath, name))
				if os.path.isfile(path):
					zf.write(path, path)


	zf.close()
	print("create archive", base_name)
	return base_name


def build():
	cur = os.path.abspath(os.path.dirname(__file__))
	os.chdir(cur)
	
	compile(cur)
	copy(cur, ".py")
	remove(cur, ".py")
	zipName= make_archive(cur)
	make_archive_single(zipName)
	os.remove(os.path.join(cur,zipName))
	shutil.rmtree(cur+"/../temp000",ignore_errors=True)

build()
