document.addEventListener("DOMContentLoaded", function () {

    const loginForm = document.getElementById("loginForm");
    const loginMessage = document.getElementById("loginMessage");
    const loginButton = document.querySelector(".login-button");

    loginForm.addEventListener("submit", function (event) {

        // Prevent the browser from submitting the form normally
        event.preventDefault();

        const username = document.getElementById("username").value.trim();
        const password = document.getElementById("password").value.trim();

        // Check that both fields have something in them
        if (username === "" || password === "") {

            loginMessage.textContent =
                "Please enter your username and password.";

            loginMessage.style.color = "red";

            return;
        }

        // Show login message
        loginMessage.textContent = "Signing in...";

        loginMessage.style.color = "green";

        // Change button
        loginButton.disabled = true;

        loginButton.innerHTML =
            '<span>Signing in...</span><span class="arrow">→</span>';


        // Open dashboard
        setTimeout(function () {

            window.location.href = "dashboard.html";

        }, 800);

    });

});