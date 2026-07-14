const API_URL = "https://lucknow-house-price-api.onrender.com";

const form = document.getElementById("predictionForm");
const resultSection = document.getElementById("resultSection");
const predictedPrice = document.getElementById("predictedPrice");
const ciLow = document.getElementById("ciLow");
const ciHigh = document.getElementById("ciHigh");
const modelUsed = document.getElementById("modelUsed");
const loadingSpinner = document.getElementById("loadingSpinner");
const predictBtn = document.getElementById("predictBtn");
const formError = document.getElementById("formError");
const formErrorMessage = document.getElementById("formErrorMessage");

const FIELD_RULES = {
    area: { min: 200, max: 30000, label: "Living Area (sq ft)" },
    bedrooms: { min: 0, max: 10, label: "Bedrooms" },
    bathrooms: { min: 0, max: 10, label: "Bathrooms" },
    year_built: { min: 1850, max: 2026, label: "Year Built" },
};

const CACHE_KEY = "shpp_metrics_cache";
const CACHE_TTL = 24 * 60 * 60 * 1000;

let serverAwake = false;

function getCachedMetrics() {
    try {
        const raw = localStorage.getItem(CACHE_KEY);
        if (!raw) return null;
        const cached = JSON.parse(raw);
        if (Date.now() - cached.timestamp > CACHE_TTL) return null;
        return cached.data;
    } catch {
        return null;
    }
}

function setCachedMetrics(data) {
    try {
        localStorage.setItem(CACHE_KEY, JSON.stringify({
            timestamp: Date.now(),
            data: data,
        }));
    } catch {}
}

function validateField(id) {
    const el = document.getElementById(id);
    const errorEl = document.getElementById("error-" + id);
    const rules = FIELD_RULES[id];
    if (!rules) return true;
    const val = parseFloat(el.value);
    if (isNaN(val) || el.value.trim() === "") {
        errorEl.textContent = rules.label + " is required";
        el.classList.add("input-error");
        return false;
    }
    if (val < rules.min || val > rules.max) {
        errorEl.textContent = rules.label + " must be between " + rules.min + " and " + rules.max;
        el.classList.add("input-error");
        return false;
    }
    errorEl.textContent = "";
    el.classList.remove("input-error");
    return true;
}

function clearFieldErrors() {
    for (const id of Object.keys(FIELD_RULES)) {
        const el = document.getElementById(id);
        const errorEl = document.getElementById("error-" + id);
        if (el) el.classList.remove("input-error");
        if (errorEl) errorEl.textContent = "";
    }
}

function setServerStatus(text, state) {
    const statusEl = document.getElementById("serverStatus");
    if (!statusEl) return;
    statusEl.textContent = text;
    statusEl.className = "server-status " + state;
    if (state === "ready") {
        setTimeout(() => statusEl.classList.add("fade-out"), 3000);
    }
}

for (const id of Object.keys(FIELD_RULES)) {
    document.getElementById(id)?.addEventListener("blur", () => validateField(id));
}

form.addEventListener("submit", async (e) => {
    e.preventDefault();
    formError.classList.add("hidden");
    clearFieldErrors();
    let valid = true;
    for (const id of Object.keys(FIELD_RULES)) {
        if (!validateField(id)) valid = false;
    }
    if (!valid) return;

    predictBtn.disabled = true;
    loadingSpinner.classList.remove("hidden");
    document.querySelector("#loadingSpinner p").textContent = serverAwake
        ? "Predicting..."
        : "Waking up server & predicting...";
    resultSection.classList.add("hidden");

    const data = {
        area: Number(document.getElementById("area").value),
        bedrooms: Number(document.getElementById("bedrooms").value),
        bathrooms: Number(document.getElementById("bathrooms").value),
        overall_qual: Number(document.getElementById("overall_qual").value),
        year_built: Number(document.getElementById("year_built").value),
        has_pool: document.getElementById("has_pool").value,
        has_garage: document.getElementById("has_garage").value,
        has_ac: document.getElementById("has_ac").value,
    };

    try {
        const response = await fetchWithRetry(API_URL + "/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        });

        const result = await response.json();
        if (!response.ok) {
            if (result.details && Array.isArray(result.details)) {
                throw new Error(result.details.map(d => d.message).join(". "));
            }
            throw new Error(result.error || "Prediction failed");
        }

        serverAwake = true;
        setServerStatus("Server ready", "ready");

        predictedPrice.textContent = Number(result.predicted_price).toLocaleString("en-US", {
            maximumFractionDigits: 0,
        });
        ciLow.textContent = Number(result.confidence_interval.low).toLocaleString("en-US", {
            maximumFractionDigits: 0,
        });
        ciHigh.textContent = Number(result.confidence_interval.high).toLocaleString("en-US", {
            maximumFractionDigits: 0,
        });
        modelUsed.textContent = result.model_used;
        resultSection.classList.remove("hidden");
        resultSection.scrollIntoView({ behavior: "smooth", block: "center" });
    } catch (error) {
        formErrorMessage.textContent = error.message || "Server is starting up. Please try again in 30 seconds.";
        formError.classList.remove("hidden");
    } finally {
        predictBtn.disabled = false;
        loadingSpinner.classList.add("hidden");
    }
});

function resetForm() {
    form.reset();
    resultSection.classList.add("hidden");
    formError.classList.add("hidden");
    clearFieldErrors();
    window.scrollTo({ top: 0, behavior: "smooth" });
}

function renderComparisonTable(data) {
    const tableWrapper = document.getElementById("tableWrapper");
    const tableLoading = document.getElementById("tableLoading");
    const tbody = document.getElementById("comparisonBody");
    if (!data.comparison) return;
    const sorted = Object.entries(data.comparison).sort((a, b) => a[1].RMSE - b[1].RMSE);
    tbody.innerHTML = "";
    sorted.forEach(([name, metrics], index) => {
        const row = document.createElement("tr");
        if (index === 0) row.className = "best-row";
        const rankClass = "rank-" + (index + 1);
        row.innerHTML = `
            <td>${name} ${index === 0 ? '\u{1F3C6}' : ''}</td>
            <td>${metrics.R2}</td>
            <td>$${Number(metrics.RMSE).toLocaleString("en-US")}</td>
            <td>$${Number(metrics.MAE).toLocaleString("en-US")}</td>
            <td class="rank-col"><span class="rank-badge ${rankClass}">${index + 1}</span></td>
        `;
        tbody.appendChild(row);
    });
    tableLoading.classList.add("hidden");
    tableWrapper.classList.remove("hidden");
}

function renderFeatureImportance(data) {
    const rankingDiv = document.getElementById("importanceRanking");
    const list = document.getElementById("importanceList");
    if (data.feature_importance && data.feature_importance.length) {
        list.innerHTML = "";
        data.feature_importance.forEach((item) => {
            const li = document.createElement("li");
            li.textContent = item.Feature;
            list.appendChild(li);
        });
        rankingDiv.classList.remove("hidden");
    }
}

async function loadModelComparison() {
    try {
        const response = await fetch(API_URL + "/metrics");
        const data = await response.json();
        if (!response.ok) throw new Error("Failed");
        setCachedMetrics(data);
        renderComparisonTable(data);
        serverAwake = true;
        setServerStatus("Server ready", "ready");
    } catch {
        const cached = getCachedMetrics();
        if (!cached) {
            document.getElementById("tableLoading").innerHTML =
                '<p style="color: var(--accent-red);"><i class="fas fa-exclamation-circle"></i> Could not load model comparison</p>';
        }
    }
}

async function loadFeatureImportance() {
    const img = document.getElementById("importanceImage");
    const loading = document.getElementById("importanceLoading");
    img.src = API_URL + "/feature-importance";
    img.onload = () => {
        loading.classList.add("hidden");
        img.classList.remove("hidden");
    };
    img.onerror = () => {
        loading.innerHTML = '<p style="color: var(--accent-red);"><i class="fas fa-exclamation-circle"></i> Could not load feature importance chart</p>';
    };

    try {
        const response = await fetch(API_URL + "/metrics");
        const data = await response.json();
        renderFeatureImportance(data);
    } catch {}
}

async function fetchWithRetry(url, options, retries = 3, delayMs = 5000) {
    for (let attempt = 0; attempt <= retries; attempt++) {
        if (attempt > 0) {
            document.querySelector("#loadingSpinner p").textContent =
                "Server waking up... retry " + attempt + "/" + retries;
            await new Promise(r => setTimeout(r, delayMs));
        }
        try {
            const controller = new AbortController();
            const timeout = setTimeout(() => controller.abort(), 30000);
            const response = await fetch(url, {
                ...options,
                signal: controller.signal,
            });
            clearTimeout(timeout);
            if (response.status === 503 && attempt < retries) continue;
            return response;
        } catch (err) {
            if (attempt === retries) throw err;
        }
    }
}

async function wakeUpServer() {
    setServerStatus("Connecting to server...", "waking");
    try {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 60000);
        const res = await fetch(API_URL + "/", { signal: controller.signal });
        clearTimeout(timeout);
        if (res.ok) {
            serverAwake = true;
            setServerStatus("Server ready", "ready");
        }
    } catch {
        setServerStatus("Server waking up... (free tier, ~30s)", "waking");
    }
}

// Show cached data instantly, then wake server & refresh
const cached = getCachedMetrics();
if (cached) {
    renderComparisonTable(cached);
    renderFeatureImportance(cached);
}

// Fire all in parallel — don't block anything
wakeUpServer();
loadModelComparison();
loadFeatureImportance();
