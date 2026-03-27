# Copyright (C) 2026 Matti Räsänen
# Lisensoitu GPLv3:lla. Päivitetty macOS-yhteensopivaksi.

from flask import Flask, render_template, jsonify, send_from_directory
import os
import subprocess
import re
import json
import hashlib
import exifread

app = Flask(__name__)

# --- POLKUJEN HALLINTA ---
# Käytetään BASE_DIR-muuttujaa, jotta polut ovat aina oikein suhteessa app.py:hyn
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_FILE = os.path.join(BASE_DIR, "mml_key.txt")
PATHS_FILE = os.path.join(BASE_DIR, "polut.txt")
CACHE_DIR = os.path.join(BASE_DIR, "static", "cache")

# Varmistetaan cache-kansion olemassaolo
os.makedirs(CACHE_DIR, exist_ok=True)

def load_api_key():
    """Lataa API-avaimen mml_key.txt-tiedostosta."""
    if os.path.exists(KEY_FILE):
        try:
            with open(KEY_FILE, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except:
            pass
    return "AVAIN_PUUTTUU"

def get_media_sources():
    """Lukee polut polut.txt-tiedostosta tai käyttää macOS-oletuksia."""
    sources = {}
    
    if os.path.exists(PATHS_FILE):
        with open(PATHS_FILE, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Laajentaa ~ ja ympäristömuuttujat
                expanded_path = os.path.expandvars(os.path.expanduser(line))
                
                if os.path.exists(expanded_path):
                    name = os.path.basename(expanded_path.rstrip(os.sep)) or f"asema_{i}"
                    sources[name] = expanded_path

    # macOS-kohtaiset oletuskansiot, jos polut.txt on tyhjä
    if not sources:
        # macOS:ssä 'Kuvat' on 'Pictures' ja 'Videot' on 'Movies'
        default_kuvat = os.path.expanduser("~/Pictures")
        default_videot = os.path.expanduser("~/Movies")
        
        if os.path.exists(default_kuvat):
            sources["Kuvat (Mac)"] = default_kuvat
        if os.path.exists(default_videot):
            sources["Videot (Mac)"] = default_videot
            
    return sources

MML_API_KEY = load_api_key()
MEDIA_SOURCES = get_media_sources()

# --- METADATAN KÄSITTELY ---

def hae_kuvan_koordinaatit(kuva_polku):
    hash_obj = hashlib.md5(kuva_polku.encode())
    cache_file = os.path.join(CACHE_DIR, f"img_{hash_obj.hexdigest()}.json")

    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
                return data.get('lat'), data.get('lon')
        except: pass

    lat, lon = None, None
    try:
        with open(kuva_polku, 'rb') as f:
            tags = exifread.process_file(f, details=False)
            if 'GPS GPSLatitude' in tags and 'GPS GPSLongitude' in tags:
                def to_decimal(values):
                    def eval_frac(val):
                        return float(val.num) / float(val.den) if hasattr(val, 'num') and val.den != 0 else float(val)
                    return eval_frac(values[0]) + (eval_frac(values[1]) / 60.0) + (eval_frac(values[2]) / 3600.0)

                lat = to_decimal(tags['GPS GPSLatitude'].values)
                lon = to_decimal(tags['GPS GPSLongitude'].values)
                if str(tags.get('GPS GPSLatitudeRef', 'N')) == 'S': lat = -lat
                if str(tags.get('GPS GPSLongitudeRef', 'E')) == 'W': lon = -lon
                lat, lon = round(lat, 6), round(lon, 6)
    except Exception: pass

    with open(cache_file, 'w') as f:
        json.dump({'lat': lat, 'lon': lon}, f)
    return lat, lon

def hae_videon_reitti(mp4_polku):
    hash_obj = hashlib.md5(mp4_polku.encode())
    cache_file = os.path.join(CACHE_DIR, f"vid_{hash_obj.hexdigest()}.json")

    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f: return json.load(f)
        except: pass

    # macOS:ssä ffmpeg on asennettu Brew'lla, varmista että se on PATHissa
    komento = ['ffmpeg', '-y', '-i', mp4_polku, '-map', '0:s:0', '-f', 'srt', '-']
    reitti = []
    try:
        tulos = subprocess.run(komento, capture_output=True, text=True, timeout=10)
        blocks = tulos.stdout.replace('\r', '').split('\n\n')
        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                time_match = re.search(r'(\d{2}):(\d{2}):(\d{2})', lines[1])
                coord_match = re.search(r'([-+]?\d+\.\d+)\s*,\s*([-+]?\d+\.\d+)', lines[-1])
                
                if time_match and coord_match:
                    h, m, s = map(int, time_match.groups())
                    sekunnit = h * 3600 + m * 60 + s
                    lat, lon = float(coord_match.group(1)), float(coord_match.group(2))
                    if lat < lon: lat, lon = lon, lat
                    reitti.append({"t": sekunnit, "lat": lat, "lng": lon})
    except: pass

    if reitti:
        tallennettava = reitti[::2] if len(reitti) > 100 else reitti
        with open(cache_file, 'w') as f: json.dump(tallennettava, f)
        return tallennettava
    return []

# --- REITTIEHDOT ---

@app.route('/')
def index():
    return render_template('index.html', mml_key=MML_API_KEY)

@app.route('/api/data')
def get_data():
    files_data = []
    valid_cache_files = set()
    sources = get_media_sources()

    for category, base_path in sources.items():
        if not os.path.exists(base_path): continue
        for root, _, files in os.walk(base_path):
            for file in files:
                # macOS suodatus: Ohitetaan piilotiedostot (kuten .DS_Store tai ._tiedosto)
                if file.startswith('.'):
                    continue

                full_path = os.path.join(root, file)
                rel_path = f"{category}/{os.path.relpath(full_path, base_path)}"
                file_lower = file.lower()
                hash_obj = hashlib.md5(full_path.encode()).hexdigest()

                if file_lower.endswith(('.mp4', '.mov', '.mpg')):
                    valid_cache_files.add(f"vid_{hash_obj}.json")
                    reitti = hae_videon_reitti(full_path)
                    files_data.append({
                        "type": "video", "name": file, "path": rel_path, "route": reitti or None
                    })
                elif file_lower.endswith(('.jpg', '.jpeg', '.png', '.avif')):
                    valid_cache_files.add(f"img_{hash_obj}.json")
                    lat, lon = hae_kuvan_koordinaatit(full_path)
                    files_data.append({
                        "type": "image", "name": file, "path": rel_path, "lat": lat, "lng": lon
                    })
    
    # Siivotaan vanhentuneet välimuistitiedostot
    if os.path.exists(CACHE_DIR):
        for cache_file in os.listdir(CACHE_DIR):
            if cache_file.endswith('.json') and cache_file not in valid_cache_files:
                try: os.remove(os.path.join(CACHE_DIR, cache_file))
                except OSError: pass

    return jsonify(files_data)

@app.route('/media/<category>/<path:filename>')
def serve_media(category, filename):
    sources = get_media_sources()
    if category in sources:
        return send_from_directory(sources[category], filename)
    return "Ei löydy", 404

if __name__ == '__main__':
    # macOS:ssä portti 9000 on vapaa ja 0.0.0.0 sallii pääsyn lähiverkosta
    app.run(host='0.0.0.0', port=9000, debug=False)
