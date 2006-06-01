[Setup]
AppName=The Musical Cow
AppVerName=The Musical Cow 0.2 (29 May 2006)
DefaultDirName={pf}\The Musical Cow
DefaultGroupName=The Musical Cow
UninstallDisplayIcon={app}\.exe
Compression=lzma/max
SolidCompression=yes

[Languages]
Name: "en"; MessagesFile: "compiler:Default.isl"; LicenseFile: "COPYING"
Name: "fr"; MessagesFile: "compiler:Languages/French.isl"; LicenseFile: "COPYING"
Name: "nl"; MessagesFile: "compiler:Languages/Dutch.isl"; LicenseFile: "COPYING"

[Components]
Name: "main"; Description: "Main Files"; Types: full compact custom; Flags: fixed

[Tasks]
Name: "quicklaunchicon"; Description: "Créer une icône de lancement rapide"; Flags: checkedonce; GroupDescription: "Icônes additionelles:";  Components: main
Name: "desktopicon"; Description: "Créer une icône sur le bureau"; Flags: checkedonce; GroupDescription: "Icônes additionelles:";  Components: main

[Files]
Source: "lyricscow.exe"; DestDir: "{app}"
Source: "*"; Excludes: "*.~*,\Temp\*,error.log,setup.iss"; Flags: recursesubdirs; DestDir: "{app}"
; Source: "Readme.txt"; DestDir: "{app}"; Flags: isreadme

[Icons]
Name: "{group}\The Musical Cow"; Filename: "{app}\lyricscow.exe"; WorkingDir: "{app}"; Comment: "A simple lyrics viewer with a library lyrics tagger"
Name: "{group}\Uninstall The Musical Cow"; Filename: "{uninstallexe}"
