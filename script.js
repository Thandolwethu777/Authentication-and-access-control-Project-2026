
document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("loginForm");
    const loginMessage = document.getElementById("loginMessage");
    const loginButton = document.querySelector(".login-button");

    loginForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const username = document.getElementById("username").value.trim();
        const password = document.getElementById("password").value;

        if (username === "" || password === "") {
            loginMessage.textContent =
                "Please enter your username and password.";
            loginMessage.style.color = "red";
            return;
        }

        loginMessage.textContent = "Signing in...";
        loginMessage.style.color = "green";
        loginButton.disabled = true;

        try {
            const response = await fetch("/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    username: username,
                    password: password
                })
            });

            const result = await response.json();

            if (!response.ok) {
                loginMessage.textContent =
                    result.error || "Login failed. Please try again.";
                loginMessage.style.color = "red";
                return;
            }

            loginMessage.textContent = "Login successful!";
            loginMessage.style.color = "green";

            window.location.href = "/dashboard.html";

        } catch (error) {
            loginMessage.textContent =
                "Could not connect to the server. Please try again.";
            loginMessage.style.color = "red";
        } finally {
            loginButton.disabled = false;
            loginButton.innerHTML =
                '<span>Sign In</span><span class="arrow">→</span>';
        }
    });
});
