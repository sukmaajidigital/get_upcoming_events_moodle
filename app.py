import webbrowser
import requests
from bs4 import BeautifulSoup
import time
import re
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

# URL Moodle
login_url = 'https://sunan.umk.ac.id/login/index.php'
test_session_url = 'https://sunan.umk.ac.id/login/index.php?testsession=17253'
dashboard_url = 'https://sunan.umk.ac.id/'
events_url = 'https://sunan.umk.ac.id/lib/ajax/service.php'

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
    # **Gunakan Selenium untuk login dan mendapatkan semua cookie**
    print("Menggunakan Selenium untuk login...")

    # Path ke ChromeDriver (ganti dengan path Anda)
    chrome_driver_path = "chromedriver-win64/chromedriver.exe"  # Ganti dengan path ke chromedriver Anda

    # Konfigurasi ChromeDriver
    service = Service(chrome_driver_path)
    options = webdriver.ChromeOptions()

    # Hapus mode headless untuk melihat browser
    # options.add_argument("--headless")  # Hapus baris ini untuk melihat browser
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    # Inisialisasi WebDriver
    driver = webdriver.Chrome(service=service, options=options)

    # Buka halaman login
    driver.get(login_url)
    time.sleep(3)  # Tunggu halaman sepenuhnya dimuat

    # Isi form login
    username = driver.find_element(By.NAME, "username")
    password = driver.find_element(By.NAME, "password")
    login_button = driver.find_element(By.ID, "loginbtn")
    chaptcha_button = driver.find_element(By.CLASS_NAME, "g-recaptcha")

    username.send_keys("202253138")  # Ganti dengan username Anda
    print("typing password....")
    password.send_keys("Ajisukma@mastiktod")  # Ganti dengan password Anda
    print("checklist chaptcha...")

    # Klik tombol login
    chaptcha_button.click()
    time.sleep(2)  # Beri waktu 30 detik untuk menyelesaikan CAPTCHA
    print("checklist chaptcha DONE")
    login_button.click()
    print("redirect to dashboard...")
    # Tunggu hingga login selesai dan redirect ke dashboard
    time.sleep(5)
    # Buka dashboard untuk memastikan semua cookie diatur
    driver.get(dashboard_url)
    time.sleep(5)

    # Ambil semua cookie
    print("get all cookies...")
    cookies = driver.get_cookies()
    print("Semua cookie yang diterima:", cookies)

    # Simpan cookie ke file JSON
    with open("cookies.json", "w", encoding="utf-8") as f:
        json.dump(cookies, f, indent=4, ensure_ascii=False)

    print("Cookie telah disimpan ke cookies.json")

    # Tutup browser
    driver.quit()

    # Muat cookie dari file JSON
    with open("cookies.json", "r", encoding="utf-8") as f:
        cookies = json.load(f)

    # Tambahkan cookie ke sesi requests
    for cookie in cookies:
        session.cookies.set(cookie["name"], cookie["value"], domain=cookie["domain"], path=cookie["path"])

    # Ambil sesskey dari halaman dashboard
    try:
        print("Mengakses dashboard untuk mengambil sesskey...")
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
        print(f"Gagal mengakses dashboard: {e}")
        exit()

    # Simpan sesi ke file JSON
    session_data = {
        "sesskey": sesskey,
        "cookies": {cookie["name"]: cookie["value"] for cookie in cookies}  # Simpan semua cookie
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

# Path ke file index.php (ganti dengan path yang sesuai)
index_file_path = "localhost/notif_sunan/index.php"

chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"  # Contoh path di Windows

# Daftarkan Chrome sebagai browser
webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))

# Buka file index.php di Chrome
webbrowser.get('chrome').open(index_file_path)