<?php
loadEnv(__DIR__ . '/.env');

function loadEnv($filePath)
{
    if (!file_exists($filePath)) {
        die("File .env tidak ditemukan.");
    }

    $lines = file($filePath, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    foreach ($lines as $line) {
        // Abaikan komentar
        if (strpos(trim($line), '#') === 0) {
            continue;
        }

        // Pecah berdasarkan tanda =
        list($key, $value) = explode('=', $line, 2);
        $key = trim($key);
        $value = trim($value);

        // Hapus tanda kutip jika ada
        $value = trim($value, '"');

        // Simpan di variabel environment
        putenv("$key=$value");
        $_ENV[$key] = $value;
    }
}

// Baca token dari .env
$token = getenv('FOONTE_API') ?: $_ENV['FOONTE_API'] ?? null;
$target = getenv('TARGETNUMBER') ?: $_ENV['TARGETNUMBER'] ?? null;


// Debug: Tampilkan token
echo "Token: " . $token . "\n";
echo "Token: " . $target . "\n";

// Baca file events.json
$json_file = 'events.json';
if (file_exists($json_file)) {
    $json_data = file_get_contents($json_file); // Baca isi file
    $data = json_decode($json_data, true); // Decode JSON ke array PHP

    // Pastikan JSON tidak error dan memiliki data events
    if ($data && is_array($data)) {
        $events = $data; // Data langsung berupa array event
    } else {
        die("Data tidak ditemukan atau format JSON tidak valid.");
    }
} else {
    die("File events.json tidak ditemukan.");
}

// Format pesan WhatsApp
$message = "INFO INFO SUNAN KIE:\n\n";
foreach ($events as $event) {
    $message .= "*-------------------------------------------------------*" . "\n";
    $message .= "*INFO*" . "\n";
    $message .= "*" . htmlspecialchars($event['name']) . "*" . "\n";
    $message .= "*-------------------------------------------------------*" . "\n";
    $message .= "*" . htmlspecialchars($event['course']['fullname']) . "*" . "\n";
    $message .= "Tanggal & Waktu: " . $event['formattedtime'] . "\n";
    $message .= "*Link Event:* " . $event['url'] . "\n\n";
    $message .= "\n";
}

// Kirim pesan menggunakan API Fonnte
$curl = curl_init();

curl_setopt_array($curl, array(
    CURLOPT_URL => 'https://api.fonnte.com/send',
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_ENCODING => '',
    CURLOPT_MAXREDIRS => 10,
    CURLOPT_TIMEOUT => 0,
    CURLOPT_FOLLOWLOCATION => true,
    CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
    CURLOPT_CUSTOMREQUEST => 'POST',
    CURLOPT_POSTFIELDS => array(
        'target' => $target, // Ganti dengan nomor tujuan
        'message' => $message,
        'countryCode' => '62',
    ),
    CURLOPT_HTTPHEADER => array(
        'Authorization: ' . $token // Gunakan token API Fonnte
    ),
));

$response = curl_exec($curl);
if (curl_errno($curl)) {
    $error_msg = curl_error($curl);
}
curl_close($curl);

if (isset($error_msg)) {
    echo $error_msg;
}
echo $response;
