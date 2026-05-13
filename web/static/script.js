// Pump Narrative Scanner - Dashboard Script

document.addEventListener("DOMContentLoaded", function () {
    const tokenList = document.getElementById("token-list");
    const resultsCount = document.getElementById("results-count");
    const searchInput = document.getElementById("search-input");
    const minScoreInput = document.getElementById("min-score-input");
    const riskSelect = document.getElementById("risk-select");
    const applyBtn = document.getElementById("apply-filters");
    const clearBtn = document.getElementById("clear-filters");

    // Load tokens on page load
    loadTokens();

    // Filter button events
    applyBtn.addEventListener("click", loadTokens);
    clearBtn.addEventListener("click", function () {
        searchInput.value = "";
        minScoreInput.value = "";
        riskSelect.value = "";
        loadTokens();
    });

    // Enter key triggers search
    searchInput.addEventListener("keypress", function (e) {
        if (e.key === "Enter") loadTokens();
    });
    minScoreInput.addEventListener("keypress", function (e) {
        if (e.key === "Enter") loadTokens();
    });

    function loadTokens() {
        tokenList.innerHTML = '<div class="loading">Loading tokens...</div>';

        // Build query params
        const params = new URLSearchParams();
        const search = searchInput.value.trim();
        const minScore = minScoreInput.value.trim();
        const risk = riskSelect.value;

        if (search) params.set("search", search);
        if (minScore) params.set("min_score", minScore);
        if (risk) params.set("risk_level", risk);

        const url = "/api/tokens" + (params.toString() ? "?" + params.toString() : "");

        fetch(url)
            .then(response => response.json())
            .then(data => {
                renderTokens(data.tokens);
                resultsCount.textContent = `${data.count} token${data.count !== 1 ? "s" : ""} found`;
            })
            .catch(err => {
                tokenList.innerHTML = '<div class="empty-state">Error loading tokens.</div>';
                resultsCount.textContent = "Error";
                console.error("Failed to load tokens:", err);
            });
    }

    function renderTokens(tokens) {
        if (!tokens || tokens.length === 0) {
            tokenList.innerHTML = '<div class="empty-state">No tokens match the current filters.</div>';
            return;
        }

        tokenList.innerHTML = tokens.map(token => createTokenCard(token)).join("");
    }

    function createTokenCard(token) {
        const riskClass = (token.risk_level || "medium").toLowerCase();
        const finalScore = (token.final_score || 0).toFixed(4);
        const hantaScore = (token.hantavirus_like_score || 0).toFixed(4);
        const narrativeScore = (token.narrative_score || 0).toFixed(4);
        const momentumScore = (token.momentum_score || 0).toFixed(4);
        const socialScore = (token.social_score || 0).toFixed(4);
        const safetyScore = (token.safety_score || 0).toFixed(4);
        const freshnessScore = (token.freshness_score || 0).toFixed(4);

        const scoreClass = getScoreClass(token.final_score);
        const hantaClass = getHantaScoreClass(token.hantavirus_like_score);

        const pumpUrl = token.pump_url || "";
        const openButton = pumpUrl
            ? `<a href="${escapeHtml(pumpUrl)}" target="_blank" rel="noopener noreferrer" class="btn-open">Open Token</a>`
            : "";

        return `
        <div class="token-card risk-${riskClass}">
            <div class="token-header">
                <div>
                    <span class="token-name">${escapeHtml(token.name || "Unknown")}</span>
                    <span class="token-symbol">${escapeHtml(token.symbol || "???")}</span>
                </div>
                <span class="risk-badge ${riskClass}">${riskClass} risk</span>
            </div>

            <div class="token-details">
                <div class="detail-item">
                    <span class="detail-label">Narrative</span>
                    <span class="narrative-badge ${token.narrative_category || ""}">${escapeHtml(token.narrative_category || "unknown")}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Final Score</span>
                    <span class="detail-value score ${scoreClass}">${finalScore}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Hantavirus-like</span>
                    <span class="detail-value score ${hantaClass}">${hantaScore}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Narrative Score</span>
                    <span class="detail-value score">${narrativeScore}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Momentum</span>
                    <span class="detail-value score">${momentumScore}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Social</span>
                    <span class="detail-value score">${socialScore}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Safety</span>
                    <span class="detail-value score">${safetyScore}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Freshness</span>
                    <span class="detail-value score">${freshnessScore}</span>
                </div>
            </div>

            <div class="detail-item" style="margin-bottom: 10px;">
                <span class="detail-label">Mint Address</span>
                <span class="mint-address">${escapeHtml(token.mint_address || "")}</span>
            </div>

            <div class="token-reason">${escapeHtml(token.reason || "No analysis available.")}</div>

            <div class="token-footer">
                ${openButton}
            </div>
        </div>`;
    }

    function getScoreClass(score) {
        if (score >= 0.7) return "score-low";     // High final score = good (green)
        if (score >= 0.5) return "score-medium";  // Medium = caution (orange)
        return "score-high";                       // Low final score = concern (red)
    }

    function getHantaScoreClass(score) {
        if (score >= 0.6) return "score-high";    // High hanta = danger (red)
        if (score >= 0.35) return "score-medium"; // Medium = caution (orange)
        return "score-low";                        // Low hanta = safer (green)
    }

    function escapeHtml(str) {
        if (!str) return "";
        const div = document.createElement("div");
        div.textContent = str;
        return div.innerHTML;
    }
});
