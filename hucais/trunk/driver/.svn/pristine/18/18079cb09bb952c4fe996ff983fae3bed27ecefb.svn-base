# coding: utf-8
# author: ives
# date: 2017-11-16
# desc: 位置管理总入口 
import sys
import os
import bottle
import content

import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)


@bottle.route('/scada/alarm')	
def get_res_file(path):
	obj = json.load(requst.data)
	return "{'alarm':'1','desc':'alarm desc'}"


@bottle.route('/images/<path:path>')	
def get_res_file(path):
	return bottle.static_file(path,"./images")

@bottle.route('/css/<path:path>')	
def get_res_file(path):
	return bottle.static_file(path,"./css")
	
@bottle.route('/js/<path:path>')	
def get_js_file(path):
	return bottle.static_file(path,"./js")

g_productId = None
g_num = 0

@bottle.route('/modMes', method='Get')
#@bottle.view('modMes')
def url_modMes():
	global g_num
	html = content.sec1 + content.sec2 + ('%d' %g_num) + content.sec21 + content.sec4
	print(type(html))
	return html

@bottle.route('/modMes', method='POST')
#@bottle.view('modMes')
def url_BomAssembly():
	global g_num
	productId = bottle.request.forms.get('ctl01$PortalContent$BomAssembly1$WebGroupBox1$txtSn')
	isBuild = bottle.request.forms.get('ctl01$PortalContent$BomAssembly1$WebGroupBox1$txtSecSn')
	print('+++++++++++++++++++++++++++', isBuild)
	html = content.sec1
	if isBuild and len(isBuild) > 0:
		g_num += 1
		html += content.sec2 + ('%d' %g_num) + content.sec21 + content.sec4
	else:
		numStr = ('%d' %g_num)
		html += "value=\"" + productId + "\" " + content.sec2
		html += ('%d' %g_num)
		html += content.sec21  + content.sec3 + content.sec4
	return html



#====================================================================================
if __name__ == '__main__':
	bottle.run(host='0.0.0.0', port=9002,debug=True,reloader=True)

