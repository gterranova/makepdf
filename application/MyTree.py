#!/usr/bin/python
# -*- coding: utf-8 -*-

#used some code from the WxPython wiki:
#-1.4 Recursively building a list into a wxTreeCtrl (yet another sample) by Rob
#-1.5 Simple Drag and Drop by Titus
#-TraversingwxTree

#tested on wxPython 2.5.4 and Python 2.4, under Windows and Linux

import os
import  wx

#---------------------------------------------------------------------------

class MyTreeCtrl(wx.TreeCtrl):
    def __init__(self, parent, id, pos, size, style, log):
        wx.TreeCtrl.__init__(self, parent, id, pos, size, style)

        self.log = log

        self.buffer = None
        
        # some hack-ish code here to deal with imagelists
        self.iconentries = {}
        isize = (16,16)
        il = wx.ImageList(isize[0], isize[1])
        
        self.imagelist = il

        # blank default
        self.iconentries['default'] = il.Add(wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER,isize))        
        self.iconentries['directory'] = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER,  wx.ART_OTHER, isize))
        self.iconentries['directory_open'] = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN,  wx.ART_OTHER, isize))
        self.addIcon(os.path.join("images","pdf.png"), wx.BITMAP_TYPE_PNG, '.pdf')
                
    def Copy(self, source):
        # Save the source
        self.buffer = self.SaveItemsToList(source)        
        pass

    def Cut(self, source):
        # Save + delete the source
        self.buffer = self.SaveItemsToList(source)
        self.Delete(source)

    def Move(self, source, target):
        # Prevent the user from dropping an item inside of itself
        if self.ItemIsChildOf(target, source):
            print "the tree item can not be moved in to itself! "
            self.Unselect()
            return
        
        def deletesource():
            self.Delete(source)
            
        self.Copy(source)
        self.Paste(target, oncompletion=deletesource)       
        
    def Paste(self, target, oncompletion=None):
        if self.buffer == None:
            return # Nothing to paste
        
        # Get the target's parent's ID
        targetparent = self.GetItemParent(target)
        if not targetparent.IsOk():
            targetparent = self.GetRootItem()

        # One of the following methods of inserting will be called...   
        def MoveHere(event):
            newitems = self.InsertItemsFromList(self.buffer, targetparent, target)
            self.buffer = None
            #self.tree.UnselectAll()
            for item in newitems:
                self.SelectItem(item)
            if oncompletion:
                oncompletion()

        def InsertInToThisGroup(event):
            newitems = self.InsertItemsFromList(self.buffer, target)
            self.buffer = None
            #self.tree.UnselectAll()
            for item in newitems:
                self.SelectItem(item)
            if oncompletion:
                oncompletion()

        #---------------------------------------

        if self.GetPyData(target)["type"] == "container": # and self.dragType == "right button":
            menu = wx.Menu()
            menu.Append(101, "Insert after this group", "")
            menu.Append(102, "Insert into this group", "")
            menu.UpdateUI()
            menu.Bind(wx.EVT_MENU, MoveHere, id=101)
            menu.Bind(wx.EVT_MENU, InsertInToThisGroup,id=102)
            self.PopupMenu(menu)
        else:
            if self.IsExpanded(target):
               InsertInToThisGroup(None)
            else:
               MoveHere(None)
    
    def addIcon(self, filepath, wxBitmapType, name):
        """Adds an icon to the imagelist and registers it with the iconentries dict
        using the given name. Use so that you can assign custom icons to the tree
        just by passing in the value stored in self.iconentries[name]
        @param filepath: path to the image
        @param wxBitmapType: wx constant for the file type - eg wx.BITMAP_TYPE_PNG
        @param name: name to use as a key in the self.iconentries dict - get your imagekey by calling
            self.iconentries[name]
        """
        try:
            if os.path.exists(filepath):
                key = self.imagelist.Add(wx.Bitmap(filepath, wxBitmapType))
                self.iconentries[name] = key
        except Exception, e:
            print e

    def getFileExtension(self, filename):
        """Helper function for getting a file's extension"""
        # check if directory
        if not os.path.isdir(filename):
            # search for the last period
            index = filename.rfind('.')
            if index > -1:
                return filename[index:]
            return ''
        else:
            return 'directory'
        
    def processFileExtension(self, filename):
        """Helper function. Called for files and collects all the necessary
        icons into in image list which is re-passed into the tree every time
        (imagelists are a lame way to handle images)"""
        ext = self.getFileExtension(filename)
        ext = ext.lower()

        excluded = ['', '.exe', '.ico']
        # do nothing if no extension found or in excluded list
        if ext not in excluded:

            # only add if we dont already have an entry for this item
            if ext not in self.iconentries.keys():

                # sometimes it just crashes
                try:
                    # use mimemanager to get filetype and icon
                    # lookup extension
                    filetype = wx.TheMimeTypesManager.GetFileTypeFromExtension(ext)

                    if hasattr(filetype, 'GetIconInfo'):
                        info = filetype.GetIconInfo()
                        
                        if info is not None:
                            icon = info[0]
                            if icon.Ok():
                                # add to imagelist and store returned key
                                iconkey = self.imagelist.AddIcon(icon)
                                self.iconentries[ext] = iconkey

                                # update tree with new imagelist - inefficient
                                self.SetImageList(self.imagelist)

                                # return new key
                                return iconkey
                except:
                    return self.iconentries['default']
                        
            # already have icon, return key
            else:
                return self.iconentries[ext]

        # if exe, get first icon out of it
        elif ext == '.exe':
            #TODO: get icon out of exe withOUT using weird winpy BS
            pass
            
        # if ico just use it
        elif ext == '.ico':
            try:
                icon = wx.Icon(filename, wx.BITMAP_TYPE_ICO)
                if icon.IsOk():
                    return self.imagelist.AddIcon(icon)

            except Exception, e:
                print e
                return self.iconentries['default']

        # if no key returned already, return default
        return self.iconentries['default']

    def Traverse(self, func, startNode):
        """Apply 'func' to each node in a branch, beginning with 'startNode'. """
        def TraverseAux(node, depth, func):
            nc = self.GetChildrenCount(node, 0)
            child, cookie = self.GetFirstChild(node)
            # In wxPython 2.5.4, GetFirstChild only takes 1 argument
            for i in xrange(nc):
                func(child, depth)
                TraverseAux(child, depth + 1, func)
                child, cookie = self.GetNextChild(node, cookie)
        func(startNode, 0)
        TraverseAux(startNode, 1, func)

    def ItemIsChildOf(self, item1, item2):
        ''' Tests if item1 is a child of item2, using the Traverse function '''
        self.result = False
        def test_func(node, depth):
            if node == item1:
                self.result = True

        self.Traverse(test_func, item2)
        return self.result

    def SaveItemsToList(self, startnode):
        ''' Generates a python object representation of the tree (or a branch of it),
            composed of a list of dictionaries with the following key/values:
            label:      the text that the tree item had
            data:       the node's data, returned from GetItemPyData(node)
            children:   a list containing the node's children (one of these dictionaries for each)
        '''
        global list
        list = []

        def save_func(node, depth):
            tmplist = list
            for x in range(depth):
                if type(tmplist[-1]) is not dict:
                    tmplist.append({})
                tmplist = tmplist[-1].setdefault('children', [])

            item = {}
            item['label'] = self.GetItemText(node)
            item['data'] = self.GetItemPyData(node)            
##            item['icon-normal'] = self.GetItemImage(node, wx.TreeItemIcon_Normal)
##            item['icon-selected'] = self.GetItemImage(node, wx.TreeItemIcon_Selected)
##            item['icon-expanded'] = self.GetItemImage(node, wx.TreeItemIcon_Expanded)
##            item['icon-selectedexpanded'] = self.GetItemImage(node, wx.TreeItemIcon_SelectedExpanded)

            tmplist.append(item)

        self.Traverse(save_func, startnode)
        return list

    def InsertItemsFromList(self, itemlist, parent, insertafter=None, appendafter=False):
        ''' Takes a list, 'itemslist', generated by SaveItemsToList, and inserts
            it in to the tree. The items are inserted as children of the
            treeitem given by 'parent', and if 'insertafter' is specified, they
            are inserted directly after that treeitem. Otherwise, they are put at
            the begining.
            
            If 'appendafter' is True, each item is appended. Otherwise it is prepended.
            In the case of children, you want to append them to keep them in the same order.
            However, to put an item at the start of a branch that has children, you need to
            use prepend. (This will need modification for multiple inserts. Probably reverse
            the list.)

            Returns a list of the newly inserted treeitems, so they can be
            selected, etc..'''
        newitems = []
        for item in itemlist:
            if insertafter:
                node = self.InsertItem(parent, insertafter, item['label'])
            elif appendafter:
                node = self.AppendItem(parent, item['label'])
            else:
                node = self.PrependItem(parent, item['label'])
            self.SetItemPyData(node, item['data'])
            if item['data']['type'] == 'item':
                imagekey = self.processFileExtension(item['data']['name'])
                self.SetItemImage(node, imagekey, wx.TreeItemIcon_Normal)
                self.SetItemImage(node, imagekey, wx.TreeItemIcon_Selected)
            else:
                self.SetItemImage(node, self.iconentries['directory'], wx.TreeItemIcon_Normal)
                self.SetItemImage(node, self.iconentries['directory_open'], wx.TreeItemIcon_Expanded)
                
            newitems.append(node)
            if 'children' in item:
                self.InsertItemsFromList(item['children'], node, appendafter=True)

        self.SetImageList(self.imagelist)        
        return newitems

    def AddRoot(self, label):
        root = wx.TreeCtrl.AddRoot(self, label)
        self.SetPyData(root, {"type":"container"})
        self.SetItemImage(root, self.iconentries['directory'], wx.TreeItemIcon_Normal)
        self.SetItemImage(root, self.iconentries['directory_open'], wx.TreeItemIcon_Expanded)
        return root

    def InsertItemsFromPath(self, path):
        if self.IsEmpty():
            print "no root... adding"
            parent = self.AddRoot(os.path.basename(path))
        else:
            node = self.GetSelection()
            if node.IsOk():
                print "good selection..."                
                data = self.GetPyData(node)
                if data['type'] == 'item':
                    print "insert after item..."                                                    
                    parent = self.InsertItem(self.GetItemParent(node), node, os.path.basename(path))
                else:
                    print "append to folder..."                                                                        
                    parent = self.AppendItem(node, os.path.basename(path))
            else:
                print "bad selection..."                                
                parent = self.AppendItem(self.GetRootItem(), os.path.basename(path))
            self.SetPyData(parent, {"type":"container", "name": path})
            self.SetItemImage(parent, self.iconentries['directory'], wx.TreeItemIcon_Normal)
            self.SetItemImage(parent, self.iconentries['directory_open'], wx.TreeItemIcon_Expanded)            

        ids = {path : parent}

        for (dirpath, dirnames, filenames) in os.walk(path):
            for dirname in dirnames:
                fullpath = os.path.join(dirpath, dirname)
                ids[fullpath] = self.AppendItem(ids[dirpath], dirname)
                self.SetPyData(ids[fullpath], {"type":"container", "name": fullpath})
                self.SetItemImage(ids[fullpath], self.iconentries['directory'], wx.TreeItemIcon_Normal)
                self.SetItemImage(ids[fullpath], self.iconentries['directory_open'], wx.TreeItemIcon_Expanded)
                
            for filename in sorted(filenames):
                # process the file extension to build image list
                #skip doc temporary files
                if filename.startswith("~$"):
                    continue
                fullpath = os.path.join(dirpath, filename)
                imagekey = self.processFileExtension(fullpath)                        
                item = self.AppendItem(ids[dirpath],  filename)
                self.SetPyData(item, {"type":"item", "name": fullpath})
                self.SetItemImage(item, imagekey, wx.TreeItemIcon_Normal)
                self.SetItemImage(item, imagekey, wx.TreeItemIcon_Selected)

        self.SetImageList(self.imagelist)
        self.EnsureVisible(parent)        
        self.Expand(parent)
        
def OnCompareItems(self, item1, item2):
        t1 = self.GetItemText(item1)
        t2 = self.GetItemText(item2)
        self.log.WriteText('compare: ' + t1 + ' <> ' + t2 + '\n')
        if t1 < t2: return -1
        if t1 == t2: return 0
        return 1


#---------------------------------------------------------------------------

class MyTreeCtrlPanel(wx.Panel):
    def __init__(self, parent, log):
        # Use the WANTS_CHARS style so the panel doesn't eat the Return key.
        wx.Panel.__init__(self, parent, -1, style=wx.WANTS_CHARS)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        self.log = log
        tID = wx.NewId()

        self.tree = MyTreeCtrl(self, tID, wx.DefaultPosition, wx.DefaultSize,
                                    wx.TR_HAS_BUTTONS | wx.TR_EDIT_LABELS, self.log)
        # Example needs some more work to use wx.TR_MULTIPLE

        self.root = None #self.AddRoot("Root")        
#        self.tree.Expand(self.root)
        
        self.tree.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDClick)
        self.tree.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
        self.tree.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)

        # These go at the end of __init__
        self.tree.Bind(wx.EVT_TREE_BEGIN_RDRAG, self.OnBeginRightDrag)
        self.tree.Bind(wx.EVT_TREE_BEGIN_DRAG, self.OnBeginLeftDrag)
        self.tree.Bind(wx.EVT_TREE_END_DRAG, self.OnEndDrag)

    def AddRoot(self, label):
        return self.tree.AddRoot(label)

    def GetRootItem(self):
        if self.tree.IsEmpty():
            return None
        return self.tree.GetRootItem()
        
    def OnBeginLeftDrag(self, event):
        '''Allow drag-and-drop for leaf nodes.'''
        self.log.WriteText("OnBeginDrag")
        event.Allow()
        self.dragType = "left button"
        self.dragItem = event.GetItem()

    def OnBeginRightDrag(self, event):
        '''Allow drag-and-drop for leaf nodes.'''
        self.log.WriteText("OnBeginDrag")
        event.Allow()
        self.dragType = "right button"
        self.dragItem = event.GetItem()

    def OnEndDrag(self, event):
        print "OnEndDrag"

        # If we dropped somewhere that isn't on top of an item, ignore the event
        if event.GetItem().IsOk():
            target = event.GetItem()
        else:
            return

        # Make sure this member exists.
        try:
            source = self.dragItem
        except:
            return

##        # Prevent the user from dropping an item inside of itself
##        if self.tree.ItemIsChildOf(target, source):
##            print "the tree item can not be moved in to itself! "
##            self.tree.Unselect()
##            return
##
##        # Get the target's parent's ID
##        targetparent = self.tree.GetItemParent(target)
##        if not targetparent.IsOk():
##            targetparent = self.tree.GetRootItem()

        self.tree.Move(source, target)
        
##        # One of the following methods of inserting will be called...   
##        def MoveHere(event):
##            # Save + delete the source
##            save = self.tree.SaveItemsToList(source)
##            self.tree.Delete(source)
##            newitems = self.tree.InsertItemsFromList(save, targetparent, target)
##            #self.tree.UnselectAll()
##            for item in newitems:
##                self.tree.SelectItem(item)
##
##        def InsertInToThisGroup(event):
##            # Save + delete the source
##            save = self.tree.SaveItemsToList(source)
##            self.tree.Delete(source)
##            newitems = self.tree.InsertItemsFromList(save, target)
##            #self.tree.UnselectAll()
##            for item in newitems:
##                self.tree.SelectItem(item)
##        #---------------------------------------
##
##        if self.tree.GetPyData(target)["type"] == "container" and self.dragType == "right button":
##            menu = wx.Menu()
##            menu.Append(101, "Move to after this group", "")
##            menu.Append(102, "Insert into this group", "")
##            menu.UpdateUI()
##            menu.Bind(wx.EVT_MENU, MoveHere, id=101)
##            menu.Bind(wx.EVT_MENU, InsertInToThisGroup,id=102)
##            self.PopupMenu(menu)
##        else:
##            if self.tree.IsExpanded(target):
##               InsertInToThisGroup(None)
##            else:
##               MoveHere(None)

    def OnRightUp(self, event):
        pt = event.GetPosition();
        item, flags = self.tree.HitTest(pt)
        self.log.WriteText("OnRightUp: %s (manually starting label edit)\n" % self.tree.GetItemText(item))
        self.tree.EditLabel(item)

    def OnLeftDown(self, event):
        print "control key is", event.m_controlDown

        pt = event.GetPosition();
        item, flags = self.tree.HitTest(pt)
        self.tree.SelectItem(item)
        event.Skip()

    def OnRightDown(self, event):
        print "control key is", event.m_controlDown

        pt = event.GetPosition();
        item, flags = self.tree.HitTest(pt)
        self.tree.SelectItem(item)
        event.Skip()

    def OnLeftDClick(self, event):
        pt = event.GetPosition();
        item, flags = self.tree.HitTest(pt)
        #self.log.WriteText("OnLeftDClick: %s\n" % self.tree.GetItemText(item))

        #expand/collapse toggle
        data = self.tree.GetPyData(item)
        if data["type"] == "item":
            os.startfile(data['name'])
        else:
            self.tree.Toggle(item)
            #print "toggled ", item
        #event.Skip()

    def OnSize(self, event):
        w,h = self.GetClientSizeTuple()
        self.tree.SetDimensions(0, 0, w, h)

