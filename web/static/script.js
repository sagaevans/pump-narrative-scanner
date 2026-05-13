// Pump Narrative Scanner - Dashboard Script

document.addEventListener("DOMContentLoaded", function () {
    console.log("Pump Narrative Scanner dashboard loaded.");

    // Health check on load
    fetch("/api/health")
        .then(response => response.json())
        .then(data => {
            console.log("API status:", data.status);
        })
        .catch(err => {
            console.error("API health check failed:", err);
        });
});
