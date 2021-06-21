#coding=utf-8 
# ycat			 2017/12/22      create
import sys,os,platform
import configparser
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)  
from selenium import webdriver 
import selenium 
import time
import traceback
import mqtt
import mesApi

#url='http://192.168.32.166/SITApps/SITPortal/PortalPage/Comba/BomAssembly.aspx'
url="http://192.168.32.166/SITApps/SITPortal/PortalPage/MemberLogin.aspx"

def is_win64():
	# python 64
	return platform.architecture()[0] == "64bit"
	
def is_win32():
	# python 32
	return platform.architecture()[0] == "32bit"

#iedriver路径
if is_win64():
	print("use 64bit")
	iedriver = r'./ie64/IEDriverServer.exe' 
elif is_win32():
	iedriver = r'./ie32/IEDriverServer.exe' 
os.environ["webdriver.ie.driver"] = iedriver #设置环境变量
g_driver = None

html = '<TR id="ycat_rt_id"><TD style="WIDTH: 25%"><SPAN style="color:red">载具序列号：</SPAN></TD><TD style="WIDTH: 50%" colSpan=2><INPUT id="ycat_jig_id" disabled style="BORDER-BOTTOM: #7c7c94 1px solid; BORDER-LEFT: #7c7c94 1px solid; TEXT-TRANSFORM: uppercase; BACKGROUND-COLOR: whitesmoke; WIDTH: 90%; BORDER-TOP: #7c7c94 1px solid; BORDER-RIGHT: #7c7c94 1px solid"></TD>	<TD style="WIDTH: 25%" ></TD></TR>'
g_currentNum = 0
g_lastProduct = ""

textId = "ctl01_PortalContent_BomAssembly1_WebGroupBox1_txtSn"
numId = "ctl01_PortalContent_BomAssembly1_WebGroupBox1_lblCount"
jigId = "ycat_jig_id"


# 配置
g_lineTopic = None
g_lineSeatId = ""
g_lineInterval = 1

# 初始化
def _init():
	global g_lineTopic,g_lineSeatId,g_lineInterval
	fileName = './default.ini'
	if not os.path.exists(fileName):
		print('can not find default.ini file!')
		exit(1)
	try:
		config = configparser.ConfigParser()
		config.read(fileName)
		svrIp = str(config.get("mqtt", "ip"))
		port = int(config.get("mqtt", "port"))
		user = str(config.get("mqtt", "user"))
		pwd = str(config.get("mqtt", "password"))
		mqtt.initMqttObj(svrIp, user, pwd, port)
		g_lineTopic = ("scada/%s/product" %(str(config.get("line", "name"))))
		print("lineTopic: ", g_lineTopic)
		g_lineSeatId = str(config.get("device", "seatId"))
		print("seatId: ", g_lineSeatId)
		g_lineInterval = int(config.get("line", "scanInterval"))
		print("lineInterval: ", g_lineInterval)
	except:
		print('read default.ini failed!')
		exit(2)
	global g_driver
	g_driver = webdriver.Ie(iedriver)
	g_driver.get(url)


#查找网页元素的值
def getWebTextByInput(page, id):
	index = page.find(" id=" + id + " ")
	if index > 0:
		src = page[index:-1]
		src = src[0:src.find('>')]
		index = src.find(" value=")
		if index > 0:
			src = src[index + 1 : ]
			index = src.find(' ')
			if index > 0:
				src = src[6 : index]
			else:
				src = src[6:]
			return src.replace(' ', '')
		else:
			return ""
	else:
		return ""



def getWebTextBySpan(page, id):
	index = page.find(" id=" + id + " ")
	if index > 0:
		src = page[index:-1]
		src = src[0 : src.find('</SPAN>')]
		src = src[src.find('>') + 1 : ]
		return src.replace(' ', '')
	else:
		return ""


def findJigInput(page, id):
	index = page.find(" id=" + id + " ")
	return index > 0


g_jobDic = {}
def getJobId(productId):
	global g_jobDic
	for key in g_jobDic:
		if productId in g_jobDic[key]:
			return key

	jobList = mesApi.loadProductsBySN(productId)
	if len(jobList) < 1:
		return ""
	jobId = jobList[0]['job']
	if jobId not in g_jobDic:
		g_jobDic[jobId] = []
	for idx in range(len(jobList)):
		g_jobDic[jobId].append(jobList[idx]['productID'])
	return jobId


def run():
	global g_currentNum,g_lastProduct,g_lineTopic,g_driver,g_lineSeatId,g_lineInterval
	_init()
	time.sleep(10)
	lastJigId = ""
	while True:
		time.sleep(g_lineInterval)
		try: 
			page = g_driver.page_source
			n = getWebTextBySpan(page, numId)
			if not n.isdigit():
				continue

			if not findJigInput(page, jigId):
				js = "$('#ctl01_PortalContent_BomAssembly1_WebGroupBox1_Label2').closest('tr').before('"+html +"');"
				g_driver.execute_script(js)
				js2 = '''$('#%s').keydown(function(evt) { 
						if(evt.keyCode===13) { 
							var tempSn = $('#%s').val().toUpperCase(); 
							if (tempSn.indexOf("GZ-") == 0) { 
								evt.preventDefault(); 
								var d = new Date(); 
								d.setTime(d.getTime()+1800000); 
								var expires = "expires="+d.toGMTString(); 
								document.cookie = "mes_jig_id=" + tempSn + "; " + expires; 
								$('#%s').val(''); 
								$('#%s').val(tempSn);
							}; 
						} 
					} ); ''' %(textId, textId, textId, jigId)
				g_driver.execute_script(js2)

			productId = getWebTextByInput(page, textId)
			if len(productId) > 0:
				g_lastProduct = productId
			webJigId = getWebTextByInput(page, jigId)
			if len(webJigId) > 0:
				lastJigId = webJigId
			else:
				js3 = r'''var mes_jig_val = ""; 
					var name = "mes_jig_id="; 
					var ca = document.cookie.split(';'); 
					for(var i=0; i<ca.length; i++) { 
						var c = ca[i].replace(/(^\s*)|(\s*$)/g, ""); 
						if (c.indexOf(name)==0) { 
							mes_jig_val = c.substring(name.length,c.length); 
							break;
						}; 
					}; 
					if ($.find('#ycat_jig_id').length ===0) { 
						return ""; 
					} else { 
						$('#ycat_jig_id').val(mes_jig_val); 
						return $('#ycat_jig_id').val();
					};'''
				lastJigId = g_driver.execute_script(js3).replace(' ', '')

			num = int(n)
			if num == 0:
				continue
			if g_currentNum == num:
				continue
			if (g_currentNum == 0) and (num - g_currentNum) > 1:
				g_currentNum = num
				continue
			g_currentNum = num
			print("Num changed ",g_currentNum)

			if len(g_lastProduct) > 0 and len(lastJigId) > 0:
				jobId = getJobId(g_lastProduct)
				print("send jigId=%s productId=%s jobId=%s." %(lastJigId, g_lastProduct, jobId))
				mqtt.mqttObjSend(g_lineTopic, {'JigSN': lastJigId, 'productId': g_lastProduct, 'seatId' : g_lineSeatId, "job":jobId})
			else:
				print('[error]: jigId=%s, productId=%s.' %(lastJigId, g_lastProduct))

		except selenium.common.exceptions.NoSuchWindowException as e:
			print("quit")
			break
		except selenium.common.exceptions.NoSuchElementException:
			continue
		except selenium.common.exceptions.StaleElementReferenceException:
			continue
		except selenium.common.exceptions.UnexpectedAlertPresentException:
			continue
		except Exception as e: 
			s = "Exception: " + str(e) + "\n" 
			s += traceback.format_exc()
			print(s)
	

if __name__ == '__main__':
	run()

	
