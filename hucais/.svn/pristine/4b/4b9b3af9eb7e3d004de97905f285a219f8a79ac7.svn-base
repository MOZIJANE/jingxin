
import os,sys
import math
import json
import PyQt5  
from PyQt5.QtCore import Qt
from PyQt5.Qt import QLineEdit
from PyQt5.QtWidgets import QMessageBox, QApplication, QWidget, QLabel, QPushButton, QScrollArea, QScrollBar, QHBoxLayout, QVBoxLayout,QGridLayout
                            
import qtawesome as qta
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__) 

import local
import utility


class ConfigView(PyQt5.QtWidgets.QWidget):
    def __init__(self):
        super(ConfigView, self).__init__()
        self.taskInfo = {}
        self.taskInfoUpdate = {}
        self.tipsInfo = {}
        self.taskObj = {}
        self.indexList = []
        self.actionList = []
        self.paramList = []
        self.initTask()
        self.mainUI()
    
    def mainUI(self):
        self.scroll_area = QScrollArea()
        self.taskConfigListLayout = QWidget()
        self.task = QVBoxLayout()

        # print(self.indexList, self.actionList, self.paramList)
        self.refreshTask(self.indexList, self.actionList, self.paramList)

        self.confirm = QPushButton()
        self.confirm.setText('保存')
        self.confirm.setFixedSize(100,30)
        self.confirm.clicked.connect(self.saveTask)

        self.add = QPushButton()
        self.add.setText('添加')
        self.add.setFixedSize(100,30)
        self.add.clicked.connect(self.addTask)

        self.delete = QPushButton()
        self.delete.setText('删除')
        self.delete.setFixedSize(100,30)
        self.delete.clicked.connect(self.deleteTask)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.add)
        hbox.addWidget(self.delete)
        hbox.addWidget(self.confirm)

        self.taskConfigListLayout.setLayout(self.task)
            
        self.scroll_area.setWidget(self.taskConfigListLayout)

        self.scrollbar = QScrollBar(Qt.Vertical, self)    
        self.scrollbar.setMaximum(self.scroll_area.verticalScrollBar().maximum())

        self.getTips()
        self.tips = QLabel()
        tipsInfo = self.makeInfo()
        self.makeInfo()

        self.tips.setText(tipsInfo)
        self.tips.setFixedSize(620,110)
        self.tips.setWordWrap(True)

        self.ui = QVBoxLayout()
        self.ui.addWidget(self.scroll_area)
        # self.ui.addWidget(self.scrollbar)
        self.ui.addWidget(self.tips)
        self.ui.addLayout(hbox)
        
        self.setLayout(self.ui)
        self.setGeometry(0,0,600,500)
        # self.setFixedSize(660, 500)
        self.setWindowIcon(qta.icon('fa.snowflake-o'))
        self.setWindowTitle('taskConfig')
    
    def makeInfo(self):
        ret = ''
        for k,v in self.tipsInfo.items():
            if isinstance(v, list):
                v = ' '.join(v)
            ret += '  '
            ret += v
            ret += '\n'
        return ret

    
    def refreshTask(self,indexList, actionList, paramList):
        # print('refreshTask---------------', indexList, actionList, paramList, type(indexList))
        if not actionList:
            actionList = ' '
        if not paramList:
            paramList = ' '

        for index, k,v in zip(indexList, actionList, paramList):
            onetask = QHBoxLayout()
            num = QPushButton()
            num.setText(index)
            onetask.addWidget(num)
            
            textboxAction = QLineEdit()
            textboxAction.resize(380, 60)
            textboxAction.setText(k)
            onetask.addWidget(textboxAction)
            # textboxAction.textChanged.connect(lambda:self.updateTask(num.text(),textboxAction.text(),textboxParam.text()))
            textboxAction.textChanged.connect(lambda:self.updateTask())

            textboxParam = QLineEdit()
            textboxParam.resize(380, 60)
            textboxParam.setText(';'.join(v))
            onetask.addWidget(textboxParam)

            textboxParam.textChanged.connect(lambda:self.updateTask())
            self.taskInfo[str(index)] = {}
            self.taskInfo[str(index)][str(k)] = v 

            self.taskObj[str(index)] = [textboxAction, textboxParam]

            self.task.addLayout(onetask)
            
    def initTask(self):
        proName = local.get("project","name")
        if utility.is_test():
            proName = 'test'
        file = "/projects/"+proName+"/" + 'task.json'
        with open(os.path.abspath(os.path.dirname(__file__) + file), 'r', encoding='utf8') as f:
            data = json.load(f)
            for a in data:
                if a=='tips':
                    continue
                item = data[a]
                for x in item:
                    try:
                        self.indexList.append(x)
                        self.actionList.append(item[x]['action'])
                        self.paramList.append(item[x]['param'])
                    except Exception as e:
                        self.indexList.append(x)
                        self.actionList.append('')
                        self.paramList.append('')
    
    def updateTask(self):
        self.taskInfoUpdate = {}
        for k,v in self.taskObj.items():
            try:
                action = v[0].text()
                param = v[1].text()
                param = list(param.split(';'))
                self.taskInfoUpdate[str(k)] = {}
                self.taskInfoUpdate[str(k)]['action'] = action
                self.taskInfoUpdate[str(k)]['param'] = param
            except RuntimeError as e:
                print('RuntimeError:', RuntimeError)

        # print('updateTask+--------', self.taskInfoUpdate)

    def saveTask(self):
        reply = QMessageBox.question(self, 'Message', '确认保存更改到文件吗?',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.getTaskInfo()
            self.updateTask()
            proName = local.get("project","name")
            if utility.is_test():
                proName = 'test'
            file = "/projects/"+proName+"/" + 'task.json'
            with open(os.path.abspath(os.path.dirname(__file__) + file), 'r', encoding='utf8') as f:
                content = f.read()


            content = json.loads(content)
            content['mode']={}
            content['mode']=self.taskInfoUpdate
            # print('saveTask---------', content)

            with open(os.path.abspath(os.path.dirname(__file__) + file), 'w', encoding='utf8') as f:
                f.write(json.dumps(content, ensure_ascii=False))
        else:
            pass

        

    def getTaskInfo(self):
        for index, k,v in zip(self.indexList, self.actionList, self.paramList):
            self.taskInfo[str(index)] = {}
            self.taskInfo[str(index)][str(k)] = v 
    
    def getTips(self):
        proName = local.get("project","name")
        if utility.is_test():
            proName = 'test'
        file = "/projects/"+proName+"/" + 'task.json'
        with open(os.path.abspath(os.path.dirname(__file__) + file), 'r', encoding='utf8') as f:
            data = json.load(f)
            for a in data:
                if a=='tips':
                    item = data[a]
                    self.tipsInfo = item
    
    def addTask(self):
        length = len(self.indexList)
        self.indexList.append(str(length+1))
        self.actionList.append('')
        self.paramList.append('')
        # print('addTask:', self.indexList, self.actionList, self.paramList)

        # method 1 --> add oneline at the end
        # self.refreshTask([self.indexList[-1]], [self.actionList[-1]], [self.paramList[-1]])

        # method 2  add a new 
        self.taskConfigListLayout.setParent(None)
        self.taskConfigListLayout = QWidget()
        self.task = QVBoxLayout()
        self.refreshTask(self.indexList, self.actionList, self.paramList)
        self.taskConfigListLayout.setLayout(self.task)
        self.scroll_area.setWidget(self.taskConfigListLayout)

        
    
    def deleteTask(self):
        self.taskConfigListLayout.setParent(None)
        self.indexList = self.indexList[:-1]
        self.actionList = self.actionList[:-1]
        self.paramList = self.paramList[:-1]
        # print('deleteTask:', self.indexList, self.actionList, self.paramList)

        self.taskConfigListLayout = QWidget()
        self.task = QVBoxLayout()
        
        self.refreshTask(self.indexList, self.actionList, self.paramList)
        self.taskConfigListLayout.setLayout(self.task)
        self.scroll_area.setWidget(self.taskConfigListLayout)

        lambda:self.updateTask()

            
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = ConfigView()
    ex.show()
    sys.exit(app.exec_())


