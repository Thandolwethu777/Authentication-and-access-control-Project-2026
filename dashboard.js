
document.addEventListener("DOMContentLoaded", function () {
    const logoutButton = document.getElementById("logoutButton");

    if (logoutButton) {
        logoutButton.addEventListener("click", async function (event) {
            event.preventDefault();

            try {
                const response = await fetch("/logout", {
                    method: "POST"
                });

                if (response.ok) {
                    window.location.href = "/";
                } else {
                    alert("Could not sign out. Please try again.");
                }
            } catch (error) {
                alert("Could not connect to the server. Please try again.");
            }
        });
    }
});
