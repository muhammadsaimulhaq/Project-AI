// Car Price Prediction - Interactive Features

document.addEventListener('DOMContentLoaded', function() {
    initializeCarPricePrediction();
    setupRealTimeValidation();
    setupChartIfExists();
});

function initializeCarPricePrediction() {
    // Auto-fill prediction form from URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const formFields = ['brand', 'model', 'year', 'mileage', 'fuel_type', 'transmission', 'engine_size', 'horsepower'];
    
    formFields.forEach(field => {
        if (urlParams.has(field)) {
            const element = document.querySelector(`[name="${field}"]`);
            if (element) {
                element.value = urlParams.get(field);
            }
        }
    });
}

function setupRealTimeValidation() {
    // Real-time form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, select');
        inputs.forEach(input => {
            input.addEventListener('blur', validateField);
            input.addEventListener('input', clearFieldError);
        });
    });
}

function validateField(e) {
    const field = e.target;
    const value = field.value.trim();
    const fieldName = field.getAttribute('name');
    
    // Clear previous errors
    clearFieldError(e);
    
    let isValid = true;
    let errorMessage = '';
    
    switch(fieldName) {
        case 'year':
            if (value < 1990 || value > 2024) {
                isValid = false;
                errorMessage = 'Year must be between 1990 and 2024';
            }
            break;
            
        case 'mileage':
            if (value < 0 || value > 500000) {
                isValid = false;
                errorMessage = 'Mileage must be between 0 and 500,000 km';
            }
            break;
            
        case 'engine_size':
            if (value < 0.5 || value > 5.0) {
                isValid = false;
                errorMessage = 'Engine size must be between 0.5L and 5.0L';
            }
            break;
            
        case 'horsepower':
            if (value < 50 || value > 1000) {
                isValid = false;
                errorMessage = 'Horsepower must be between 50 and 1000';
            }
            break;
            
        case 'brand':
        case 'model':
            if (value.length < 2) {
                isValid = false;
                errorMessage = `${fieldName.charAt(0).toUpperCase() + fieldName.slice(1)} must be at least 2 characters`;
            }
            break;
    }
    
    if (!isValid) {
        showFieldError(field, errorMessage);
    }
    
    return isValid;
}

function showFieldError(field, message) {
    field.classList.add('is-invalid');
    
    let errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        field.parentNode.appendChild(errorDiv);
    }
    errorDiv.textContent = message;
}

function clearFieldError(e) {
    const field = e.target;
    field.classList.remove('is-invalid');
    
    const errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.textContent = '';
    }
}

function setupChartIfExists() {
    // Initialize feature importance chart if on dashboard
    if (document.getElementById('featureImportanceChart')) {
        initializeFeatureImportanceChart();
    }
}

function initializeFeatureImportanceChart() {
    // This would typically fetch data from an API
    // For now, we'll create a sample chart if Chart.js is available
    if (typeof Chart !== 'undefined') {
        const ctx = document.getElementById('featureImportanceChart').getContext('2d');
        
        // Sample data - in real app, this would come from Flask
        const featureData = {
            labels: ['Year', 'Mileage', 'Brand', 'Horsepower', 'Engine Size', 'Fuel Type', 'Model', 'Transmission'],
            datasets: [{
                label: 'Feature Importance',
                data: [0.25, 0.20, 0.15, 0.12, 0.10, 0.08, 0.06, 0.04],
                backgroundColor: [
                    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
                    '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
                ],
                borderWidth: 1
            }]
        };
        
        new Chart(ctx, {
            type: 'bar',
            data: featureData,
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Feature Importance in Price Prediction'
                    },
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Importance Score'
                        }
                    }
                }
            }
        });
    }
}

// API Functions
async function predictPriceAPI(carData) {
    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(carData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            return result.predicted_price;
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Utility Functions
function formatIndianCurrency(amount) {
    return '₹' + amount.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function showLoading(element) {
    element.disabled = true;
    element.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Predicting...';
}

function hideLoading(element, originalText) {
    element.disabled = false;
    element.textContent = originalText;
}

// Event Listeners for Enhanced UX
document.addEventListener('DOMContentLoaded', function() {
    // Add loading states to forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                showLoading(submitBtn);
            }
        });
    });
    
    // Add price range suggestions
    const priceInputs = document.querySelectorAll('input[type="number"]');
    priceInputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.title = getSuggestionForField(this.name);
        });
    });
});

function getSuggestionForField(fieldName) {
    const suggestions = {
        'year': 'Typically 1990-2024',
        'mileage': 'Average: 10,000-100,000 km',
        'engine_size': 'Common: 1.0L - 3.0L',
        'horsepower': 'Range: 70-300 HP'
    };
    return suggestions[fieldName] || '';
}
