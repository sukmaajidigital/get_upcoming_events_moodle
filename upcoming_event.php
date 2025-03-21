<?php
session_start();

// Ambil cookie dari browser
$cookie = '_ga=GA1.3.2105331365.1740756049; _fbp=fb.2.1740768062945.999206360717923976; _ga_XZM8Q0G9EW=GS1.3.1740768075.1.0.1740768075.0.0.0; __dtsu=4C30174050906003C437B8433E529AD5; _cc_id=d02b7ea88ea0730947954a6b297474f3; _ga_DFRX9T5L0K=GS1.3.1740952728.3.1.1740952867.0.0.0; cf_clearance=j0jSzaURxSmxAuRJ4GlkOKIfRO25pkwXzyYm5FbibNg-1742402480-1.2.1.1-pcDcmHaEsjijthlF57plEwc8n7tock22UPvLgI4I9cUsEMJ5RRgdo_sdr0W1__rsubymc3XQ5pyaz_1O3K7UjTrvCv5TFHHYykIj8KQWFAyo6IioU6EVxHRFd0CiHnbdb3E_dgqaebms31xucvy2QRM0RIAt3B9EuWOsGbaVNVZaUSZZCkEGSIZKkbFkI.XYmJuulcaWLEq4t91SgAcVYkQDIj04tViFwuojYT1IMsJyvUOSwsyOSJF56lE1VTG.6iIniqKUShT7P_yVsfzEf4lApjKnyq.qRAf6aIYKzJy.m0GF1UqEnw0hvPwu2UlYjxzvmDGk1SnWcjOgO0vlhs50UIwjk0W1na6GadHo_ko; MoodleSession=r0vlqj6fg9pbuhokaud72482im';

// Ambil sesskey dari halaman Moodle
$dashboard_url = 'https://sunan.umk.ac.id/'; // Halaman dashboard Moodle

$ch = curl_init($dashboard_url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_HEADER, false);
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
curl_setopt($ch, CURLOPT_COOKIE, $cookie);
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
]);

$response = curl_exec($ch);
curl_close($ch);

// Cari sesskey di HTML
preg_match('/"sesskey":"(.*?)"/', $response, $matches);
if (!isset($matches[1])) {
    echo json_encode(["status" => "error", "message" => "Gagal mengambil sesskey. Pastikan sudah login di browser."]);
    exit;
}

$sesskey = $matches[1];

// URL untuk upcoming events
$url = 'https://sunan.umk.ac.id/lib/ajax/service.php?sesskey=' . $sesskey . '&info=core_calendar_get_calendar_upcoming_view';

// Payload data
$data = json_encode([
    [
        'index' => 0,
        'methodname' => 'core_calendar_get_calendar_upcoming_view',
        'args' => []
    ]
]);

// Ambil upcoming events
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
    $response_data = json_decode($response, true);
    if (isset($response_data[0]['error']) && !$response_data[0]['error']) {
        $events = $response_data[0]['data']['events'];
    } else {
        die("Data tidak ditemukan atau terdapat error dalam response.");
    }
} else {
    echo json_encode(["status" => "error", "message" => "Gagal mengambil data event. Sesi mungkin telah kadaluarsa atau sesskey tidak valid."]);
    exit;
}
?>
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

        th,
        td {
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
        <?php foreach ($events as $event): ?>
            <tr>
                <td><?php echo htmlspecialchars($event['name']); ?></td>
                <td><?php echo htmlspecialchars($event['course']['fullname']); ?></td>
                <td><?php echo $event['formattedtime']; ?></td>
                <td><a href="<?php echo $event['url']; ?>" target="_blank">Lihat Event</a></td>
            </tr>
        <?php endforeach; ?>
    </table>
</body>

</html>