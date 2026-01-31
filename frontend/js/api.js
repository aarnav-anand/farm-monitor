// ===========================
// API Communication
// ===========================

// Configuration
// When deployed: set PRODUCTION_API_URL below to your Render backend URL (e.g. https://farm-monitor-api.onrender.com).
// Local: uses http://localhost:8000 automatically.
const PRODUCTION_API_URL = 'https://your-app.onrender.com'; // Replace with your Render URL when deploying
const API_CONFIG = {
    baseURL: (typeof window !== 'undefined' && window.location && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1')
        ? PRODUCTION_API_URL
        : 'http://localhost:8000',
    timeout: 120000 // 2 minutes timeout for satellite processing
};

// API endpoints
const API_ENDPOINTS = {
    generateReport: '/api/generate-report',
    healthCheck: '/api/health'
};

// Generate farm report
async function generateReport(farmData) {
    try {
        const response = await fetch(`${API_CONFIG.baseURL}${API_ENDPOINTS.generateReport}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(farmData),
            signal: AbortSignal.timeout(API_CONFIG.timeout)
        });
        
        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            const message = parseApiErrorDetail(error.detail);
            throw new Error(message);
        }
        
        const result = await response.json();
        return result;
        
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Health check to wake up the server
async function checkServerHealth() {
    try {
        const response = await fetch(`${API_CONFIG.baseURL}${API_ENDPOINTS.healthCheck}`, {
            method: 'GET',
            signal: AbortSignal.timeout(10000)
        });
        
        return response.ok;
    } catch (error) {
        console.error('Health check failed:', error);
        return false;
    }
}

// Download PDF file
async function downloadPDF(pdfUrl, filename) {
    try {
        const response = await fetch(pdfUrl);
        const blob = await response.blob();
        
        // Create download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename || 'farm-report.pdf';
        document.body.appendChild(a);
        a.click();
        
        // Cleanup
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
    } catch (error) {
        console.error('Download error:', error);
        throw new Error('Failed to download PDF');
    }
}

// Validate form data before sending
function validateFarmData(data) {
    if (!data.polygon || !data.polygon.coordinates) {
        throw new Error('Please draw a field polygon on the map');
    }
    
    if (!data.farm_name || data.farm_name.trim() === '') {
        throw new Error('Please enter a farm name');
    }
    
    if (!data.crop_type || data.crop_type === '') {
        throw new Error('Please select a crop type');
    }
    
    if (data.email && !isValidEmail(data.email)) {
        throw new Error('Please enter a valid email address');
    }
    
    return true;
}

// Email validation
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Parse FastAPI error detail (string or array of { loc, msg, type })
function parseApiErrorDetail(detail) {
    if (detail == null) return 'Failed to generate report';
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) {
        return detail
            .map(function (d) { return d.msg || (typeof d === 'string' ? d : JSON.stringify(d)); })
            .join('. ') || 'Request validation failed. Please check your inputs.';
    }
    if (typeof detail === 'object') return detail.message || detail.msg || JSON.stringify(detail);
    return String(detail);
}

// Format error message for display
function formatErrorMessage(error) {
    if (error && error.message && error.message !== '[object Object]') {
        return error.message;
    }
    
    if (typeof error === 'string') {
        return error;
    }
    
    if (error && typeof error === 'object' && error.detail) {
        return parseApiErrorDetail(error.detail);
    }
    
    return 'An unexpected error occurred. Please try again.';
}

// Check if backend is available
async function ensureBackendAvailable() {
    const isHealthy = await checkServerHealth();
    
    if (!isHealthy) {
        throw new Error(
            'Unable to connect to the server. The free tier may be sleeping. ' +
            'Please wait 30-60 seconds and try again.'
        );
    }
    
    return true;
}

// Progress tracking
class ProgressTracker {
    constructor() {
        this.steps = ['step1', 'step2', 'step3', 'step4'];
        this.currentStep = 0;
    }
    
    start() {
        this.currentStep = 0;
        this.steps.forEach(stepId => {
            const element = document.getElementById(stepId);
            element.classList.remove('active', 'complete');
        });
        this.updateStep();
    }
    
    next() {
        if (this.currentStep < this.steps.length) {
            const prevStep = document.getElementById(this.steps[this.currentStep]);
            prevStep.classList.remove('active');
            prevStep.classList.add('complete');
            
            this.currentStep++;
            this.updateStep();
        }
    }
    
    updateStep() {
        if (this.currentStep < this.steps.length) {
            const currentElement = document.getElementById(this.steps[this.currentStep]);
            currentElement.classList.add('active');
        }
    }
    
    complete() {
        this.steps.forEach(stepId => {
            const element = document.getElementById(stepId);
            element.classList.remove('active');
            element.classList.add('complete');
        });
    }
    
    reset() {
        this.steps.forEach(stepId => {
            const element = document.getElementById(stepId);
            element.classList.remove('active', 'complete');
        });
        this.currentStep = 0;
    }
}

// Export for use in other modules
window.API = {
    generateReport,
    downloadPDF,
    validateFarmData,
    formatErrorMessage,
    ensureBackendAvailable,
    ProgressTracker
};
