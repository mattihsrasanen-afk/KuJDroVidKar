#!/bin/bash

# macOS:ssä ei suositella sudoa koko skriptille, 
# mutta tarkistetaan silti oikeudet asennuksiin tarvittaessa.
APP_DIR=$(pwd)

echo "--- Tarkistetaan Homebrew ---"
if ! command -v brew &> /dev/null; then
    echo "Virhe: Homebrew ei ole asennettu. Asenna se osoitteesta https://brew.sh/"
    exit 1
fi

echo "--- Asennetaan järjestelmäriippuvuudet (macOS) ---"
# LISÄTTY: exiftool
brew install python ffmpeg exiftool

echo "--- Luodaan virtuaaliympäristö ja asennetaan Python-paketit ---"
python3 -m venv venv
./venv/bin/pip install -r requirements.txt

echo "--- Tarkistetaan API-avain ---"
if [ ! -f "mml_key.txt" ] || grep -q "x" "mml_key.txt"; then
    read -p "Syötä MML API-avain: " apikey
    echo "$apikey" > mml_key.txt
fi

echo "--- macOS-huomio: Palvelun käynnistys ---"
echo "macOS ei tue systemd-palveluita (kuvakartta.service)."
echo "Voit käynnistää ohjelman manuaalisesti skriptillä: ./kaynnista_mac.sh"
echo "------------------------------------------"
