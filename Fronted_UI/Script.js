
const API_URL = "http://127.0.0.1:5000";

const form = document.getElementById("predictionForm");
const resultSection = document.getElementById("resultSection");
const predictedPrice = document.getElementById("predictedPrice");
const loadingSpinner = document.getElementById("loadingSpinner");


form.addEventListener("submit", async (e) => {
    e.preventDefault();

   
    loadingSpinner.classList.remove("hidden");
    resultSection.classList.add("hidden");

   
    const data = {
        area: Number(document.getElementById("area").value),
        bedrooms: Number(document.getElementById("bedrooms").value),
        bathrooms: Number(document.getElementById("bathrooms").value),
        stories: Number(document.getElementById("stories").value),
        parking: Number(document.getElementById("parking").value),
        has_pool: document.getElementById("has_pool").value,
        has_garage: document.getElementById("has_garage").value,
        has_ac: document.getElementById("has_ac").value
    };

    try {
        const response = await fetch(`${API_URL}/predict`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (result.error) {
            throw new Error(result.error);
        }

        
        predictedPrice.textContent = result.predicted_price.toLocaleString();
        resultSection.classList.remove("hidden");

    } catch (error) {
        alert("Prediction failed: " + error.message);
    } finally {
        loadingSpinner.classList.add("hidden");
    }
});


function resetForm() {
    form.reset();
    resultSection.classList.add("hidden");
    window.scrollTo({ top: 0, behavior: "smooth" });
}
