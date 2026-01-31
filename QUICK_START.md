# 🌾 Farm Monitor - Quick Reference

## 🚀 Quick Start (5 Minutes)

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python main.py
```

### Frontend
```bash
cd frontend
python -m http.server 8080
# Open http://localhost:8080
```

## 📁 Project Structure
```
farm-monitor/
├── frontend/           # Vanilla HTML/CSS/JS
│   ├── index.html
│   ├── css/styles.css
│   └── js/
│       ├── map.js      # Leaflet map
│       ├── api.js      # Backend calls
│       └── app.js      # Main logic
├── backend/            # Python FastAPI
│   ├── main.py         # Entry point
│   ├── services/
│   │   ├── weather.py  # Open-Meteo
│   │   ├── satellite.py # GEE
│   │   ├── analysis.py # Agronomic logic
│   │   └── pdf_gen.py  # ReportLab
│   └── requirements.txt
└── docs/               # Documentation
    ├── SETUP.md
    ├── DEPLOYMENT.md
    ├── FEATURES.md
    └── TESTING.md
```

## 🔑 Required Setup

### 1. Google Earth Engine (Most Important!)
1. Sign up: https://earthengine.google.com/signup/
2. Create service account in Google Cloud Console
3. Download JSON credentials → save as `backend/gee-credentials.json`
4. Details in `docs/SETUP.md`

### 2. Environment Variables
```bash
cd backend
cp .env.example .env
# Edit .env:
GEE_CREDENTIALS_PATH=gee-credentials.json
```

## 🎯 Key Features
- ✅ Interactive map with polygon drawing
- ✅ Satellite imagery (Sentinel-2) + NDVI calculation
- ✅ Weather data (30-day history + 7-day forecast)
- ✅ Intelligent agronomic recommendations
- ✅ Risk assessment (drought, flood, disease)
- ✅ Professional PDF reports
- ✅ 100% free infrastructure

## 🌐 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/api/health` | GET | Health check |
| `/api/generate-report` | POST | Generate farm report |

## 📊 Request Example
```json
POST /api/generate-report
{
  "farm_name": "Green Valley Farm",
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
  "area": 10.5,
  "center": {"lat": 37.75, "lng": -122.35}
}
```

## 🚢 Deployment (Free Tier)

### Backend → Render.com
```bash
1. Push to GitHub
2. Render → New Web Service
3. Connect repo, set:
   - Root: backend
   - Build: pip install -r requirements.txt
   - Start: uvicorn main:app --host 0.0.0.0 --port $PORT
4. Add GEE credentials as secret file
```

### Frontend → Vercel
```bash
1. Vercel → Import Project
2. Root directory: frontend
3. Framework: None (Vanilla)
4. Deploy
5. Update api.js with Render URL
```

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| GEE not initialized | Check gee-credentials.json path |
| CORS error | Update ALLOWED_ORIGINS in backend |
| Map not loading | Check internet, try different browser |
| Server sleeping | First request takes 30-60s (free tier) |
| No satellite data | Extend date range, check cloud cover |

## 📚 Documentation

- **Setup Guide**: `docs/SETUP.md` - Detailed setup instructions
- **Deployment**: `docs/DEPLOYMENT.md` - Production deployment
- **Features**: `docs/FEATURES.md` - Technical details
- **Testing**: `docs/TESTING.md` - Testing strategies

## 🔗 Data Sources
- **Satellite**: Sentinel-2 (ESA) via Google Earth Engine
- **Weather**: Open-Meteo API (free, no key required)
- **Maps**: OpenStreetMap
- **All FREE** for non-commercial use!

## 📦 Dependencies

### Frontend
- Leaflet.js 1.9.4 (maps)
- Leaflet Draw (polygon drawing)
- Vanilla JavaScript (no framework)

### Backend
- FastAPI (web framework)
- earthengine-api (satellite)
- reportlab (PDF generation)
- requests (HTTP client)
- See requirements.txt for full list

## ⚡ Performance
- Weather: 1-3 seconds
- Satellite: 5-15 seconds
- PDF: 2-5 seconds
- **Total: 10-25 seconds**

## 💰 Cost
**Monthly**: $0 (100% free tier)
- Render: 750 hours/month free
- Vercel: Unlimited static hosting
- GEE: Free for research/education
- Open-Meteo: Free unlimited

## 🎓 Learning Resources
- Leaflet: https://leafletjs.com
- FastAPI: https://fastapi.tiangolo.com
- GEE: https://developers.google.com/earth-engine
- NDVI: https://eos.com/make-an-analysis/ndvi

## 🤝 Support
- Check `docs/` folder for detailed guides
- Review error messages in browser console
- Check backend logs for API errors
- Test with sample data first

## ⚠️ Important Notes
1. **Never commit** gee-credentials.json
2. Add to .gitignore
3. Use environment variables in production
4. Free tier has rate limits
5. Satellite data depends on cloud cover

## 📈 Next Steps
1. ✅ Complete local setup
2. ✅ Test with sample farm
3. ✅ Deploy to production
4. ✅ Share with farmers!

---

**Version**: 1.0.0  
**License**: MIT  
**Built with**: ❤️ for farmers worldwide
