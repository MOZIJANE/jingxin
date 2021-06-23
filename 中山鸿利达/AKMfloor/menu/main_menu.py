#coding=utf-8
import  os,os.path
import json
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)

import webutility
import scadaUtility
import json_codec
import mongodb as db
import auth.authApi
import bottle
import utility
	
g_initOperation = False	
g_menu = None

#图标库在 https://fontawesome.com/v4.7.0/icons/
#webMain\node_modules\vue-awesome\icons
MENU_FILE = 'menu.json'

def getFiles(pathName):
	files=[]
	for file in os.listdir(pathName):
		f = os.path.join(pathName,file,MENU_FILE)
		if os.path.exists(f):
			files.append(f)
	return files

def _updateName(pp):
	if "hidden" not in pp:
		pp["hidden"] = False
	if "path" not in pp:
		pp["path"] = ""
	if "order" not in pp:
		pp["order"] = 0
	pp["name"] = pp["path"].replace("/","-").strip("-")
	if not pp["name"]:
		pp["name"] = pp["title"]
		
	if __name__ != '__main__' and  not pp["hidden"]: 
		if "admin" in pp and pp["admin"]:
			pp["hidden"] = not auth.authApi.isSysAdmin()	
		else:
			pp["hidden"] = not auth.authApi.checkOp(pp["name"]+".view")
	
	if "children" not in pp:
		return pp
	for p in pp["children"]:
		_updateName(p)
	return pp
	
#如果子节点有hidden为True，父节点也为True
def _updateHidden(pages):
	def hasVisible(p): 
		if "children" not in p:
			return not p["hidden"]
		for p1 in p["children"]:
			if hasVisible(p1):
				p["hidden"] = False
				return True
		return False
	for p in pages:
		hasVisible(p)	
	
def getMenu():
	global g_initOperation
	if not g_initOperation:
		g_initOperation = True
		createOperation()
	return loadMenu("../")

	
def append(page1,page2):
	for p in page1["children"]:
		if p["title"] == page2["title"]:
			if "children" in page2:
				for c in page2["children"]:
					append(p,c) 
			return page1
	page1["children"].append(page2)
	page1["children"] = sorted(page1["children"],key=lambda x : x["order"])
	return page1

	
def loadMenu(pathName):
	pages = {"title":"root","children":[]}
	files = getFiles(pathName)
	for file in files:
		pp = json_codec.load_file(file)
		_updateName(pp)
		pages = append(pages,pp)
	pages = pages["children"]
	_updateHidden(pages)
	return sorted(pages,key=lambda x : x["order"])

	
def _insertOperation(menu):
	ids = []
	for m in menu:
		db.update_one("c_operation",{"_id":m["name"]+".view"},{"_id":m["name"]+".view","name":"查看"+m["title"],"type":"view","auto":True},update_or_insert=True)
		ids.append(m["name"]+".view")
		if "children" in m:
			ids += _insertOperation(m["children"])
			continue
		db.update_one("c_operation",{"_id":m["name"]+".edit"},{"_id":m["name"]+".edit","name":"编辑"+m["title"],"type":"edit","auto":True},update_or_insert=True)
		ids.append(m["name"]+".edit")
	return ids
		
	
#返回所有的权限集合 	
def createOperation():
	m = getMenu()
	ids = _insertOperation(m)
	db.delete_many("c_operation",{"auto":True,"_id":{"$nin":ids}})
	
	
@scadaUtility.get("/api/menu/load")
def urlMenuGet(): 
	return {"pages": getMenu()}

	
#for uwsgi 
app = application = bottle.default_app()


if __name__ == '__main__': 
	print(loadMenu("..")) 
	createOperation()
	webutility.run()
else:
	#run in uwsgi
	pass 
	
	
	
	