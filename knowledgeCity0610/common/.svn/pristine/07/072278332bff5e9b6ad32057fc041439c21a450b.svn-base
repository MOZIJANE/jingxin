#coding=utf-8 
# ycat			 2015/11/17      create
import sys,os
import os.path
import datetime
import xml.etree.ElementTree as xml
import re
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import utility,webutility
import mongodb as db
import dbQuery.query as query
import scadaUtility
import bottle
import urllib.parse

#例子1,文件夹用法:
#db = querySet("dbstript")
#dataset = db.run("db_stript.test1")
#db.run("db_stript.test1")

#例子2,文件用法:
#db = querySet("example.xml")
#dataset = db.run("test1")

class querySet:
	#filename可以写文件名，或者为目录 
	def __init__(self,filename):
		self.querys = {}
		fileList={}
		self.isDir = False
		if os.path.isdir(filename):
			self.isDir = True
			for file in os.listdir(filename):
				data = os.path.splitext(file) 
				if data[1] == ".xml":
					fileList[data[0]] = self._readXml(filename+"/"+file)
		else:
			data = os.path.splitext(filename)
			if data[1] == ".xml":
				fileList[data[0]] = self._readXml(filename)

		for (k,v) in fileList.items() :
			node = xml.fromstring(v[0])
			nn = node.findall("query")
			for n in nn:
				t = n.attrib["name"].strip() 
				if self.isDir:				
					key = k+"."+t
				else:
					key = t
				if key in self.querys:
					#不可以有重复的名字 
					print(key,self.querys)
					assert 0
				assert key not in self.querys
				self.querys[key]= query.query(n,globalVars=v[1])		

	def run(self,queryName,**variables):	
		return self.querys[queryName].run(**variables)
	
	#设置url地址 
	def setup(self):
		for q in self.querys:
			if self.querys[q].url:
				scadaUtility.add(self.querys[q].url,self._handleUrl) 
			
	#添加自定义函数 
	def addHandle(self,name,func):
		self.querys[q].handleFunc = func
		 
		 
	def _handleUrl(self):
		p = urllib.parse.urlparse(bottle.request.url).path
		if not p:
			assert 0 #URL的路径为空  
			return
		for q in self.querys:
			if p == self.querys[q].url:
				qq = self.querys[q]
				params = {}
				for key in qq.variables:
					value = webutility.get_param(key)
					if value is None:
						raise Exception("查询"+qq.name+"找不到参数"+key)
					params[key] = value
				ds = self.run(q,**params).list()
				ret = qq.handle(ds)
				if hasattr(qq,"handleFunc"):
					return qq.handleFunc(ret)
				return ret
		
	def _readXml(self,filename):
		f = open(filename,  mode='r', encoding='UTF-8')
		txt= f.read()
		f.close()
		
		root = xml.fromstring(txt) 
		n = root.find("global")
		variables = {}
		if n:
			nn = n.findall("variable")
			for v in nn:
				variables[v.attrib["name"]] = v.text.strip()
		return txt,variables
				
	
########### unit test ############### 
def test_variable():
	params = {"test1":1,"test2":2}
	data = {
	  "_id": "10280",
	  "city": "NEW YORK",
	  "state": "NY",
	  "pop": 5574,
	  "loc": [
		-74.016323,
		40.710537
	  ]
	}	
	db.drop_table("test_test_find")
	db.drop_table("test_test_aggregate")
	db.insert("test_test_aggregate",data)
	
	data = {
    "_id": "50a8240b927d5d8b5891743c",
    "cust_id": "abc123",
    "ord_date": datetime.datetime(2018,1,8,0,0,0),
    "status": 'A',
    "price": 25,
    "items": [ { "sku": "mmm", "qty": 5, "price": 2.5 },
              { "sku": "nnn", "qty": 5, "price": 2.5 } ]
}
	db.drop_table("test_test_mr")
	db.insert("test_test_mr",data)
	
	db.insert_many("test_test_find",[
		   { "item": "journal", "qty": 25, "tags": ["blank", "red"], "dim_cm": [ 14, 21 ] },
		   { "item": "notebook", "qty": 50, "tags": ["red", "blank"], "dim_cm": [ 14, 21 ] },
		   { "item": "paper", "qty": 100, "tags": ["red", "blank", "plain"], "dim_cm": [ 14, 21 ] },
		   { "item": "planner", "qty": 75, "tags": ["blank", "red"], "dim_cm": [ 22.85, 30 ] },
		   { "item": "postcard", "qty": 45, "tags": ["blue"], "dim_cm": [ 10, 15.25 ] }
		])
	
	qs2 = querySet("./example.xml")	
	ds=qs2.run("ycat测试1",**params)
	assert ds.next()
	assert ds["state"] == "NY"
	assert ds["biggestCity"] == {'pop': 5574, 'name': 'NEW YORK'}
	assert ds["smallestCity"] == {'pop': 5574,'name': 'NEW YORK'}
	
	qs = querySet("./")
	ds = qs.run("example.ycat测试1",**params)
	assert ds.next()
	assert ds["state"] == "NY"
	assert ds["biggestCity"] == {'pop': 5574, 'name': 'NEW YORK'}
	assert ds["smallestCity"] == {'pop': 5574,'name': 'NEW YORK'}
	
	dd = qs.run("example.ycat测试2",**params) 
	assert len(dd) == 2
	assert dd[0]["_id"] == "mmm"
	assert dd[0]["value"] == {'count': 1.0, 'qty': 5.0, 'avg': 5.0}
	
	assert dd[1]["_id"] == "nnn"
	assert dd[1]["value"] == {'count': 1.0, 'qty': 5.0, 'avg': 5.0}
	
	dd = qs.run("example.ycat测试3",**params).list()  
	assert len(dd) == 1
	assert dd[0]["qty"] == 75
	assert dd[0]["dim_cm"] ==  [22.85, 30]	
	assert "tags" not in dd[0]
	
	dd = qs.run("example.ycat测试4",**params).list()  
	assert len(dd) == 2
	assert dd[0]["qty"] == 50 
	assert dd[1]["qty"] == 75 
	
	db.drop_table("test_test_find")
	db.drop_table("test_test_find_out")
	db.drop_table("test_test_mr")
	db.drop_table("test_test_mr_results")
	db.drop_table("test_test_aggregate")
	 
if __name__== "__main__": 
	utility.run_tests()
	

