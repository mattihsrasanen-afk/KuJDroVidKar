# Copyright (C) 2026 Matti Räsänen
# Lisensoitu GPLv3:lla. Kehitetty Debian 13 (Trixie) / Windows 11 -ympäristöön.

from flask import Flask, render_template, jsonify, send_from_directory, request
import sys
import os
import subprocess
import re
import json
import hashlib
import exifread
import time
import tkinter as tk
from tkinter import filedialog

app = Flask(__name__)

# --- POLKUJEN HALLINTA (Linux-yhteensopiva) ---
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Linuxissa oletetaan, että nämä on asennettu järjestelmään (esim. apt install)
EXIFTOOL_PATH = "exiftool"
FFMPEG_PATH = "ffmpeg"

KEY_FILE = os.path.join(BASE_DIR, "mml_key.txt")
PATHS_FILE = os.path.join(BASE_DIR, "polut.txt")
CACHE_DIR = os.path.join(BASE_DIR, "static", "cache")

os.makedirs(CACHE_DIR, exist_ok=True)
for f in [KEY_FILE, PATHS_FILE]:
    if not os.path.exists(f):
        with open(f, "w", encoding="utf-8") as tmp: pass

# --- APUFUNKTIOT ---
def load_api_key():
    if os.path.exists(KEY_FILE):
        try:
            with open(KEY_FILE, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except: pass
    return ""

def get_media_sources():
    sources = {}
    if os.path.exists(PATHS_FILE):
        with open(PATHS_FILE, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                line = line.strip()
                if not line or line.startswith('#'): continue
                expanded_path = os.path.expandvars(os.path.expanduser(line))
                if os.path.exists(expanded_path):
                    name = os.path.basename(expanded_path.rstrip(os.sep)) or f"asema_{i}"
                    sources[name] = expanded_path
    return sources

def hae_kuvan_koordinaatit(kuva_polku):
    hash_obj = hashlib.md5(kuva_polku.encode('utf-8'))
    cache_file = os.path.join(CACHE_DIR, f"img_{hash_obj.hexdigest()}.json")
    tiedoston_mtime = os.path.getmtime(kuva_polku)

    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
                if data.get('mtime') == tiedoston_mtime:
                    return data.get('lat'), data.get('lon'), data.get('year')
        except: pass

    lat, lon, year = None, None, None
    
    try:
        with open(kuva_polku, 'rb') as f:
            tags = exifread.process_file(f, details=False)
            
            # 1. Haetaan vuosi ensisijaisesti EXIF-metadatasta
            if 'EXIF DateTimeOriginal' in tags:
                y = str(tags['EXIF DateTimeOriginal'])[:4]
                if y.isdigit() and 2010 <= int(y) <= 2026: year = int(y)
            elif 'Image DateTime' in tags:
                y = str(tags['Image DateTime'])[:4]
                if y.isdigit() and 2010 <= int(y) <= 2026: year = int(y)

            # Sijainnin käsittely
            if 'GPS GPSLatitude' in tags and 'GPS GPSLongitude' in tags:
                def to_decimal(values):
                    def eval_frac(val):
                        return float(val.num) / float(val.den) if hasattr(val, 'num') and val.den != 0 else float(val)
                    return eval_frac(values[0]) + (eval_frac(values[1]) / 60.0) + (eval_frac(values[2]) / 3600.0)
                lat = to_decimal(tags['GPS GPSLatitude'].values)
                lon = to_decimal(tags['GPS GPSLongitude'].values)
                if str(tags.get('GPS GPSLatitudeRef', 'N')) == 'S': lat = -lat
                if str(tags.get('GPS GPSLongitudeRef', 'E')) == 'W': lon = -lon
                lat, lon = round(lat, 5), round(lon, 5)
    except: pass
    
    # 2. Varakeino: otetaan vuosi tiedoston oikeasta luontiajasta (Windows ctime)
    if not year:
        tiedoston_ctime = os.path.getctime(kuva_polku)
        y = time.localtime(tiedoston_ctime).tm_year
        if 2010 <= y <= 2026: year = y

    with open(cache_file, 'w') as f:
        json.dump({'lat': lat, 'lon': lon, 'year': year, 'mtime': tiedoston_mtime}, f)
    return lat, lon, year

def hae_videon_tiedot(mp4_polku):
    hash_obj = hashlib.md5(mp4_polku.encode('utf-8'))
    cache_file = os.path.join(CACHE_DIR, f"vid_{hash_obj.hexdigest()}.json")
    tiedoston_mtime = os.path.getmtime(mp4_polku)
    
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f: 
                data = json.load(f)
                if data.get('mtime') == tiedoston_mtime:
                    return data
        except: pass

    komento = [FFMPEG_PATH, '-y', '-i', mp4_polku, '-map', '0:s:0', '-f', 'srt', '-']
    reitti = []
    year = None
    tiedoston_nimi = os.path.basename(mp4_polku)
    
    # Videon vuoden tarkistus (nimi -> mtime)
    match = re.search(r'(20\d{2})', tiedoston_nimi)
    if match and 2010 <= int(match.group(1)) <= 2026:
        year = int(match.group(1))
    else:
        y = time.localtime(tiedoston_mtime).tm_year
        if 2010 <= y <= 2026: year = y

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

    tallennettava_reitti = reitti[::2] if len(reitti) > 100 else reitti
    tulos_obj = {"route": tallennettava_reitti, "year": year, "mtime": tiedoston_mtime}
    
    with open(cache_file, 'w') as f: json.dump(tulos_obj, f)
    return tulos_obj

# --- REITIT ---
@app.route('/')
def index():
    return render_template('index.html', mml_key=load_api_key())

@app.route('/api/data')
def get_data():
    files_data = []
    valid_cache_files = set()
    sources = get_media_sources()

    for category, base_path in sources.items():
        if not os.path.exists(base_path): continue
        for root, _, files in os.walk(base_path):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = f"{category}/{os.path.relpath(full_path, base_path)}".replace('\\', '/')
                file_lower = file.lower()
                hash_obj = hashlib.md5(full_path.encode('utf-8')).hexdigest()

                if file_lower.endswith(('.mp4', '.mov', '.mpg')):
                    valid_cache_files.add(f"vid_{hash_obj}.json")
                    video_data = hae_videon_tiedot(full_path)
                    reitti = video_data.get('route')
                    vuosi = video_data.get('year')
                    files_data.append({"type": "video", "name": file, "path": rel_path, "route": reitti or None, "year": vuosi})
                elif file_lower.endswith(('.jpg', '.jpeg', '.png', '.avif')):
                    valid_cache_files.add(f"img_{hash_obj}.json")
                    lat, lon, vuosi = hae_kuvan_koordinaatit(full_path)
                    files_data.append({"type": "image", "name": file, "path": rel_path, "lat": lat, "lng": lon, "year": vuosi})
    return jsonify(files_data)

@app.route('/media/<category>/<path:filename>')
def serve_media(category, filename):
    sources = get_media_sources()
    if category in sources:
        return send_from_directory(sources[category], filename)
    return "Ei löydy", 404

@app.route('/api/config/key', methods=['POST'])
def save_key():
    key = request.json.get('key', '')
    with open(KEY_FILE, 'w', encoding='utf-8') as f:
        f.write(key.strip())
    return jsonify({"status": "ok"})

@app.route('/api/config/pick_folder')
def pick_folder():
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    folder_path = filedialog.askdirectory()
    root.destroy()
    return jsonify({"path": folder_path})

@app.route('/api/config/add_folder', methods=['POST'])
def add_folder():
    path = request.json.get('path', '').strip()
    if path and os.path.exists(path):
        with open(PATHS_FILE, 'a', encoding='utf-8') as f:
            f.write(f"\n{path}")
        return jsonify({"status": "ok"})
    return jsonify({"status": "error", "message": "Polkua ei ole"}), 400

@app.route('/api/update_gps', methods=['POST'])
def update_gps():
    try:
        data = request.json
        paths = data.get('paths')
        
        new_lat = float(data.get('lat'))
        new_lon = float(data.get('lng'))

        if not paths:
            return jsonify({"status": "error", "message": "Polut puuttuvat"}), 400

        sources = get_media_sources()
        valid_files = []
        
        for rel_path in paths:
            rel_path = rel_path.replace('\\', '/')
            try:
                if '/' in rel_path:
                    cat, fname = rel_path.split('/', 1)
                    if cat in sources:
                        full_path = os.path.join(sources[cat], fname)
                        if os.path.exists(full_path):
                            valid_files.append(full_path)
                else:
                    for cat_path in sources.values():
                        full_path = os.path.join(cat_path, rel_path)
                        if os.path.exists(full_path):
                            valid_files.append(full_path)
                            break
            except Exception as e:
                print(f"[VIRHE] Polun {rel_path} käsittely: {e}")
                continue

        if not valid_files:
            return jsonify({"status": "error", "message": "Tiedostoja ei löytynyt levyltä"}), 400

        lat_ref = 'N' if new_lat >= 0 else 'S'
        lon_ref = 'E' if new_lon >= 0 else 'W'

        komento = [
            EXIFTOOL_PATH, '-overwrite_original',
            f'-GPSLatitude={abs(new_lat)}', f'-GPSLatitudeRef={lat_ref}',
            f'-GPSLongitude={abs(new_lon)}', f'-GPSLongitudeRef={lon_ref}'
        ] + valid_files
        
        print(f"Suoritetaan Exiftool {len(valid_files)} kuvalle...")
        
        tulos = subprocess.run(komento, capture_output=True, text=True)
        
        if tulos.returncode != 0:
            print(f"[EXIFTOOL VIRHE] {tulos.stderr}")
            return jsonify({"status": "error", "message": "ExifTool virhe: " + tulos.stderr}), 500
            
        print("[OK] ExifTool:", tulos.stdout.strip())
        
        for fpath in valid_files:
            hash_obj = hashlib.md5(fpath.encode('utf-8')).hexdigest()
            cache_file = os.path.join(CACHE_DIR, f"img_{hash_obj}.json")
            if os.path.exists(cache_file): 
                os.remove(cache_file)
            
        return jsonify({"status": "ok"})
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Palvelinvirhe: " + str(e)}), 500

if __name__ == '__main__':
    print(f"Palvelin käynnistyy porttiin 9000...")
    app.run(host='0.0.0.0', port=9000, debug=False)
