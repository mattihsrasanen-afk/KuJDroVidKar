[Setup]
; 1. TÄRKEIN PÄIVITYSTEN KANNALTA: AppId. 
; ÄLÄ KOSKAAN muuta tätä koodia tulevissa versioissa, jotta asennusohjelma tunnistaa vanhan version!
AppId={{B5A8F9D2-1234-5678-90AB-CDEF12345678}

AppName=Kuvat ja videot karttalla By Matti Räsänen - Windows 11
; Nostettu versionumero
AppVersion=3.0
AppPublisher=Matti Räsänen

DefaultDirName={localappdata}\Kuvakartta
DefaultGroupName=Mediakirjasto
OutputDir=Output
OutputBaseFilename=Kuvakartta_v3.0
UninstallDisplayIcon={app}\app.exe

; NÄMÄ TEKEVÄT PÄIVITYKSESTÄ SUJUVAN:
DisableDirPage=auto
DisableProgramGroupPage=auto
CloseApplications=yes

Compression=lzma
SolidCompression=yes
PrivilegesRequired=lowest

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\app\app.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\app\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Kuvakartta"; Filename: "{app}\app.exe"
Name: "{autodesktop}\Kuvakartta"; Filename: "{app}\app.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\app.exe"; Description: "{cm:LaunchProgram,Kuvakartta Pro}"; Flags: nowait postinstall skipifsilent