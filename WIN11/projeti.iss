[Setup]
; 1. TÄRKEIN PÄIVITYSTEN KANNALTA: AppId. 
AppId={{B5A8F9D2-1234-5678-90AB-CDEF12345678}

AppName=Kuvakartta Pro Windows
AppVersion=3.0
AppPublisher=Matti Räsänen

DefaultDirName={autopf}\Kuvakartta
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

[Dirs]
; Annetaan oikeudet välimuistikansiolle sen oikeassa sijainnissa
Name: "{app}\_internal\static\cache"; Permissions: users-modify
; Annetaan oikeudet asennuskansiolle (jotta .txt tiedostot voidaan tallentaa)
Name: "{app}"; Permissions: users-modify
[Files]
Source: "dist\app\app.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\app\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "*.json"

[Icons]
; TÄMÄ OTSIKKO PUUTTUI. Nämä luovat pikakuvakkeet käynnistysvalikkoon ja työpöydälle.
Name: "{group}\Kuvakartta Pro"; Filename: "{app}\app.exe"
Name: "{autodesktop}\Kuvakartta Pro"; Filename: "{app}\app.exe"; Tasks: desktopicon

[Run]
; Käynnistysvalinta asennuksen lopuksi
Filename: "{app}\app.exe"; Description: "{cm:LaunchProgram,Kuvakartta Pro}"; Flags: nowait postinstall skipifsilent
[UninstallDelete]
; POISTON AIKANA: Tuhoaa välimuistin ja vanhat kansionpolut,
; mutta JÄTTÄÄ mml_key.txt -tiedoston (API-avaimen) rauhaan päivityksiä varten.
Type: filesandordirs; Name: "{app}\_internal\static\cache"
Type: files; Name: "{app}\polut.json"

[UninstallDelete]
; Siivoaa tyhjät kansiot pois (jättää juurikansion, jos mml_key.txt on siellä)
Type: dirifempty; Name: "{app}\_internal\static"
Type: dirifempty; Name: "{app}\_internal"
Type: dirifempty; Name: "{app}"