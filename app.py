import requests
from bs4 import BeautifulSoup
import time
import re
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# URL dan data login
login_url = 'https://sunan.umk.ac.id/login/index.php'
dashboard_url = 'https://sunan.umk.ac.id/'
events_url = 'https://sunan.umk.ac.id/lib/ajax/service.php'

# Data login
username = '202253138'
password = 'Ajisukma@mastiktod'

# Setup session dengan retry mechanism
session = requests.Session()
retry = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[500, 502, 503, 504]
)
adapter = HTTPAdapter(max_retries=retry)
session.mount("http://", adapter)
session.mount("https://", adapter)

# Header untuk meniru browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Referer': login_url,
}

# Ambil token CSRF
try:
    response = session.get(login_url, headers=headers, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    token = soup.find('input', {'name': 'logintoken'})['value']
except requests.exceptions.RequestException as e:
    print(f"Gagal mengambil token CSRF: {e}")
    exit()

# Data form login
login_data = {
    'username': username,
    'password': password,
    'logintoken': token
}

# Submit form login
try:
    print("Melakukan login...")
    response = session.post(login_url, data=login_data, headers=headers, timeout=10)
    response.raise_for_status()
    if 'MoodleSession' in session.cookies:
        print("Login berhasil!")
    else:
        print("Login gagal. Periksa username dan password.")
        exit()
except requests.exceptions.RequestException as e:
    print(f"Gagal melakukan login: {e}")
    exit()

# Tunggu beberapa detik untuk menghindari deteksi robot
time.sleep(5)

# Ambil sesskey dari halaman dashboard
try:
    print("Mengambil sesskey...")
    response = session.get(dashboard_url, headers=headers, timeout=10)
    response.raise_for_status()
    sesskey = re.search(r'"sesskey":"(.*?)"', response.text).group(1)
    print(f"Sesskey: {sesskey}")
except requests.exceptions.RequestException as e:
    print(f"Gagal mengambil sesskey: {e}")
    exit()

# Ambil data event
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
    events = response.json()[0]['data']['events']
    print("Data event berhasil diambil!")
except requests.exceptions.RequestException as e:
    print(f"Gagal mengambil data event: {e}")
    exit()

# Tampilkan data event dalam bentuk tabel HTML
html = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daftar Event</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            padding: 20px;
            background-color: #f4f4f4;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
        }
        th, td {
            padding: 10px;
            border: 1px solid #ddd;
            text-align: left;
        }
        th {
            background-color: #007BFF;
            color: white;
        }
        tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        a {
            text-decoration: none;
            color: #007BFF;
        }
    </style>
</head>
<body>
    <h2>Daftar Event</h2>
    <table>
        <tr>
            <th>Nama Event</th>
            <th>Kursus</th>
            <th>Tanggal & Waktu</th>
            <th>Link</th>
        </tr>
"""

for event in events:
    html += f"""
        <tr>
            <td>{event['name']}</td>
            <td>{event['course']['fullname']}</td>
            <td>{event['formattedtime']}</td>
            <td><a href="{event['url']}" target="_blank">Lihat Event</a></td>
        </tr>
    """

html += """
    </table>
</body>
</html>
"""

# Simpan hasil ke file HTML
with open('events.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Data event telah disimpan ke events.html")