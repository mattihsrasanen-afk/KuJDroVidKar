[Setup]
AppName=Kuvakartta
AppVersion=1.0
DefaultDirName={autopf}\Kuvakartta
DefaultGroupName=Kuvakartta
UninstallDisplayIcon={app}\app.exe
Compression=lzma
SolidCompression=yes
OutputDir=C:\Users\vboxuser\Desktop\WIN11\Output
OutputBaseFilename=Kuvakartta_Setup

[Files]
Source: "C:\Users\vboxuser\Desktop\WIN11\dist\app.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\vboxuser\Desktop\WIN11\ffmpeg-2026-03-22-git-9c63742425-full_build\*"; DestDir: "{app}\ffmpeg-2026-03-22-git-9c63742425-full_build"; Flags: ignoreversion recursesubdirs createallsubdirs
; Huom: Asennetaan avain suoraan AppDataan
Source: "C:\Users\vboxuser\Desktop\WIN11\mml_key.txt"; DestDir: "{localappdata}\Kuvakartta"; Flags: ignoreversion

[Icons]
Name: "{group}\Kuvakartta"; Filename: "{app}\app.exe"
Name: "{commondesktop}\Kuvakartta"; Filename: "{app}\app.exe"

[UninstallDelete]
; Tämä varmistaa, että tyhjät kansiot poistetaan AppDatasta
Type: filesandordirs; Name: "{localappdata}\Kuvakartta"

[Code]
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  // Kun poisto on valmistunut
  if CurUninstallStep = usPostUninstall then
  begin
    if MsgBox('Haluatko poistaa myös välimuistin ja tallennetut asetukset (API-avain ja kansiot)?', 
              mbConfirmation, MB_YESNO) = IDYES then
    begin
      // DelTree poistaa kansion, vaikka se ei olisi tyhjä
      DelTree(ExpandConstant('{localappdata}\Kuvakartta'), True, True, True);
    end;
  end;
end;

[Run]
Filename: "{app}\app.exe"; Description: "Käynnistä Kuvakartta"; Flags: nowait postinstall skipifsilent