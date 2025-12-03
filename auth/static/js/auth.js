/* LOGIN JS */ 
if (data.status === "success") {
    msg.style.color = "green";
    msg.innerHTML = "Login Success! Redirecting...";

    // Save token
    localStorage.setItem("access_token", data.token);

    // Redirect to profile page
    setTimeout(() => {
        window.location.href = "profile.html";
    }, 1000);
}

/* PROFILE JS */ 
async function loadProfile() {
    const token = localStorage.getItem("access_token");

    if (!token) {
        window.location.href = "/";
        return;
    }

    let response = await fetch("/profile", {
        method: "GET",
        headers: {
            "Authorization": "Bearer " + token
        }
    });

    let data = await response.json();

    if (data.status === "success") {
        document.getElementById("username").textContent = data.user;
    } else {
        window.location.href = "/profile_page";
    }
}

loadProfile();

/* BASE JS */
async function login() {
    const user_name = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    let response = await fetch("http://127.0.0.1:5000/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: `user_name=${encodeURIComponent(user_name)}&password=${encodeURIComponent(password)}`
    });

    let data = await response.json();

    const msg = document.getElementById("message");

    if (data.status === "success") {
        msg.style.color = "green";
        msg.innerHTML = "Login Success! Token:<br><small>" + data.token + "</small>";

        // store token for later use
        localStorage.setItem("access_token", data.token);
    } else {
        msg.style.color = "red";
        msg.textContent = "Invalid username or password";
    }
}