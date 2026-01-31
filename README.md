# Farm Monitoring Application - Vanilla Implementation

## 🌾 Overview
A zero-cost farm monitoring application that generates PDF reports with weather analysis, satellite health monitoring (NDVI), and agronomic advice.

## 📁 Project Structure
```
farm-monitor/
├── frontend/
│   ├── index.html          # Main HTML page
│   ├── css/
│   │   └── styles.css      # All styles
│   ├── js/
│   │   ├── map.js          # Map initialization & drawing
│   │   ├── api.js          # Backend API calls
│   │   └── app.js          # Main application logic
│   └── assets/
│       └── loading.gif     # Optional loading spinner
├── backend/
│   ├── main.py             # FastAPI entry point
│   ├── services/
│   │   ├── weather.py      # Open-Meteo integration
│   │   ├── satellite.py    # Google Earth Engine integration
│   │   ├── analysis.py     # Agronomic logic
│   │   └── pdf_gen.py      # PDF generation
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # Environment variables template
└── docs/
    ├── SETUP.md            # Detailed setup guide
    └── DEPLOYMENT.md       # Deployment instructions
```

## 🚀 Quick Start

### Prerequisites
1. Python 3.9+
2. Google Earth Engine account (https://earthengine.google.com/signup/)
3. Supabase account (optional, for storing reports)

### Backend Setup (5 minutes)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Frontend Setup (1 minute)
```bash
cd frontend
# Use a different port than the backend (backend uses 8000)
python -m http.server 5500
# Then visit: http://localhost:5500
```
See **TEST_LOCAL.md** for step-by-step backend + frontend testing.

## 🔑 API Keys Setup

1. **Google Earth Engine**:
   - Sign up at https://earthengine.google.com
   - Download service account JSON key
   - Save as `backend/gee-credentials.json`

2. **Environment Variables**:
   ```bash
   cp backend/.env.example backend/.env
   # Edit .env with your credentials
   ```

## 📦 Free Hosting Deployment

### Frontend (Vercel/Netlify)
- Drag and drop the `frontend/` folder
- No configuration needed!

### Backend (Render.com)
- Connect GitHub repository
- Root directory: `backend`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## 🎯 Features
- ✅ Interactive map with polygon drawing
- ✅ Real-time weather data (Open-Meteo)
- ✅ Satellite imagery & NDVI calculation
- ✅ Automated agronomic advice
- ✅ PDF report generation
- ✅ 100% free infrastructure

## 📚 Documentation
See `docs/SETUP.md` for detailed setup instructions.
