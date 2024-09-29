<?php
require 'config.php';

function showMessage($message, $type = 'info') {
    echo "<div class='message $type'>$message</div>";
}

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $username = $_POST['username'];
    $password = password_hash($_POST['password'], PASSWORD_DEFAULT);

    $stmt = $pdo->prepare("SELECT id FROM users WHERE username = :username");
    $stmt->execute(['username' => $username]);
    if ($stmt->rowCount() > 0) {
        showMessage("Username already taken", "error");
    } else {
        $stmt = $pdo->prepare("INSERT INTO users (username, password) VALUES (:username, :password)");
        if ($stmt->execute(['username' => $username, 'password' => $password])) {
            header("Location: login.php");
            exit();
        } else {
            showMessage("Registration failed.", "error");
        }
    }
}
?>

<!DOCTYPE html>
<html>
<head>
    <title>Register</title>
    <link rel="stylesheet" type="text/css" href="static/style.css">
    <link rel="stylesheet" type="text/css" href="static/index_style.css">
    <link rel="stylesheet" type="text/css" href="static/message.css">
</head>
<body>
    <nav>
        <ul>
            <li><a href="login.php">Login</a></li>
            <li><a href="register.php">Register</a></li>
        </ul>
    </nav>
    <div class="login-register-container">
        <h2>Register</h2>
        <form method="POST" action="">
            Username: <input type="text" name="username" required>
            Password: <input type="password" name="password" required>
            <button type="submit">Register</button>
        </form>
    </div>
    <div id="messages"></div>
</body>
</html>