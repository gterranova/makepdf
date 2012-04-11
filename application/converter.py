#!/usr/bin/python
# -*- coding: utf-8 -*-

import win32print
from win32com import client 
import pythoncom
import subprocess, time

from PIL import Image
import PSDraw
import pil2exe

import os
import math
from base64 import b64encode
import config

def randStr(n):
    return b64encode(os.urandom(int(math.ceil(0.75*n))),'Az')[:n]

#tempprinter = "Metafile to EPS Converter"
tempprinter = "MS Publisher Imagesetter"

def word2eps(iname, oname):
    pythoncom.CoInitialize()
    if not check_printer():
        return False
    
    currentprinter = win32print.GetDefaultPrinter()
    win32print.SetDefaultPrinter(tempprinter)
    try:
        word = client.Dispatch("Word.Application")
        try:
            word.Documents.Open(os.path.abspath(iname))
            time.sleep(1)
            word.ActiveDocument.PrintOut(False, False, 0, os.path.abspath(oname))
            time.sleep(1)
            word.ActiveDocument.Close()
        except:
            word.Quit()
            win32print.SetDefaultPrinter(currentprinter)
            return False
        word.Quit()
    except:
        win32print.SetDefaultPrinter(currentprinter)            
        return False
    
    win32print.SetDefaultPrinter(currentprinter)                    
    pythoncom.CoUninitialize()
    return True

def resize(img, box, fit=False, out=''):
    '''Downsample the image.
@param img: Image -  an Image-object
@param box: tuple(x, y) - the bounding box of the result image
@param fix: boolean - crop the image to fill the box
@param out: file-like-object - save the image into the output stream
'''
    #preresize image with factor 2, 4, 8 and fast algorithm
    factor = 1
    while img.size[0]/factor > 2*box[0] and img.size[1]*2/factor > 2*box[1]:
        factor *=2
    if factor > 1:
        img.thumbnail((img.size[0]/factor, img.size[1]/factor), Image.NEAREST)
    #calculate the cropping box and get the cropped part
    if fit:
        x1 = y1 = 0
        x2, y2 = img.size
        wRatio = 1.0 * x2/box[0]
        hRatio = 1.0 * y2/box[1]
        if hRatio > wRatio:
            y1 = y2/2-box[1]*wRatio/2
            y2 = y2/2+box[1]*wRatio/2
        else:
            x1 = x2/2-box[0]*hRatio/2
            x2 = x2/2+box[0]*hRatio/2
        img = img.crop((int(x1),int(y1),int(x2),int(y2)))
    #Resize the image with best quality algorithm ANTI-ALIAS
    img.thumbnail(box, Image.ANTIALIAS)

    #save it into a file-like object
    if not out == '':
        img.save(out, "JPEG", quality=75)
        
    return img
    
def _img2pdf(iname, oname):

    import win32ui
    currentprinter = win32print.GetDefaultPrinter()
    win32print.SetDefaultPrinter(tempprinter)

    #
    # Constants for GetDeviceCaps
    #
    #
    # HORZRES / VERTRES = printable area
    #
    HORZRES = 8
    VERTRES = 10
    #
    # LOGPIXELS = dots per inch
    #
    LOGPIXELSX = 88
    LOGPIXELSY = 90
    #
    # PHYSICALWIDTH/HEIGHT = total area
    #
    PHYSICALWIDTH = 110
    PHYSICALHEIGHT = 111
    #
    # PHYSICALOFFSETX/Y = left / top margin
    #
    PHYSICALOFFSETX = 112
    PHYSICALOFFSETY = 113

    printer_name = win32print.GetDefaultPrinter ()

    #
    # You can only write a Device-independent bitmap
    #  directly to a Windows device context; therefore
    #  we need (for ease) to use the Python Imaging
    #  Library to manipulate the image.
    #
    # Create a device context from a named printer
    #  and assess the printable size of the paper.
    #
    hDC = win32ui.CreateDC ()
    hDC.CreatePrinterDC (printer_name)
    printable_area = hDC.GetDeviceCaps (HORZRES), hDC.GetDeviceCaps (VERTRES)
    printer_size = hDC.GetDeviceCaps (PHYSICALWIDTH), hDC.GetDeviceCaps (PHYSICALHEIGHT)
    #printer_margins = hDC.GetDeviceCaps (PHYSICALOFFSETX), hDC.GetDeviceCaps (PHYSICALOFFSETY)
    printer_margins = (400,400)
    hDC.DeleteDC ()
    win32print.SetDefaultPrinter(currentprinter)
    
    #
    # Open the image, rotate it if it's wider than
    #  it is high, and work out how much to multiply
    #  each pixel by to get it as big as possible on
    #  the page without distorting.
    #
    im = Image.new("RGB", printer_size, (255,255,255))
    bmp = Image.open (iname, 'r')
    bmp.load()

    if bmp.mode != "RGB":
        bmp = bmp.convert("RGB")
    
    if bmp.size[0] > bmp.size[1]:
      bmp = bmp.rotate (90)

    ratios = [1.0 * (printable_area[0]-printer_margins[0]) / bmp.size[0], 1.0 * (printable_area[1]-printer_margins[1]) / bmp.size[1]]
    scale = min (ratios)

    #
    # Start the print job, and draw the bitmap to
    #  the printer device at the scaled size.
    #
    scaled_width, scaled_height = [int (scale * i) for i in bmp.size]
    bmp = resize(bmp, (scaled_width, scaled_height) )
    bmp = bmp.resize((scaled_width, scaled_height))

    scaled_width, scaled_height = bmp.size
    
    x1 = int ((printer_margins[0] + (printable_area[0]-printer_margins[0]) - scaled_width) / 2)
    y1 = int ((printer_margins[1] + (printable_area[1]-printer_margins[1]) - scaled_height) / 2)
    x2 = x1 + scaled_width
    y2 = y1 + scaled_height
            
    im.paste(bmp.copy(), (x1, y1, x2, y2))
    
    im.save(oname, "PDF")
    return True

def eps2pdf(iname, oname):

    try:
        assert (os.path.exists(config.epstopdf))
        proc = subprocess.call([config.epstopdf, iname], shell=True) #, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except:
        return False
    return True

def doc2pdf(ifile, ofile=None):
    ext = os.path.splitext(ifile)[1]
    ofile = ofile or "%s.pdf" % ifile[:-len(ext)]
    epsfile = "%s.eps" % ofile[:-4]
    try:    
        if word2eps(ifile,epsfile):
            if not eps2pdf(epsfile, ofile):
                return False
    except:
        print "Conversion of %s failed" % ifile
        return False            
    return True

def img2pdf(ifile, ofile=None):
    ext = os.path.splitext(ifile)[1]
    ofile = ofile or "%s.pdf" % ifile[:-len(ext)]
    try:
        if not _img2pdf(ifile, ofile):
            return False
    except:
        print "Conversion of %s failed" % ifile
        return False
    return True

    
def check_printer():
    myprinter = None
    A = win32print.EnumPrinters (win32print.PRINTER_ENUM_NAME, None, 2)
    for i in range (len (A)):
        if A[i]['pPrinterName'] == tempprinter:
            return True
    return False

    
