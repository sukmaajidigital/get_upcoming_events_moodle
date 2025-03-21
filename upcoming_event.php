<?php
session_start();
// Ambil cookie MoodleSession
$cookie = '_ga=GA1.3.2105331365.1740756049; _fbp=fb.2.1740768062945.999206360717923976; _ga_XZM8Q0G9EW=GS1.3.1740768075.1.0.1740768075.0.0.0; __dtsu=4C30174050906003C437B8433E529AD5; _cc_id=d02b7ea88ea0730947954a6b297474f3; _ga_DFRX9T5L0K=GS1.3.1740952728.3.1.1740952867.0.0.0; cf_clearance=j0jSzaURxSmxAuRJ4GlkOKIfRO25pkwXzyYm5FbibNg-1742402480-1.2.1.1-pcDcmHaEsjijthlF57plEwc8n7tock22UPvLgI4I9cUsEMJ5RRgdo_sdr0W1__rsubymc3XQ5pyaz_1O3K7UjTrvCv5TFHHYykIj8KQWFAyo6IioU6EVxHRFd0CiHnbdb3E_dgqaebms31xucvy2QRM0RIAt3B9EuWOsGbaVNVZaUSZZCkEGSIZKkbFkI.XYmJuulcaWLEq4t91SgAcVYkQDIj04tViFwuojYT1IMsJyvUOSwsyOSJF56lE1VTG.6iIniqKUShT7P_yVsfzEf4lApjKnyq.qRAf6aIYKzJy.m0GF1UqEnw0hvPwu2UlYjxzvmDGk1SnWcjOgO0vlhs50UIwjk0W1na6GadHo_ko; MoodleSession=r0vlqj6fg9pbuhokaud72482im';

// Ambil sesskey (HARUS DISAMAKAN dengan sesskey dari halaman Moodle)
$sesskey = 'BWMCAKob22';  // Pastikan ini diambil dari halaman Moodle

// URL endpoint untuk upcoming events
$url = 'https://sunan.umk.ac.id/lib/ajax/service.php?sesskey=' . $sesskey . '&info=core_calendar_get_calendar_upcoming_view';

// Payload data
$data = json_encode([
    [
        'index' => 0,
        'methodname' => 'core_calendar_get_calendar_upcoming_view',
        'args' => []
    ]
]);

// Inisialisasi cURL
$ch = curl_init($url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_HEADER, false);
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
curl_setopt($ch, CURLOPT_COOKIE, $cookie);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Content-Type: application/json',
    'Referer: https://sunan.umk.ac.id/',
    'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
]);

$response = curl_exec($ch);
$http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

// Cek apakah permintaan berhasil
if ($http_code == 200) {
    header('Content-Type: application/json');
    echo $response;
} else {
    echo json_encode(["status" => "error", "message" => "Gagal mengambil data event. Sesi mungkin telah kadaluarsa atau sesskey tidak valid."]);
}
