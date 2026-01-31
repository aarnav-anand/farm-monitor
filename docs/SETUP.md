# Farm Monitor - Detailed Setup Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Google Earth Engine Setup](#google-earth-engine-setup)
3. [Backend Setup](#backend-setup)
4. [Frontend Setup](#frontend-setup)
5. [Local Development](#local-development)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Accounts (All Free)
- [ ] Google account (for Earth Engine)
- [ ] GitHub account (for deployment)
- [ ] Render.com account (backend hosting)
- [ ] Vercel or Netlify account (frontend hosting)

### Required Software
- [ ] Python 3.9 or higher
- [ ] pip (Python package installer)
- [ ] A modern web browser
- [ ] Text editor (VS Code recommended)
- [ ] Git (optional but recommended)

## Google Earth Engine Setup

This is the most critical step - without GEE credentials, satellite features won't work.

### Step 1: Sign Up for Google Earth Engine

1. Go to https://earthengine.google.com/signup/
2. Sign in with your Google account
3. Fill out the registration form:
   - Select "Research" or "Education" as purpose
   - Describe project: "Farm monitoring application for agriculture"
4. Wait for approval email (usually within 24 hours)

### Step 2: Create Service Account

Once approved:

1. Go to Google Cloud Console: https://console.cloud.google.com/
2. Create a new project or select existing
3. Enable Earth Engine API:
   - Go to "APIs & Services" → "Enable APIs and Services"
   - Search for "Earth Engine API"
   - Click "Enable"

4. Create Service Account:
   - Go to "IAM & Admin" → "Service Accounts"
   - Click "Create Service Account"
   - Name: `farm-monitor-gee`
   - Grant role: "Earth Engine Resource Admin"
   - Click "Create Key" → JSON format
   - Download the JSON file

5. Register Service Account with Earth Engine:
   ```bash
   # Install earthengine-api
   pip install earthengine-api
   
   # Authenticate
   earthengine authenticate
   
   # Register service account
   earthengine set_project your-project-id
   ```

6. Save the JSON file as `gee-credentials.json` in the `backend/` folder

### Step 3: Verify GEE Setup

```python
import ee
ee.Initialize()
print("GEE initialized successfully!")
```

## Backend Setup

### Step 1: Create Virtual Environment

```bash
cd backend
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- FastAPI (web framework)
- uvicorn (server)
- earthengine-api (satellite data)
- reportlab (PDF generation)
- requests (HTTP client)
- And more...

### Step 3: Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and set:
```
GEE_CREDENTIALS_PATH=gee-credentials.json
```

### Step 4: Test Backend

```bash
python main.py
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Starting Farm Monitor API...
INFO:     Initializing Google Earth Engine...
INFO:     GEE initialized with service account
INFO:     API ready!
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Visit http://localhost:8000 to see API info.

### Step 5: Test API Endpoints

```bash
# Health check
curl http://localhost:8000/api/health

# Should return:
{
  "status": "healthy",
  "services": {
    "weather": "available",
    "satellite": "available",
    "pdf": "available"
  }
}
```

## Frontend Setup

### Step 1: Configure API URL

Edit `frontend/js/api.js`:

```javascript
const API_CONFIG = {
    baseURL: 'http://localhost:8000',  // For local development
    timeout: 120000
};
```

### Step 2: Serve Frontend

Option 1: Simple Python server
```bash
cd frontend
python -m http.server 8080
```

Option 2: VS Code Live Server
- Install "Live Server" extension
- Right-click `index.html` → "Open with Live Server"

Option 3: Node.js http-server
```bash
npm install -g http-server
cd frontend
http-server -p 8080
```

### Step 3: Test Frontend

1. Open http://localhost:8080
2. You should see the Farm Monitor interface
3. Try drawing a polygon on the map
4. Fill in farm details
5. Click "Generate Report"

## Local Development

### Running Both Frontend and Backend

Terminal 1 (Backend):
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python main.py
```

Terminal 2 (Frontend):
```bash
cd frontend
python -m http.server 8080
```

Then visit: http://localhost:8080

### Development Workflow

1. Make changes to code
2. Backend changes:
   - Stop server (Ctrl+C)
   - Restart: `python main.py`
3. Frontend changes:
   - Just refresh browser (no restart needed)

### Testing with Sample Data

Create a test polygon:
```json
{
  "farm_name": "Test Farm",
  "crop_type": "wheat",
  "polygon": {
    "type": "Polygon",
    "coordinates": [
      [
        [-122.4, 37.8],
        [-122.4, 37.7],
        [-122.3, 37.7],
        [-122.3, 37.8],
        [-122.4, 37.8]
      ]
    ]
  },
  "area": 10.5,
  "center": {
    "lat": 37.75,
    "lng": -122.35
  }
}
```

Use curl or Postman:
```bash
curl -X POST http://localhost:8000/api/generate-report \
  -H "Content-Type: application/json" \
  -d @test-data.json
```

## Troubleshooting

### Backend Issues

**Problem: "GEE not initialized"**
```
Solution:
1. Check gee-credentials.json exists
2. Verify file path in .env
3. Re-authenticate: earthengine authenticate
4. Check service account has Earth Engine permissions
```

**Problem: "ModuleNotFoundError"**
```
Solution:
1. Activate virtual environment
2. Reinstall: pip install -r requirements.txt
3. Verify Python version: python --version (should be 3.9+)
```

**Problem: "Address already in use (Port 8000)"**
```
Solution:
# Find and kill process
# On macOS/Linux:
lsof -ti:8000 | xargs kill -9

# On Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or use different port:
uvicorn main:app --port 8001
```

**Problem: "Weather API not responding"**
```
Solution:
- Check internet connection
- Verify Open-Meteo is accessible: curl https://api.open-meteo.com/v1/forecast
- Check for firewall blocking
```

### Frontend Issues

**Problem: "CORS error"**
```
Solution:
1. Verify backend is running
2. Check backend CORS settings in main.py
3. Use correct API URL in api.js
4. Don't use file:// protocol - use http://localhost
```

**Problem: "Map not loading"**
```
Solution:
1. Check internet connection (loads tiles from OpenStreetMap)
2. Check browser console for errors
3. Verify Leaflet scripts are loading
4. Try different browser
```

**Problem: "Cannot draw polygon"**
```
Solution:
1. Check Leaflet Draw is loaded
2. Verify no JavaScript errors in console
3. Try refreshing page
4. Clear browser cache
```

### Google Earth Engine Issues

**Problem: "Quota exceeded"**
```
Solution:
- Wait for quota reset (daily limit)
- Use smaller date ranges
- Reduce number of requests
- Check GEE quota dashboard
```

**Problem: "No imagery available"**
```
Solution:
- Try different date range (last 30 days)
- Check location (ocean areas have no data)
- Increase cloud cover threshold
- Use mock data for testing
```

### PDF Generation Issues

**Problem: "PDF is blank or corrupted"**
```
Solution:
1. Check reportlab installation
2. Verify all data is present
3. Check logs for errors
4. Test with minimal data first
```

## Performance Tips

### Backend
- Use async where possible
- Cache satellite data (same location)
- Limit concurrent requests
- Monitor memory usage

### Frontend
- Use loading indicators
- Implement request debouncing
- Cache map tiles
- Optimize polygon complexity

## Next Steps

Once local development is working:
1. See `DEPLOYMENT.md` for production deployment
2. Configure custom domain
3. Add monitoring
4. Set up analytics
5. Implement email notifications

## Getting Help

- Check GitHub issues
- Review API logs: `backend/app.log`
- Enable debug mode: Set `log_level="debug"` in uvicorn.run()
- Test each component individually

## Useful Commands

```bash
# Backend
cd backend
source venv/bin/activate
pip list  # Show installed packages
python -c "import ee; ee.Initialize(); print('OK')"  # Test GEE

# Frontend
cd frontend
# Just open in browser or use http server

# Git
git status
git add .
git commit -m "message"
git push

# Environment
pip freeze > requirements.txt  # Save dependencies
pip install -r requirements.txt  # Install dependencies
```

## Security Notes

⚠️ **Important Security Considerations:**

1. **Never commit** `gee-credentials.json` to Git
2. Add to `.gitignore`:
   ```
   gee-credentials.json
   .env
   *.pyc
   __pycache__/
   venv/
   ```
3. Use environment variables in production
4. Restrict CORS origins in production
5. Implement rate limiting
6. Validate all user inputs

## Performance Benchmarks

Expected response times:
- Health check: < 100ms
- Weather data: 1-3 seconds
- Satellite data: 5-15 seconds
- PDF generation: 2-5 seconds
- **Total**: 10-25 seconds per report

Cold start (Render free tier): +30-60 seconds

---

🌾 Happy farming! If you encounter issues, check the logs and error messages carefully.
