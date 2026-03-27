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
# macOS:ssä käytetään brewia apt:n sijaan
brew install python ffmpeg

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
echo "Voit käynnistää ohjelman manuaalisesti komennolla:"
echo "source venv/bin/activate && python3 app.py"
echo "------------------------------------------"

# macOS palomuuri (SocketFilterFW) on erilainen kuin Linuxin ufw/iptables.
# Yleensä macOS kysyy lupaa portille, kun sovellus käynnistyy.
read -p "Haluatko käynnistää sovelluksen nyt? (k/e): " vastaus
if [[ $vastaus == "k" || $vastaus == "K" ]]; then
    ./venv/bin/python app.py
fi
# Lisäysvinkki mac-skriptin loppuun:
IP_ADDR=$(ipconfig getifaddr en0)
echo "Pääset palveluun osoitteessa: http://$IP_ADDR:9000"
