#!/bin/bash

# Tarkistetaan onko käyttäjä root
if [ "$EUID" -ne 0 ]; then 
  echo "Suorita skripti sudo-oikeuksilla: sudo ./asenna.sh"
  exit
fi

USER_NAME=$SUDO_USER
APP_DIR=$(pwd)

echo "--- Asennetaan järjestelmäriippuvuudet (Debian 13) ---"
apt update
# LISÄTTY python3-tk, jotta kansionvalintaikkuna (Tkinter) toimii Linuxissa
apt install -y python3-pip python3-venv python3-tk ffmpeg libimage-exiftool-perl

echo "--- Luodaan virtuaaliympäristö ja asennetaan Python-paketit ---"
# LISÄTTY sudo -u, jotta venv ja paketit asennetaan sinun käyttäjäsi omistukseen, ei rootin!
sudo -u $USER_NAME python3 -m venv venv
sudo -u $USER_NAME ./venv/bin/pip install -r requirements.txt

echo "--- Tarkistetaan API-avain ---"
# Kysytään avainta jos tiedosto puuttuu TAI jos se sisältää x-merkkejä
if [ ! -f "mml_key.txt" ] || grep -q "x" "mml_key.txt"; then
    read -p "Syötä MML API-avain: " apikey
    echo "$apikey" > mml_key.txt
    chown $USER_NAME:$USER_NAME mml_key.txt
fi

echo "--- Luodaan systemd-palvelu ---"
# LISÄTTY Environment-rivit! Ilman näitä taustalla pyörivä ohjelma ei voi avata kansionvalintaa työpöydällesi.
cat <<EOF > /etc/systemd/system/kuvakartta.service
[Unit]
Description=Kuvakartta Flask Palvelu
After=network.target

[Service]
User=$USER_NAME
WorkingDirectory=$APP_DIR
Environment="DISPLAY=:0"
Environment="XAUTHORITY=/home/$USER_NAME/.Xauthority"
ExecStart=$APP_DIR/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo "--- Käynnistetään palvelu ---"
systemctl daemon-reload
systemctl enable kuvakartta
systemctl restart kuvakartta

echo "--- Valmis! Palvelin pyörii nyt taustalla. Osoite: http://localhost:9000 ---"
