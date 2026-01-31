// ===========================
// Map Initialization & Drawing
// ===========================

let map;
let drawnItems;
let drawControl;
let currentPolygon = null;

// Initialize the map
function initMap() {
    // Create map centered on a default location
    map = L.map('map').setView([20.5937, 78.9629], 5); // India center
    
    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(map);
    
    // Initialize drawn items layer
    drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);
    
    // Configure draw control
    drawControl = new L.Control.Draw({
        position: 'topright',
        draw: {
            polygon: {
                allowIntersection: false,
                drawError: {
                    color: '#e76f51',
                    message: '<strong>Error:</strong> Shape edges cannot cross!'
                },
                shapeOptions: {
                    color: '#2d6a4f',
                    fillOpacity: 0.3,
                    weight: 3
                },
                showArea: true,
                metric: true
            },
            polyline: false,
            rectangle: false,
            circle: false,
            marker: false,
            circlemarker: false
        },
        edit: {
            featureGroup: drawnItems,
            remove: true
        }
    });
    
    map.addControl(drawControl);
    
    // Event listeners for drawing
    setupDrawingEvents();
}

// Setup drawing event listeners
function setupDrawingEvents() {
    // When a polygon is created
    map.on(L.Draw.Event.CREATED, function(event) {
        const layer = event.layer;
        
        // Remove previous polygon if exists
        if (currentPolygon) {
            drawnItems.removeLayer(currentPolygon);
        }
        
        // Add new polygon
        drawnItems.addLayer(layer);
        currentPolygon = layer;
        
        // Calculate and display field statistics
        updateFieldStats(layer);
        
        // Show farm details form
        showFarmForm();
        
        // Show clear button
        document.getElementById('clearBtn').style.display = 'inline-block';
    });
    
    // When a polygon is edited
    map.on(L.Draw.Event.EDITED, function(event) {
        const layers = event.layers;
        layers.eachLayer(function(layer) {
            updateFieldStats(layer);
        });
    });
    
    // When a polygon is deleted
    map.on(L.Draw.Event.DELETED, function() {
        currentPolygon = null;
        hideFarmForm();
        document.getElementById('clearBtn').style.display = 'none';
    });
}

// Update field statistics display
function updateFieldStats(layer) {
    // Get GeoJSON of the polygon
    const geoJson = layer.toGeoJSON();
    const coordinates = geoJson.geometry.coordinates[0];
    
    // Calculate area in square meters using Leaflet's built-in method
    const area = L.GeometryUtil.geodesicArea(layer.getLatLngs()[0]);
    const hectares = (area / 10000).toFixed(2); // Convert to hectares
    
    // Get center point
    const bounds = layer.getBounds();
    const center = bounds.getCenter();
    
    // Update display
    document.getElementById('areaDisplay').textContent = hectares + ' ha';
    document.getElementById('coordsDisplay').textContent = 
        `${center.lat.toFixed(4)}°N, ${center.lng.toFixed(4)}°E`;
    
    // Store polygon data globally for report generation
    // API expects coordinates as array of rings: [[[lng,lat], ...]] (GeoJSON Polygon)
    window.farmPolygon = {
        type: 'Polygon',
        coordinates: geoJson.geometry.coordinates,
        area: hectares,
        center: {
            lat: center.lat,
            lng: center.lng
        }
    };
}

// Show farm details form
function showFarmForm() {
    document.getElementById('farmForm').style.display = 'block';
    document.getElementById('farmForm').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Hide farm details form
function hideFarmForm() {
    document.getElementById('farmForm').style.display = 'none';
    document.getElementById('fieldStats').innerHTML = `
        <p><strong>Field Area:</strong> <span id="areaDisplay">-</span> hectares</p>
        <p><strong>Coordinates:</strong> <span id="coordsDisplay">-</span></p>
    `;
}

// Clear drawn polygon
function clearPolygon() {
    if (currentPolygon) {
        drawnItems.removeLayer(currentPolygon);
        currentPolygon = null;
        hideFarmForm();
        document.getElementById('clearBtn').style.display = 'none';
    }
}

// Locate user's current position
function locateUser() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;
                
                map.setView([lat, lng], 15);
                
                // Add a temporary marker
                const marker = L.marker([lat, lng]).addTo(map);
                marker.bindPopup('📍 You are here!').openPopup();
                
                setTimeout(() => {
                    map.removeLayer(marker);
                }, 5000);
            },
            function(error) {
                alert('Unable to get your location: ' + error.message);
            }
        );
    } else {
        alert('Geolocation is not supported by your browser');
    }
}

// Get polygon coordinates for API
function getPolygonCoordinates() {
    if (!currentPolygon) {
        return null;
    }
    
    const geoJson = currentPolygon.toGeoJSON();
    return geoJson.geometry.coordinates;
}

// Get polygon bounds
function getPolygonBounds() {
    if (!currentPolygon) {
        return null;
    }
    
    const bounds = currentPolygon.getBounds();
    return {
        north: bounds.getNorth(),
        south: bounds.getSouth(),
        east: bounds.getEast(),
        west: bounds.getWest()
    };
}

// Initialize map when page loads
document.addEventListener('DOMContentLoaded', initMap);
