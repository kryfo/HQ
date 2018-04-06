from imports import *

import exportSetManager
import pw_settings as stngs
import mGeoReader
import mddWriter
import icons_rc

class mayaGeoWriter(QMainWindow, ui.Ui_mgeoWindow):
    def __init__(self, parent=None):
        super(mayaGeoWriter, self).__init__(parent)
        self.setupUi(self)
        ########## VARIABLES
        self.setObjectName('mGeoExporterWindow')
        self.version = '1.0'
        self.textVariables = {'outFormats':['.geo','.geo.gz','.bgeo','.bgeo.gz']             #file format
                            }
        self.outFormat = 0

        self.settings = stngs.settingsClass()
        self.url = 'http://paulwinex.blogspot.com/2013/08/mgeo-exporter-v10.html'

        self.lastPath = os.path.expanduser('~')
        self.gconvert = None

        self.uvExportNaming = 1
        self.colorExportNaming = 1
        self.progress = ''
        self.last = None
        self.canceled = False
        #settings
        self.readSettings()

        #Setup UI
        self.title = 'mGeo Exporter v' + self.version
        self.setWindowTitle(self.title+ '  |  PaulWinex')
        self.msg2(0, self.title + ' Ready!!!')
        self.statusMsg(self.title + ' Ready!!!')
        self.setList_lw = exportSetManager.exportSetManager(self)
        self.sets_ly.addWidget(self.setList_lw)

        #buttons
        sz = 20
        self.createSet_btn.setText('')
        self.createSet_btn.setIconSize(QSize(sz,sz))
        self.createSet_btn.setIcon(QIcon(QPixmap(":/newSet.png")))

        self.deleteSet_btn.setText('')
        self.deleteSet_btn.setIconSize(QSize(sz,sz))
        self.deleteSet_btn.setIcon(QIcon(QPixmap(":/deleteSet.png")))

        self.addToSet_btn.setText('')
        self.addToSet_btn.setIconSize(QSize(sz,sz))
        self.addToSet_btn.setIcon(QIcon(QPixmap(":/addToSet.png")))

        self.removeFromSet_btn.setText('')
        self.removeFromSet_btn.setIconSize(QSize(sz,sz))
        self.removeFromSet_btn.setIcon(QIcon(QPixmap(":/removeFromSet.png")))

        self.replaceSet_btn.setText('')
        self.replaceSet_btn.setIconSize(QSize(sz,sz))
        self.replaceSet_btn.setIcon(QIcon(QPixmap(":/replaceSet.png")))

        self.clearSet_btn.setText('')
        self.clearSet_btn.setIconSize(QSize(sz,sz))
        self.clearSet_btn.setIcon(QIcon(QPixmap(":/clearSet.png")))

        self.exportGeo_cb = QCheckBox()
        self.exportGeo_cb.setObjectName('exportGeo_cb')
        self.mainTab.tabBar().setTabButton(0, QTabBar.LeftSide, self.exportGeo_cb)
        self.exportCurv_cb = QCheckBox()
        self.exportCurv_cb.setObjectName('exportCurv_cb')
        self.mainTab.tabBar().setTabButton(1, QTabBar.LeftSide, self.exportCurv_cb)
        self.exportparticles_cb = QCheckBox()
        self.exportparticles_cb.setObjectName('exportparticles_cb')
        self.mainTab.tabBar().setTabButton(2, QTabBar.LeftSide, self.exportparticles_cb)
        self.pivot_cb = QCheckBox()
        self.pivot_cb.setObjectName('pivot_cb')
        self.mainTab.tabBar().setTabButton(3, QTabBar.LeftSide, self.pivot_cb)

        for c in self.exportGeo_cb, self.exportCurv_cb, self.exportparticles_cb, self.pivot_cb:
            c.clicked.connect(partial(self.setList_lw.saveUiSettings, widget=c.objectName()))

        ############################################### CONNECTS
        self.exportGeo_cb.clicked.connect(self.updateUi)
        self.exportCurv_cb.clicked.connect(self.updateUi)
        self.exportparticles_cb.clicked.connect(self.updateUi)
        self.pivot_cb.clicked.connect(self.updateUi)

        self.geoExport_btn.clicked.connect(self.startExport)
        self.setrange_btn.clicked.connect(self.setRange)
        self.clearText_btn.clicked.connect(self.output_te.clear)
        self.applets_btn.clicked.connect(self.getFileName)

        self.about_act.triggered.connect(self.showAbout)
        self.help_act.triggered.connect(self.showHelp)
        self.default_act.triggered.connect(self.defaultUi)
        self.saveDefault_act.triggered.connect(self.saveDefaultUi)

        self.createSet_btn.clicked.connect(self.setList_lw.createSet)
        self.deleteSet_btn.clicked.connect(self.setList_lw.removeSet)
        self.addToSet_btn.clicked.connect(self.setList_lw.addToSet)
        self.replaceSet_btn.clicked.connect(self.setList_lw.replaceSetContent)
        self.removeFromSet_btn.clicked.connect(self.setList_lw.removeFromSet)
        self.reloadSets_btn.clicked.connect(self.setList_lw.refreshSets)
        self.clearSet_btn.clicked.connect(self.setList_lw.clearSet)

        self.singleFrame_rb.toggled.connect(self.animrangeToggler)

        self.extReport_act.changed.connect(self.saveSettings)
        self.isolateExported_act.changed.connect(self.saveSettings)
        self.save_act.triggered.connect(self.saveOptions)
        self.load_act.triggered.connect(self.loadOptions)
        self.colorInd_act.triggered.connect(self.colorIndicatorSwitch)
        self.showWarnings_act.triggered.connect(self.saveSettings)

        ### reconnect iterate
        lines = self.findChildren(QLineEdit)
        for line in lines:
            line.editingFinished.connect(partial(self.setList_lw.saveUiSettings, widget=line.objectName()))
            line.returnPressed.connect(partial(self.setList_lw.saveUiSettings, widget=line.objectName()))
        del lines

        cb = self.findChildren(QCheckBox)
        for c in cb:
            c.clicked.connect(partial(self.setList_lw.saveUiSettings, widget=c.objectName()))
        del cb

        rb = self.findChildren(QRadioButton)
        for r in rb:
            r.clicked.connect(partial(self.setList_lw.saveUiSettings, widget=r.objectName()))
        del rb

        self.formatBgeo_rb.clicked.connect(self.getHFS)
        self.exportUv_cb.mousePressEvent = self.exportUv_cbMousePressEvent
        self.exportVertexColor_cb.mousePressEvent = self.exportCd_cbMousePressEvent
        ########################### UI
        self.textWidget_sp.setSizes([1000,0])
        self.splitter.setSizes([290, 450])
        self.setGeometry(300, 200, 560, 610)

        ## HIDE
        self.reloadSets_btn.setVisible(0)

        ########################### LOAD SCENE
        self.setList_lw.refreshSets()
        self.updateUi()
        self.enableUi()

    def exportUv_cbMousePressEvent(self, event):
        if event.button() == 2:
            self.uvCkeckBoxMenu(event.globalPos())
        QCheckBox.mousePressEvent(self.exportUv_cb, event)

    def uvCkeckBoxMenu(self, pos):
        menu = QMenu(self)

        a1 = QAction('uv, uv1, uv2...', self)
        a1.setObjectName('uvSetName1_act')
        a1.setCheckable(True)
        a1.setChecked(self.uvExportNaming == 1)
        @a1.triggered.connect
        def a1tr():
            self.uvExportNaming = 1
            self.setList_lw.saveUiSettings(a1.objectName())
        menu.addAction(a1)

        a2 = QAction('uv, uv_<setName>, uv_<setName>...', self)
        a1.setObjectName('uvSetName2_act')
        a2.setCheckable(True)
        a2.setChecked(self.uvExportNaming == 2)
        @a2.triggered.connect
        def a2tr():
            self.uvExportNaming = 2
            self.setList_lw.saveUiSettings(a1.objectName())
        menu.addAction(a2)

        a3 = QAction('uv_<setName>, uv_<setName>, uv_<setName>...', self)
        a1.setObjectName('uvSetName3_act')
        a3.setCheckable(True)
        a3.setChecked(self.uvExportNaming == 3)
        @a3.triggered.connect
        def a3tr():
            self.uvExportNaming = 3
            self.setList_lw.saveUiSettings(a1.objectName())
        menu.addAction(a3)

        act = menu.exec_(pos)
        if act:
            self.setList_lw.saveUiSettings()

    def exportCd_cbMousePressEvent(self, event):
        if event.button() == 2:
            self.CdCkeckBoxMenu(event.globalPos())
        QCheckBox.mousePressEvent(self.exportVertexColor_cb, event)

    def CdCkeckBoxMenu(self, pos):
        menu = QMenu(self)

        a1 = QAction('Cd, Cd1, Cd2...', self)
        a1.setObjectName('cdSetName1_act')
        a1.setCheckable(True)
        a1.setChecked(self.colorExportNaming == 1)
        @a1.triggered.connect
        def a1tr():
            self.colorExportNaming = 1
            self.setList_lw.saveUiSettings(a1.objectName())
        menu.addAction(a1)

        a2 = QAction('Cd, Cd_<setName>, Cd_<setName>...', self)
        a1.setObjectName('cdSetName2_act')
        a2.setCheckable(True)
        a2.setChecked(self.colorExportNaming == 2)
        @a2.triggered.connect
        def a2tr():
            self.colorExportNaming = 2
            self.setList_lw.saveUiSettings(a1.objectName())
        menu.addAction(a2)

        a3 = QAction('Cd_<setName>, Cd_<setName>, Cd_<setName>...', self)
        a1.setObjectName('cdSetName3_act')
        a3.setCheckable(True)
        a3.setChecked(self.colorExportNaming == 3)
        @a3.triggered.connect
        def a3tr():
            self.colorExportNaming = 3
            self.setList_lw.saveUiSettings(a1.objectName())
        menu.addAction(a3)

        act = menu.exec_(pos)
        if act:
            self.setList_lw.saveUiSettings()

    def savenaming(self, typ, widget):
        pass

    def animrangeToggler(self, state):
        self.range_wd.setEnabled(not state)
        self.sequence_rb.setEnabled(not state)
        self.mdd_rb.setEnabled(not state)

    def updateUi(self):
        self.polyScroll_sa.setEnabled(self.exportGeo_cb.isChecked())
        self.curvScroll_sa.setEnabled(self.exportCurv_cb.isChecked())
        self.partScroll_sa.setEnabled(self.exportparticles_cb.isChecked())
        self.pivScroll_sa.setEnabled(self.pivot_cb.isChecked())

    def setRange(self):
        self.startFrame_le.setText(str(int(cmds.playbackOptions(minTime=True, q=1))))
        self.endFrame_le.setText(str(int(cmds.playbackOptions(maxTime=True, q=1))))
        self.setList_lw.saveUiSettings(self.startFrame_le.objectName())
        self.setList_lw.saveUiSettings(self.endFrame_le.objectName())

    def colorIndicatorSwitch(self):
        self.setList_lw.refreshSets()
        self.saveSettings()


    ##################################### EXPORT

    def exportEnable(self, state):
        self.geoExport_btn.setEnabled(state)
        return state

    def isCacneled(self):
        if self.progress:
            if cmds.progressBar(self.progress, q=1, ic=1):
                return True
        return False

    def startExport(self):
        self.setList_lw.refreshSets()
        start_time = time.time()
        if not self.checkWarnings():
            return
        self.msg2(0, '\nStart export!!!')

        continium = True
        for i in range(self.setList_lw.count()):
            if not continium:
                break
            #cancel next set
            if self.isCacneled():
                break
            item = self.setList_lw.item(i)
            if self.setList_lw.itemWidget(item).state():
                setName = self.getSetName(item)
                if cmds.sets(setName, q=True):
                    #get options
                    op = eval(self.setList_lw.readAttrib(item))
                    if not op['exportpath']:
                        sPause = time.time()
                        name = self.getFileName()
                        ePause = time.time() - sPause
                        start_time -= ePause
                        if name:
                            op['exportpath'] = name
                            op['fileExists'] = 1
                        else:
                            self.msg2(0, 'Export canceled')
                            return
                    #parse path
                    path = self.detectPath(op['exportpath'], op['fileformat']) #check path
                    if path:
                        #getect GZIP
                        if op['gzip']:
                            uipath = path + '.gz'
                            self.exportPath_le.setText(uipath)
                        else:
                            self.exportPath_le.setText(path)
                        op['exportpath'] = path #update path
                        self.setList_lw.writeAttrib(setName, op) #write path to node
                        uiPath = op['exportpath']
                        #check HFS
                        if not op['fileformat'] and not self.gconvert:
                            self.getHFS()
                        if not os.path.exists(self.gconvert):
                            self.getHFS()
                        self.selectSetObjects(setName, op['expvis'], op['expHi'])
                        self.isolaetgSelected(1)
                        #progress
                        self.progress = mel.eval('$tmp = $gMainProgressBar')
                        cmds.progressBar(self.progress, edit=True,
                            beginProgress=True,
                            isInterruptable=True,
                            status=str(self.setList_lw.itemWidget(item).text)+' processing...',
                            maxValue=100)

                        if op['expanim']:#animation

                            start = int(op['animrange'][0])
                            end = int(op['animrange'][1])
                            step = float(op['animrange'][2])
                            #check range
                            if start > end or step > (end - start):
                                self.msg2(1,'Error frame range: ' + str(start) + ' / '+ str(end) + '/' + str(step))
                                return
                            sequenceframe = start
                            if op['animtype']: #geo sequence
                                for j in self.frange(start, end+1, step):
                                    self.statusMsg('Write cache frame '+str(j))
                                    #progress
                                    prc = (j*100.0)/(end-start)
                                    cmds.progressBar(self.progress, edit=True, pr=int(prc))
                                    cmds.currentTime(j)
                                    op['exportpath'] = self.addNumberToPath(uiPath, sequenceframe, True)
                                    # if cmds.progressBar(self.progress, q=1, ic=1):
                                    if self.isCacneled():
                                        self.cacelExport()
                                        continium = False
                                        break
                                    res = self.exportSingleFrame(op)
                                    if not res:
                                        self.msg2(1, 'EXPORT ERROR!!! Frame: ' + str(j))
                                    del res
                                    sequenceframe += 1
                                cmds.currentTime(start, edit=True)
                            else: # MDD
                                cmds.currentTime(start)
                                op['exportpath'] = self.addNumberToPath(op['exportpath'])
                                json = self.exportSingleFrame(op)
                                if not json:
                                    self.msg2(1, 'EXPORT ERROR!!! Frame: ' + str(start))
                                res = self.exportMDD(self.extensionToMDD(op['exportpath']), start, end, step, op['scale'], op)
                                del json
                                if not res:
                                    break
                            if self.progress:
                                cmds.progressBar(self.progress, edit=True, endProgress=True)
                            self.isolaetgSelected(0)
                        else:#export single frame
                            op['exportpath'] = self.addNumberToPath(op['exportpath'])
                            res = self.exportSingleFrame(op)
                            if not res:
                                self.msg2(1,'EXPORT ERROR!!! Frame: ' + str(i))
                            del res
                            self.isolaetgSelected(0)
                    else:
                        self.msg2(1, 'Error path!!! ' + op['exportpath'])
        if self.progress:
            cmds.progressBar(self.progress, edit=True, endProgress=True)
        if self.canceled:
            self.msg2(1, 'EXPORT CANCELED!!!')
        else:
            expTime = time.time() - start_time
            tm = str(datetime.timedelta(seconds=(round(expTime, 2))))
            while tm[-1] == '0':
                tm = tm[:-1]
            timeMsg = 'Export complete: ' + str(tm)
            self.msg2(0, timeMsg)
            self.statusMsg(timeMsg)
        self.isolaetgSelected(0)
        self.progress = None

    def cacelExport(self):
        self.canceled = True
        gc.collect()

    def getVisFast(self):
        return self.expVis_cb.isChecked()

    def selectSetObjects(self, name, vis, hi=False):
        #START EXPORT SET
        cmds.select(cmds.sets(name, q=1))
        if hi:
            cmds.select(hi=1)
        cmds.select(cmds.ls(sl=1, tr=1))
        if vis:
            cmds.select(vis=1)
            self.selectVisibleOnly()
        cmds.currentTime(cmds.currentTime(q=1))

    def isolaetgSelected(self, state):
        if self.isolateExported_act.isChecked():
            currentPanel = cmds.getPanel(withFocus=True)
            if cmds.panel(currentPanel, ex=1):
                try:
                    if state:
                        cmds.isolateSelect(currentPanel, state=1)
                        cmds.isolateSelect(currentPanel, addSelected=True)
                    else:
                        cmds.isolateSelect(currentPanel, state=0)
                        cmds.isolateSelect(currentPanel, removeSelected = True)
                except:
                    cmds.warning('Panel not found')

    def selectVisibleOnly(self):
        # select visible only
        sel = cmds.ls(sl=1)
        new = []
        for s in sel:
            if cmds.getAttr(s + '.overrideVisibility'):
                new.append(s)
        cmds.select(new)

    def exportSingleFrame(self, op):
        newPath = self.checkFileExists(op['exportpath'], op['fileExists'])
        j = mGeoReader.jsonDataReaderClass(op, self)
        if newPath:
            op['exportpath'] = newPath
            op['gconvert'] = self.gconvert
            if op['writefile']:
                result = j.readData()
                if result:
                    sz = self.getFileSize(result)
                    self.msg2(0, 'GEO file saved:', result, sz)
                    # s = sys.getsizeof(result)
        gc.collect()
        return True

    def exportMDD(self, path, start, end, step, scale, op):
        path = self.checkFileExists(path, op['fileExists'])
        res = True
        if path:
            mdd = mddWriter.mddWriterClass(self,  op)
            self.msg2(2, 'Write frames', start, '-', end, 'to MDD cache')
            res = mdd.export(path, start, end, step, scale)
            if res:
                sz = self.getFileSize(path)
                self.msg2(0, 'MDD file saved:', path, sz)
        return res

    def checkFileExists(self, path, state):
        #owerwrite
        if state == 1:
            return path
        #skip
        elif state == 2:
            self.msg2(2, 'Write file', path, 'skipped')
            return False
        #ask
        elif state == 0:
            if os.path.exists(path):
                return self.getFileName()
            else:
                return path
        #rename
        elif state == 3:
            if not os.path.exists(path):
                return path
            else:
                while os.path.exists(path):
                    path = self.incrementName(path)
                self.msg2(2, 'File renamed to', path)
                return path

    def incrementName(self,path):
        #return incremental name
        nameExt = os.path.basename(path)
        name, ext = os.path.splitext(nameExt)
        dir = os.path.dirname(path)
        splt = name.split('_')
        nameNum = '01'
        if len(splt) > 1:
            num = splt[-1]
            if num.isdigit():
                nameNum = int(num) + 1
                nzero = len(num)
                if nzero < 2: nzero = 2
                if nzero > len(str(nameNum)):
                    nameNum = str(nameNum).zfill(nzero)
                nName = '_'.join(splt[:-1]) + '_' + nameNum
            else:
                nName = '_'.join(splt) + '_' + nameNum
        else:
            nName = name + '_' + str(nameNum)
        result = '/'.join([dir,nName+ext])
        return result

    def getFileSize(self, path):
        if os.path.exists(path):
            size = os.path.getsize(path)
            if size > 1048576:
                result = str(round(size/1048576, 2))+' Mb'
            elif size < 1024:
                return '1 Kb'
            else:
                result = str(int(size / 1024)) + ' Kb'
            return result
        return 'File Error'

    def addNumberToPath(self, path, i=None, force=False):
        if i is None:
            i = int(cmds.currentTime(q=1))
        st = path.find('$F')
        if st > 0:
            pat = ''
            for f in path[st+2:]:
                if f.isdigit():
                    pat += f
                else:
                    break
            num = 1
            if pat:
                num = int(pat)
            frame = str(i).zfill(num)
            pat = path[st:st+len(str(pat))+2]
            result = path.replace(pat, frame)
            return result
        if force:
            ext = os.path.splitext(path)[1]
            if ext == '.gz':
                ext = os.path.splitext(path[:-3])[1]+'.gz'
            return ('_'+str(i).zfill(5)).join([path.replace(ext, ''), ext])

        return path

    def extensionToMDD(self,path):
        path = path.replace('.geo', '').replace('.bgeo', '').replace('.gz', '')
        return path + '.mdd'

    def checkDuplNames(self):
        inObj = cmds.ls(sl=True)
        n = 0
        for i in range (len(inObj)):
            shrtname = mel.eval('shortNameOf("%s")' % inObj[i])
            if "|" in shrtname:
                newname = inObj[i].split("|")
                cmds.rename(inObj[i], newname[len(newname) - 1] + "_%d" % n)
                n = n + 1

    def checkDupPathInSets(self):
        result = True
        sets = {}
        for i in range(self.setList_lw.count()):
            item = self.setList_lw.item(i)
            if item.checkState():
                op = eval(self.setList_lw.readAttrib(item))
                sets[str(item.data(32).toString())] = [op['exportpath'],
                                                      op['fileformat'],
                                                      op['gzip'],
                                                      op['expanim']]
        match = []
        for k in sets.keys():
            msg = "The same path is found!\nContinue?"
            reply = QMessageBox.question(self, 'Warning!!!', msg, QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.No:
                result = False
        return result

    def checkWarnings(self):

        #get sets
        control = {}
        atrs = {}
        for i in range(self.setList_lw.count()):
            item = self.setList_lw.item(i)
            if self.setList_lw.itemWidget(item).state():
                op = eval(self.setList_lw.readAttrib(item))
                name = self.setList_lw.itemWidget(item).text
                # name = self.getSetName(item).replace(self.setList_lw.prefix,'')
                control[name] = {'path':op['exportpath'],
                                 'ower':op['fileExists'],
                                 'anim':op['expanim'],
                                 'fileformat':op['fileformat'],
                                 'gzip':op['gzip'],
                                 'sequ':op['animtype']
                                 }
                atrs[name] = {'part':op['exppartattrib'],
                              'piv':op['exppivattrib']#,'poly':op['geocustomattr'],
                              }
        msg = ''#'Something wrong!\n'
        emptyPath = []
        #check Empty path
        for c in control:
            if not control[c]['path']:
                emptyPath.append(c)

        #check match path
        matchPath = []
        l = len(control) - 1
        it = control.keys()
        for i, c in enumerate(it):
            j = i
            while j < l:
                next = control[it[j+1]]
                if control[c] == next and next:
                    if not control[c]['path'] == '':
                        matchPath.append([c, it[j+1]])
                j += 1
        #check attrib names
        matchAttr = {}

        for s in atrs:
            m = []
            for st in atrs[s]:
                if atrs[s][st][0]:
                    m += re.findall(r'\S+', atrs[s][st][1])
            if m:
                clon = []
                for a in m:
                    if m.count(a) > 1:
                        if not a in clon:
                            clon.append(a)
                if clon:
                    matchAttr[s] = clon

        #build message
        arrays = [matchPath, emptyPath]
        if any(arrays) and self.showWarnings_act.isChecked():
            if matchPath:
                msg += 'Matched paths:\n'
                for m in matchPath:
                    print m
                    if all([m[0], m[1]]):
                        msg+= ' == '.join(m) + '\n'
            if emptyPath:
                msg += '\nEmpty paths:\n'
                for p in emptyPath:
                    msg += p + '\n'
            #show dialog
            import warningDialog as wd
            dial = wd.warningDialogClass(1, self)
            r = dial.showWarning(msg)
            if not r:
                return False
        #error export
        if matchAttr:
            msg = 'Matched point attributes name:\n\n'
            for a in matchAttr:
                msg += a + ' - ' + ','.join(matchAttr[a]) + '\n'
            msg += '\nExport will be canceled!'
            import warningDialog as wd
            dial = wd.warningDialogClass(0, self)
            dial.showWarning(msg)
            return False

        return True

    def checkDuplicatepath(self, set1, set2):
        if set1['path'] == sets['path']:
            if all():
                return True

    def getSetName(self, item):
        #PyQt
        try:
            setName = str(item.data(32).toString())
        #PySide
        except:
            setName = str(item.data(32))
        return setName

    ######################################### SETTINGS

    def getUiOptions(self):
        op = {}
        #global
        op['expanim'] = self.rangeFrame_rb.isChecked()
        op['animrange'] = [str(self.startFrame_le.text()), str(self.endFrame_le.text()), str(self.stepFrame_le.text())]
        op['animtype'] = self.sequence_rb.isChecked()
        op['fileformat'] = self.formatGeo_rb.isChecked()
        op['gzip'] = self.formatGzip_cb.isChecked()
        op['exportpath'] = str(self.exportPath_le.text())
        op['globalpos'] = self.worldPos_rb.isChecked()
        op['scale'] = float(str(self.scale_le.text()))
        op['writefile'] = self.writeFile_cb.isChecked()
        fileexists = 0
        if self.fileOverride_rb.isChecked(): fileexists = 1
        elif self.fileSkip_rb.isChecked(): fileexists = 2
        elif self.fileRename_rb.isChecked(): fileexists = 3
        op['fileExists'] = fileexists
        op['expvis'] = self.expVis_cb.isChecked()
        op['expHi'] = self.expHierarchy_cb.isChecked()
        #geometry
        op['exportgeo'] = self.exportGeo_cb.isChecked()
        op['geoglobalname'] = str(self.expGeoGlobalGroupName_le.text())
        op['geoglobalEnable'] = self.polyGroupEnable_cb.isChecked()
        op['expuv'] = self.exportUv_cb.isChecked()
        op['expvertexnorm'] = self.exportVerNorm_cb.isChecked()
        op['expcolor'] = self.exportVertexColor_cb.isChecked()
        op['expcrease'] = self.exportCrease_cb.isChecked()
        op['geocustomattr'] = [self.customGeoAttr_cb.isChecked(), str(self.customGeoAttr_le.text())]
        op['expgeogrp_mtl'] = [self.byMtl_cb.isChecked(), str(self.byMtl_le.text()), str(self.byMtlPref_le.text())]
        op['expgeogrp_parent'] = [self.byPar_cb.isChecked(), str(self.byPar_le.text()), str(self.byParPref_le.text())]
        op['expgeogrp_obj'] = [self.byObj_cb.isChecked(), str(self.byObj_le.text()), str(self.byObjPref_le.text())]
        op['expgeogrp_shp'] = [self.byShape_cb.isChecked(), str(self.byShape_le.text()), str(self.bySpahePref_le.text())]
        op['expgeogrp_layer'] = [self.displayer_cb.isChecked(), str(self.byLayer_le.text()), str(self.byLayerPref_le.text())]
        #curves
        op['expcurve'] = self.exportCurv_cb.isChecked()
        op['asnurmbs'] = self.curvToNURBS_rb.isChecked()
        op['expcurveglobname'] = str(self.expCurvesGlobalGroupName_le.text())
        op['expcurveglobEnable'] = self.curveGroupEnable_cb.isChecked()
        op['curvgrp_obj'] = [self.byCrvObj_cb.isChecked(), str(self.byCurvObj_le.text()), str(self.byCurvObjPref_le.text())]
        op['curvgrp_par'] = [self.byCrvPar_cb.isChecked(), str(self.byCurvPar_le.text()), str(self.byCurvParPref_le.text())]
        op['curvgrp_layer'] = [self.curvDisplayer_cb.isChecked(), str(self.byCurvLayer_le.text()), str(self.byCurvLayerPref_le.text())]
        #particles
        op['expparticle'] = self.exportparticles_cb.isChecked()
        op['expparticlglobname'] = str(self.expParticlesGlobalGroupName_le.text())
        op['expparticlglobEnable'] = self.partGroupEnable_cb.isChecked()
        op['exppartgrp_shape'] = [self.byPartObj_cb.isChecked(), str(self.byPartObj_le.text()), str(self.byPartObjPref_le.text())]
        op['exppartgrp_emit'] = [self.byEmit_cb.isChecked(), str(self.byEmit_le.text()), str(self.byEmitPref_le.text())]
        op['exppartattrib'] = [self.customAttr_cb.isChecked(), str(self.customAttr_le.text())]
        #pivots
        op['exppiv'] = self.pivot_cb.isChecked()
        op['exppivotglobname'] = str(self.expPivotsGlobalGroupName_le.text())
        op['exppivotglobEnable'] = self.pivotGroupEnable_cb.isChecked()
        op['exppivgrp_obj'] = [self.expPivotObj_cb.isChecked(), str(self.expPivotObj_le.text()), str(self.expPivotObjPref_le.text())]
        op['exppivgrp_shape'] = [self.expPivotShape_cb.isChecked(), str(self.expPivotShape_le.text()), str(self.expPivotShapePref_le.text())]
        op['exppivgrp_parent'] = [self.expPivotParent_cb.isChecked(), str(self.expPivotParent_le.text()), str(self.expPivotParentPref_le.text())]
        op['exppivgrp_layer'] = [self.expPivotLayer_cb.isChecked(), str(self.expPivotlayer_le.text()), str(self.expPivotLayerPref_le.text())]
        op['exppivorient'] = self.exportOrient_cb.isChecked()
        op['exppivscale'] = self.scale_cb.isChecked()
        op['exppivattrib'] = [self.customPivotAttr_cb.isChecked(), str(self.customPivotAttr_le.text())]
        op['exppivfilter'] = str(self.pivotFilter_le.text())
        op['exppivskipnoshape'] = self.pivSkipTransform_cb.isChecked()
        #other
        op['uvnaming'] = self.uvExportNaming
        op['colornaming'] = self.colorExportNaming

        return op

    def setUiOptions(self, op):
        if op:
            if op['expanim']:
                self.rangeFrame_rb.setChecked(1)
                self.rangeFrame_rb.emit(SIGNAL('clicked'))
            else:
                self.singleFrame_rb.setChecked(1)
            self.startFrame_le.setText(str(op['animrange'][0]))
            self.endFrame_le.setText(str(op['animrange'][1]))
            self.stepFrame_le.setText(str(op['animrange'][2]))

            if op['animtype']:
                self.sequence_rb.setChecked(1)
            else:
                self.mdd_rb.setChecked(1)
            self.exportPath_le.setText(op['exportpath'])
            if op['fileformat']:
                self.formatGeo_rb.setChecked(1)
            else:
                self.formatBgeo_rb.setChecked(1)
            self.formatGzip_cb.setChecked(op['gzip'])
            if op['globalpos']:
                self.worldPos_rb.setChecked(1)
            else:
                self.localPos_rb.setChecked(1)
            self.scale_le.setText(str(op['scale']))

            self.writeFile_cb.setChecked(op.get('writefile', True))

            if op['fileExists'] == 0:
                self.fileAsk_rb.setChecked(1)
            elif op['fileExists'] == 1:
                self.fileOverride_rb.setChecked(1)
            elif op['fileExists'] == 2:
                self.fileSkip_rb.setChecked(1)
            elif op['fileExists'] == 3:
                self.fileRename_rb.setChecked(1)

            self.expVis_cb.setChecked(op.get('expvis', False))
            self.expHierarchy_cb.setChecked(op.get('expHi', True))

            self.exportGeo_cb.setChecked(op['exportgeo'])
            self.expGeoGlobalGroupName_le.setText(op['geoglobalname'])
            self.polyGroupEnable_cb.setChecked(op.get('geoglobalEnable', True))
            self.exportUv_cb.setChecked(op['expuv'])
            self.exportVerNorm_cb.setChecked(op['expvertexnorm'])
            self.exportVertexColor_cb.setChecked(op['expcolor'])
            self.exportCrease_cb.setChecked(op['expcrease'])
            self.customGeoAttr_le.setText(op.get('geocustomattr', [1, ''])[1])
            self.customGeoAttr_cb.setChecked(op.get('geocustomattr', [1, 1])[0])

            self.byMtl_cb.setChecked(op['expgeogrp_mtl'][0])
            self.byMtl_le.setText(op['expgeogrp_mtl'][1])
            self.byMtlPref_le.setText(op['expgeogrp_mtl'][2])
            self.byPar_cb.setChecked(op['expgeogrp_parent'][0])
            self.byPar_le.setText(op['expgeogrp_parent'][1])
            self.byParPref_le.setText(op['expgeogrp_parent'][2])
            self.byObj_cb.setChecked(op['expgeogrp_obj'][0])
            self.byObj_le.setText(op['expgeogrp_obj'][1])
            self.byObjPref_le.setText(op['expgeogrp_obj'][2])
            self.byShape_cb.setChecked(op.get('expgeogrp_shp',[0,0])[0])
            self.byShape_le.setText(op.get('expgeogrp_shp', [0, ''])[1])
            self.bySpahePref_le.setText(op.get('expgeogrp_shp', [0, 0, 'SHAPE_'])[2])
            self.displayer_cb.setChecked(op['expgeogrp_layer'][0])
            self.byLayer_le.setText(op['expgeogrp_layer'][1])
            self.byLayerPref_le.setText(op['expgeogrp_layer'][2])

            self.exportCurv_cb.setChecked(op['expcurve'])
            if op['asnurmbs']:
                self.curvToNURBS_rb.setChecked(1)
            else:
                self.curvToPoly_rb.setChecked(1)
            self.expCurvesGlobalGroupName_le.setText(op['expcurveglobname'])
            self.curveGroupEnable_cb.setChecked(op.get('expcurveglobEnable', True))
            self.byCrvObj_cb.setChecked(op['curvgrp_obj'][0])
            self.byCurvObj_le.setText(op['curvgrp_obj'][1])
            self.byCurvObjPref_le.setText(op['curvgrp_obj'][2])
            self.byCrvPar_cb.setChecked(op['curvgrp_par'][0])
            self.byCurvPar_le.setText(op['curvgrp_par'][1])
            self.byCurvParPref_le.setText(op['curvgrp_par'][2])
            self.curvDisplayer_cb.setChecked(op['curvgrp_layer'][0])
            self.byCurvLayer_le.setText(op['curvgrp_layer'][1])
            self.byCurvLayerPref_le.setText(op['curvgrp_layer'][2])

            self.exportparticles_cb.setChecked(op['expparticle'])
            self.partGroupEnable_cb.setChecked(op.get('expparticlglobEnable',True))
            self.expParticlesGlobalGroupName_le.setText(op['expparticlglobname'])
            self.byPartObj_cb.setChecked(op['exppartgrp_shape'][0])
            self.byPartObj_le.setText(op['exppartgrp_shape'][1])
            self.byPartObjPref_le.setText(op['exppartgrp_shape'][2])
            self.byEmit_cb.setChecked(op['exppartgrp_emit'][0])
            self.byEmit_le.setText(op['exppartgrp_emit'][1])
            self.byEmitPref_le.setText(op['exppartgrp_emit'][2])
            self.customAttr_cb.setChecked(op['exppartattrib'][0])
            self.customAttr_le.setText(op['exppartattrib'][1])

            self.pivot_cb.setChecked(op['exppiv'])
            self.expPivotsGlobalGroupName_le.setText(op['exppivotglobname'])
            self.pivotGroupEnable_cb.setChecked(op.get('exppivotglobEnable',True))
            self.expPivotObj_cb.setChecked(op['exppivgrp_obj'][0])
            self.expPivotObj_le.setText(op['exppivgrp_obj'][1])
            self.expPivotObjPref_le.setText(op['exppivgrp_obj'][2])
            self.expPivotShape_cb.setChecked(op['exppivgrp_shape'][0])
            self.expPivotShape_le.setText(op['exppivgrp_shape'][1])
            self.expPivotShapePref_le.setText(op['exppivgrp_shape'][2])
            self.expPivotParent_cb.setChecked(op['exppivgrp_parent'][0])
            self.expPivotParent_le.setText(op['exppivgrp_parent'][1])
            self.expPivotParentPref_le.setText(op['exppivgrp_parent'][2])
            self.expPivotLayer_cb.setChecked(op['exppivgrp_layer'][0])
            self.expPivotlayer_le.setText(op['exppivgrp_layer'][1])
            self.expPivotLayerPref_le.setText(op['exppivgrp_layer'][2])
            self.exportOrient_cb.setChecked(op['exppivorient'])
            self.scale_cb.setChecked(op['exppivscale'])
            self.customPivotAttr_le.setText(op['exppivattrib'][1])
            self.customPivotAttr_cb.setChecked(op['exppivattrib'][0])
            self.pivotFilter_le.setText(op.get('exppivfilter',''))
            self.pivSkipTransform_cb.setChecked(op.get('exppivskipnoshape', True))

            self.uvExportNaming = op['uvnaming']
            self.colorExportNaming = op['colornaming']

    def defaultUi(self):
        import defaultSettings
        reload(defaultSettings)
        ui = defaultSettings.settings
        self.setUiOptions(ui)
        self.setList_lw.toDefault(ui)

    def saveDefaultUi(self):
        reply = QMessageBox.question(self, 'Update default settings', "Warning! Defaults will be overwritten.\n Are you sure?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            ui = self.getUiOptions()
            file = os.path.join(os.path.dirname(__file__), 'defaultSettings.py')
            try:
                f = open(file, 'w')
                f.write('settings = {')
                for k in sorted(ui.keys()):
                    val = str({k:ui[k]}).replace('{', '').replace('}', '')
                    f.write(val + ',\n\t\t\t')
                f.write('}')
                f.close()
            except IOError:
                self.msg2(1, 'Error save default settings!!!')

    def getHFS(self):
        if not self.gconvert or not os.path.exists(self.gconvert):
            box = QMessageBox(self)
            box.setWindowTitle('HFS path')
            box.setText('Please, set the $HFS path')
            box.setDetailedText('Set the path to houdini install folder')
            box.exec_()
            name = str(QFileDialog.getExistingDirectory(self, directory=self.lastPath))
            if name:
                gconvert = self.getGconvertFileName()
                fullPath = os.path.join(name, gconvert)
                if os.path.exists(fullPath):
                    self.gconvert = fullPath
                    self.saveSettings()
                else:
                    box = QMessageBox(self)
                    box.setWindowTitle('HFS path')
                    box.setText('WRONG PATH!!!')
                    box.exec_()
                    self.formatGeo_rb.setChecked(1)
            else:
                self.formatGeo_rb.setChecked(1)
            self.setList_lw.saveUiSettings()

    def getGconvertFileName(self):
        return  os.path.join('bin', 'gconvert.exe')


    def parsePath(self, line, format, zipp):
        #Check format
        if zipp:
            if not line[-7:] == '.geo.gz':
                line = line.replace('.geo','')
                line = line + self.textVariables['outFormats'][self.outFormat]
        else:
            if not line[-4:] == '.geo':
                line = line.replace('.geo.gz','')
                line = line + self.textVariables['outFormats'][self.outFormat]

        self.exportPath_le.setText(line)

        if self.rangeFrame_rb.isChecked():

            st = line.find('$F')
            if st > 0:
                pat = ''
                for f in line[st+2:]:
                    if f.isdigit():
                        pat += f
                    else:
                        break
                num = 1
                if pat:
                    num = int(pat)
                frame = str(int(cmds.currentTime(q=1))).zfill(num)
                pat = line[st:st+len(str(pat))+2]
                result = line.replace(pat, frame)
                return result
            else:
                split = os.path.splitext(line)
                line = ''.join([split[0],'_$F5', split[1]])
                return self.parsePath(line)
        else:
            return line

    def detectPath(self, sourcePath, format):
        if not sourcePath:
            return False
        #get File name
        extDict = {True:'geo', False: 'bgeo'}
        path = os.path.dirname(sourcePath)
        if not os.path.exists(path):
            return False
        file = os.path.basename(sourcePath)
        file = file.replace('.geo', '').replace('.bgeo', '').replace('.gz', '')
        ext = extDict[format]

        file = '.'.join([file,ext])
        result = os.path.join(path, file).replace('\\', '/')
        return result

    def getFileName(self):
        self.readSettings()
        dir = self.lastPath
        name = QFileDialog.getSaveFileName(self, 'Select file name', dir, self.getFileOpenFormat())
        #PyGt
        if qt == 'qt':
            name = str(name)
        #PySide
        elif qt == 'side':
            name = name[0]
        if name:
            self.exportPath_le.setText(name)
            self.lastPath = os.path.abspath(os.path.dirname(name))
            self.saveSettings()
            self.setList_lw.saveUiSettings('exportPath_le')
            return name

    def getFileOpenFormat(self):
        return ('*.geo; *.geo.gz; *.bgeo; *.bgeo.gz;')

    def enableUi2(self, *args):
        count = len(self.setList_lw.selectedItems())
        self.optionsWidget_wd.setEnabled(count == 1)
        self.outFile_gb.setEnabled(count == 1)
        self.frameRangeSettings_gb.setEnabled(count == 1)
        self.expoptions_gb.setEnabled(count == 1)
        for b in self.addToSet_btn, self.removeFromSet_btn, self.replaceSet_btn:
            b.setEnabled(count > 0)
        for b in self.deleteSet_btn, self.clearSet_btn:
            b.setEnabled(count > 0)
        # print count
        if count < 1:
            self.defaultUi()
        self.sequence_rb.setEnabled(self.rangeFrame_rb.isChecked())
        self.mdd_rb.setEnabled(self.rangeFrame_rb.isChecked())
        self.updateUi()

    def enableUi(self, *args):
        count = len(self.setList_lw.selectedItems())
        self.optionsWidget_wd.setEnabled(count)
        self.exportPath_le.setEnabled(count == 1)
        self.applets_btn.setEnabled(count == 1)
        self.frameRangeSettings_gb.setEnabled(count)
        self.expoptions_gb.setEnabled(count)
        for b in self.addToSet_btn, self.removeFromSet_btn, self.replaceSet_btn, self.deleteSet_btn, self.clearSet_btn:
            b.setEnabled(count)
        if not count:
            self.defaultUi()
        # self.writeFile_cb.setEnabled(self.mdd_rb.isChecked())
        self.sequence_rb.setEnabled(self.rangeFrame_rb.isChecked())
        self.mdd_rb.setEnabled(self.rangeFrame_rb.isChecked())
        self.updateUi()


    def readSettings(self):
        self.lastPath = self.settings.getValue('lastdir', os.path.expanduser('~'))
        self.gconvert = self.settings.getValue('gconvert', '')
        c = self.settings.getValue('report', False)
        self.extReport_act.setChecked(c)
        c = self.settings.getValue('isolate', False)
        self.isolateExported_act.setChecked(c)
        c = self.settings.getValue('marker', False)
        self.colorInd_act.setChecked(c)
        c = self.settings.getValue('warnings', True)
        self.showWarnings_act.setChecked(c)

    def saveSettings(self):
        self.settings.setValue('lastdir', self.lastPath)
        self.settings.setValue('report', self.extReport_act.isChecked())
        self.settings.setValue('isolate', self.isolateExported_act.isChecked())
        if self.gconvert:
            self.settings.setValue('gconvert', self.gconvert)
        self.settings.setValue('marker', self.colorInd_act.isChecked())
        self.settings.setValue('warnings', self.showWarnings_act.isChecked())


    def setInfoLabel(self):
        from .import text
        self.info_lb.setText(text.info)

    ## OUTPUT

    def msg2(self, w=0, *line):
        #extendet report
        if w == 2:
            if not self.extReport_act.isChecked():
                return
        #color
        color = {0: 'd3d3d3', 1: 'f0743d', 2: '6a6a6a'}
        #time
        now = datetime.datetime.now()
        nowtime = str(now.hour).zfill(2)+':' + str(now.minute).zfill(2)+':'+str(now.second).zfill(2)
        #generate message
        msg = '<span style="color:#%s;">%s &gt; %s</span><><br>' % (color.get(w, 0), nowtime, ' '.join(str(x) for x in line))
        self.output_te.insertHtml(msg)
        #scroll
        self.output_te.moveCursor(QTextCursor.End)
        self.output_te.ensureCursorVisible()
        #paint widget
        self.output_te.repaint()

    def clearOutput(self):
        self.output_te.clear()

    def statusMsg(self, line):
        self.statusBar.showMessage(line)

    def saveOptions(self):
        if len(self.setList_lw.selectedItems()) == 1:
            item = self.setList_lw.selectedItems()[0]
            path = QFileDialog.getSaveFileName(self, "Save file", self.lastPath, "mGeo Exporter (*.mgeo)")
            #PySide
            if qt == 'side':
                path = path[0]
            if path:
                ui = self.getUiOptions()
                try:
                    p = open(path, 'w')
                    for u in ui:
                        v = ui[u]
                        if isinstance(v, str):
                            v = '\'' + v + '\''
                        p.write(u + '=' + str(v) + '\n')
                    p.close()
                    self.msg2(0, 'Save settings for', item.text())
                except IOError:
                    self.msg2(1, 'Can not open file', path)
        else:
            self.msg2(1, 'Select one item for save')

    def loadOptions(self):
        if len(self.setList_lw.selectedItems()) == 1:
            path = QFileDialog.getOpenFileName(None, "Open File", self.lastPath, "mGeo Exporter (*.mgeo)")
            if qt == 'side':
                path = path[0]
            if path:
                ui = {}
                try:
                    p = open(path, 'r')
                    lines = p.readlines()
                    p.close()
                    for a in lines:
                        ui[a.partition('=')[0]] = eval(a.partition('=')[2].strip())
                    item = self.setList_lw.selectedItems()[0]
                    self.setList_lw.writeAttrib(self.setList_lw.getSetName(item), ui)
                    self.setList_lw.updateUi(item)
                    self.msg2(0, 'Load settings for', item.text())
                    self.updateUi()
                except IOError:
                    self.msg2(1, 'Can not open file', path)
        else:
            self.msg2(1, 'Select one item for load')

    def frange(self, start, stop, step):
        x = start
        while True:
            if x >= stop: return
            yield x
            x += step

############################################################ MENU
    def showHelp(self):
        d = QDesktopServices()
        x = self.url
        d.openUrl(QUrl(x))

    def showAbout(self):
        widget = aboutDialog(self)
        widget.show()


class aboutDialog(QDialog):
    def __init__(self, parent=None):
        super(aboutDialog, self).__init__(parent)
        self.parent = parent
        self.Layout = QVBoxLayout()
        self.label = QLabel()
        self.setWindowFlags( self.windowFlags() & ~Qt.WindowContextHelpButtonHint )
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setPixmap(QPixmap(":/pw_logo.png"))
        self.Layout.addWidget(self.label)

        self.text = QLabel()
        from . import text
        self.text.setText(text.getInfo(parent.version))
        self.text.setAlignment(Qt.AlignCenter)
        self.text.mouseReleaseEvent = self.openLink
        self.Layout.addWidget(self.text)

        self.pushButton = QPushButton('Close')
        self.pushButton.clicked.connect(self.close)
        self.Layout.addWidget(self.pushButton)
        self.setLayout(self.Layout)
        self.resize(300,250)
        self.setWindowTitle("About mGeo Exporter v{0}".format(parent.version))

    def openLink(self, event):
        self.parent.showHelp()


# def clear():
#     windows = qMayaWindow.findChildren(QWidget, 'mGeoExporterWindow')
#     for w in windows:
#        w.setParent(None)

# clear()
#mGeoWrite = mayaGeoWriter(qMayaWindow)
mGeoWrite = None

def show():
    if qt and support:
        global mGeoWrite
        mGeoWrite = mayaGeoWriter(qMayaWindow)
        mGeoWrite.show()


