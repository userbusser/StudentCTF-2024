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
$username = $_SESSION['username'];

if ($_SERVER['REQUEST_METHOD'] == 'POST' && isset($_FILES['photo'])) {
    $file_name = $_POST['file_name'];
    $target_dir = "uploads/";
    $target_file = $target_dir . $file_name;
    $uploadOk = 1;
    $imageFileType = strtolower(pathinfo($target_file, PATHINFO_EXTENSION));

    $check = getimagesize($_FILES["photo"]["tmp_name"]);
    if ($check !== false) {
        $uploadOk = 1;
    } else {
        showMessage("File is not an image.", "error");
        $uploadOk = 0;
    }

    if (file_exists($target_file)) {
        showMessage("Sorry, file already exists.", "error");
        $uploadOk = 0;
    }

    if ($_FILES["photo"]["size"] > 1000000) {
        showMessage("Sorry, your file is too large.", "error");
        $uploadOk = 0;
    }

    if ($imageFileType != "jpg" && $imageFileType != "png" && $imageFileType != "jpeg" && $imageFileType != "gif") {
        showMessage("Sorry, only JPG, JPEG, PNG & GIF files are allowed.", "error");
        $uploadOk = 0;
    }

    if ($uploadOk == 0) {
        showMessage("Sorry, your file was not uploaded.", "error");
    } else {
        if (move_uploaded_file($_FILES["photo"]["tmp_name"], $target_file)) {
            $stmt = $pdo->prepare("INSERT INTO photos (user_id, file_path) VALUES (:user_id, :file_path)");
            $stmt->execute(['user_id' => $user_id, 'file_path' => $target_file]);
            showMessage("The file " . htmlspecialchars(basename($_FILES["photo"]["name"])) . " has been uploaded.", "succes");
        } else {
            showMessage("Sorry, there was an error uploading your file.", "error");
        }
    }
}

if ($_SERVER['REQUEST_METHOD'] == 'POST' && isset($_POST['photo_url'])) {
    $photo_url = $_POST['photo_url'];
    $target_dir = "uploads/";

    $file_name = basename(parse_url($photo_url, PHP_URL_PATH));

    $headers = get_headers($photo_url, 1);
    $is_image = isset($headers["Content-Type"]) && strpos($headers["Content-Type"], "image") !== false;

    $allowed_extensions = ['jpg', 'jpeg', 'png', 'gif'];
    $file_extension = strtolower(pathinfo($file_name, PATHINFO_EXTENSION));
    $is_allowed_extension = in_array($file_extension, $allowed_extensions);

    if ($is_image && $is_allowed_extension) {
        $output = [];
        $return_var = 0;
        $wget_command = "wget --quiet --show-progress -P " . escapeshellarg($target_dir) . " " . escapeshellarg($photo_url);

        exec($wget_command, $output, $return_var);

        $downloaded_file = $target_dir . $file_name;

        if ($return_var === 0 && file_exists($downloaded_file) && filesize($downloaded_file) <= 5000000) {
            $stmt = $pdo->prepare("INSERT INTO photos (user_id, file_path) VALUES (:user_id, :file_path)");
            $stmt->execute(['user_id' => $user_id, 'file_path' => $downloaded_file]);
            showMessage("The image from URL has been saved.", 'succes');
        } else {
            showMessage("Sorry, there was an error downloading the image or the image is too large.", "error");
            if (file_exists($downloaded_file)) {
                unlink($downloaded_file);
            }
        }
    } else {
        showMessage("The URL does not point to an image or the file type is not allowed. Only JPG, JPEG, PNG & GIF files are allowed.", 'error');
    }
}
?>

<!DOCTYPE html>
<html>
<head>
    <title>Profile</title>
    <link rel="stylesheet" type="text/css" href="static/style.css">
    <link rel="stylesheet" type="text/css" href="static/message.css">
</head>
<body>
    <div class="profile-container">
        <div class="profile-header" style="margin-bottom: 100px">
            <a href="profile.php" class="fform bbutton" style="margin-bottom: 100px">Profile</a>
        </div>
        <h2>Upload Photo</h2>
        <form action="upload.php" method="post" enctype="multipart/form-data">
            Select image to upload:
            <input type="file" name="photo" id="photo" required>
            <br>
            Enter file name:
            <input type="text" name="file_name" id="file_name" required>
            <br>
            <input type="submit" value="Upload Image" name="submit">
        </form>

        <h2>Upload Photo from URL</h2>
        <form action="upload.php" method="post">
            Enter image URL:
            <input type="text" name="photo_url" required>
            <br>
            <input type="submit" value="Upload from URL">
        </form>
        <div id="messages"></div>
    </div>
</body>
</html>