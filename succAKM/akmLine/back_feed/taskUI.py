# coding=utf-8
# ycat			2019-11-03	  create
import os, sys
import math
import PyQt5
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import qtawesome as qta
import datetime
import setup

if __name__ == '__main__':
    setup.setCurPath(__file__)
import utility
import local
import enhance
import log
import json_codec as json
import ui.listDlg
import qtutility
import mongodb as db
import utility


class akmTaskUI(PyQt5.QtWidgets.QWidget):
    def __init__(self, ip=None, port=None):
        super(akmTaskUI, self).__init__()
        self.table = self.createTable()
        layout = PyQt5.QtWidgets.QHBoxLayout()
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.setWindowTitle("AGV任务列表")
        self.setMinimumSize(800, 400)
        if ip is None or port is None:
            ip = local.get("taskUI", "ip", "192.168.5.137")
            # ip = local.get("taskUI", "ip", "172.16.65.28")
            port = local.get("taskUI", "port", 8999)
        self.url = 'http://%s:%s' % (ip, port)
        self.columns = []
        self.count = 5
        if __name__ == '__main__':
            self.first = False
        else:
            self.first = True
        self.timer = PyQt5.QtCore.QTimer(self)  # 初始化一个定时器
        self.timer.timeout.connect(self.autoUpdateTask)  # 计时结束调用operate()方法
        self.timer.start(5000)

    def createTable(self):
        table = PyQt5.QtWidgets.QTableWidget()
        columns = ["名称", "AGV", "任务类型", "任务当前步骤", "任务状态", "消息", "源位置", "目标位置", "创建时间", "开始时间", "结束时间", "源位置IO",
                   "目标位置IO", "任务ID"]
        table.setColumnCount(len(columns))
        table.setEditTriggers(PyQt5.QtWidgets.QAbstractItemView.NoEditTriggers)
        table.setSelectionBehavior(PyQt5.QtWidgets.QAbstractItemView.SelectRows)
        table.setSelectionMode(PyQt5.QtWidgets.QAbstractItemView.SingleSelection)
        # table.resizeColumnsToContents()
        table.setHorizontalHeaderLabels(columns)
        table.setSortingEnabled(True)

        head = table.horizontalHeader()
        head.setStretchLastSection(True)
        head.setSectionsClickable(True)
        head.setSectionResizeMode(
            PyQt5.QtWidgets.QHeaderView.ResizeToContents | PyQt5.QtWidgets.QHeaderView.Interactive)
        s = "QHeaderView::section {""color: black;padding-left: 4px;border: 1px solid #6c6c6c;}"
        head.setStyleSheet(s)

        v = table.verticalHeader()
        v.setSectionsClickable(True)
        v.setStyleSheet(s)
        return table

    def onClickTable(self, event):
        pass

    # QTableWidgetItem
    def tableItemChanged(self, current, previous):
        pass

    def updateTask(self, task, rowIndex):

        def setItemColor(rowIndex,cellIndex,color=None,bgColor=None):
            assert color or bgColor
            if color:
                self.table.itemAt(rowIndex,cellIndex).setForeground(PyQt5.QtGui.QBrush(PyQt5.QtGui.QColor(color)))
            if bgColor:
                self.table.itemAt(rowIndex,cellIndex).setBackground(PyQt5.QtGui.QBrush(PyQt5.QtGui.QColor(bgColor)))
        def getColor(status):
            if status is None:
                return "white"
            elif status == "fail":
                return "red"
            elif status == "error":
                return "grey"
            elif status == "working" or status == "running":
                return "yellow"
            elif status == "finished" or status == "success":
                return "green"
            elif status == "waiting":
                return "black"
            else:
                return "black"
        if task["status"]:
            resultColor = getColor(task["status"])
            # print(task["status"], resultColor)
        else:
            resultColor = "black"

        def set(col, text):
            if isinstance(text, str):
                item = PyQt5.QtWidgets.QTableWidgetItem(text)
            else:
                item = text
            # setItemColor(rowIndex,col,color = resultColor)
            if item:
                item.setForeground(PyQt5.QtGui.QBrush(PyQt5.QtGui.QColor(resultColor)))
            self.table.setItem(rowIndex, col, item)
            return item

        i = 0
        set(i, task["name"])

        i += 1
        set(i, task["agvId"])

        i += 1
        set(i, task["type"])

        i += 1
        set(i, task["step"])

        i += 1
        set(i, task["status"])

        i += 1
        set(i, task["msg"])

        i += 1
        set(i, task["source"])

        i += 1
        set(i, task["target"])

        i += 1
        set(i, task["createTime"])

        i += 1
        set(i, task["startTime"])

        i += 1
        set(i, task["endTime"])

        i += 1
        set(i, task["s_io"])

        i += 1
        set(i, task["t_io"])

        i += 1
        set(i, task["id"])

    def updateTaskBydb(self):
        tasks = getAkmTask()
        c = self.table.rowCount()
        for i in range(c):
            self.table.removeRow(c - i - 1)
        # self.table.clearContents()
        length = len(tasks)
        for i in range(length):
            self.table.insertRow(i)
            index = i
            self.updateTask(tasks[i], index)
        self.table.sortByColumn(13, PyQt5.QtCore.Qt.DescendingOrder)

    def autoUpdateTask(self):
        if self.first:
            # 服务器未启动，第一次不更新
            self.first = False
            return
        try:
            if self.count < 5:
                self.count = self.count + 1
            else:
                self.count = 0
                self.updateTaskBydb()
                # self.update()
        except Exception as e:
            log.exception("update task error:", e)
            self.table.sortByColumn(13, PyQt5.QtCore.Qt.DescendingOrder)
        return


class akmArarmUI(PyQt5.QtWidgets.QWidget):
    def __init__(self, ip=None, port=None):
        super(akmArarmUI, self).__init__()
        self.table = self.createTable()
        layout = PyQt5.QtWidgets.QHBoxLayout()
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.setWindowTitle("告警列表")
        self.setMinimumSize(800, 400)
        if ip is None or port is None:
            ip = local.get("taskUI", "ip", "192.168.5.137")
            # ip = local.get("taskUI", "ip", "172.16.65.28")
            port = local.get("taskUI", "port", 8999)
        self.url = 'http://%s:%s' % (ip, port)
        self.columns = []
        self.count = 5
        if __name__ == '__main__':
            self.first = False
        else:
            self.first = True
        self.timer = PyQt5.QtCore.QTimer(self)  # 初始化一个定时器
        self.timer.timeout.connect(self.autoUpdateTask)  # 计时结束调用operate()方法
        self.timer.start(5000)

    def createTable(self):
        table = PyQt5.QtWidgets.QTableWidget()
        columns = ["名称", "告警编号", "告警时间", "告警描述", "告警ID"]
        table.setColumnCount(len(columns))
        table.setEditTriggers(PyQt5.QtWidgets.QAbstractItemView.NoEditTriggers)
        table.setSelectionBehavior(PyQt5.QtWidgets.QAbstractItemView.SelectRows)
        table.setSelectionMode(PyQt5.QtWidgets.QAbstractItemView.SingleSelection)
        # table.resizeColumnsToContents()
        table.setHorizontalHeaderLabels(columns)
        table.setSortingEnabled(True)

        head = table.horizontalHeader()
        head.setStretchLastSection(True)
        head.setSectionsClickable(True)
        head.setSectionResizeMode(
            PyQt5.QtWidgets.QHeaderView.ResizeToContents | PyQt5.QtWidgets.QHeaderView.Interactive)
        s = "QHeaderView::section {""color: black;padding-left: 4px;border: 1px solid #6c6c6c;}"
        head.setStyleSheet(s)

        v = table.verticalHeader()
        v.setSectionsClickable(True)
        v.setStyleSheet(s)
        return table

    def onClickTable(self, event):
        pass

    # QTableWidgetItem
    def tableItemChanged(self, current, previous):
        pass

    def updateTask(self, task, rowIndex):

        def set(col, text):
            if isinstance(text, str):
                item = PyQt5.QtWidgets.QTableWidgetItem(text)
            else:
                item = text
            # item.setBackground(PyQt5.QtGui.QBrush(PyQt5.QtGui.QColor("gainsboro")))
            self.table.setItem(rowIndex, col, item)
            return item

        i = 0
        set(i, task["moid"])

        i += 1
        set(i, task["typeld"])

        i += 1
        set(i, task["desc"])

        i += 1
        set(i, task["createTime"])

        i += 1
        set(i, task["id"])

    def updateTaskBydb(self):
        tasks = akmArarm()
        c = self.table.rowCount()
        for i in range(c):
            self.table.removeRow(c - i - 1)
        # self.table.clearContents()
        length = len(tasks)
        for i in range(length):
            self.table.insertRow(i)
            index = i
            self.updateTask(tasks[i], index)
        self.table.sortByColumn(13, PyQt5.QtCore.Qt.DescendingOrder)

    def autoUpdateTask(self):
        if self.first:
            # 服务器未启动，第一次不更新
            self.first = False
            return
        try:
            if self.count < 5:
                self.count = self.count + 1
            else:
                self.count = 0
                self.updateTaskBydb()
                # self.update()
        except Exception as e:
            log.exception("update task error:", e)
            self.table.sortByColumn(13, PyQt5.QtCore.Qt.DescendingOrder)
        return


def getAkmTask():
    t = datetime.datetime.now()
    t = t - datetime.timedelta(hours=2)
    ds = db.find("u_scada_task", {"createTime": {"$gt": t}})
    ret = []
    while ds.next():
        i = {
            "id": str(ds["_id"]),
            "name": ds["taskName"],
            "source": ds["source"],
            "target": ds["target"],
            "s_io": ds["s_io"],
            "t_io": ds["t_io"],
            "line": ds["line"],
            "type": ds["type"],
            "createTime": ds["createTime"].strftime('%Y-%m-%d %H:%M:%S') if ds["createTime"] else '',
            "startTime": ds["startTime"].strftime('%Y-%m-%d %H:%M:%S') if ds["startTime"] else '',
            "endTime": ds["endTime"].strftime('%Y-%m-%d %H:%M:%S') if ds["endTime"] else '',
            "status": ds["status"],
            "step": ds["step"],
            "agvId": ds["agvId"],
            "msg": ds["msg"]
        }
        ret.append(i)
    return ret


def akmArarm():
    t = datetime.datetime.now()
    t = t - datetime.timedelta(hours=2)
    ds = db.find("r_alarm", {"createTime": {"$gt": t}})
    ret = []
    while ds.next():
        i = {
            "id": str(ds["_id"]),
            "moid": ds["moid"],
            "typeld": ds["typeld"],
            "desc": ds["desc"],
            "createTime": ds["createTime"].strftime('%Y-%m-%d %H:%M:%S') if ds["createTime"] else ''
        }
        ret.append(i)
    return ret


def run_app():
    from PyQt5.QtCore import Qt
    app = PyQt5.QtWidgets.QApplication(sys.argv)
    mainWindow = QTabWidget()
    akmTaskWin = akmTaskUI()
    akmArarmWin = akmArarmUI()
    mainWindow.setMinimumSize(1000, 600)
    mainWindow.addTab(akmTaskWin, "任务列表")
    mainWindow.addTab(akmArarmWin, "告警")
    # mainWin.setWindowFlags( Qt.WindowStaysOnTopHint)
    mainWindow.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    run_app()

