#!/usr/bin/python
# -*- coding: utf-8 -*-

#used some code from the WxPython wiki:
#-1.4 Recursively building a list into a wxTreeCtrl (yet another sample) by Rob
#-1.5 Simple Drag and Drop by Titus
#-TraversingwxTree

#tested on wxPython 2.5.4 and Python 2.4, under Windows and Linux

import os, sys
import  wx
import wx.stc
import thread
import time

import cPickle as pickle

from shutil import copy, copytree, rmtree
import config
from converter import doc2pdf, img2pdf, randStr

HAS_LICENCE=False

if HAS_LICENCE:
    from license import License
    
from MyFrame import MyFrame
from MyTree import MyTreeCtrlPanel

APP_NAME = "PDF Assistant"

class MyLog:
    def __init__(self):
        pass
    def WriteText(self, text):
        print text

class RedirectText:
    def __init__(self,aWxTextCtrl):
        self.out=aWxTextCtrl
  
    def write(self,string):
        self.out.AddText(string)
  
class ProcessRunnerMix:
    def __init__(self, input, handler=None):
        if handler is None:
            handler = self
        self.handler = handler
        handler.Bind(wx.EVT_IDLE, self.OnIdle)
        handler.Bind(wx.EVT_END_PROCESS, self.OnProcessEnded)
  
        input.reverse() # so we can pop
        self.input = input
  
        self.reset()
  
    def reset(self):
        self.process = None
        self.pid = -1
        self.output = []
        self.errors = []
        self.inputStream = None
        self.errorStream = None
        self.outputStream = None
        self.outputFunc = None
        self.errorsFunc = None
        self.finishedFunc = None
        self.finished = False
        self.responded = False
  
    def execute(self, cmd):
        self.process = wx.Process(self.handler)
        self.process.Redirect()
  
        self.pid = wx.Execute(cmd, wx.EXEC_ASYNC, self.process)
  
        self.inputStream = self.process.GetOutputStream()
        self.errorStream = self.process.GetErrorStream()
        self.outputStream = self.process.GetInputStream()
  
        # self.OnIdle()
        wx.WakeUpIdle()
  
    def setCallbacks(self, output, errors, finished):
        self.outputFunc = output
        self.errorsFunc = errors
        self.finishedFunc = finished
  
    def detach(self):
        if self.process is not None:
            self.process.CloseOutput()
            self.process.Detach()
            self.process = None
  
    def kill(self):
        if self.process is not None:
            self.process.CloseOutput()
            if wx.Process.Kill(self.pid, wx.SIGTERM) != wx.KILL_OK:
                wx.Process.Kill(self.pid, wx.SIGKILL)
            self.process = None
  
    def updateStream(self, stream, data):
        if stream and stream.CanRead():
            if not self.responded:
                self.responded = True
            text = stream.read()
            data.append(text)
            return text
        else:
            return None
  
    def updateInpStream(self, stream, input):
        if stream and input:
            line = input.pop()
            stream.write(line)
  
    def updateErrStream(self, stream, data):
        return self.updateStream(stream, data)
  
    def updateOutStream(self, stream, data):
        return self.updateStream(stream, data)
  
    def OnIdle(self, event=None):
        if self.process is not None:
            self.updateInpStream(self.inputStream, self.input)
            e = self.updateErrStream(self.errorStream, self.errors)
            if e is not None and self.errorsFunc is not None:
                wx.CallAfter(self.errorsFunc, e)
            o = self.updateOutStream(self.outputStream, self.output)
            if o is not None and self.outputFunc is not None:
                wx.CallAfter(self.outputFunc, o)
  
            #wxWakeUpIdle()
            #time.sleep(0.001)
  
    def Close(self):
        # print "Subprocess terminated"
        return
  
    def OnProcessEnded(self, event):
        self.OnIdle()
  
        if self.process:
            self.process.Destroy()
            self.process = None
  
        self.finished = True
  
        # XXX doesn't work ???
        #self.handler.Disconnect(-1, wxEVT_IDLE)
  
        if self.finishedFunc:
            wx.CallAfter(self.finishedFunc)
  
class ProcessRunner(wx.EvtHandler, ProcessRunnerMix):
    def __init__(self, input):
        wx.EvtHandler.__init__(self)
        ProcessRunnerMix.__init__(self, input)
  
def wxPopen3(cmd, input, output, errors, finish, handler=None):
    p = ProcessRunnerMix(input, handler)
    p.setCallbacks(output, errors, finish)
    p.execute(cmd)
    return p

class MainFrame(MyFrame):
    def __init__(self, *args, **kwds):
        MyFrame.__init__(self, *args, **kwds)
        
        log = MyLog()

        # variables
        self.modify = False
        self.last_name_saved = ''
        self.replace = False

        self.pnl = MyTreeCtrlPanel(self, log)
        self.gauge = wx.Gauge(self)
##        self.log = wx.TextCtrl(self, -1, size=(500,100),
##                               style = wx.TE_MULTILINE|wx.TE_READONLY|
##                               wx.HSCROLL)

        self.log = wx.stc.StyledTextCtrl(id=-1, parent=self, size=(500,100),
                               style = wx.TE_MULTILINE|wx.TE_READONLY|
                               wx.HSCROLL)

        # -- Set up console redirection
        redir = RedirectText(self.log)
        sys.stdout = redir
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox1.Add(self.pnl, proportion=1, flag=wx.EXPAND)
        sizer.Add(hbox1, proportion=1, flag=wx.EXPAND | wx.ALL)

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2.Add(self.log, proportion=1, flag=wx.EXPAND)
        sizer.Add(hbox2, proportion=0, flag=wx.EXPAND | wx.ALL)        
        sizer.Add(self.gauge, proportion=0, flag=wx.EXPAND)

        self.log.Show(False)
        self.gauge.Show(False)
        self.SetSizer(sizer)

        self.mystatusbar.SetFieldsCount(3)
        self.mystatusbar.SetStatusWidths([-5, -1, -1])

        if HAS_LICENCE:
            self.license = License.load("license.lic")            
            self.mystatusbar.SetStatusText( str(self.license), 0)

        self.Show(True)

    def OnQuit(self,e):
        self.Close(True)

    def OnNew(self, e):
        newframe = MainFrame(None, -1, "Make PDF", size=(600, 500))
        newframe.Show(1)
        
    def OnOpen(self, event):
        curdir = os.getcwd()        
        file_name = os.path.basename(self.last_name_saved)
        if self.modify:
            dlg = wx.MessageDialog(self, 'Save changes?', '', wx.YES_NO | wx.YES_DEFAULT |
	 wx.CANCEL | wx.ICON_QUESTION)
            val = dlg.ShowModal()
            if val == wx.ID_YES:
                self.OnSaveFile(event)
                self.DoOpenFile()
            elif val == wx.ID_CANCEL:
                dlg.Destroy()
            else:
                self.DoOpenFile()
        else:
            self.DoOpenFile()
        os.chdir(curdir)

    def DoOpenFile(self):
        wcd='Project files (*.prj)|*.prj|All files(*)|*'
        open_dlg = wx.FileDialog(self, message='Choose a file', defaultDir=os.getcwd(), defaultFile='', 
			wildcard=wcd, style=wx.OPEN|wx.CHANGE_DIR)
        if open_dlg.ShowModal() == wx.ID_OK:
            path = open_dlg.GetPath()

            try:
                f = open(path, "r")
                test = pickle.load(f)
                f.close()
                tree = self.pnl.tree
                tree.DeleteAllItems()
                root = self.pnl.AddRoot(test[0]['label'])
                tree.InsertItemsFromList(test[0]['children'], root, appendafter=True)
                tree.Expand(root)
                
                self.last_name_saved = path
                self.mystatusbar.SetStatusText('', 1)
                self.modify = False

            except IOError, error:
                dlg = wx.MessageDialog(self, 'Error opening file\n' + str(error))
                dlg.ShowModal()

            except UnicodeDecodeError, error:
                dlg = wx.MessageDialog(self, 'Error opening file\n' + str(error))
                dlg.ShowModal()
        open_dlg.Destroy()

    def OnSave(self, event):
        if self.last_name_saved:

            try:                
                test = self.pnl.tree.SaveItemsToList(self.pnl.GetRootItem())
                f = open(self.last_name_saved, "w")
                pickle.dump(test, f)
                f.close()            
                self.mystatusbar.SetStatusText(os.path.basename(self.last_name_saved) + ' saved', 0)
                self.modify = False
                self.mystatusbar.SetStatusText('', 1)

            except IOError, error:
                dlg = wx.MessageDialog(self, 'Error saving file\n' + str(error))
                dlg.ShowModal()
        else:
            self.OnSaveAs(event)

    def OnSaveAs(self, event):
        wcd='Project files (*.prj)|*.prj|All files(*)|*'
        curdir = os.getcwd()        
        save_dlg = wx.FileDialog(self, message='Save file as...', defaultDir=curdir, defaultFile='', 
			wildcard=wcd, style=wx.SAVE | wx.OVERWRITE_PROMPT)
        if save_dlg.ShowModal() == wx.ID_OK:
            path = save_dlg.GetPath()

            try:
                test = self.pnl.tree.SaveItemsToList(self.pnl.GetRootItem())
                f = open(path, 'w')
                pickle.dump(test, f)
                f.close()            
                self.last_name_saved = os.path.basename(path)
                self.mystatusbar.SetStatusText(self.last_name_saved + ' saved', 0)
                self.modify = False
                self.mystatusbar.SetStatusText('', 1)

            except IOError, error:
                dlg = wx.MessageDialog(self, 'Error saving file\n' + str(error))
                dlg.ShowModal()
        save_dlg.Destroy()
        os.chdir(curdir)        

    def OnAddFolder(self, event):
        dlg = wx.DirDialog(self)
        try:
            if dlg.ShowModal() == wx.ID_OK:                
                tree = self.pnl.tree
#                tree.DeleteAllItems()                
                path = dlg.GetPath()
                tree.InsertItemsFromPath(path)                
        finally:
            dlg.Destroy()

    def makepdf(self, children):
        for item in children:
            if item['data']['type'] == 'item':
                filename = item['data']['name']
                ext = os.path.splitext(filename)[1].lower()
                ofile_base = randStr(6)
                ofile = os.path.join(config.build_path, ofile_base+".pdf")
                
                if ext in ['.doc', '.docx', '.htm', '.html'] and not os.path.basename(filename).startswith("~$"):
                    self.log.AddText("Converting %s...\n" % filename)
                    temp_doc = os.path.join(config.build_path, ofile_base+ext)
                    copy (filename, temp_doc)
                    if doc2pdf(temp_doc):
                        item['data']['pdf'] = "%s.pdf" % ofile_base

                elif ext in ['.pdf']:
                    self.log.AddText("Copying %s...\n" % filename)
                    copy (filename, ofile)
                    item['data']['pdf'] = "%s.pdf" % ofile_base

                elif ext in ['.gif', '.jpg', '.png', '.tif']:
                    self.log.AddText("Converting %s...\n" % filename)
                    temp_img = os.path.join(config.build_path, ofile_base+ext)
                    copy (filename, temp_img)
                    if img2pdf(temp_img):
                        item['data']['pdf'] = "%s.pdf" % ofile_base
                else:
                    item['data']['pdf'] = ""
                    
            if item.has_key('children'):
                self.makepdf(item['children'])

    def DoMakePDF(self):
        
        assert(os.path.exists(config.stub_path))
        assert(os.path.exists(config.pdflatex))
        assert(os.path.exists(config.makeindex))

        wx.CallAfter(self.gauge.SetValue, 0)
        self.log.ClearAll()
        
        try:
            rmtree(config.build_path, True)
        except e:
            print e
            pass
        
        copytree(config.stub_path, config.build_path)
        wx.CallAfter(self.gauge.SetValue, 5)
        
        self.log.AddText("Copying files...\n")
        test = self.pnl.tree.SaveItemsToList(self.pnl.GetRootItem())        
        self.makepdf(test[0]['children'])

        import pyratemp
        t = pyratemp.Template(filename=os.path.join(config.build_path, "export.tmpl"), encoding="utf-8", escape=pyratemp.LATEX)
        result = t(items=test)

        os.chdir(config.build_path)
        
        self.log.AddText("Making LaTex source...\n")
        import codecs
        texfile = 'export.tex' #os.path.join(config.build_path, 'export.tex')
        idxfile = 'export.idx' #os.path.join(config.build_path, 'export.idx')
        
        codecs.open(os.path.join(config.build_path, 'export.tex'), 'w', encoding='utf-8').write(result)
      
        def output(v):
            # -- In this program we don't really need to see this
            #    as the output is incorrectly going to errors first
            print v
            self.log.EnsureCaretVisible()
            wx.Yield()
            return

        def errors(v):
            print 'ERRORS:', v
      
        def step1():
            wx.CallAfter(self.gauge.SetValue, 10)            
            self.log.AddText("Creating PDF (step 1/3)...\n")        
            cmd = " ".join([config.pdflatex,'-interaction=batchmode',texfile])
            p = wxPopen3(cmd, [], output, errors, step2, self)

        def step2():
            self.log.AddText("Making index...\n")
            cmd = " ".join([config.makeindex,idxfile])
            p = wxPopen3(cmd, [], output, errors, step3, self)

        def step3():
            wx.CallAfter(self.gauge.SetValue, 40)                    
            self.log.AddText("Creating PDF (step 2/3)...\n")
            cmd = " ".join([config.pdflatex,'-interaction=batchmode',texfile])
            p = wxPopen3(cmd, [], output, errors, step4, self)

        def step4():
            wx.CallAfter(self.gauge.SetValue, 70)                            
            self.log.AddText("Creating PDF (step 3/3)...\n")        
            cmd = " ".join([config.pdflatex,'-interaction=batchmode',texfile])
            p = wxPopen3(cmd, [], output, errors, step5, self)

        def step5():
            os.chdir(config.current_path)
            wx.CallAfter(self.gauge.SetValue, 100)
            wx.CallAfter(self.OnMakePDFDone)                

        step1()

    def OnGeneratePDF(self,e):
        if not self.pnl.GetRootItem():
            return

        if HAS_LICENCE:
            if not self.license.isvalid() or self.license.count < 0:
                return
                  
        self.log.Clear()        
        self.log.Show(True)
        self.gauge.Show(True)        
        self.GetSizer().Layout()            
##        thread.start_new_thread(self.DoMakePDF, ())
        self.DoMakePDF()
        
    def OnMakePDFDone(self):        
        self.log.Show(False)        
        self.gauge.Show(False)
        self.GetSizer().Layout()
        
        f = open(os.path.join(config.build_path,"export.log"), "r")
        log = f.read()
        f.close()
        a = log.split("Output written on export.pdf (")
        if len(a)>1:
            pages = int(a[1].split(" ")[0])
            print "Output %d pages" % pages
            if HAS_LICENCE:
                self.license.dec(pages)
                self.license.save("license.lic")
                self.mystatusbar.SetStatusText( str(self.license), 0)
        
        os.startfile(os.path.join(config.build_path,"export.pdf"))
        
    def OnViewStatusbar(self, event):
        if self.mystatusbar.IsShown():
            self.mystatusbar.Hide()
        else:
            self.mystatusbar.Show()
        evt = wx.SizeEvent(self.GetSize(), self.GetId())
        evt.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(evt) 

##    def StatusBar(self):
##        self.mystatusbar = self.CreateStatusBar()
##        self.mystatusbar.SetFieldsCount(3)
##        self.mystatusbar.SetStatusWidths([-5, -2, -1])

    def OnAbout(self, event):
        info = wx.AboutDialogInfo()
        info.Name = APP_NAME
        info.Version = "1.0"
        info.Copyright = "Copyright (c) 2011, Gianpaolo Terranova"
        info.Description = "Merge documents to create a single PDF document."
        info.WebSite = ("http://www.terranovanet.it", "Author's website")
        info.Developers = [ "Gianpaolo Terranova" ]
        # Then we call wx.AboutBox giving it that info object
        wx.AboutBox(info)       
        
class MyApp(wx.App):
    def OnInit(self):
        wx.InitAllImageHandlers()
        frame_1 = MainFrame(None, -1, APP_NAME, size=(600, 500))
        self.SetTopWindow(frame_1)
        frame_1.Show(1)
        return 1

# end of class MyApp

def main():
    app = MyApp(0)
    app.MainLoop()
    
if __name__ == "__main__":
    main()
