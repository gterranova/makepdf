@rd Output /q /s
setup.py py2exe
"c:\Programmi\Inno Setup 5\iscc.exe" makepdf.iss
pause
@rd build /q /s
@rd dist /q /s
