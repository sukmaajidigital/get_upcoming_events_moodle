@echo off
echo Menginstal dependensi Python...
pip install -r requirements.txt

echo Memeriksa ChromeDriver...
set CHROME_DRIVER_PATH=chromedriver-win64\chromedriver.exe
if not exist %CHROME_DRIVER_PATH% (
    echo ChromeDriver tidak ditemukan. Silakan unduh dari https://sites.google.com/chromium.org/driver/
    pause
    exit
)

echo Instalasi selesai. Jalankan skrip Python Anda.
pause