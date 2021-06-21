# coding: utf-8
# author: ives
# date: 2017-11-09
# desc: 用户管理

import sys
import os
import datetime
import setup,bottle
if __name__ == '__main__':
	setup.setCurPath(__file__)
import meta as m


opSel=m.select(tableName='c_operation',valueField="_id",nameField="name",domain=False)
roleSel=m.select(tableName='u_role')

@m.table("u_role","角色")
@m.field(id="_id",name="id",visible=False,readonly=True)
@m.field(id="name", name="名称", type=str, default=None, rules=[m.require()],unique=True)
@m.field(id="operation", name="权限", type=m.stringList, editCtrl=opSel, default=[], rules=[]) 
@m.field(id="isAdmin", name="是否为管理员", type=bool, default=False)
@m.timestampField()
class roleManager(m.manager):
	def __init__(self):
		m.manager.__init__(self)


@m.table("u_user","用户",layout=m.layout2())
@m.field(id="_id",name="id", visible=False,readonly=True)
@m.field(id="uname", name="登陆名", type=str, default=None, rules=[m.require()],unique=True)
@m.field(id="name", name="姓名", type=str, default=None, rules=[m.require()])
@m.field(id="enable", name="启用", type=bool, default=True, rules=[m.require()])
@m.field(id="password", name="密码", type=m.password, default=None, rules=[m.require()])
@m.field(id="role", name="角色", type=m.stringList, editCtrl=roleSel, default=None, rules=[])
@m.timestampField()
class userManager(m.manager):
	def __init__(self):
		m.manager.__init__(self)
			 

@m.table("c_operation","权限", permission=[],domain=False)
@m.field(id="_id",name="编码", type=str)
@m.field(id="name", name="名称", type=str)
@m.field(id="type", name="类型", type=str) 
class authManager(m.manager):
	def __init__(self):
		m.manager.__init__(self)

		
#for uwsgi 
app = application = bottle.default_app()

if __name__ == '__main__':
	webutility.run()
else:
	pass


