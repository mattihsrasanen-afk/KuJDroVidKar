[Setup]
; 1. TÄRKEIN PÄIVITYSTEN KANNALTA: AppId. 
; ÄLÄ KOSKAAN muuta tätä koodia tulevissa versioissa, jotta asennusohjelma tunnistaa vanhan version!
AppId={{B5A8F9D2-1234-5678-90AB-CDEF12345678}

AppName=Kuvat ja Videot Kartalla
; 2. Muista kasvattaa tätä numeroa aina kun teet uuden päivityksen (esim. 2.1, 2.2...)
AppVersion=2.0

DefaultDirName={autopf}\Kuvakartta
DefaultGroupName=Mediakirjasto
OutputDir=Output
; Vinkki: Voit laittaa versionumeron myös asennustiedoston nimeen
OutputBaseFilename=Kuvakartta_v2.0

; 3. NÄMÄ TEKEVÄT PÄIVITYKSESTÄ SUJUVAN:
; Piilottaa kansion valinnan, jos ohjelma on jo asennettu
DisableDirPage=auto
DisableProgramGroupPage=auto
; Käskee Windowsia sulkemaan ohjelman automaattisesti, jos käyttäjä yrittää päivittää sen sen ollessa auki
CloseApplications=yes

Compression=lzma
SolidCompression=yes
PrivilegesRequired=lowest

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; 1. Kopioidaan PyInstallerin tekemä exe
Source: "dist\app\app.exe"; DestDir: "{app}"; Flags: ignoreversion

; 2. Kopioidaan kaikki muut PyInstallerin tekemät tiedostot ja apukansiot
Source: "dist\app\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; 3. Pakotetaan templates-kansio mukaan asennukseen
Source: "templates\*"; DestDir: "{app}\templates"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Kuvat ja Videot Kartalla"; Filename: "{app}\app.exe"
Name: "{autodesktop}\Kuvat ja Videot Kartalla"; Filename: "{app}\app.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\app.exe"; Description: "Käynnistä Kuvat ja Videot Kartalla"; Flags: nowait postinstall skipifsilent