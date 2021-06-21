from PyQt5.QtCore import QIODevice, QByteArray
from PyQt5.QtSerialPort import QSerialPortInfo, QSerialPort
from PyQt5.QtWidgets import *
import time
import threading
import setup

if __name__ == '__main__':
    setup.setCurPath(__file__)

import buffer


class master():
    def __init__(self, port, onRecived=None):
        self._serial = QSerialPort()  # 用于连接串口的对象
        self.onRecived = onRecived
        self._serial.readyRead.connect(self.onReadyRead)  # 绑定数据读取信号
        # 首先获取可用的串口列表
        self.port = port
        self.getAvailablePorts()

    def run(self):
        # 打开或关闭串口按钮
        if self._serial.isOpen():
            # 如果串口是打开状态则关闭
            self._serial.close()
            return

        # 根据配置连接串口
        name = self.port
        if name not in self._ports or not name:
            return
        port = self._ports[name]
        #         self._serial.setPort(port)
        # 根据名字设置串口（也可以用上面的函数）
        self._serial.setPortName(port.systemLocation())
        # 设置波特率
        self._serial.setBaudRate(QSerialPort.Baud9600)
        # 设置校验位
        self._serial.setParity(QSerialPort.NoParity)
        # 设置数据位
        self._serial.setDataBits(QSerialPort.Data8)
        # 设置停止位
        self._serial.setStopBits(QSerialPort.OneStop)

        # 读写方式打开串口
        ok = self._serial.open(QIODevice.ReadWrite)
        if ok:
            print('串口连接ok')
        else:
            print('串口连接错误')

    def send(self, sendingBuffer):
        # 发送消息按钮
        if not self._serial.isOpen():
            print('串口未连接')
            return
        text = QByteArray(sendingBuffer)

        # 发送数据
        print('发送数据:', text)
        self._serial.writeData(bytes(sendingBuffer))
        result = self._serial.flush()
        print(result)

    def isRunning(self):
        return self._serial.isOpen()

    def onReadyRead(self):
        # 数据接收响应发送数据
        if self._serial.bytesAvailable():
            # 当数据可读取时
            # 这里只是简答测试少量数据,如果数据量太多了此处readAll其实并没有读完
            # 需要自行设置粘包协议
            data = self._serial.readAll()
            data=data.data()
            try:
                print('我收到了: ' + data.decode('gb2312'))
            except:
                # 解码失败
                print('我收到了-解码失败: ' + repr(data))
            if self.onRecived:
                self.onRecived(data)

    def getAvailablePorts(self):
        # 获取可用的串口
        self._ports = {}  # 用于保存串口的信息
        infos = QSerialPortInfo.availablePorts()
        infos.reverse()  # 逆序
        for info in infos:
            # 通过串口名字-->关联串口变量
            self._ports[info.portName()] = info

    def end(self):
        if self._serial.isOpen():
            self._serial.close()
