#!/bin/bash
cd "$(dirname "$0")"

# macOS ei tarvitse DISPLAY-muuttujaa Tkinteriä varten, 
# se avaa kansionvalintaikkunan natiivisti.

echo "Käynnistetään Kuvakartta (macOS)..."
./venv/bin/python app.py
