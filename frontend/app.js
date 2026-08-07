const API_BASE_URL = 'http://127.0.0.1:8000';

document.getElementById('claimForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const resultBox = document.getElementById('submitResult');
    resultBox.innerHTML = 'Processing...';
    resultBox.className = 'result-box';

    const payload = {
        claim_amount: parseFloat(document.getElementById('claim_amount').value),
        previous_claim_count: parseInt(document.getElementById('previous_claim_count').value, 10),
        days_since_last_claim: parseInt(document.getElementById('days_since_last_claim').value, 10),
        claim_category: document.getElementById('claim_category').value
    };

    try {
        const response = await fetch(`${API_BASE_URL}/predict`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok) {
            // Handle HTTP errors (400, 422, 500)
            const errorMsg = data.detail || 'An error occurred';
            const formattedError = typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg);
            resultBox.innerHTML = `<strong>Error:</strong> ${formattedError}`;
            resultBox.classList.add('error');
            return;
        }

        // Display Success
        resultBox.innerHTML = `
            <strong>Success!</strong><br>
            Claim ID: ${data.claim_id}<br>
            Risk Score: ${(data.risk_score * 100).toFixed(2)}%<br>
            Prediction: <strong>${data.prediction}</strong>
        `;
        resultBox.classList.add('success');
        
    } catch (error) {
        resultBox.innerHTML = `<strong>Network Error:</strong> ${error.message}`;
        resultBox.classList.add('error');
    }
});

document.getElementById('retrieveBtn').addEventListener('click', async () => {
    const claimId = document.getElementById('search_claim_id').value;
    const resultBox = document.getElementById('retrieveResult');
    resultBox.innerHTML = 'Searching...';
    resultBox.className = 'result-box';

    if (!claimId) {
        resultBox.innerHTML = '<strong>Error:</strong> Please enter a Claim ID';
        resultBox.classList.add('error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/claim/${claimId}`);
        const data = await response.json();

        if (!response.ok) {
            const errorMsg = data.detail || 'Claim not found';
            resultBox.innerHTML = `<strong>Error:</strong> ${errorMsg}`;
            resultBox.classList.add('error');
            return;
        }

        resultBox.innerHTML = `
            <strong>Claim Details:</strong><br>
            Amount: $${data.claim_amount}<br>
            Previous Claims: ${data.previous_claim_count}<br>
            Days Since Last: ${data.days_since_last_claim}<br>
            Category: ${data.claim_category}<br>
            <hr>
            <strong>Risk Result:</strong><br>
            Score: ${(data.risk_score * 100).toFixed(2)}%<br>
            Prediction: <strong>${data.prediction}</strong>
        `;
        resultBox.classList.add('success');

    } catch (error) {
        resultBox.innerHTML = `<strong>Network Error:</strong> ${error.message}`;
        resultBox.classList.add('error');
    }
});
