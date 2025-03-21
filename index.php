<?php
// Ambil data JSON dari file
$json_file = 'events.json'; // Path ke file JSON

// Baca file JSON
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