<?php
session_start();
require 'config.php';

function showMessage($message, $type = 'info') {
    echo "<div class='message $type'>$message</div>";
}

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $username = $_POST['username'];
    $password = $_POST['password'];

    $stmt = $pdo->prepare("SELECT id, password FROM users WHERE username = :username");
    $stmt->execute(['username' => $username]);
    $user = $stmt->fetch(PDO::FETCH_ASSOC);

    if ($user && password_verify($password, $user['password'])) {
        $_SESSION['user_id'] = $user['id'];
        $_SESSION['username'] = $username;
        
        header("Location: profile.php");
        exit();
    } else {
        showMessage("Invalid username or password", "error");
    }
}
?>

<!DOCTYPE html>
<html>
<head>
    <title>Login</title>
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
        <h2>Login</h2>
        <form method="POST" action="">
            Username: <input type="text" name="username" required>
            Password: <input type="password" name="password" required>
            <button type="submit">Login</button>
        </form>
    </div>
    <div id="messages"></div>
</body>
</html>