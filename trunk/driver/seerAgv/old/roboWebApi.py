import time
import requests
import json
from urllib.parse import urljoin

baseurl = 'http://roboroute.example.com:55200/'
auth = '{"username": "admin","password": "admin"}'

headers={
		'Accept': 'application/json',
		 'Content-Type':'application/json'
}

class robobase(object):
	def __init__(self, properties):
		self.properties = properties


	def getdict(self):
		dict = {}
		dict.update(self.__dict__)
		return dict


class transportOrder(robobase):
	def __init__(self, deadline, intendedVehicle, destinations, properties):
		robobase.__init__(self,properties)
		self.deadline = deadline
		self.intendedVehicle = intendedVehicle
		self.destinations = destinations




class destinations(robobase):
	def __init__(self, destinations, operation, properties):
		robobase.__init__(self,properties)
		self.destinations = destinations
		self.operation = operation


class properties(object):
	def __init__(self, key, value):
		self.key = key
		self.value = value


def CreateTransportOrder(postData):
	data ={}
	result=None
	rsp = requests.post(urljoin(baseurl, '/v1/transportOrders/TOrder-1234'),  headers=headers,data=postData,verify=False)
	if	rsp.status_code==200:
		result = json.loads(rsp.text)

	return result

def GetTransportOrder(data):
	global token
	data = {}
	rsp = requests.get(urljoin(baseurl, '/v1/events?timeout=5000'), auth=token, headers={
		'Accept': 'application/json'},verify=False)
	if rsp.status_code == 200:
		result = json.loads(rsp.text)
		if result['status'] == 0:
			data = json.loads(result['data'])
	return data

def getData():
	unloadProps=list()
	unloadProps.append(properties('destination-specific key','some-value'))
	unloadProps.append(properties('destination-specific key2','some-value2'))

	destinationcollection=list()
	destinationcollection.append(destinations("Storage 01","Load cargo",[]))
	destinationcollection.append(destinations("Storage 02","Unload cargo",unloadProps))

	transport_order("2018-04-16T08:55:34.501Z","Vehicle-01",destinationcollection,[])

def test_CreateTransportOrder():
	postData=getData()
	result= CreateTransportOrder(postData=postData)
	assert result


if __name__ == '__main__':
	test_CreateTransportOrder()
