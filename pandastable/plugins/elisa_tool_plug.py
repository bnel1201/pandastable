#!/usr/bin/env python
"""
    DataExplore Application plugin example.
    Created Oct 2015
    Copyright (C) Damien Farrell

    This program is free software; you can redistribute it and/or
    modify it under the terms of the GNU General Public License
    as published by the Free Software Foundation; either version 3
    of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

Created on January 2019
@author:  Marek Bawiec, Grzegorz Banach
The DataExplore plugin for ELISA experiment
__author__ = "Marek Bawiec, Grzegorz Banach"
__copyright__ = "Copyright 2019, Physiolution Polska"
__credits__ = [""]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Marek Bawiec"
__email__ = "m.bawiec@physiolution.pl"
__status__ = "Production"
"""

from __future__ import absolute_import, division, print_function
from tkinter import *
import tkinter
import re
import os
import sys
import time

import json
import pandas as pd
import elisa_tool_repo.main_func as mf
import logging

from tkinter import ttk


try:
    from tkinter.ttk import *
    from tkinter.scrolledtext import ScrolledText
except:
    from ttk import *
from pandastable.plugin import Plugin

if (sys.version_info > (3, 0)):
    from tkinter import filedialog, messagebox, simpledialog
else:
    import tkFileDialog as filedialog
    import tkSimpleDialog as simpledialog
    import tkMessageBox as messagebox
    from ScrolledText import ScrolledText

class elisaPlugin(Plugin):
    """Template plugin for DataExplore"""
    
    #uncomment capabilities list to appear in menu
    capabilities = ['gui', 'uses_sidepane']  # ['gui','uses_sidepane']
    requires = ['']
    menuentry = 'ELISA Plugin'
    pluginrow = 6  # row to add plugin frame beneath table
    
    def main(self, parent):
        """Customise this or _doFrame for your widgets"""

        if parent is None:
            return
        self.parent = parent
        self.parentframe = None
        lic_infoX, logo_pathX, errorsDictionaryX = self.setup()
        self.isFloat = self.parent.register(self.validate_float)
        self.isInt = self.parent.register(self.validate_int)
        self._doFrame(lic_info=lic_infoX, logo_path=logo_pathX, errDictionary=errorsDictionaryX)
        self.choiceVar.trace("w", self.on_trace_choice)
        self.choiceVarV.trace("w", self.on_trace_choice)
        self.choiceVarCon.trace("w", self.on_trace_choice)
        self.dataFileVar.trace("w", self.on_trace_choice)
        self.setupFileVar.trace("w", self.on_trace_choice)
        self.logoFileVar.trace("w", self.on_trace_choice)

        # self.refresh()
        return

    def getSize(self):
        parent = self.parent.master
        x = parent.winfo_rootx()
        y = parent.winfo_rooty()
        w = parent.winfo_width()
        h = parent.winfo_height()
        return x,y,w,h

    def validate_float(self, value):
        try:
            if value:
                v = float(value)
            return True
        except ValueError:
            return False
    
    def validate_int(self, value):
        try:
            if value:
                v = int(value)
            return True
        except ValueError:
            return False

    def _doFrame(self, lic_info, logo_path, errDictionary):

        if 'uses_sidepane' in self.capabilities:
            self.table = self.parent.getCurrentTable()
            self.mainwin = Frame(self.table.parentframe)
            #self.mainwin.pack(fill=BOTH, expand=True)
            self.mainwin.grid(row=6,column=0,columnspan=2,sticky='news')
            x,y,w,h = self.getSize()    
            self.parent.master.geometry('%dx%d+%d+%d' %(w+100,h,x,y-100))         
        else:
            self.mainwin = Toplevel()
            self.mainwin.title('A DataExplore Plugin')
            self.mainwin.geometry('600x600+200+100')

        self.ID = 'ELISA Plugin'
        self.mainwin.bind("<Destroy>", self.quit)

        # elisaPlugin widget
        self.elisaPlugin = ttk.Frame(self.mainwin)
        #self.elisaPlugin = Tk()
        self.elisaPlugin.configure(height='120', takefocus='true')

        # Notebooks widget
        self.nb = ttk.Notebook(self.elisaPlugin)
        self.nb.grid(column='0', row='0')
        self.tabApproximation = ttk.Frame(self.nb)
        self.nb.add(self.tabApproximation, text="Approximation")
        self.tabConfiguration = ttk.Frame(self.nb)
        self.nb.add(self.tabConfiguration, text="Configuration")
        self.tabValidation = ttk.Frame(self.nb)
        self.nb.add(self.tabValidation, text="Validation")

        # approximationframe widget
        self.approximationframe = ttk.Frame(self.tabApproximation)
        self.approximationframe.configure(padding='8')
        self.methodChooseFrame = ttk.Frame(self.approximationframe)
        self.methodChooseLabel = ttk.Label(self.methodChooseFrame, text='Choose Method')
        self.methodChooseLabel.grid(column='0', row='0')
        self.methodChooseCombobox = ttk.Combobox(self.methodChooseFrame, state='readonly',
                                                 textvariable=self.choiceVar)
        self.methodChooseCombobox.grid(column='0', row='1')
        list_itemsA = ["4PL curve_fit", "5PL curve_fit", "LN curve_fit", "LIN curve_fit", 
                       "4PL diff_evol", "5PL diff_evol", "LN diff_evol", "LIN diff_evol"]
        self.methodChooseCombobox['values'] = list_itemsA
        self.methodChooseCombobox.set(list_itemsA[0])
        
        self.methodChooseFrame.grid(column='0', row='0')
        # paramsFrame widget
        self.paramsFrame = ttk.Frame(self.approximationframe)
        self.paramsFrame.configure(height='20')
        # paramA widget
        self.paramA = ttk.Label(self.paramsFrame)
        self.paramA.configure(text='A ')
        self.paramA.grid(column='0', row='0')
        # paramB widget
        self.paramB = ttk.Label(self.paramsFrame)
        self.paramB.configure(text='B ')
        self.paramB.grid(column='0', row='1')
        # paramC widget
        self.paramC = ttk.Label(self.paramsFrame)
        self.paramC.configure(text='C ')
        self.paramC.grid(column='0', row='2')
        # paramD widget
        self.paramD = ttk.Label(self.paramsFrame)
        self.paramD.configure(text='D ')
        self.paramD.grid(column='0', row='3')
        # paramE widget
        self.paramE = ttk.Label(self.paramsFrame)
        self.paramE.configure(text='E ')
        self.paramE.grid(column='0', row='4')
        # paramAfrom widget
        self.paramAfrom = ttk.Entry(self.paramsFrame)
        self.paramAfrom.insert(END, 'from')
        self.paramAfrom.configure(width='9', validate='key',
                                  validatecommand=(self.isFloat, '%P'))
        self.paramAfrom.grid(column='1', row='0')
        # paramBfrom widget
        self.paramBfrom = ttk.Entry(self.paramsFrame)
        self.paramBfrom.configure(width='9', validate='key',
                                  validatecommand=(self.isFloat, '%P'))
        self.paramBfrom.insert(END, 'from')
        self.paramBfrom.grid(column='1', row='1')
        # paramCfrom widget
        self.paramCfrom = ttk.Entry(self.paramsFrame)
        self.paramCfrom.configure(width='9', validate='key',
                                  validatecommand=(self.isFloat, '%P'))
        self.paramCfrom.insert(END, 'from')
        self.paramCfrom.grid(column='1', row='2')
        # paramDfrom widget
        self.paramDfrom = ttk.Entry(self.paramsFrame)
        self.paramDfrom.configure(width='9', validate='key',
                                  validatecommand=(self.isFloat, '%P'))
        self.paramDfrom.insert(END, 'from')
        self.paramDfrom.grid(column='1', row='3')
        # paramEfrom widget
        self.paramEfrom = ttk.Entry(self.paramsFrame)
        self.paramEfrom.configure(width='9', state=DISABLED, validate='key',
                                  validatecommand=(self.isFloat, '%P'))
        self.paramEfrom.insert(END, 'from')
        self.paramEfrom.grid(column='1', row='4')
         # separator1 widget
        self.separator1 = ttk.Label(self.paramsFrame)
        self.separator1.configure(text=':')
        self.separator1.grid(column='2', row='0')
        # separator2 widget
        self.separator2 = ttk.Label(self.paramsFrame)
        self.separator2.configure(text=':')
        self.separator2.grid(column='2', row='1')
        # separator3 widget
        self.separator3 = ttk.Label(self.paramsFrame)
        self.separator3.configure(text=':')
        self.separator3.grid(column='2', row='2')
        # separator4 widget
        self.separator4 = ttk.Label(self.paramsFrame)
        self.separator4.configure(text=':')
        self.separator4.grid(column='2', row='3')
         # separator4 widget
        self.separator5 = ttk.Label(self.paramsFrame)
        self.separator5.configure(text=':')
        self.separator5.grid(column='2', row='4')
        # paramAto widget
        self.paramAto = ttk.Entry(self.paramsFrame)
        self.paramAto.insert(END, 'to')
        self.paramAto.configure(width='9', validate='key',
                                validatecommand=(self.isFloat, '%P'))
        self.paramAto.grid(column='4', row='0')
        # paramBto widget
        self.paramBto = ttk.Entry(self.paramsFrame)
        self.paramBto.configure(width='9', validate='key',
                                validatecommand=(self.isFloat, '%P'))
        self.paramBto.insert(END, 'to')
        self.paramBto.grid(column='4', row='1')
        # paramCto widget
        self.paramCto = ttk.Entry(self.paramsFrame)
        self.paramCto.configure(width='9', validate='key',
                                validatecommand=(self.isFloat, '%P'))
        self.paramCto.insert(END, 'to')
        self.paramCto.grid(column='4', row='2')
        # paramDto widget
        self.paramDto = ttk.Entry(self.paramsFrame)
        self.paramDto.configure(width='9', validate='key',
                                validatecommand=(self.isFloat, '%P'))
        self.paramDto.insert(END, 'to')
        self.paramDto.grid(column='4', row='3')
         # paramEto widget
        self.paramEto = ttk.Entry(self.paramsFrame)
        self.paramEto.configure(width='9', state=DISABLED, validate='key',
                                validatecommand=(self.isFloat, '%P'))
        self.paramEto.insert(END, 'to')
        self.paramEto.grid(column='4', row='4')
        self.paramsFrame.grid(column='0', row='1')
        self.approximationframe.grid(column='0', row='1')
        # commandFrame widget
        self.commandFrame = ttk.Frame(self.tabApproximation)
        # buttonFrame widget
        self.buttonFrame = ttk.Labelframe(self.commandFrame)
        self.buttonFrame.configure(labelanchor='n', padding='5',  text='Commands') # , relief='flat')
        # buttonDataFile widget
        self.buttonDataFile = ttk.Button(self.buttonFrame,
                    command=lambda: self.getFile('data'))
        self.buttonDataFile.configure(text='Read Raw Data')
        self.buttonDataFile.grid(column='0', row='0')
        # entryDataFile widget
        self.entryDataFile = ttk.Entry(self.buttonFrame)
        self.entryDataFile.insert(END, 'file with taken data')
        self.entryDataFile.grid(column='1', row='0')
        # buttonSetupFile widget
        self.buttonSetupFile = ttk.Button(self.buttonFrame, 
                    command=lambda: self.getFile('setup'))
        self.buttonSetupFile.configure(text='Setup')
        self.buttonSetupFile.grid(column='0', row='1')
        # entrySetupFile widget
        self.entrySetupFile = ttk.Entry(self.buttonFrame)
        self.entrySetupFile.insert(END, 'xlsx/xls file with setup')
        self.entrySetupFile.grid(column='1', row='1')
        # buttonCheck widget
        self.buttonCheck = ttk.Button(self.buttonFrame)
        self.buttonCheck.configure(text='Check', command=self.callCheck)
        self.buttonCheck.grid(column='0', row='2')
        # lableCheck widget
        self.lableCheck = ttk.Label(self.buttonFrame)
        self.lableCheck.configure(text='status')
        self.lableCheck.grid(column='1', row='2')
        # buttonWriteReport widget
        self.buttonWriteReport = ttk.Button(self.buttonFrame,  command=self.getFolder)
        self.buttonWriteReport.configure(text='Report')
        self.buttonWriteReport.grid(column='0', row='3')
        # entryReportFile widget
        self.entryReportFile = ttk.Entry(self.buttonFrame)
        self.entryReportFile.configure(font='TkDefaultFont')
        self.entryReportFile.insert(END, 'folder to store report')
        self.entryReportFile.grid(column='1', row='3')
        # buttonCalculate widget
        self.buttonCalculate = ttk.Button(self.buttonFrame,
                                          command=self.callCalculateA)
        self.buttonCalculate.configure(text='Calculate')
        self.buttonCalculate.grid(column='0', row='4')
        # labelCalcuateStatus widget
        self.labelCalcuateStatus = ttk.Label(self.buttonFrame)
        self.labelCalcuateStatus.configure(text='status')
        self.labelCalcuateStatus.grid(column='1', row='4')
        self.buttonFrame.grid(column='0', row='0')
        self.commandFrame.grid(column='1', row='1')
        
        # #####################VALIDATION################
        # validationFrame widget
        self.validationFrame = ttk.Frame(self.tabValidation)
        self.validationFrame.configure(padding='5')

        self.allParamsFrameV = ttk.Frame(self.validationFrame)
        self.allParamsFrameV.configure(padding='5')

        self.methodChooseFrameV = ttk.Frame(self.allParamsFrameV)
        self.methodChooseLabelV = ttk.Label(self.methodChooseFrameV,
                                            text='Choose Method')
        self.methodChooseLabelV.grid(column='0', row='0')
        self.methodChooseComboboxV = ttk.Combobox(
                                    self.methodChooseFrameV,
                                    state='readonly',
                                    textvariable=self.choiceVarV)
        self.methodChooseComboboxV.grid(column='0', row='1')
        list_itemsV = ["4PL curve_fit-val", "5PL curve_fit-val", "LIN curve_fit-val", "LN curve_fit-val", 
                       "4PL diff_evol-val", "5PL diff_evol-val", "LIN diff_evol-val", "LN diff_evol-val"]
        self.methodChooseComboboxV['values'] = list_itemsV
        self.methodChooseComboboxV.set(list_itemsV[0])

        # paramsFrameV widget
        self.paramsFrameV = ttk.Frame(self.allParamsFrameV)
        self.paramsFrameV.configure(height='20', padding='5')
        # noise widget
        self.noise = ttk.Label(self.paramsFrameV)
        self.noise.configure(text='noise')
        self.noise.grid(column='0', row='0')
        # points widget
        self.points = ttk.Label(self.paramsFrameV)
        self.points.config(text='points')
        self.points.grid(column='0', row='1')
        # noiseEntry widget
        self.noiseEntry = ttk.Entry(self.paramsFrameV)
        self.noiseEntry.insert(END, '0')
        self.noiseEntry.config(width='9', validate='key',
                               validatecommand=(self.isFloat, '%P'))
        self.noiseEntry.grid(column='1', row='0')
        # pointsEntry widget
        self.pointsEntry = ttk.Entry(self.paramsFrameV)
        self.pointsEntry.configure(width='9', validate='key',
                                   validatecommand=(self.isInt, '%P'))
        self.pointsEntry.insert(END, '40')
        self.pointsEntry.grid(column='1', row='1')
        self.pointsEntry.propagate(False)     
        
        # commandFrameV widget
        self.commandFrameV = ttk.Frame(self.validationFrame)
        # buttonFrameV widget
        self.buttonFrameV = ttk.Labelframe(self.commandFrameV)
        self.buttonFrameV.configure(labelanchor='n', padding='5', text='Commands')
        # buttonWriteReportV widget
        self.buttonWriteReportV = ttk.Button(self.buttonFrameV, command=lambda: self.getFolder())
        self.buttonWriteReportV.configure(text='Report')
        self.buttonWriteReportV.grid(column='0', row='0')
        # labelReportFileV widget
        self.entryReportFileV = ttk.Entry(self.buttonFrameV)
        self.entryReportFileV.insert(END, 'folder to store report')
        self.entryReportFileV.grid(column='1', row='0')
        # buttonCalculateV widget
        self.buttonCalculateV = ttk.Button(self.buttonFrameV, command=lambda: self.callCalculateV())
        self.buttonCalculateV.configure(text='Calculate')
        self.buttonCalculateV.grid(column='0', row='1')
        # labelCalcuateStatusV widget
        self.labelCalcuateStatusV = ttk.Label(self.buttonFrameV)
        self.labelCalcuateStatusV.configure(text='status')
        self.labelCalcuateStatusV.grid(column='1', row='1')
        
        self.validationFrame.grid(column='0', row='0')
        self.allParamsFrameV.grid(column='0', row='0')
        self.methodChooseFrameV.grid(column='0', row='0')
        self.paramsFrameV.grid(column='0', row='1')
        self.commandFrameV.grid(column='1', row='0')
        self.buttonFrameV.grid(column='0', row='0')
       
        # labelTool widget
        self.labelTool = ttk.Label(self.elisaPlugin)
        self.labelTool.configure(font='{} 12 {bold}', text='ELISA Tool')
        self.labelTool.grid(column='0', row='0', sticky='en')
        self.labelTool.propagate(True)
        
        self.displayConfigParams(self.methodChooseCombobox.get())

        # #####################CONFIGURATION################
        # configurationFrame widget
        self.configurationFrame = ttk.Frame(self.tabConfiguration)
        self.configurationFrame.configure(padding='5')

        self.allParamsFrameC = ttk.Frame(self.configurationFrame)
        self.allParamsFrameC.configure(padding='5')
        # Input Method widget (repres_run)
        self.methodChooseFrameC = ttk.Frame(self.allParamsFrameC)
        self.methodChooseLabelC = ttk.Label(self.methodChooseFrameC, text='Input Form:')
        self.methodChooseLabelC.grid(column='0', row='0')
        self.methodChooseComboboxC = ttk.Combobox(self.methodChooseFrameC,
                                    state='readonly', textvariable=self.choiceVarCon)
        self.methodChooseComboboxC.grid(column='1', row='0')
        list_itemsC = ["lin_lin", "ln_lin", "lin_ln", "ln_ln"]
        self.methodChooseComboboxC['values'] = list_itemsC
        self.methodChooseComboboxC.set(list_itemsC[0])

        # paramsFrameC widget
        self.paramsFrameC = ttk.Frame(self.allParamsFrameC)
        self.paramsFrameC.configure(height='20', padding='5')
        # noise widget
        self.noise2 = ttk.Label(self.paramsFrameC)
        self.noise2.configure(text='License:')
        self.noise2.grid(column='0', row='0')
        # noiseEntry widget

        self.noiseEntry2 = ttk.Entry(self.paramsFrameC)
        self.noiseEntry2.config(width='46')
        self.noiseEntry2.insert(END, lic_info)
        #self.noiseEntry2.config(width='30', textvariable=StringVar())
        self.noiseEntry2.grid(column='1', row='0')

        # buttonDataFile widget
        self.buttonDataFileLogo = ttk.Button(self.paramsFrameC, 
                                             command=lambda: self.getPngPath('logo'))
        self.buttonDataFileLogo.configure(text='Logo file:')
        self.buttonDataFileLogo.grid(column='0', row='1')
        
        self.entryDataFileLogo = ttk.Entry(self.paramsFrameC)
        self.entryDataFileLogo.config(width='46')
        self.entryDataFileLogo.insert(END, logo_path)
        self.entryDataFileLogo.grid(column='1', row='1')
        #logo_file = self.entryDataFileLogo.get()

        self.configurationFrame.grid(column='0', row='0')
        self.allParamsFrameC.grid(column='0', row='0')
        self.methodChooseFrameC.grid(column='0', row='0')
        self.paramsFrameC.grid(column='0', row='1')
        
################################################################################

        self.elisaPlugin.grid(column='0', row='0')
      
        return

    def quit(self, evt=None):
        """Override this to handle pane closing"""
        
        return

    def about(self):
        """About this plugin"""
        txt = "ELISA plugin implements ...\n" + "version: %s" %self.version
        return txt

    def getFile(self, name, path=None):
        """Get a file"""
        if path is None:
            path = filedialog.askopenfilename(parent=self.mainwin,
                    initialdir=self.currentdir, filetypes=(("Excel 2007-365,",
                    "*.xlsx"), ("Excel 97-2003,",
                    "*.xls"), ("all files", "*.*")),
                    title='Show me the data file')
        else:
            path = filedialog.askopenfilename(parent=self.mainwin,
                    initialdir=path, filetypes=(("Excel 2007-365,",
                    "*.xlsx"), ("Excel 97-2003,",
                    "*.xls"), ("all files", "*.*")),
                    title='Show me the data file')
        if name == "setup":
            self.setupFileVar.set(path)
        elif name == "data":
            self.dataFileVar.set(path)
        table = self.parent.getCurrentTable()
        table.loadExcel(path)
        table.redraw()
        return

    def getPngPath(self, name, path=None):
        """Get a png file"""
        if path is None:
            path = filedialog.askopenfilename(parent=self.mainwin,
                    initialdir=self.currentdir, filetypes=(("Graphics,",
                    "*.png"), ("all files", "*.*")),
                    title='Show me the png file')
        else:
            path = filedialog.askopenfilename(parent=self.mainwin,
                    initialdir=path, filetypes=(("Graphics,",
                    "*.png"), ("all files", "*.*")),
                    title='Show me the png file')
        if name == "logo":
            self.logoFileVar.set(path)
        #table = self.parent.getCurrentTable()
        #table.loadExcel(path)
        #table.redraw()
        return


    def refreshSetupFileEntry(self, path):
        self.entrySetupFile.delete(0, END)
        self.entrySetupFile.insert(0, path)

    def refreshDataFileEntry(self, path):
        self.entryDataFile.delete(0, END)
        self.entryDataFile.insert(0, path)

    def refreshLogoFileEntry(self, path):
        self.entryDataFileLogo.delete(0, END)
        self.entryDataFileLogo.insert(0, path)

    def on_trace_choice(self, name, index, mode):
        if name == str(self.choiceVar):
            self.refreshParams(self.choiceVar.get())
        if name == str(self.dataFileVar):
            self.refreshDataFileEntry(self.dataFileVar.get())
        if name == str(self.setupFileVar):
            self.refreshSetupFileEntry(self.setupFileVar.get())
        if name == str(self.logoFileVar):
            self.refreshLogoFileEntry(self.logoFileVar.get())
        return

    def setup(self):
        # self.currentdir = os.path.expanduser('~user')
        self.currentdir = os.path.expanduser("~/repos/physiolution/elisa-tool/template")
        # variable used with comboboxs 
        self.choiceVar = tkinter.StringVar()
        self.choiceVarV = tkinter.StringVar()
        self.choiceVarCon = tkinter.StringVar()
        self.reportFolerVar = tkinter.StringVar()
        self.reportFolerVarV = tkinter.StringVar()
        self.logoFileVar = tkinter.StringVar()
        self.dataFileVar = tkinter.StringVar()
        self.setupFileVar = tkinter.StringVar()

        """
        Readinng configuration file elias_tool_repo/elisa-tool.conf:
        1. license text
        2. logo
        3. ranges for parameters of methods
        We need error support here: no_file
        """
        errors_file = open('pandastable/plugins/elisa_tool_repo/error_table.conf')
        errors_dic = errors_file.read()
        self.errDictionary = json.loads(errors_dic)
        errorsDictionary = self.errDictionary

        conf_file = open('pandastable/plugins/elisa_tool_repo/elisa-tool.conf')
        conf_str = conf_file.read()
        self.etConfig = json.loads(conf_str)
        lic_info = self.etConfig["licence_notice"]
        logo_path = self.etConfig["logo"]
        """
        set default parametres in plot tool 
        """
        table = self.parent.getCurrentTable()
        a = table.pf
        a.applyPlotoptions()
        kwds = a.mplopts.kwds
        kwds['use_index'] = False
        kwds['marker'] = 'x'
        kwds['alpha'] = 0.5
        kwds['linewidth'] = 2.6
        kwds['fontsize'] = 11
        kwds['ms'] = 11
        kwds['grid'] = True
        a.updateStyle()
        a.toolslayout = 'vertical'
        a.refreshLayout()
        a._initFigure()
        return lic_info, logo_path, errorsDictionary

    def displayConfigParams(self, what):
        setup = self.etConfig[what]
        for idx, i in enumerate(setup):
            ancorFrom = getattr(self, 'param'+chr(65+idx)+'from')
            ancorFrom.delete(0, END)
            ancorFrom.insert(0, setup[i][0])
            ancorTo = getattr(self,  'param'+chr(65+idx)+'to')
            ancorTo.delete(0, END)
            ancorTo.insert(0, setup[i][1])
            
        return

    def refreshParams(self, what):
        if what.find('LN') >= 0:
            self.paramCfrom.config(state=DISABLED)
            self.paramCto.config(state=DISABLED)
            self.paramDfrom.config(state=DISABLED)
            self.paramDto.config(state=DISABLED)
            self.paramEfrom.config(state=DISABLED)
            self.paramEto.config(state=DISABLED)
            self.displayConfigParams(what)

        elif what.find('4') >= 0:
            self.paramCfrom.config(state=NORMAL)
            self.paramCto.config(state=NORMAL)
            self.paramDfrom.config(state=NORMAL)
            self.paramDto.config(state=NORMAL)
            self.paramEfrom.config(state=DISABLED)
            self.paramEto.config(state=DISABLED)
            self.displayConfigParams(what)

        elif what.find('5') >= 0:
            self.paramCfrom.config(state=NORMAL)
            self.paramCto.config(state=NORMAL)
            self.paramDfrom.config(state=NORMAL)
            self.paramDto.config(state=NORMAL)
            self.paramEfrom.config(state=NORMAL)
            self.paramEto.config(state=NORMAL)
            self.displayConfigParams(what)

        elif what.find('LI') >= 0:
            self.paramCfrom.config(state=DISABLED)
            self.paramCto.config(state=DISABLED)
            self.paramDfrom.config(state=DISABLED)
            self.paramDto.config(state=DISABLED)
            self.paramEfrom.config(state=DISABLED)
            self.paramEto.config(state=DISABLED)
            self.displayConfigParams(what)

        return

    def getParams(self):
        params = []
        params.append([self.paramAfrom.get(), self.paramAto.get()])
        params.append([self.paramBfrom.get(), self.paramBto.get()])
        params.append([self.paramCfrom.get(), self.paramCto.get()])
        params.append([self.paramDfrom.get(), self.paramDto.get()])
        params.append([self.paramEfrom.get(), self.paramEto.get()])
        return params

    def callCheck(self):
        """
        Data consistency: the signal function implemented in order to validate some formatting parameters of the input data.
        """

        print(self.entryDataFile.get())
        print(self.entrySetupFile.get())
        if (not os.path.isfile(self.entryDataFile.get()) or
           not os.path.isfile(self.entrySetupFile.get())):
            self.lableCheck["text"] = "failed"
            messagebox.showerror("Error", 'There is not such file: %s \n  and/or \n %s' %  (self.entryDataFile.get(), self.entrySetupFile.get()))
            return
        else:
            path_rd = self.entryDataFile.get()
            path_st = self.entrySetupFile.get()

            check_res, df = mf.check_function(Fpath_tekan=path_rd,
                                        Fpath_config=path_st)
            print("@check_res?:",check_res)

        params = self.getParams()
        print("@params?:",params)
        method = self.methodChooseCombobox.get()
        print("@method?:",method)

        if method.find('LN') >= 0:
            nbParams = 2
        elif method.find('4') >= 0:
            nbParams = 4
        elif method.find('5') >= 0:
            nbParams = 5
        elif method.find('LI') >= 0:
            nbParams = 2

        for idx in range(nbParams):
            print(chr(65+idx), ' : ', params[idx])
            # check if all params set
            try:
                #list(map(float, params[idx]))
                print("float(", chr(65+idx), ') : ',
                      list(map(float, params[idx])))
            except ValueError:
                print("wrong value")
                self.lableCheck["text"] = "failed"
                messagebox.showerror("Error", 'Wrong values for parameter: '+chr(65+idx))
            self.lableCheck["text"] = "passed"

            table = self.parent.getCurrentTable()
            table.model.df = df
            table.redraw()
            self.plotResult_std(df, check_res)

        return

    def callCalculateA(self):
        # print("Do what you wont!")
        # print("Report folder: ", self.entryReportFile.get())
        if not os.path.isdir(self.entryReportFile.get()):
            self.labelCalcuateStatus["text"] = "failed"
            messagebox.showerror("Error", 'There is not such dir: %s' %
                                 self.entryReportFile.get())
            return

        else:
            res_fol = self.entryReportFile.get()
            self.labelCalcuateStatus["text"] = "starated"
        
        path_rd = self.entryDataFile.get()
        path_st = self.entrySetupFile.get()
        repres_run = self.methodChooseComboboxC.get()
        examp_run = self.methodChooseCombobox.get()
        
        if ((examp_run == "LN diff_evol") or (examp_run == "LN curve_fit")):
            self.etConfig[examp_run] = {"A": [float(self.paramAfrom.get()),
                                              float(self.paramAto.get())],
                                        "B": [float(self.paramBfrom.get()),
                                              float(self.paramBto.get())]}
        if ((examp_run == "4PL diff_evol") or (examp_run == "4PL curve_fit")):
            self.etConfig[examp_run] = {"A": [float(self.paramAfrom.get()),
                                              float(self.paramAto.get())],
                                        "B": [float(self.paramBfrom.get()),
                                              float(self.paramBto.get())],
                                        "C": [float(self.paramCfrom.get()),
                                              float(self.paramCto.get())],
                                        "D": [float(self.paramDfrom.get()),
                                              float(self.paramDto.get())]}
        if ((examp_run == "5PL diff_evol") or (examp_run == "5PL curve_fit")):
            self.etConfig[examp_run] = {"A": [float(self.paramAfrom.get()),
                                              float(self.paramAto.get())],
                                        "B": [float(self.paramBfrom.get()),
                                              float(self.paramBto.get())],
                                        "C": [float(self.paramCfrom.get()),
                                              float(self.paramCto.get())],
                                        "D": [float(self.paramDfrom.get()),
                                              float(self.paramDto.get())],
                                        "E": [float(self.paramEfrom.get()),
                                              float(self.paramEto.get())]}
        if ((examp_run == "LIN diff_evol") or (examp_run == "LIN curve_fit")):
            self.etConfig[examp_run] = {"A": [float(self.paramAfrom.get()),
                                              float(self.paramAto.get())],
                                        "B": [float(self.paramBfrom.get()),
                                              float(self.paramBto.get())]}
           
        if "val" not in examp_run:
            print("@repres_run: ", repres_run)
            lic_info = self.etConfig["licence_notice"]
            logo_path = self.etConfig["logo"]            
            start_range = self.etConfig[examp_run]
            errorsDictionary = self.errDictionary
            df, error_info, status_info = mf.main_calc(repres_run, examp_run, path_rd, path_st, res_fol, 
                                        start_range, lic_info, logo_path, errorsDictionary)
            self.labelCalcuateStatus["text"] = status_info
            print("@@status_info: ", status_info)
            if "err:" not in status_info:         
                table = self.parent.getCurrentTable()
                table.model.df = df
                table.redraw()
                self.plotResult(df, error_info)                       
            if ("data warning" in error_info) or ("method warning" in error_info):         
                table = self.parent.getCurrentTable()
                table.model.df = df
                table.redraw()
                self.plotResult(df, error_info)                       
        mainloop()   
        return

    def callCalculateV(self):
        """
        Validation    
        """
        examp_run = self.methodChooseComboboxV.get()
        tmp2 = self.pointsEntry.get()
        tmp1 = self.noiseEntry.get()
        if not os.path.isdir(self.entryReportFileV.get()):
            self.labelCalcuateStatusV["text"] = "failed"
            messagebox.showerror("Error", 'There is not such dir: %s' %self.entryReportFileV.get())
            return
        else:
            name_report = self.entryReportFileV.get()
        self.labelCalcuateStatusV["text"] = "starated"
        if "val" in examp_run:
           df, err_info = \
            mf.validation_eng(option=examp_run, noise=float(tmp1), points=int(tmp2),
                              val_report=name_report)
        """
        output: df('X_theor', 'Y_theor', 'X_std', 'Y_std', 'X_sam', 'Y_sam') - _theor is bigger than _std and _sam!
        """
        self.labelCalcuateStatusV["text"] = err_info
        text_output = "is it works?"
        table = self.parent.getCurrentTable()
        table.model.df = df
        table.redraw()
        self.plotResult(df, text_output)
        mainloop()
        return

    def plotResult(self, df, text_output):
        table = self.parent.getCurrentTable()
        a = table.pf
        a.applyPlotoptions()
        kwds = a.mplopts.kwds
        a._initFigure()
        kwds = a.mplopts.kwds
        a.data = df
        ax = a.fig.add_subplot(111)
        if kwds['grid']:
            ax.grid(True)
        
        ax.plot(df.iloc[:, [0]], df.iloc[:, [1]], 'b',
                linestyle=kwds['linestyle'],
                linewidth=kwds['linewidth'],
                label=df.columns.values[1],
                alpha=kwds['alpha'])

        ax.plot(df.iloc[:, [2]], df.iloc[:, [3]], 'gx',
                markersize=kwds['ms'],
                marker=kwds['marker'],
                label=df.columns.values[3],
                alpha=kwds['alpha'])

        ax.plot(df.iloc[:, [4]], df.iloc[:, [5]],  'ro',
                markersize=kwds['ms'],
                #marker=kwds['marker'],
                label=df.columns.values[5],
                alpha=kwds['alpha'])

        ax.legend(loc='best')
        ax.set_title('Calculation: ' + text_output)
        a.canvas.draw()

    def plotResult_std(self, df, text_output):
        table = self.parent.getCurrentTable()
        a = table.pf
        a.applyPlotoptions()
        kwds = a.mplopts.kwds
        a._initFigure()
        kwds = a.mplopts.kwds
        a.data = df
        ax = a.fig.add_subplot(111)
        if kwds['grid']:
            ax.grid(True)
        
        ax.plot(df.iloc[:, [0]], df.iloc[:, [1]],  'ro',
                markersize=kwds['ms'],
                #marker=kwds['marker'],
                label=df.columns.values[1],
                alpha=kwds['alpha'])

        ax.legend(loc='best')
        ax.set_title('Std data mean: ' + text_output)
        a.canvas.draw()


    def getFolder(self, path=None):
        """Get a folder"""
        if path is None:
            path = filedialog.askdirectory(parent=self.mainwin,
                                           initialdir=self.currentdir,
                                           title='Select folder for report')
        else:
            path = filedialog.askdirectory(parent=self.mainwin,
                                           initialdir=path,
                                           title='Select folder for reprot')
        self.entryReportFile.delete(0, END)
        self.entryReportFile.insert(0, path)
        self.entryReportFileV.delete(0, END)
        self.entryReportFileV.insert(0, path)

        return
