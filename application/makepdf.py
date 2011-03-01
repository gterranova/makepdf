#!/usr/bin/python
# -*- coding: utf-8 -*-

#used some code from the WxPython wiki:
#-1.4 Recursively building a list into a wxTreeCtrl (yet another sample) by Rob
#-1.5 Simple Drag and Drop by Titus
#-TraversingwxTree

#tested on wxPython 2.5.4 and Python 2.4, under Windows and Linux

import os
import  wx
import thread

import cPickle as pickle

from shutil import copy, copytree, rmtree
from converter import doc2pdf, img2pdf, randStr

from license import License
from MyFrame import MyFrame
from MyTree import MyTreeCtrlPanel

APP_NAME = "PDF Assistant"

class MyLog:
    def __init__(self):
        pass
    def WriteText(self, text):
        print text

class MainFrame(MyFrame):
    def __init__(self, *args, **kwds):
        MyFrame.__init__(self, *args, **kwds)
        log = MyLog()

        # variables
        self.modify = False
        self.last_name_saved = ''
        self.replace = False


##        self.SetIcon(wx.Icon("makepdf.ico", wx.BITMAP_TYPE_ICO))
##        
##        file = wx.Menu()
##        new = wx.MenuItem(file, ID_NEW, '&New\tCtrl+N', 'Creates a new document')
###        new.SetBitmap(wx.Bitmap('icons/stock_new-16.png'))
##        file.AppendItem(new)
##
##        open = wx.MenuItem(file, ID_OPEN, '&Open\tCtrl+O', 'Open an existing file')
###        open.SetBitmap(wx.Bitmap('icons/stock_open-16.png'))
##        file.AppendItem(open)
##        file.AppendSeparator()
##
##        save = wx.MenuItem(file, ID_SAVE, '&Save\tCtrl+S', 'Save the file')
###        save.SetBitmap(wx.Bitmap('icons/stock_save-16.png'))
##        file.AppendItem(save)
##
##        saveas = wx.MenuItem(file, ID_SAVE_AS, 'Save &As...\tShift+Ctrl+S', 
##		'Save the file with a different name')
###        saveas.SetBitmap(wx.Bitmap('icons/stock_save_as-16.png'))
##        file.AppendItem(saveas)
##        file.AppendSeparator()
##
##        quit = wx.MenuItem(file, ID_QUIT, '&Quit\tCtrl+Q', 'Quit the Application')
###        quit.SetBitmap(wx.Bitmap('icons/stock_exit-16.png'))
##        file.AppendItem(quit)
##
##        edit = wx.Menu()
##
##        view = wx.Menu()
##        view.Append(ID_STATUS_TOGGLE, '&Statusbar', 'Show StatusBar')
##
##        make = wx.Menu()
##        make.Append(ID_MAKE_PDF, '&Make PDF...', 'Make PDF')
##
##        help = wx.Menu()
##        about = wx.MenuItem(help, ID_ABOUT, '&About\tF1', 'About Editor')
###        about.SetBitmap(wx.Bitmap('icons/stock_about-16.png'))
##        help.AppendItem(about)
##
##        menubar = wx.MenuBar()
##        menubar.Append(file,"&File")
##        menubar.Append(edit, "&Edit")
##        menubar.Append(view, '&View')
##        menubar.Append(make, '&Make')        
##        menubar.Append(help, '&Help')
##        self.SetMenuBar(menubar)
##
##        self.Bind(wx.EVT_MENU, self.OnSelectFolder, id=ID_NEW)
##        self.Bind(wx.EVT_MENU, self.OnOpenFile, id=ID_OPEN)
##        self.Bind(wx.EVT_MENU, self.OnSaveFile, id=ID_SAVE)
##        self.Bind(wx.EVT_MENU, self.OnSaveAsFile, id=ID_SAVE_AS)                        
##        self.Bind(wx.EVT_MENU, self.OnExit, id=ID_QUIT)
##        self.Bind(wx.EVT_MENU, self.OnMakePDF, id=ID_MAKE_PDF)
##        self.Bind(wx.EVT_MENU, self.ToggleStatusBar, id=ID_STATUS_TOGGLE)
##        self.Bind(wx.EVT_MENU, self.OnAbout, id=ID_ABOUT)
##        
##
##        tb = self.CreateToolBar( wx.TB_HORIZONTAL | wx.NO_BORDER | 
##		wx.TB_FLAT | wx.TB_TEXT)
##        isize = (32,32)
###        tb.AddSimpleTool(wx.NewId(), wx.Bitmap(os.path.join("images","projectnew32.png"), wx.BITMAP_TYPE_PNG), 'New Project')
##        tb.AddSimpleTool(ID_NEW, wx.Bitmap(os.path.join("images","importfolder32.png"), wx.BITMAP_TYPE_PNG), 'Import folder')
##        tb.AddSimpleTool(ID_OPEN, wx.Bitmap(os.path.join("images","fileopen32.png"), wx.BITMAP_TYPE_PNG), 'Open')
##        tb.AddSimpleTool(ID_SAVE, wx.Bitmap(os.path.join("images","filesave32.png"), wx.BITMAP_TYPE_PNG), 'Save')
##        tb.AddSimpleTool(ID_SAVE_AS, wx.Bitmap(os.path.join("images","filesaveas32.png"), wx.BITMAP_TYPE_PNG), 'Save as...')                
###        tb.AddSeparator()
###        tb.AddSimpleTool(ID_ADD_FILE, wx.Bitmap(os.path.join("images","filenew32.png"), wx.BITMAP_TYPE_PNG), 'Add file')
###        tb.AddSimpleTool(ID_ADD_FOLDER, wx.Bitmap(os.path.join("images","foldernew32.png"), wx.BITMAP_TYPE_PNG), 'Add folder')        
##        tb.AddSeparator()
##        tb.AddSimpleTool(ID_MAKE_PDF, wx.Bitmap(os.path.join("images","pdf32.png"), wx.BITMAP_TYPE_PNG), 'Make PDF')
##        tb.AddSeparator()
##        tb.AddSimpleTool(ID_ABOUT, wx.Bitmap(os.path.join("images","info32.png"), wx.BITMAP_TYPE_PNG), 'Help')
##        tb.Realize()
##
##        self.StatusBar()
##        self.Centre()

        self.pnl = MyTreeCtrlPanel(self, log)
        self.gauge = wx.Gauge(self)
        self.log = wx.TextCtrl(self, -1, size=(500,100),
                               style = wx.TE_MULTILINE|wx.TE_READONLY|
                               wx.HSCROLL)
        
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

        self.license = License.load("license.lic")
        self.mystatusbar.SetFieldsCount(3)
        self.mystatusbar.SetStatusWidths([-5, -1, -1])
        
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
                ofile = "build/%s.pdf" % (ofile_base)
                
                if ext in ['.doc', '.docx'] and not os.path.basename(filename).startswith("~$"):
                    self.log.WriteText("Converting %s...\n" % filename)
                    temp_doc = "build/%s%s" % (ofile_base, ext)
                    copy (filename, temp_doc)
                    if doc2pdf(temp_doc):
                        item['data']['pdf'] = "%s.pdf" % ofile_base

                elif ext in ['.pdf']:
                    self.log.WriteText("Copying %s...\n" % filename)
                    copy (filename, ofile)
                    item['data']['pdf'] = "%s.pdf" % ofile_base

                elif ext in ['.gif', '.jpg', '.png', '.tif']:
                    self.log.WriteText("Converting %s...\n" % filename)
                    temp_img = "build/%s%s" % (ofile_base, ext)
                    copy (filename, temp_img)
                    if img2pdf(temp_img):
                        item['data']['pdf'] = "%s.pdf" % ofile_base
                else:
                    item['data']['pdf'] = ""
                    
            if item.has_key('children'):
                self.makepdf(item['children'])

    def DoMakePDF(self):
        current_path = os.getcwd()
        build_path = os.path.abspath(os.path.join(os.getcwd(),"build"))
        stub_path =  os.path.abspath(os.path.join(os.getcwd(),"stub"))

        pdflatex = os.path.join(os.path.join(os.getcwd(),"miktex-portable","miktex","bin", "pdflatex.exe"))
        makeindex = os.path.join(os.path.join(os.getcwd(),"miktex-portable","miktex","bin", "makeindex.exe"))

        assert(os.path.exists(stub_path))
        assert(os.path.exists(pdflatex))
        assert(os.path.exists(makeindex))

        try:
            rmtree(build_path, True)
        except:
            pass
        
        copytree(stub_path, build_path)
        wx.CallAfter(self.gauge.SetValue, 5)
        
        self.log.WriteText("Copying files...\n")
        test = self.pnl.tree.SaveItemsToList(self.pnl.GetRootItem())        
        self.makepdf(test[0]['children'])

        import pyratemp
        t = pyratemp.Template(filename=os.path.join(build_path, "export.tmpl"), encoding="utf-8", escape=pyratemp.LATEX)
        result = t(items=test)

        os.chdir(build_path)
        
        self.log.WriteText("Making LaTex source...\n")
        import codecs
        codecs.open('export.tex', 'w', encoding='utf-8').write(result)
        wx.CallAfter(self.gauge.SetValue, 10)
        
        import subprocess, sys

        def myexec(cmd):            
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            while True:
                out = proc.stdout.read(1)
                if out == '' and proc.poll() != None:
                    break
                if out != '':
                    self.log.WriteText(out)
                    while proc.poll() == None:
                        self.log.WriteText(proc.stdout.readline())
                (out, err) = proc.communicate()
                self.log.WriteText(out)
                self.log.WriteText(err)

        self.log.WriteText("Creating PDF (step 1/3)...\n")
        
        self.log.WriteText("Executing %s...\n" % pdflatex)
        myexec([pdflatex,'-interaction=nonstopmode','export.tex'])        
#        myexec([pdflatex,'-interaction=batchmode','export.tex'])
        self.log.WriteText("Making index...\n")
        myexec([makeindex,'export.idx'])
        wx.CallAfter(self.gauge.SetValue, 40)        

        self.log.WriteText("Creating PDF (step 2/3)...\n")
        myexec([pdflatex,'-interaction=nonstopmode','export.tex'])        
#        myexec([pdflatex,'-interaction=batchmode','export.tex'])
        wx.CallAfter(self.gauge.SetValue, 70)                

        myexec([pdflatex,'-interaction=nonstopmode','export.tex'])        
#        myexec([pdflatex,'-interaction=batchmode','export.tex'])
        os.chdir(current_path)
        wx.CallAfter(self.gauge.SetValue, 100)
        wx.CallAfter(self.OnMakePDFDone)                

    def OnGeneratePDF(self,e):
        if not self.pnl.GetRootItem():
            return

        if not self.license.isvalid() or self.license.count < 0:
            return
                  
        self.log.Clear()        
        self.log.Show(True)
        self.gauge.Show(True)        
        self.GetSizer().Layout()            
        thread.start_new_thread(self.DoMakePDF, ())
        
    def OnMakePDFDone(self):        
        self.log.Show(False)        
        self.gauge.Show(False)
        self.GetSizer().Layout()

        f = open(os.path.join("build","export.log"), "r")
        log = f.read()
        f.close()
        a = log.split("Output written on export.pdf (")
        if len(a)>1:
            pages = int(a[1].split(" ")[0])
            print "Output %d pages" % pages
            self.license.dec(pages)
            self.license.save("license.lic")
            self.mystatusbar.SetStatusText( str(self.license), 0)
        
        os.startfile(os.path.join("build","export.pdf"))
        
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
