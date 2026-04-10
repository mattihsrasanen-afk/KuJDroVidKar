#!/bin/bash
cd "$(dirname "$0")"

# Varmistetaan näyttömuuttuja, jotta työpöytäikkunat (kansionvalinta) varmasti toimivat
export DISPLAY=:0

echo "Käynnistetään Kuvakartta..."
./venv/bin/python app.py
