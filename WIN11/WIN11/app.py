# Copyright (C) 2026  Matti Räsänen
# GPLv3 Licensed

import os
import subprocess
import re
import json
import hashlib
import sys
import webbrowser
import tkinter as tk
from tkinter import filedialog
from threading import Timer
from flask import Flask, render_template, jsonify, send_from_directory, request, redirect

# --- POLKUJEN HALLINTA ---
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
    RESOURCES_DIR = sys._MEIPASS 
    user_data_dir = os.path.join(os.environ['LOCALAPPDATA'], 'Kuvakartta')
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    RESOURCES_DIR = BASE_DIR
    user_data_dir = os.path.join(os.environ['LOCALAPPDATA'], 'Kuvakartta')

KEY_FILE = os.path.join(user_data_dir, "mml_key.txt")
CACHE_DIR = os.path.join(user_data_dir, "cache")
FOLDERS_FILE = os.path.join(user_data_dir, "folders.txt")

# Luodaan tarvittavat kansiot
os.makedirs(user_data_dir, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

FFMPEG_PATH = os.path.join(BASE_DIR, "ffmpeg-2026-03-22-git-9c63742425-full_build", "bin", "ffmpeg.exe")

def load_extra_folders():
    folders = {}
    if os.path.exists(FOLDERS_FILE):
        try:
            with open(FOLDERS_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    if '|' in line:
                        name, path = line.strip().split('|')
                        if os.path.exists(path):
                            folders[name] = path
        except: pass
    return folders

def get_all_sources():
    sources = {
        "kuvat": os.path.expanduser("~\\Pictures"),
        "videot": os.path.expanduser("~\\Videos")
    }
    sources.update(load_extra_folders())
    return sources

# --- FLASK-OLION LUONTI ---
app = Flask(__name__, 
            template_folder=os.path.join(RESOURCES_DIR, "templates"),
            static_folder=os.path.join(RESOURCES_DIR, "static"))

def load_api_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, 'r') as f:
            avain = f.read().strip()
            if avain: # Jos tiedostossa on jotain...
                return avain
    return "AVAIN_PUUTTUU"

MML_API_KEY = load_api_key()

# --- APUFUNKTIOT ---

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
        import exifread
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

    komento = [FFMPEG_PATH, '-y', '-i', mp4_polku, '-map', '0:s:0', '-f', 'srt', '-']
    reitti = []
    try:
        luonti_liput = 0x08000000 if os.name == 'nt' else 0
        tulos = subprocess.run(komento, capture_output=True, text=True, timeout=10, creationflags=luonti_liput)
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

# --- REITIT (ROUTES) ---

@app.route('/')
def index():
    # Luetaan avain tiedostosta JOKAISELLA sivun latauksella
    nykyinen_avain = load_api_key()
    return render_template('index.html', api_key=nykyinen_avain)

@app.route('/api/browse')
def browse_folder():
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True) # Tuo ikkunan muiden päälle
        root.update() # Pakota päivitys, jotta ikkuna ei jumiudu
        directory = filedialog.askdirectory(parent=root, title='Valitse projektikansio')
        root.destroy()
        
        # Palautetaan polku oikeilla kenoviivoilla Windowsia varten
        if directory:
            return jsonify({"path": directory.replace('/', os.sep)})
        return jsonify({"path": ""})
    except Exception as e:
        print(f"Virhe: {e}")
        return jsonify({"path": ""})

@app.route('/add_folder', methods=['POST'])
def add_folder():
    name = request.form.get('folder_name', '').strip()
    path = request.form.get('folder_path', '').strip()
    if name and path and os.path.exists(path):
        with open(FOLDERS_FILE, 'a', encoding='utf-8') as f:
            f.write(f"{name}|{path}\n")
    return redirect('/')

import datetime
def hae_kuvan_vuosi(kuva_polku):
    """Yrittää lukea kuvan alkuperäisen ottovuoden EXIF-tiedoista."""
    try:
        import exifread
        with open(kuva_polku, 'rb') as f:
            tags = exifread.process_file(f, stop_tag='EXIF DateTimeOriginal', details=False)
            date_tag = tags.get('EXIF DateTimeOriginal') or tags.get('Image DateTime')
            
            if date_tag:
                date_str = str(date_tag.values)
                vuosi_match = re.match(r'(\d{4})', date_str)
                if vuosi_match:
                    return vuosi_match.group(1)
    except Exception:
        pass
    
    try:
        mtime = os.path.getmtime(kuva_polku)
        return str(datetime.datetime.fromtimestamp(mtime).year)
    except:
        return "Muut"

# --- TÄMÄ ON VARSINAINEN API-REITTI ---
@app.route('/api/data')
def get_data():
    files_data = []
    sources = get_all_sources()
    for category, base_path in sources.items():
        if not os.path.exists(base_path): continue
        for root, _, files in os.walk(base_path):
            for file in files:
                full_path = os.path.join(root, file)
                file_lower = file.lower()
                
                # Haetaan vuosi älykkäästi (EXIF -> mtime)
                vuosi = hae_kuvan_vuosi(full_path)

                rel_path = f"{category}/{os.path.relpath(full_path, base_path).replace(os.sep, '/')}"
                hash_obj = hashlib.md5(full_path.encode()).hexdigest()

                if file_lower.endswith(('.mp4', '.mov', '.mpg')):
                    reitti = hae_videon_reitti(full_path)
                    files_data.append({
                        "type": "video", "name": file, "path": rel_path, 
                        "year": vuosi, "category": category, "route": reitti or None
                    })
                elif file_lower.endswith(('.jpg', '.jpeg', '.png', '.avif')):
                    lat, lon = hae_kuvan_koordinaatit(full_path)
                    files_data.append({
                        "type": "image", "name": file, "path": rel_path, 
                        "year": vuosi, "category": category, "lat": lat, "lng": lon
                    })
    return jsonify(files_data)
@app.route('/media/<category>/<path:filename>')
def serve_media(category, filename):
    sources = get_all_sources()
    if category in sources:
        return send_from_directory(sources[category], filename)
    return "Not found", 404

@app.route('/set_key', methods=['POST'])
def set_key():
    key = request.form.get('api_key', '').strip()
    if key:
        with open(KEY_FILE, 'w') as f:
            f.write(key)
        # Päivitetään muuttuja lennosta, jotta ohjelmaa ei tarvitse käynnistää uudelleen
        global MML_API_KEY
        MML_API_KEY = key
    return redirect('/')

@app.route('/clear_folders')
def clear_folders():
    if os.path.exists(FOLDERS_FILE):
        os.remove(FOLDERS_FILE)
    return redirect('/')

# --- KÄYNNISTYS ---
def open_browser():
    webbrowser.open_new("http://127.0.0.1:9000")

if __name__ == '__main__':
    Timer(1.5, open_browser).start()
    app.run(host='127.0.0.1', port=9000, debug=False)