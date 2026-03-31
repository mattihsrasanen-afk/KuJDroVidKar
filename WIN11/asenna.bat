@echo off
setlocal
title Kuvakartta - Asennus

echo =========================================
echo ASENNETAAN KUVAKARTTA-SOVELLUS
echo =========================================
echo.

:: 1. TARKISTETAAN PYTHON
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [VIRHE] Pythonia ei loytynyt! 
    echo Asenna Python osoitteesta python.org. 
    echo MUISTA RAKSITTAA: "Add python.exe to PATH".
    echo.
    pause
    exit /b
)

:: 2. LUODAAN VIRTUAALIYMPARISTO
echo Luodaan virtuaaliymparisto (venv)...
python -m venv venv

:: 3. ASENNETAAN KIRJASTOT
echo Aktivoidaan ja asennetaan paketit (Flask, Exifread)...
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install Flask exifread

:: 4. LUODAAN KAYNNISTYSKUVAKE TYOPOYDALLE
:: Kaytetaan imageres.dll,203 (Kartta-ikoni)
set "SHORTCUT_NAME=Kuvakartta.lnk"
set "DESKTOP_PATH=%USERPROFILE%\Desktop\Kuvakartta.lnk"
set "SCRIPT_PATH=%~dp0kaynnista.bat"
set "ICON_PATH=imageres.dll,203"

echo Luodaan kaynnistyskuvake tyopoydalle...
powershell -Command "$s=(New-Object -ComObject WScript.Shell).CreateShortcut('%DESKTOP_PATH%'); $s.TargetPath='%SCRIPT_PATH%'; $s.WorkingDirectory='%~dp0'; $s.IconLocation='%ICON_PATH%'; $s.Save()"

echo.
echo =========================================
echo ASENNUS VALMIS!
echo.
echo 1. Muista lisata API-avaimesi mml_key.txt -tiedostoon.
echo 2. Voit nyt kaynnistaa ohjelman tyopoydan Kuvakartta-kuvakkeesta.
echo =========================================
echo.
pause
