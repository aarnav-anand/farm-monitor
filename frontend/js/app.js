// ===========================
// Main Application Logic
// ===========================

// Initialize progress tracker
const progressTracker = new window.API.ProgressTracker();

// DOM elements
let loadingModal, resultModal, errorModal;
let generateBtn, clearBtn, locateBtn;
let detailsForm;

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    // Initialize i18n first so initial UI is translated before user interacts
    if (window.I18N && typeof window.I18N.init === 'function') {
        window.I18N.init();
    }

    // Get DOM elements
    loadingModal = document.getElementById('loadingModal');
    resultModal = document.getElementById('resultModal');
    errorModal = document.getElementById('errorModal');
    
    generateBtn = document.getElementById('generateBtn');
    clearBtn = document.getElementById('clearBtn');
    locateBtn = document.getElementById('locateBtn');
    
    detailsForm = document.getElementById('detailsForm');
    
    // Setup event listeners
    setupEventListeners();
});

// Setup all event listeners
function setupEventListeners() {
    // Form submission
    detailsForm.addEventListener('submit', handleFormSubmit);
    
    // Clear button
    clearBtn.addEventListener('click', function() {
        clearPolygon();
    });
    
    // Locate button
    locateBtn.addEventListener('click', function() {
        locateUser();
    });
    
    // Modal close buttons
    document.getElementById('closeResult').addEventListener('click', function() {
        closeModal(resultModal);
    });
    
    document.getElementById('closeError').addEventListener('click', function() {
        closeModal(errorModal);
    });
    
    // New report button
    document.getElementById('newReportBtn').addEventListener('click', function() {
        closeModal(resultModal);
        resetForm();
    });
    
    // Retry button
    document.getElementById('retryBtn').addEventListener('click', function() {
        closeModal(errorModal);
    });
    
    // Close modals on outside click
    window.addEventListener('click', function(event) {
        if (event.target === loadingModal) {
            // Don't allow closing loading modal by clicking outside
            return;
        }
        if (event.target === resultModal) {
            closeModal(resultModal);
        }
        if (event.target === errorModal) {
            closeModal(errorModal);
        }
    });
}

// Handle form submission
async function handleFormSubmit(event) {
    event.preventDefault();
    
    // Disable submit button
    setButtonLoading(generateBtn, true);
    
    try {
        // Collect form data
        const farmData = collectFormData();
        
        // Validate data
        window.API.validateFarmData(farmData);
        
        // Show loading modal
        showLoadingModal();
        
        // Check if backend is available
        updateLoadingStatus(window.I18N ? window.I18N.t('loading_status_connecting_server') : 'Connecting to server...');
        await window.API.ensureBackendAvailable();
        
        // Start progress tracking
        progressTracker.start();
        
        // Generate report
        updateLoadingStatus(window.I18N ? window.I18N.t('loading_status_processing') : 'Processing your request...');
        const result = await window.API.generateReport(farmData);
        
        // Mark all steps complete
        progressTracker.complete();
        
        // Hide loading, show result
        closeModal(loadingModal);
        showResultModal(result);
        
    } catch (error) {
        console.error('Error generating report:', error);
        closeModal(loadingModal);
        showErrorModal(error);
    } finally {
        setButtonLoading(generateBtn, false);
    }
}

// Ensure polygon coordinates are array of rings: [[[lng,lat], ...]] (GeoJSON Polygon)
function ensurePolygonRings(coords) {
    if (!coords || !coords.length) return coords;
    // Already array of rings: [[[lng,lat], ...]]
    if (Array.isArray(coords[0]) && Array.isArray(coords[0][0]) && coords[0][0].length >= 2) {
        return coords;
    }
    // Single ring: [[lng,lat], ...] -> wrap as one ring
    return [coords];
}

// Collect form data
function collectFormData() {
    // Get polygon data
    const polygon = window.farmPolygon;
    
    if (!polygon) {
        throw new Error(window.I18N ? window.I18N.t('err_draw_field_first') : 'Please draw a field on the map first');
    }
    
    // Get form values
    const farmName = document.getElementById('farmName').value.trim();
    const cropType = document.getElementById('cropType').value;
    const email = document.getElementById('email').value.trim();
    const plantingDate = document.getElementById('plantingDate').value;
    
    return {
        farm_name: farmName,
        crop_type: cropType,
        email: email || null,
        planting_date: plantingDate || null,
        language: window.I18N ? window.I18N.getLanguage() : 'en',
        polygon: {
            type: polygon.type,
            coordinates: ensurePolygonRings(polygon.coordinates)
        },
        area: parseFloat(polygon.area),
        center: polygon.center
    };
}

// Show loading modal
function showLoadingModal() {
    loadingModal.classList.add('active');
    progressTracker.start();
}

// Update loading status message
function updateLoadingStatus(message) {
    document.getElementById('loadingStatus').textContent = message;
}

// Show result modal with report data
function showResultModal(result) {
    // Populate preview
    const preview = document.getElementById('reportPreview');
    const t = (k) => (window.I18N ? window.I18N.t(k) : k);
    preview.innerHTML = `
        <h3>📊 ${t('report_summary_title')}</h3>
        <p><strong>${t('report_farm')}</strong> ${result.farm_name}</p>
        <p><strong>${t('report_crop')}</strong> ${result.crop_type}</p>
        <p><strong>${t('report_area')}</strong> ${result.area} hectares</p>
        <p><strong>${t('report_ndvi')}</strong> ${result.ndvi_value || 'N/A'}</p>
        <p><strong>${t('report_health')}</strong> ${result.health_status || 'Good'}</p>
        ${result.recommendations ? `
            <div style="margin-top: 1rem; padding: 1rem; background: #fff3cd; border-radius: 8px;">
                <strong>🌾 ${t('report_recommendations')}</strong>
                <p style="margin-top: 0.5rem;">${result.recommendations}</p>
            </div>
        ` : ''}
    `;
    
    // Setup download link
    const downloadLink = document.getElementById('downloadLink');
    if (result.pdf_url) {
        downloadLink.href = result.pdf_url;
        downloadLink.onclick = function(e) {
            e.preventDefault();
            const suffix = window.I18N ? window.I18N.t('pdf_filename_suffix') : 'report';
            window.API.downloadPDF(result.pdf_url, `${result.farm_name}_${suffix}.pdf`);
        };
    } else if (result.pdf_base64) {
        // Handle base64 PDF
        const blob = base64toBlob(result.pdf_base64, 'application/pdf');
        const url = URL.createObjectURL(blob);
        downloadLink.href = url;
        const suffix = window.I18N ? window.I18N.t('pdf_filename_suffix') : 'report';
        downloadLink.download = `${result.farm_name}_${suffix}.pdf`;
    }
    
    resultModal.classList.add('active');
}

// Show error modal
function showErrorModal(error) {
    const message = window.API.formatErrorMessage(error);
    document.getElementById('errorMessage').textContent = message;
    errorModal.classList.add('active');
}

// Close modal
function closeModal(modal) {
    modal.classList.remove('active');
}

// Set button loading state
function setButtonLoading(button, isLoading) {
    const btnText = button.querySelector('.btn-text');
    const btnLoader = button.querySelector('.btn-loader');
    
    if (isLoading) {
        btnText.style.display = 'none';
        btnLoader.style.display = 'inline';
        button.disabled = true;
    } else {
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
        button.disabled = false;
    }
}

// Reset form
function resetForm() {
    detailsForm.reset();
    clearPolygon();
    progressTracker.reset();
}

// Convert base64 to blob
function base64toBlob(base64Data, contentType) {
    contentType = contentType || '';
    const sliceSize = 1024;
    const byteCharacters = atob(base64Data);
    const bytesLength = byteCharacters.length;
    const slicesCount = Math.ceil(bytesLength / sliceSize);
    const byteArrays = new Array(slicesCount);
    
    for (let sliceIndex = 0; sliceIndex < slicesCount; ++sliceIndex) {
        const begin = sliceIndex * sliceSize;
        const end = Math.min(begin + sliceSize, bytesLength);
        
        const bytes = new Array(end - begin);
        for (let offset = begin, i = 0; offset < end; ++i, ++offset) {
            bytes[i] = byteCharacters[offset].charCodeAt(0);
        }
        byteArrays[sliceIndex] = new Uint8Array(bytes);
    }
    
    return new Blob(byteArrays, { type: contentType });
}

// Simulate progress updates (for better UX)
function simulateProgress() {
    const delays = [2000, 3000, 4000, 5000]; // Delays between steps
    
    delays.forEach((delay, index) => {
        setTimeout(() => {
            progressTracker.next();
        }, delay);
    });
}

// Auto-simulate progress when loading starts
const originalShowLoadingModal = showLoadingModal;
showLoadingModal = function() {
    originalShowLoadingModal();
    simulateProgress();
};

// Handle keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // ESC to close modals
    if (event.key === 'Escape') {
        if (resultModal.classList.contains('active')) {
            closeModal(resultModal);
        }
        if (errorModal.classList.contains('active')) {
            closeModal(errorModal);
        }
    }
});

// Show welcome message in console
console.log(`
🌾 Farm Monitor Application
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Powered by:
  🛰️  Sentinel-2 Satellite Data
  🌦️  Open-Meteo Weather API
  🗺️  OpenStreetMap

To get started:
  1. Draw a polygon on the map
  2. Fill in farm details
  3. Generate your report!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`);
