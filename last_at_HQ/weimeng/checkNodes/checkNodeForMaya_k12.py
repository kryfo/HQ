#!/usr/bin/env python
#coding=cp936
#coding=utf-8
__author__ = 'huangshuai,dengtao'
import maya.cmds as mc
from maya import OpenMayaUI as omui
from shiboken import wrapInstance
from PySide import QtCore, QtGui
import sys
#path='E:/work/7_0616_CheckNode/bak/checkNodes/'
path='E:/work/7_0616_CheckNode/'
path2='C:/Users/dengtao/Documents/maya/2015-x64/scripts/fantaTexClass'
if not path in sys.path:
    sys.path.append(path)
if not path2 in sys.path:
    sys.path.append(path2)
    
import check
    
from k_checkNodesWidget import Ui_checkNodesWindow
import checkNodeForMayaReplyWin
import json 
class Communicate(QtCore.QObject):
        buttonSignal=QtCore.Signal(QtGui.QWidget)

class checkNodes(Ui_checkNodesWindow,QtCore.QObject):
    kcb=[]
    k_Treturn={}
    def __init__(self,checkNodesWidget):
        QtCore.QObject.__init__(self)
        Ui_checkNodesWindow.setupUi(self,checkNodesWidget)
        self.close_Button.clicked.connect(checkNodesWidget.close)
        self.jsDir=json.loads(open(path+'k_enable.json').read(),encoding='gbk')
        self.checkBoxKeys=self.jsDir.keys()
        self.checkBoxKeys.sort()
        self.buttonList=[]
        self.buttonText=[]
        for cb in self.checkBoxKeys:
            button=self.jsDir[cb][3]
            Text=self.jsDir[cb][4]
            if not button in self.buttonList:
                self.buttonList.append(button)
                self.buttonText.append(Text)
        self.widgetList=[]
        self.klayoutList=[]
        for i in range(len(self.buttonList)):
            self.kframe_1 = QtGui.QFrame(self.scrollAreaWidgetContents)
            self.kframe_1.setFrameShape(QtGui.QFrame.Box)
            self.kframe_1.setFrameShadow(QtGui.QFrame.Raised)
            self.kframe_1.setObjectName(self.buttonList[i]+"kframe_1") 
            self.verticalLayout_2.addWidget(self.kframe_1)
            self.kQVB_1 = QtGui.QVBoxLayout(self.kframe_1)
            self.kQVB_1.setObjectName(self.buttonList[i]+"kQVB_1")
            self.kQVB_1.setContentsMargins(3, 3, 3, 3)
            self.kQVB_1.setSpacing(2)
            bt=QtGui.QPushButton()
            bt.setObjectName(self.buttonList[i])
            bt.setStyleSheet("background-color: #595959;height:20px;border-style:inset;border-width:1px;border-color: QLinearGradient(x1:0, y1:0, x2:0, y2:1, stop:0 #616161, stop:0.5 #616161 stop:1 #616161);font-size: 12px;text-align: left;\n"
            "")
            bt.setText(self.buttonText[i])          
            self.kQVB_1.addWidget(bt)
            bt.clicked.connect(self.signalEmit)
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(":/newPrefix/icon/kopen.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            bt.setIcon(icon)
            font = QtGui.QFont()
            font.setPointSize(12)
            bt.setFont(font)
            wd=QtGui.QWidget()
            wd.setObjectName(self.buttonList[i]+'_widget')
            wd.setMinimumSize(QtCore.QSize(100, 20))
            self.kQVB_1.addWidget(wd)
            self.khorizontalLayout = QtGui.QHBoxLayout(wd)
            self.khorizontalLayout.setObjectName('khorizontalLayout')
            self.khorizontalLayout.setContentsMargins(0, 0, 0, 0)    
            self.k_frame=QtGui.QFrame(wd)
            self.k_frame.setObjectName("k_frame")
            self.k_frame.setFrameShape(QtGui.QFrame.Box)
            self.k_frame.setFrameShadow(QtGui.QFrame.Sunken)
            self.khorizontalLayout.addWidget(self.k_frame)
            self.kverticalLayout = QtGui.QVBoxLayout(self.k_frame)
            self.kverticalLayout.setObjectName(self.buttonList[i]+"_kverticalLayout")
            selectAllBt=QtGui.QPushButton()
            selectAllBt.setObjectName(self.buttonList[i]+'_selAll')
            selectAllBt.setText(u'ȫѡ')
            selectAllBt.setGeometry(0,0,65,10)
            selectAllBt.setMinimumSize(QtCore.QSize(65, 10))
            selectAllBt.setParent(wd)
            selectAllBt.clicked.connect(self.signalEmit)
            cancelAllBt=QtGui.QPushButton()
            cancelAllBt.setObjectName(self.buttonList[i]+'_canAll')
            cancelAllBt.setText(u'���')
            cancelAllBt.setGeometry(80,0,65,10)
            cancelAllBt.setMinimumSize(QtCore.QSize(65, 10))
            cancelAllBt.setParent(wd)
            cancelAllBt.clicked.connect(self.signalEmit)
            kspacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
            self.kHbLayout = QtGui.QHBoxLayout()
            self.kHbLayout.setObjectName(self.buttonList[i]+"_kHbLayout")
            self.kHbLayout.addWidget(selectAllBt)
            self.kHbLayout.addWidget(cancelAllBt)
            self.kHbLayout.addItem(kspacerItem)
            self.kverticalLayout.addLayout(self.kHbLayout)
            self.widgetList.append(wd)
            self.klayoutList.append(self.kverticalLayout)

        for n in range(len(self.checkBoxKeys)):
            for wd in self.klayoutList:
                if wd.objectName()==self.jsDir[self.checkBoxKeys[n]][3]+'_kverticalLayout':
                    cbwd=wd
                    cb=QtGui.QCheckBox()
                    cb.setObjectName(self.checkBoxKeys[n])
                    cb.setText(self.jsDir[self.checkBoxKeys[n]][2])
                    cb.setChecked(self.jsDir[self.checkBoxKeys[n]][0])
                    wd.addWidget(cb)
                    if not self.jsDir[self.checkBoxKeys[n]][1]=='true':
                        cb.setEnabled(0)
                    self.kcb.append(cb)
        spacerItem = QtGui.QSpacerItem(20, 0, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.doIt_Button.clicked.connect(self.kcheckbox)
        self.someone=Communicate()
        self.someone.buttonSignal.connect(self.buttonCmd)
    def signalEmit(self):
        sender=self.sender()
        self.someone.buttonSignal.emit(sender)
    def buttonCmd(self,sender):
        btName= sender.objectName()
        parentWd=sender.parent()
        childrenItems=parentWd.children()
        for i in self.widgetList:
            if btName+'_widget'==i.objectName():
                if i.isVisible():
                    i.setVisible(0)
                    icon = QtGui.QIcon()
                    icon.addPixmap(QtGui.QPixmap(":/newPrefix/icon/kclose.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                    sender.setIcon(icon)
                else:
                    i.setVisible(1)
                    icon = QtGui.QIcon()
                    icon.addPixmap(QtGui.QPixmap(":/newPrefix/icon/kopen.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                    sender.setIcon(icon)
        if btName.split('_')[-1]=='selAll':
            for n in childrenItems:
                if n.metaObject().className()=='QCheckBox':
                    if n.isChecked ()==False and n.isEnabled():
                        n.setChecked(True)
        if btName.split('_')[-1]=='canAll':
            for n in childrenItems:
                if n.metaObject().className()=='QCheckBox':
                    if n.isChecked ()==True and n.isEnabled():
                        n.setChecked(False)

    def kcheckbox(self):
        self.k_Treturn.clear()
        for cbs in self.kcb:
            cbv=cbs.checkState()
            if cbv:
                cbsname=cbs.objectName()
                k_gocheck=('check.'+cbsname+'()')
                k_checklist=eval(k_gocheck)
                k_update={cbsname:k_checklist}
                self.k_Treturn.update(k_update)
        k_replyNodes(self.k_Treturn)
        return self.k_Treturn
class k_replyNodes(checkNodeForMayaReplyWin.Ui_MainWindow,QtGui.QMainWindow):
    def __init__(self,k_Treturn):
        super(k_replyNodes,self).__init__()
        self.setupUi(self)
        self.show()
        if(mc.window("k_replywin",ex=1)):
            mc.deleteUI("k_replywin")
        Window2=QtGui.QMainWindow(wrapInstance(long(omui.MQtUtil.mainWindow()), QtGui.QWidget))
        Window2.setObjectName('k_replywin')
        Window2.setGeometry(1048,127,380,820)
        self.jsDir=json.loads(open(path+'k_enable.json').read(),encoding='gbk')
        self.k_reply=k_Treturn.keys()
        self.k_reply.sort()
        krow=0
        for k_reply in self.k_reply:
            if k_Treturn[k_reply]:
                pagename=self.jsDir[k_reply][2]
                knodesize=len(k_Treturn[k_reply])
                self.addpage = QtGui.QWidget()
                self.addpage.setObjectName(k_reply+"_replyPage")
                self.toolBox.insertItem(0,self.addpage,(pagename+'  ('+str(knodesize)+u'��)'))
                self.kvbreply = QtGui.QVBoxLayout(self.addpage)
                self.kvbreply.setObjectName(k_reply+"_replyPageLayout")
                self.kvbreply.setContentsMargins(0, 0, 0, 0)
                self.addTabwidget=QtGui.QTableWidget(self.addpage)
                self.addTabwidget.setObjectName(k_reply+"_replyPageTabWidget")
                self.kvbreply.addWidget(self.addTabwidget)
                TabItem=QtGui.QTableWidgetItem()
                self.addTabwidget.setColumnCount(1)
                self.addTabwidget.setVerticalHeaderItem(0, TabItem)
                self.addTabwidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
                self.addTabwidget.setColumnWidth(0,9999)              
                self.addTabwidget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
                self.addTabwidget.itemSelectionChanged.connect(self.listItemSelect)
                krow+=1
                for k_reply_node in k_Treturn[k_reply]:
                    TabItemname=QtGui.QTableWidgetItem(k_reply_node)
                    self.addTabwidget.insertRow(0)
                    self.addTabwidget.setItem(0,0,TabItemname)
                    self.addTabwidget.setRowHeight(0,20)
        if krow:
            self.toolBox.setItemText(krow,'')
        Window2.setCentralWidget(self)
        Window2.show()

    def listItemSelect(self):
        kcurrentpage=self.toolBox.currentWidget()
        kcurrentpagechild = kcurrentpage.children()
        for kcurrentpagechild in kcurrentpagechild:
            if '_replyPageTabWidget' in kcurrentpagechild.objectName():
                kslItem=kcurrentpagechild.selectedItems()
                kslItemname=[]
                for kslItem in kslItem:
                    kslItemname.append(kslItem.text())
                
                if kslItemname:
                    mc.select(kslItemname) 
                else:
                    mc.select(cl=1)

if(mc.window('checkNodesWindow',ex=1)):
    mc.deleteUI('checkNodesWindow')
Window=QtGui.QMainWindow(wrapInstance(long(omui.MQtUtil.mainWindow()), QtGui.QWidget))
ui=checkNodes(Window)
Window.show()


