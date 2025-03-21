import requests
from bs4 import BeautifulSoup
import time
import re
import json
import os

# URL Moodle
login_url = 'https://sunan.umk.ac.id/login/index.php'
dashboard_url = 'https://sunan.umk.ac.id/'
events_url = 'https://sunan.umk.ac.id/lib/ajax/service.py'

# File penyimpanan session
session_file = "session.json"

# **Coba muat sesi dari file JSON jika ada**
session = requests.Session()

def load_session():
    if os.path.exists(session_file):
        with open(session_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def save_session(data):
    with open(session_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# Header agar terlihat seperti browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Referer': login_url,
}

# **Jika session.json tersedia, gunakan kembali**
session_data = load_session()
if session_data:
    print("Memuat sesi dari file JSON...")
    sesskey = session_data.get("sesskey")
    
    # **Tambahkan semua cookie ke session**
    cookies = session_data.get("cookies", {})
    for key, value in cookies.items():
        session.cookies.set(key, value)
else:
    # **Minta username & password jika tidak ada sesi tersimpan**
    username = '202253138'
    password = 'Ajisukma@mastiktod'

    # Ambil token CSRF
    try:
        response = session.get(login_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        token_elem = soup.find('input', {'name': 'logintoken'})

        if token_elem:
            token = token_elem['value']
            print(f"Token CSRF: {token}")
        else:
            print("Gagal menemukan token CSRF.")
            exit()

    except requests.exceptions.RequestException as e:
        print(f"Gagal mengambil token CSRF: {e}")
        exit()

    # Data login
    login_data = {
        'username': username,
        'password': password,
        'logintoken': token
    }

    # Kirim form login
    try:
        print("Melakukan login...")
        response = session.post(login_url, data=login_data, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Simpan semua cookie setelah login
        cookies = session.cookies.get_dict()
        print("Cookie setelah login:", cookies)

        if 'MoodleSession' in cookies:
            print("Login berhasil!")
        else:
            print("Login gagal. Periksa username dan password.")
            exit()

    except requests.exceptions.RequestException as e:
        print(f"Gagal melakukan login: {e}")
        exit()

    # Tunggu untuk menghindari deteksi robot
    time.sleep(3)

    # Ambil sesskey dari halaman dashboard
    try:
        print("Mengambil sesskey...")
        response = session.get(dashboard_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        sesskey_match = re.search(r'"sesskey":"(.*?)"', response.text)
        if sesskey_match:
            sesskey = sesskey_match.group(1)
            print(f"Sesskey: {sesskey}")
        else:
            print("Sesskey tidak ditemukan. Pastikan sudah login.")
            exit()
    except requests.exceptions.RequestException as e:
        print(f"Gagal mengambil sesskey: {e}")
        exit()

    # Simpan sesi ke file JSON
    session_data = {
        "sesskey": sesskey,
        "cookies": session.cookies.get_dict()  # Simpan semua cookie
    }
    save_session(session_data)

# Ambil data event dengan semua cookie yang tersimpan
payload = [
    {
        'index': 0,
        'methodname': 'core_calendar_get_calendar_upcoming_view',
        'args': {}
    }
]

try:
    print("Mengambil data event...")
    response = session.post(
        f'{events_url}?sesskey={sesskey}&info=core_calendar_get_calendar_upcoming_view',
        json=payload,
        headers=headers,
        timeout=10
    )
    response.raise_for_status()
    
    # Coba parsing JSON
    try:
        response_data = response.json()
    except json.JSONDecodeError:
        print("Respons server bukan JSON yang valid.")
        print("Respons server:", response.text)
        exit()
    
    # Periksa apakah ada error dalam respons
    if isinstance(response_data, list) and response_data:
        if 'error' in response_data[0] and response_data[0]['error']:
            print(f"Error dari server: {response_data[0]['error']}")
            exit()
        elif 'data' in response_data[0] and 'events' in response_data[0]['data']:
            events = response_data[0]['data']['events']
            print("Data event berhasil diambil!")
        else:
            print("Struktur respons tidak valid. Data event tidak ditemukan.")
            print("Respons server:", response_data)
            exit()
    else:
        print("Respons server tidak valid.")
        print("Respons server:", response_data)
        exit()

except requests.exceptions.RequestException as e:
    print(f"Gagal mengambil data event: {e}")
    exit()

# Simpan event ke JSON
with open("events.json", "w", encoding="utf-8") as f:
    json.dump(events, f, indent=4, ensure_ascii=False)

print("Data event telah disimpan ke events.json")