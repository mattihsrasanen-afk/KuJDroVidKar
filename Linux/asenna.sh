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
apt install -y python3-pip python3-venv ffmpeg

echo "--- Luodaan virtuaaliympäristö ja asennetaan Python-paketit ---"
python3 -m venv venv
./venv/bin/pip install -r requirements.txt

echo "--- Tarkistetaan API-avain ---"
# Kysytään avainta jos tiedosto puuttuu TAI jos se sisältää x-merkkejä
if [ ! -f "mml_key.txt" ] || grep -q "x" "mml_key.txt"; then
    read -p "Syötä MML API-avain: " apikey
    echo "$apikey" > mml_key.txt
    chown $USER_NAME:$USER_NAME mml_key.txt
fi

echo "--- Luodaan systemd-palvelu ---"
cat <<EOF > /etc/systemd/system/kuvakartta.service
[Unit]
Description=Kuvakartta Flask Palvelu
After=network.target

[Service]
User=$USER_NAME
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo "--- Käynnistetään palvelu ---"
systemctl daemon-reload
systemctl enable kuvakartta
systemctl restart kuvakartta

echo "--- Valmis! ---"
echo "Voit seurata lokeja komennolla: journalctl -u kuvakartta -f"
echo "--- Asennus valmis! ---"
IP_ADDR=$(hostname -I | awk '{print $1}')
echo "Pääset palveluun osoitteessa: http://$IP_ADDR:9000"
echo "ja ./palomuuri.sh, jotta sivu näkyy muilla saman verkon laitteilla (tabletit, puhelimet)."
read -p "Haluatko avata palomuurin portin 9000 nyt? (k/e): " vastaus
if [[ $vastaus == "k" || $vastaus == "K" ]]; then
    bash palomuuri.sh
fi
