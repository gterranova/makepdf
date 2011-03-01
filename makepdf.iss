; -- Example1.iss --
; Demonstrates copying 3 files and creating an icon.

; SEE THE DOCUMENTATION FOR DETAILS ON CREATING .ISS SCRIPT FILES!

[Setup]
AppName=MakePDF
AppVerName=MakePDF 1.0 (beta)
DefaultDirName={pf}\MakePDF
DefaultGroupName=MakePDF
UninstallDisplayIcon={app}\makepdf.ico
Compression=lzma
SolidCompression=yes
;OutputDir=userdocs:Inno Setup Examples Output

[Dirs]
Name: "{app}/build"

[Files]
Source: "dist/*"; DestDir: "{app}"
Source: "images/*"; DestDir: "{app}/images"
Source: "stub/*"; DestDir: "{app}/stub"
Source: "miktex-portable/*"; DestDir: "{app}/miktex-portable"; Excludes: "doc,source"; Flags: recursesubdirs
Source: "makepdf.ico"; DestDir: "{app}"

[Icons]
Name: "{group}\MakePDF"; Filename: "{app}\makepdf.exe"; IconFilename: "{app}\makepdf.ico"; WorkingDir: "{app}"
Name: "{group}\Uninstall MakePDF"; Filename: "{uninstallexe}"

[UninstallDelete]
Type: files; Name: "{app}/build/*"

