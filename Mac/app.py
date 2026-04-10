# Copyright (C) 2026 Matti Räsänen
# Lisensoitu GPLv3:lla. Kehitetty Debian 13 (Trixie) -ympäristöön.

from flask import Flask, render_template, jsonify, send_from_directory, request
import os
import subprocess
import re
import json
import hashlib
import exifread

app = Flask(__name__)

# --- POLKUJEN HALLINTA (Linux-yhteensopiva) ---
# Käytetään BASE_DIR-muuttujaa, jotta polut ovat aina oikein suhteessa app.py:hyn
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_FILE = os.path.join(BASE_DIR, "mml_key.txt")
PATHS_FILE = os.path.join(BASE_DIR, "polut.txt")
CACHE_DIR = os.path.join(BASE_DIR, "static", "cache")
# Varmistetaan cache-kansion olemassaolo
os.makedirs(CACHE_DIR, exist_ok=True)

# 2. Määritellään funktiot (tämä vain kertoo Pythonille MITÄ tehdään, kun kutsutaan)
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
    """Lukee polut polut.txt-tiedostosta ja laajentaa ympäristömuuttujat."""
    sources = {}
    
    if os.path.exists(PATHS_FILE):
        with open(PATHS_FILE, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                line = line.strip()
                # Ohitetaan tyhjät ja kommentit
                if not line or line.startswith('#'):
                    continue
                
                # LAAJENNUS: Muuttaa $HOME -> /home/kayttaja
                expanded_path = os.path.expandvars(os.path.expanduser(line))
                
                if os.path.exists(expanded_path):
                    # Käytetään kansion nimeä tai viimeistä osaa polusta
                    name = os.path.basename(expanded_path.rstrip(os.sep)) or f"asema_{i}"
                    sources[name] = expanded_path

    # Jos tiedosto oli tyhjä, viallinen tai polkuja ei löytynyt, käytetään oletuksia
    if not sources:
        default_kuvat = os.path.expanduser("~/Kuvat")
        default_videot = os.path.expanduser("~/Videot")
        
        if os.path.exists(default_kuvat):
            sources["Kuvat (Oletus)"] = default_kuvat
        if os.path.exists(default_videot):
            sources["Videot (Oletus)"] = default_videot
            
    return sources

MML_API_KEY = load_api_key()
MEDIA_SOURCES = get_media_sources()

# --- REITTIEHDOT JA TOIMINNOT ---

def hae_kuvan_koordinaatit(kuva_polku):
    hash_obj = hashlib.md5(kuva_polku.encode())
    cache_file = os.path.join(CACHE_DIR, f"img_{hash_obj.hexdigest()}.json")
    
    # Haetaan tiedoston viimeisin muokkausaika
    tiedoston_mtime = os.path.getmtime(kuva_polku)

    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
                # JOS muokkausaika täsmää, käytetään välimuistia
                if data.get('mtime') == tiedoston_mtime:
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
                lat, lon = round(lat, 5), round(lon, 5)
    except Exception: pass
    with open(cache_file, 'w') as f:
        json.dump({'lat': lat, 'lon': lon, 'mtime': tiedoston_mtime}, f)
    return lat, lon

def hae_videon_reitti(mp4_polku):
    hash_obj = hashlib.md5(mp4_polku.encode())
    cache_file = os.path.join(CACHE_DIR, f"vid_{hash_obj.hexdigest()}.json")

    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f: return json.load(f)
        except: pass

    # Haetaan tekstitysraita SRT-muodossa
    komento = ['ffmpeg', '-y', '-i', mp4_polku, '-map', '0:s:0', '-f', 'srt', '-']
    reitti = []
    try:
        tulos = subprocess.run(komento, capture_output=True, text=True, timeout=10)
        # Etsitään lohkot: Numero, aikaleima ja koordinaatit
        blocks = tulos.stdout.replace('\r', '').split('\n\n')
        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                # Aikaleima riviltä 2 (esim. 00:00:01,000)
                time_match = re.search(r'(\d{2}):(\d{2}):(\d{2})', lines[1])
                # Koordinaatit viimeiseltä riviltä
                coord_match = re.search(r'([-+]?\d+\.\d+)\s*,\s*([-+]?\d+\.\d+)', lines[-1])
                
                if time_match and coord_match:
                    h, m, s = map(int, time_match.groups())
                    sekunnit = h * 3600 + m * 60 + s
                    lat, lon = float(coord_match.group(1)), float(coord_match.group(2))
                    # Suomessa lat on aina suurempi kuin lon, korjataan jos DJI kääntää ne
                    if lat < lon: lat, lon = lon, lat
                    reitti.append({"t": sekunnit, "lat": lat, "lng": lon})
    except: pass

    if reitti:
        # Tallennetaan välimuistiin (otetaan joka toinen piste jos data on tiheää)
        tallennettava = reitti[::2] if len(reitti) > 100 else reitti
        with open(cache_file, 'w') as f: json.dump(tallennettava, f)
        return tallennettava
    return []

@app.route('/')
def index():
    return render_template('index.html', mml_key=MML_API_KEY)

@app.route('/api/data')
def get_data():
    files_data = []
    valid_cache_files = set()

    for category, base_path in MEDIA_SOURCES.items():
        if not os.path.exists(base_path): continue
        for root, _, files in os.walk(base_path):
            for file in files:
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

@app.route('/api/refresh/<category>/<path:filename>')
def refresh_file(category, filename):
    sources = get_media_sources()
    if category in sources:
        full_path = os.path.join(sources[category], filename)
        if os.path.exists(full_path):
            hash_obj = hashlib.md5(full_path.encode()).hexdigest()
            # Etsitään ja poistetaan sekä kuva- että videovälimuistit tälle polulle
            for prefix in ['img_', 'vid_']:
                cache_file = os.path.join(CACHE_DIR, f"{prefix}{hash_obj}.json")
                if os.path.exists(cache_file):
                    os.remove(cache_file)
            return jsonify({"status": "ok", "message": "Välimuisti nollattu"})
    return jsonify({"status": "error", "message": "Tiedostoa ei löytynyt"}), 404

@app.route('/api/update_gps', methods=['POST'])
def update_gps():
    data = request.json
    paths = data.get('paths')
    if not paths and data.get('path'):
        paths = [data.get('path')]

    new_lat = data.get('lat')
    new_lon = data.get('lng')

    if not paths or not isinstance(paths, list) or new_lat is None or new_lon is None:
        return jsonify({"status": "error", "message": "Puutteelliset tiedot"}), 400

    sources = get_media_sources()
    valid_files = []
    for rel_path in paths:
        try:
            category, filename = rel_path.split('/', 1)
            if category in sources:
                full_path = os.path.join(sources[category], filename)
                if os.path.exists(full_path):
                    valid_files.append(full_path)
        except ValueError:
            continue

    if not valid_files:
        return jsonify({"status": "error", "message": "Tiedostoja ei löytynyt"}), 404

    lat_ref = 'N' if new_lat >= 0 else 'S'
    lon_ref = 'E' if new_lon >= 0 else 'W'

    try:
        komento = [
            'exiftool', '-overwrite_original',
            f'-GPSLatitude={abs(new_lat)}', f'-GPSLatitudeRef={lat_ref}',
            f'-GPSLongitude={abs(new_lon)}', f'-GPSLongitudeRef={lon_ref}'
        ] + valid_files

        subprocess.run(komento, check=True, capture_output=True, text=True)

        for fpath in valid_files:
            hash_obj = hashlib.md5(fpath.encode()).hexdigest()
            cache_file = os.path.join(CACHE_DIR, f"img_{hash_obj}.json")
            if os.path.exists(cache_file):
                os.remove(cache_file)

        return jsonify({"status": "ok", "message": f"Sijainti tallennettu onnistuneesti {len(valid_files)} kuvaan!"})
    except subprocess.CalledProcessError as e:
        return jsonify({"status": "error", "message": f"ExifTool-virhe: {e.stderr}"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
if __name__ == '__main__':
    # Debianissa portti 9000 on määritetty palveluun
    app.run(host='0.0.0.0', port=9000, debug=False)
