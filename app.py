import webbrowser
import requests
from bs4 import BeautifulSoup
import time
import re
import json
import os
import platform
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
import subprocess

# Deteksi sistem operasi
system = platform.system().lower()  # Mengembalikan 'windows', 'linux', atau 'darwin' (macOS

# Muat variabel lingkungan dari file .env
load_dotenv()
# Baca variabel lingkungan
username = os.getenv("DIVUSERNAME")
password = os.getenv("DIVPASSWORD")

print(f"Username: {username}")
print(f"Password: {password}")
# URL Moodle
login_url = f'{os.getenv("MOODLE_URL")}/login/index.php'
test_session_url = f'{os.getenv("MOODLE_URL")}/login/index.php?testsession=17253'
dashboard_url = f'{os.getenv("MOODLE_URL")}/'
events_url = f'{os.getenv("MOODLE_URL")}/lib/ajax/service.php'

# Header agar terlihat seperti browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Referer': login_url,
}

# **Gunakan Selenium untuk login dan mendapatkan semua cookie**
print("Menggunakan Selenium untuk login...")

# Tentukan path ke ChromeDriver berdasarkan sistem operasi
if system == 'windows':
    chrome_driver_path = 'chromedriver-win64/chromedriver.exe'
elif system == 'darwin':  # macOS
    chrome_driver_path = 'chromedriver-mac-arm64/chromedriver'
elif system == 'linux':
    chrome_driver_path = 'chromedriver-linux64/chromedriver'
else:
    raise Exception(f"Sistem operasi tidak didukung: {system}")

# Debugging: Cetak path ke ChromeDriver
print(f"Sistem operasi: {system}")
print(f"Path ke ChromeDriver: {chrome_driver_path}")

# Konfigurasi ChromeDriver
service = Service(chrome_driver_path)
options = webdriver.ChromeOptions()

# Hapus mode headless untuk melihat browser
# options.add_argument("--headless")  # Menjalankan browser di latar belakang
options.add_argument("--disable-gpu")  # Nonaktifkan GPU (diperlukan di beberapa sistem)
options.add_argument("--no-sandbox")  # Nonaktifkan sandbox (diperlukan di beberapa sistem)
options.add_argument("--disable-dev-shm-usage")  # Mengatasi masalah memori di Linux
options.add_argument("--window-size=500,500")  # Atur ukuran window

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

username.send_keys(os.getenv("DIVUSERNAME"))  # Ganti dengan username Anda
print("typing password....",os.getenv("DIVUSERNAME"))
password.send_keys(os.getenv("DIVPASSWORD"))  # Ganti dengan password Anda
print("checklist chaptcha...",os.getenv("DIVPASSWORD"))

# Klik tombol login
chaptcha_button.click()
time.sleep(20)  # Beri waktu 30 detik untuk menyelesaikan CAPTCHA
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

# Simpan cookie ke file JSON (opsional, bisa dihapus jika tidak diperlukan)
with open("cookies.json", "w", encoding="utf-8") as f:
    json.dump(cookies, f, indent=4, ensure_ascii=False)

print("Cookie telah disimpan ke cookies.json")

# Tutup browser
driver.quit()

# Inisialisasi session baru
session = requests.Session()

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


# Path ke script PHP
php_script_path = "send_whatsapp.php"

# Jalankan script PHP menggunakan subprocess
try:
    # Jalankan perintah PHP
    result = subprocess.run(
        ["php", php_script_path],  # Perintah untuk menjalankan PHP
        capture_output=True,        # Tangkap output dan error
        text=True                  # Output sebagai string (bukan bytes)
    )

    # Cetak output dari script PHP
    print("Output dari script PHP:")
    print(result.stdout)

    # Cetak error jika ada
    if result.stderr:
        print("Error dari script PHP:")
        print(result.stderr)

except FileNotFoundError:
    print("PHP tidak ditemukan. Pastikan PHP terinstal dan dapat diakses dari PATH.")
except Exception as e:
    print(f"Terjadi kesalahan saat menjalankan script PHP: {e}")