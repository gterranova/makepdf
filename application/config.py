#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

## current_path = os.getcwd()
current_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
build_path = os.path.join(current_path,"build")
stub_path =  os.path.join(current_path,"stub")

pdflatex = os.path.join(current_path,"miktex-portable","miktex","bin", "pdflatex.exe")
makeindex = os.path.join(current_path,"miktex-portable","miktex","bin", "makeindex.exe")
epstopdf = os.path.join(current_path,"miktex-portable","miktex","bin", "epstopdf.exe")

