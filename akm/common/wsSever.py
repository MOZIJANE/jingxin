#coding=utf-8
# ycat			2017-12-20	  create
# 华太agv的驱动
import sys,os
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)

def echoServer():
	import asyncio
	import websockets
	
	@asyncio.coroutine
	def echo(ws, path):
		while True:
			msg = yield from ws.recv()
			print("< {}".format(msg))
			yield from ws.send(msg)

	asyncio.get_event_loop().run_until_complete(
		websockets.serve(echo, 'localhost', 8765))
	asyncio.get_event_loop().run_forever()
	
if __name__ == '__main__':
	echoServer()
