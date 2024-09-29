<?php
session_start();
require 'config.php';

function showMessage($message, $type = 'info') {
    echo "<div class='message $type'>$message</div>";
}

if (!isset($_SESSION['user_id'])) {
    header("Location: login.php");
    exit();
}

$user_id = $_SESSION['user_id'];

if ($_SERVER['REQUEST_METHOD'] == 'POST' && isset($_POST['photo_id']) && isset($_POST['new_file_name'])) {
    $photo_id = $_POST['photo_id'];
    $new_file_name = $_POST['new_file_name'];

    $stmt = $pdo->prepare("SELECT file_path FROM photos WHERE id = :photo_id AND user_id = :user_id");
    $stmt->execute(['photo_id' => $photo_id, 'user_id' => $user_id]);
    $photo = $stmt->fetch(PDO::FETCH_ASSOC);

    if ($photo) {
        $old_file_path = $photo['file_path'];
        $target_dir = "uploads/";
        $new_file_path = $target_dir . $new_file_name;

        $imageFileType = strtolower(pathinfo($new_file_path, PATHINFO_EXTENSION));
        if ($imageFileType != "jpg" && $imageFileType != "png" && $imageFileType != "jpeg" && $imageFileType != "gif") {
            showMessage("Sorry, only JPG, JPEG, PNG & GIF files are allowed.", "error");
        } else {
            if (rename($old_file_path, $new_file_path)) {
                $stmt = $pdo->prepare("UPDATE photos SET file_path = :new_file_path WHERE id = :photo_id AND user_id = :user_id");
                $stmt->execute(['new_file_path' => $new_file_path, 'photo_id' => $photo_id, 'user_id' => $user_id]);
                showMessage("File renamed successfully.", "succes");
            } else {
                showMessage("Sorry, there was an error renaming your file.", "error");
            }
        }
    } else {
        showMessage("Photo not found.", "error");
    }
} else {
    showMessage("Invalid request.", "error");
}
?>

<!DOCTYPE html>
<html>
    <link rel="stylesheet" type="text/css" href="static/style.css">
    <link rel="stylesheet" type="text/css" href="static/index_style.css">
    <link rel="stylesheet" type="text/css" href="static/message.css">
</head>
<body>
    <div id="messages"></div>
</body>
</html>