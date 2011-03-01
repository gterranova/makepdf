'''Fix allowing PIL to work under py2exe'''

__author__ = "Miki Tebeka <>"
# $Id: pil2exe.py,v 1.2 2003/10/20 11:35:38 mikit Exp $

#FIXME:
# Hand pick only the modules you need (currently all *Plugin.py from PIL
# directory are imported)

#FIXME: Find who's the criminal and why, currently disable warnings
import warnings
warnings.filterwarnings("ignore")

from PIL import Image

from PIL import BmpImagePlugin, GifImagePlugin, JpegImagePlugin, PdfImagePlugin, PngImagePlugin, TiffImagePlugin

#import ArgImagePlugin
#import BmpImagePlugin
#import CurImagePlugin
#import DcxImagePlugin
#import EpsImagePlugin
#import FliImagePlugin
#import FpxImagePlugin
#import GbrImagePlugin
#import GifImagePlugin
#import IcoImagePlugin
#import ImImagePlugin
#import ImtImagePlugin
#import IptcImagePlugin
#import JpegImagePlugin
#import McIdasImagePlugin
#import MicImagePlugin
#import MpegImagePlugin
#import MspImagePlugin
#import PalmImagePlugin
#import PcdImagePlugin
#import PcxImagePlugin
#import PdfImagePlugin
#import PixarImagePlugin
#import PngImagePlugin
#import PpmImagePlugin
#import PsdImagePlugin
#import SgiImagePlugin
#import SunImagePlugin
#import TgaImagePlugin
#import TiffImagePlugin
#import WmfImagePlugin
#import XVThumbImagePlugin
#import XbmImagePlugin
#import XpmImagePlugin

Image._initialized=2
