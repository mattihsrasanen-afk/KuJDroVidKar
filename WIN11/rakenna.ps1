# Rakenna.ps1 - PyInstaller-koontiskripti
Write-Host "--- Siivotaan vanhat tiedostot ---" -ForegroundColor Yellow

# Poistetaan vanhat koosteet ja väliaikaistiedostot
$siivottavat = @("dist", "build", "Output")

foreach ($kohde in $siivottavat) {
    if (Test-Path $kohde) {
        Write-Host "Poistetaan: $kohde"
        Remove-Item -Recurse -Force $kohde
    }
}

# Tyhjennetään json-välimuisti ennen paketointia
if (Test-Path "static\cache") { 
    Write-Host "Tyhjennetään välimuisti..."
    Get-ChildItem -Path "static\cache\*.json" | Remove-Item -Force 
}

Write-Host "--- Aloitetaan sovelluksen paketointi ---" -ForegroundColor Cyan

# Suoritetaan PyInstaller-komento
# Rakenna.ps1 - PyInstaller-koontiskripti
Write-Host "--- Siivotaan vanhat tiedostot ---" -ForegroundColor Yellow

# Poistetaan vanhat koosteet ja väliaikaistiedostot
$siivottavat = @("dist", "build", "Output")

foreach ($kohde in $siivottavat) {
    if (Test-Path $kohde) {
        Write-Host "Poistetaan: $kohde"
        Remove-Item -Recurse -Force $kohde
    }
}

# Tyhjennetään json-välimuisti ennen paketointia
if (Test-Path "static\cache") { 
    Write-Host "Tyhjennetään välimuisti..."
    Get-ChildItem -Path "static\cache\*.json" | Remove-Item -Force 
}

Write-Host "--- Aloitetaan sovelluksen paketointi ---" -ForegroundColor Cyan

# Suoritetaan PyInstaller-komento
# Huom: Ei käytetä --contents-directory-asetusta, jotta Tkinter ei hajoa
py -m PyInstaller --noconfirm --onedir --console --clean `
--add-data "templates;templates" `
--add-data "static;static" `
--add-data "bin;bin" `
app.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n[OK] PyInstaller valmis!" -ForegroundColor Green

    # --- UUSI LISÄYS: Kopioidaan lähdekoodi talteen valmiiseen kansioon ---
    Copy-Item "app.py" -Destination "dist\app\"
    
    # 1. Tarkistetaan löytyykö Inno Setup ja ajetaan se
    $iscc = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

    if (Test-Path $iscc) {
        Write-Host "`n--- Luodaan asennuspaketti (Inno Setup) ---" -ForegroundColor Cyan
        & $iscc "projeti.iss"
    }
    
    # 2. Pakataan siirtotiedosto (ZIP)
    Write-Host "`n--- Pakataan siirtotiedosto (ZIP) ---" -ForegroundColor Cyan
    $zipNimi = "Kuvakartta_Siirtopaketti.zip"
    
    # Poistetaan vanha zip-tiedosto, jos sellainen on jo olemassa
    if (Test-Path $zipNimi) { 
        Remove-Item -Force $zipNimi 
    }

    # Käytetään Windowsin natiivia tar.exe -komentoa
    tar.exe -a -c -f $zipNimi -C dist\app .
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Kaikki pakattu onnistuneesti tiedostoon: $zipNimi" -ForegroundColor Green
    } else {
        Write-Host "[VIRHE] ZIP-pakkaus epäonnistui!" -ForegroundColor Red
    }
    
} else {
    Write-Host "`n[VIRHE] PyInstallerin suorituksessa tapahtui virhe." -ForegroundColor Red
}

Read-Host "`nProsessi valmis. Paina Enter sulkeaksesi..."