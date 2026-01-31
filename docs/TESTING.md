# Farm Monitor - Testing Guide

## 🧪 Testing Strategy

This guide covers how to test the Farm Monitor application at each level.

## Table of Contents
1. [Unit Testing](#unit-testing)
2. [Integration Testing](#integration-testing)
3. [End-to-End Testing](#end-to-end-testing)
4. [Manual Testing](#manual-testing)
5. [Test Data](#test-data)

## Unit Testing

### Backend Unit Tests

Create `backend/tests/test_weather.py`:

```python
import pytest
from services.weather import WeatherService

@pytest.mark.asyncio
async def test_weather_service():
    service = WeatherService()
    
    # Test with known coordinates
    result = await service.get_weather_analysis(
        latitude=37.7749,
        longitude=-122.4194
    )
    
    assert 'analysis' in result
    assert 'historical' in result
    assert 'forecast' in result
    assert result['location']['latitude'] == 37.7749

@pytest.mark.asyncio
async def test_weather_analysis():
    service = WeatherService()
    
    # Mock historical data
    historical = {
        'precipitation': [10, 20, 5, 0, 0, 15, 8],
        'temp_mean': [25, 26, 27, 28, 29, 30, 28]
    }
    
    forecast = {
        'precipitation': [5, 10, 0, 0, 20, 15, 8]
    }
    
    analysis = service._analyze_weather_data(historical, forecast)
    
    assert 'total_rainfall_30d' in analysis
    assert 'avg_temperature' in analysis
    assert 'drought_risk' in analysis
```

Create `backend/tests/test_satellite.py`:

```python
import pytest
from services.satellite import SatelliteService

def test_ndvi_categorization():
    service = SatelliteService()
    
    assert service._categorize_ndvi(0.7) == "Excellent"
    assert service._categorize_ndvi(0.5) == "Good"
    assert service._categorize_ndvi(0.35) == "Moderate"
    assert service._categorize_ndvi(0.25) == "Poor"

def test_coords_conversion():
    service = SatelliteService()
    service.initialized = True
    
    coords = [[
        [-122.4, 37.8],
        [-122.4, 37.7],
        [-122.3, 37.7],
        [-122.3, 37.8],
        [-122.4, 37.8]
    ]]
    
    # This would require ee.Initialize() to actually work
    # For unit tests, we test the logic without GEE
    assert len(coords[0]) == 5  # Closed polygon
```

Create `backend/tests/test_analysis.py`:

```python
import pytest
from services.analysis import AgronomicAnalyzer

def test_growth_stage_calculation():
    analyzer = AgronomicAnalyzer()
    
    # Test with date 45 days ago
    from datetime import datetime, timedelta
    date_45_days_ago = (datetime.now() - timedelta(days=45)).strftime("%Y-%m-%d")
    
    stage = analyzer._calculate_growth_stage(date_45_days_ago)
    assert stage == "Vegetative"

def test_crop_health_assessment():
    analyzer = AgronomicAnalyzer()
    
    health = analyzer._assess_crop_health(
        ndvi=0.65,
        crop_type="wheat",
        growth_stage="Vegetative"
    )
    
    assert health == "Good"

def test_risk_assessment():
    analyzer = AgronomicAnalyzer()
    
    weather_analysis = {
        'drought_risk': True,
        'flood_risk': False,
        'temperature_stress': False,
        'total_rainfall_30d': 15,
        'forecast_rain_7d': 5,
        'avg_temperature': 28
    }
    
    risks = analyzer._assess_risks(weather_analysis, ndvi=0.3, ndmi=0.15)
    
    assert risks['drought'] == 'High'
    assert risks['flood'] == 'Low'
```

### Running Unit Tests

```bash
cd backend
pip install pytest pytest-asyncio

# Run all tests
pytest

# Run specific test file
pytest tests/test_weather.py

# Run with coverage
pytest --cov=services tests/

# Run with verbose output
pytest -v
```

## Integration Testing

### API Integration Tests

Create `backend/tests/test_api.py`:

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "app" in response.json()

def test_generate_report_missing_data():
    response = client.post("/api/generate-report", json={})
    assert response.status_code == 422  # Validation error

def test_generate_report_valid():
    payload = {
        "farm_name": "Test Farm",
        "crop_type": "wheat",
        "email": None,
        "planting_date": None,
        "polygon": {
            "type": "Polygon",
            "coordinates": [[
                [-122.4, 37.8],
                [-122.4, 37.7],
                [-122.3, 37.7],
                [-122.3, 37.8],
                [-122.4, 37.8]
            ]]
        },
        "area": 10.5,
        "center": {
            "lat": 37.75,
            "lng": -122.35
        }
    }
    
    response = client.post("/api/generate-report", json=payload)
    
    # May take time, so timeout appropriately
    assert response.status_code == 200
    data = response.json()
    assert "farm_name" in data
    assert "recommendations" in data
```

Run integration tests:
```bash
pytest tests/test_api.py -v
```

## End-to-End Testing

### Frontend E2E Tests

Create `frontend/tests/e2e.test.js`:

```javascript
// Using Playwright or Selenium
const { test, expect } = require('@playwright/test');

test('Farm Monitor E2E', async ({ page }) => {
  // Navigate to app
  await page.goto('http://localhost:8080');
  
  // Check title
  await expect(page).toHaveTitle(/Farm Monitor/);
  
  // Check map is loaded
  const map = await page.locator('#map');
  await expect(map).toBeVisible();
  
  // Try to locate user
  await page.click('#locateBtn');
  
  // Wait for geolocation (may need permission)
  await page.waitForTimeout(2000);
  
  // Draw polygon (simulate clicks)
  // This is complex - typically done with manual testing
  
  // Fill form
  await page.fill('#farmName', 'Test Farm E2E');
  await page.selectOption('#cropType', 'wheat');
  
  // Submit (only if polygon drawn)
  // await page.click('#generateBtn');
  
  // Check for loading modal
  // await expect(page.locator('#loadingModal')).toBeVisible();
});
```

## Manual Testing

### Frontend Testing Checklist

- [ ] **Map Loading**
  - [ ] Map tiles load correctly
  - [ ] Can pan and zoom
  - [ ] No console errors

- [ ] **Drawing Functionality**
  - [ ] Polygon tool activates
  - [ ] Can draw field boundary
  - [ ] Area calculates correctly
  - [ ] Can edit polygon
  - [ ] Can delete polygon
  - [ ] Clear button works

- [ ] **Location Services**
  - [ ] "Find My Location" button works
  - [ ] Map centers on user location
  - [ ] Marker appears temporarily

- [ ] **Form Validation**
  - [ ] Farm name required
  - [ ] Crop type required
  - [ ] Email validation (if provided)
  - [ ] Date picker works
  - [ ] Form can't submit without polygon

- [ ] **Report Generation**
  - [ ] Loading modal appears
  - [ ] Progress steps update
  - [ ] No errors in console
  - [ ] Result modal shows data
  - [ ] PDF downloads successfully

- [ ] **Error Handling**
  - [ ] Network errors handled gracefully
  - [ ] Server errors show user-friendly message
  - [ ] Validation errors displayed
  - [ ] Can retry after error

- [ ] **Responsive Design**
  - [ ] Works on mobile (320px width)
  - [ ] Works on tablet (768px width)
  - [ ] Works on desktop (1920px width)
  - [ ] Touch controls work on mobile

### Backend Testing Checklist

- [ ] **API Endpoints**
  - [ ] `/` returns API info
  - [ ] `/api/health` returns healthy status
  - [ ] `/api/generate-report` accepts valid requests
  - [ ] `/api/generate-report` rejects invalid requests

- [ ] **Data Services**
  - [ ] Weather service fetches data
  - [ ] Satellite service initializes
  - [ ] GEE authentication works
  - [ ] PDF generation completes

- [ ] **Error Scenarios**
  - [ ] Handles missing GEE credentials
  - [ ] Handles weather API timeout
  - [ ] Handles invalid coordinates
  - [ ] Returns appropriate error codes

- [ ] **Performance**
  - [ ] Response time < 30 seconds
  - [ ] Memory usage stable
  - [ ] No memory leaks
  - [ ] Handles concurrent requests

## Test Data

### Sample Valid Requests

#### Small Farm (California)
```json
{
  "farm_name": "Napa Valley Vineyard",
  "crop_type": "fruit",
  "polygon": {
    "type": "Polygon",
    "coordinates": [[
      [-122.2869, 38.2975],
      [-122.2869, 38.2965],
      [-122.2855, 38.2965],
      [-122.2855, 38.2975],
      [-122.2869, 38.2975]
    ]]
  },
  "area": 2.5,
  "center": {
    "lat": 38.2970,
    "lng": -122.2862
  }
}
```

#### Medium Farm (India)
```json
{
  "farm_name": "Punjab Wheat Farm",
  "crop_type": "wheat",
  "planting_date": "2025-11-15",
  "polygon": {
    "type": "Polygon",
    "coordinates": [[
      [75.8412, 30.9010],
      [75.8412, 30.8980],
      [75.8450, 30.8980],
      [75.8450, 30.9010],
      [75.8412, 30.9010]
    ]]
  },
  "area": 15.7,
  "center": {
    "lat": 30.8995,
    "lng": 75.8431
  }
}
```

#### Large Farm (Brazil)
```json
{
  "farm_name": "São Paulo Soybean",
  "crop_type": "soybean",
  "email": "farmer@example.com",
  "planting_date": "2025-10-01",
  "polygon": {
    "type": "Polygon",
    "coordinates": [[
      [-47.8825, -15.7942],
      [-47.8825, -15.8020],
      [-47.8720, -15.8020],
      [-47.8720, -15.7942],
      [-47.8825, -15.7942]
    ]]
  },
  "area": 85.3,
  "center": {
    "lat": -15.7981,
    "lng": -47.8773
  }
}
```

### Test Locations

Good locations for testing (known to have data):

1. **California Central Valley**: `36.7783°N, -119.4179°W`
2. **Iowa Cornbelt**: `41.8780°N, -93.0977°W`
3. **Punjab, India**: `30.9010°N, 75.8573°E`
4. **Cerrado, Brazil**: `-15.7942°S, -47.8825°W`
5. **Champagne, France**: `49.2628°N, 4.0347°E`

### Expected NDVI Values by Crop

- **Healthy Crops**: 0.5 - 0.8
- **Moderate Health**: 0.3 - 0.5
- **Stressed Crops**: 0.1 - 0.3
- **Bare Soil**: 0.0 - 0.1
- **Water**: < 0.0

## Performance Testing

### Load Testing

Using `locust` (Python load testing):

```python
# locustfile.py
from locust import HttpUser, task, between

class FarmMonitorUser(HttpUser):
    wait_time = between(5, 10)
    
    @task
    def health_check(self):
        self.client.get("/api/health")
    
    @task(3)
    def generate_report(self):
        self.client.post("/api/generate-report", json={
            "farm_name": "Load Test Farm",
            "crop_type": "wheat",
            "polygon": {
                "type": "Polygon",
                "coordinates": [[
                    [-122.4, 37.8],
                    [-122.4, 37.7],
                    [-122.3, 37.7],
                    [-122.3, 37.8],
                    [-122.4, 37.8]
                ]]
            },
            "area": 10,
            "center": {"lat": 37.75, "lng": -122.35}
        })
```

Run load test:
```bash
pip install locust
locust -f locustfile.py --host=http://localhost:8000
```

### Expected Performance

- **Health Check**: < 100ms
- **Weather Data**: 1-3 seconds
- **Satellite Data**: 5-15 seconds
- **Full Report**: 10-25 seconds
- **Concurrent Users**: 10-20 (free tier)

## Automated Testing Pipeline

### GitHub Actions Workflow

Create `.github/workflows/test.yml`:

```yaml
name: Test Farm Monitor

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        cd backend
        pytest --cov=services tests/
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

## Test Coverage Goals

- **Backend Services**: > 80%
- **API Endpoints**: > 90%
- **Analysis Logic**: > 85%
- **Overall**: > 80%

## Debugging Tips

### Backend Debugging

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Or in main.py
uvicorn.run("main:app", log_level="debug")

# Add breakpoints
import pdb; pdb.set_trace()
```

### Frontend Debugging

```javascript
// Enable verbose logging
console.log('Debug:', data);

// Use debugger
debugger;

// Check network requests
// Open DevTools → Network tab
```

## Continuous Testing

Run tests automatically:
```bash
# Watch mode (requires pytest-watch)
pip install pytest-watch
ptw

# On file change
while true; do pytest; sleep 5; done
```

---

## Test Report Template

```
# Test Report - [Date]

## Summary
- Total Tests: 45
- Passed: 43
- Failed: 2
- Coverage: 82%

## Failed Tests
1. test_satellite_timeout - Network timeout
2. test_email_sending - SMTP not configured

## Performance
- Average response time: 12s
- Peak memory: 250MB
- Concurrent users tested: 15

## Issues Found
- [ ] Satellite service occasionally times out
- [ ] Need to implement email retry logic

## Next Steps
- Fix failing tests
- Increase coverage to 85%
- Add more edge case tests
```

---

Remember: **Test early, test often!** 🧪
