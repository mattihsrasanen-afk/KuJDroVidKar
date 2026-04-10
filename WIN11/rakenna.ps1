# Rakenna.ps1 - PyInstaller-koontiskripti
Write-Host "--- Aloitetaan sovelluksen paketointi ---" -ForegroundColor Cyan

# Suoritetaan PyInstaller-komento
py -m PyInstaller --noconfirm --onedir --console --clean `
--add-data "templates;templates" `
--add-data "static;static" `
--add-data "bin;bin" `
app.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nValmis! Sovellus löytyy dist/app -kansioista." -ForegroundColor Green
} else {
    Write-Host "`nVirhe koontivaiheessa!" -ForegroundColor Red
}

# Jätetään ikkuna auki, jotta näet mahdolliset virheet
Read-Host "`nPaina Enter sulkeaksesi..."