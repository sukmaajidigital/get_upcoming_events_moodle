<?php
session_start();

// URL Moodle untuk cek sesi (gunakan endpoint yang relevan jika berbeda)
$url = 'https://sunan.umk.ac.id/';

// Ambil cookie sesi dari browser
$cookie = isset($_COOKIE['MoodleSession']) ? 'MoodleSession=' . $_COOKIE['MoodleSession'] : '';

// Inisialisasi cURL
$ch = curl_init($url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_HEADER, false);
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
curl_setopt($ch, CURLOPT_COOKIE, $cookie);

$response = curl_exec($ch);
$http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

// Cek apakah sesi masih valid
if ($http_code == 200) {
    echo json_encode(["status" => "valid", "message" => "Sesi Valid! Anda bisa mengakses event."]);
} else {
    echo json_encode(["status" => "invalid", "message" => "Sesi Tidak Valid! Silakan login terlebih dahulu."]);
}
