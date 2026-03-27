@echo off
setlocal
title Kuvakartta - Palvelin

:: --- 1. LUODAAN PIKAKUVAKE TYÖPÖYDÄLLE (Vain ensimmäisellä kerralla) ---
:: Käytetään imageres.dll, 203 (Kartta-ikoni), joka sopii parhaiten tähän tarkoitukseen.
set "SHORTCUT_NAME=Kuvakartta.lnk"
set "DESKTOP_PATH=%USERPROFILE%\Desktop\%SHORTCUT_NAME%"
set "SCRIPT_PATH=%~dp0kaynnista.bat"
set "ICON_PATH=imageres.dll,203"

if not exist "%DESKTOP_PATH%" (
    echo Luodaan kaynnistyskuvake tyopoydalle...
    powershell -Command "$s=(New-Object -ComObject WScript.Shell).CreateShortcut('%DESKTOP_PATH%'); $s.TargetPath='%SCRIPT_PATH%'; $s.WorkingDirectory='%~dp0'; $s.IconLocation='%ICON_PATH%'; $s.Save()"
    echo.
    echo [OK] Kuvake luotu tyopoydalle!
    timeout /t 2 >nul
)

:: --- 2. TARKISTETAAN YMPÄRISTÖ ---
if not exist "venv\Scripts\activate.bat" (
    echo [VIRHE] Virtuaaliymparistoa ei loytynyt. 
    echo Aja ensin asenna.bat tai varmista, etta venv-kansio on samassa paikassa.
    pause
    exit /b
)

:: --- 3. KÄYNNISTETÄÄN PALVELIN ---
echo Aktivoidaan ajoymparisto...
call venv\Scripts\activate

echo Avataan selain osoitteeseen http://localhost:9000 ...
start http://localhost:9000

echo.
echo ========================================================
echo KUVAKARTTA ON KAYNNISSA!
echo.
echo Kayttoliittyma aukesi selaimeen.
echo Pidä tämä ikkuna auki niin kauan kuin käytät ohjelmaa.
echo ========================================================
echo.

:: Käynnistetään itse Python-sovellus
python app.py

if %errorlevel% neq 0 (
    echo.
    echo [VIRHE] Palvelin pysattyi virheeseen. Tarkista mml_key.txt.
    pause
)
