<?php
session_start();
require 'config.php';

if (!isset($_SESSION['user_id'])) {
    header("Location: login.php");
    exit();
}

$user_id = $_SESSION['user_id'];
$username = $_SESSION['username'];

$stmt = $pdo->prepare("SELECT id, file_path FROM photos WHERE user_id = :user_id");
$stmt->execute(['user_id' => $user_id]);
$photos = $stmt->fetchAll(PDO::FETCH_ASSOC);

foreach ($photos as $photo) {
    if (!file_exists($photo['file_path'])) {
        $deleteStmt = $pdo->prepare("DELETE FROM photos WHERE id = :id");
        $deleteStmt->execute(['id' => $photo['id']]);
    }
}

$stmt->execute(['user_id' => $user_id]);
$photos = $stmt->fetchAll(PDO::FETCH_ASSOC);
?>

<!DOCTYPE html>
<html>
<head>
    <title>Profile</title>
    <link rel="stylesheet" type="text/css" href="static/style.css">
</head>
<body>
    <div class="profile-container">
        <div class="profile-header">
            <h1>Welcome, <?php echo htmlspecialchars($username); ?>!</h1>
            <a href="upload.php" class="fform bbutton">Upload</a>
            <a href="logout.php" class="fform bbutton">Logout</a>
        </div>

        <h2 style="text-align: center">Photo Gallery</h2>
        <?php if ($photos): ?>
            <div class="gallery">
                <?php foreach ($photos as $photo): ?>
                    <div class="photo">
                        <img src="<?php echo htmlspecialchars($photo['file_path']); ?>" alt="Photo" style="width:100px;height:100px;">
                        <form action="edit_photo.php" method="post">
                            <input type="hidden" name="photo_id" value="<?php echo htmlspecialchars($photo['id']); ?>">
                            <input type="text" name="new_file_name" placeholder="New file name">
                            <button type="submit">Rename</button>
                        </form>
                    </div>
                <?php endforeach; ?>
            </div>
        <?php else: ?>
            <p style="text-align: center">No photos uploaded yet.</p>
        <?php endif; ?>
    </div>
</body>
</html>