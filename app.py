import requests
from bs4 import BeautifulSoup
import time
import re

# URL dan data login
login_url = 'https://sunan.umk.ac.id/login/index.php'
dashboard_url = 'https://sunan.umk.ac.id/'
events_url = 'https://sunan.umk.ac.id/lib/ajax/service.php'

# Data login
username = '202253138'
password = 'Ajisukma@mastiktod'

# Session untuk menjaga cookie
session = requests.Session()

# Header untuk meniru browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
}

# Ambil token CSRF dan CAPTCHA (jika ada)
response = session.get(login_url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')
token = soup.find('input', {'name': 'logintoken'})['value']

# Data form login
login_data = {
    'username': username,
    'password': password,
    'logintoken': token
}

# Submit form login
print("Melakukan login...")
response = session.post(login_url, data=login_data, headers=headers)

# Tunggu beberapa detik untuk menghindari deteksi robot
time.sleep(5)

# Cek apakah login berhasil
if 'MoodleSession' in session.cookies:
    print("Login berhasil!")
else:
    print("Login gagal. Periksa username dan password.")
    exit()

# Ambil sesskey dari halaman dashboard
print("Mengambil sesskey...")
response = session.get(dashboard_url, headers=headers)
sesskey = re.search(r'"sesskey":"(.*?)"', response.text).group(1)

# Ambil data event
print("Mengambil data event...")
payload = [
    {
        'index': 0,
        'methodname': 'core_calendar_get_calendar_upcoming_view',
        'args': {}
    }
]

response = session.post(
    f'{events_url}?sesskey={sesskey}&info=core_calendar_get_calendar_upcoming_view',
    json=payload,
    headers=headers
)

# Cek apakah data event berhasil diambil
if response.status_code == 200:
    events = response.json()[0]['data']['events']
    print("Data event berhasil diambil!")
else:
    print("Gagal mengambil data event.")
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