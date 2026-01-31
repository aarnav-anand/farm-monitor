# Farm Monitor - Features & Technical Details

## 🎯 Core Features

### 1. Interactive Map Interface
- **Technology**: Leaflet.js + OpenStreetMap
- **Capabilities**:
  - Pan and zoom to any location worldwide
  - Draw custom field polygons
  - Automatic area calculation (hectares)
  - GPS location finder
  - Edit and delete polygons

### 2. Satellite Health Monitoring
- **Data Source**: Sentinel-2 (ESA Copernicus)
- **Resolution**: 10 meters per pixel
- **Update Frequency**: Every 5 days
- **Metrics Calculated**:
  - **NDVI** (Normalized Difference Vegetation Index)
    - Formula: (NIR - Red) / (NIR + Red)
    - Range: -1 to +1
    - Interpretation:
      - > 0.6: Excellent vegetation health
      - 0.4-0.6: Good health
      - 0.3-0.4: Moderate health
      - < 0.3: Poor health
  
  - **NDMI** (Normalized Difference Moisture Index)
    - Formula: (NIR - SWIR) / (NIR + SWIR)
    - Indicates water stress in crops
    - Range: -1 to +1

### 3. Weather Analysis
- **Data Source**: Open-Meteo API
- **Historical Data**: Last 30 days
- **Forecast**: Next 7 days
- **Metrics Tracked**:
  - Daily rainfall (mm)
  - Temperature (min, max, mean)
  - Soil moisture (0-10cm depth)
  - Evapotranspiration
  - Wind speed
  - Precipitation probability

### 4. Intelligent Agronomic Advice
The system provides actionable recommendations based on:
- Crop type and growth stage
- Current vegetation health (NDVI)
- Moisture levels (NDMI)
- Weather patterns and forecast
- Risk assessment

**Example Recommendations**:
- "Low moisture detected (NDMI < 0.2). Consider irrigation."
- "Heavy rainfall expected. Delay fertilizer application."
- "Excellent crop health. Maintain current practices."
- "Drought risk detected. Implement water conservation."

### 5. Risk Assessment
Automatically evaluates:
- **Drought Risk**: Based on rainfall and soil moisture
- **Flood Risk**: Based on forecast precipitation
- **Disease Risk**: High rain + moderate temperature
- **Heat Stress Risk**: Temperature > 35°C
- **Overall Risk Level**: Aggregated assessment

### 6. PDF Report Generation
Professional reports include:
- Farm and crop details
- Satellite imagery analysis
- Weather summary and forecast
- NDVI/NDMI visualization
- Risk assessment matrix
- Actionable recommendations
- Data sources and timestamps

## 🔧 Technical Implementation

### Frontend Architecture

```
frontend/
├── index.html           # Main HTML structure
├── css/
│   └── styles.css       # Complete styling
└── js/
    ├── map.js           # Leaflet map & drawing
    ├── api.js           # Backend communication
    └── app.js           # Main application logic
```

**Key Technologies**:
- Vanilla JavaScript (ES6+)
- Leaflet.js 1.9.4 (maps)
- Leaflet Draw (polygon drawing)
- Fetch API (HTTP requests)
- LocalStorage (optional caching)

**No Build Process Required**: Pure HTML/CSS/JS

### Backend Architecture

```
backend/
├── main.py              # FastAPI application
└── services/
    ├── weather.py       # Open-Meteo integration
    ├── satellite.py     # Google Earth Engine
    ├── analysis.py      # Agronomic logic
    └── pdf_gen.py       # ReportLab PDF generation
```

**API Endpoints**:
- `GET /` - API information
- `GET /api/health` - Health check
- `POST /api/generate-report` - Generate farm report

**Technologies**:
- Python 3.9+
- FastAPI (async web framework)
- Google Earth Engine API
- ReportLab (PDF generation)
- Requests (HTTP client)

### Data Flow

```
1. User draws polygon on map
   ↓
2. Frontend sends coordinates + farm details to backend
   ↓
3. Backend fetches:
   - Satellite data (GEE) → Calculate NDVI, NDMI
   - Weather data (Open-Meteo) → Historical + Forecast
   ↓
4. Agronomic analyzer processes data
   - Assess crop health
   - Identify risks
   - Generate recommendations
   ↓
5. PDF generator creates report
   ↓
6. Backend returns PDF (base64 encoded)
   ↓
7. Frontend displays summary + download link
```

## 📊 Data Sources

### Google Earth Engine (Satellite)
- **Collection**: COPERNICUS/S2_SR (Sentinel-2 Surface Reflectance)
- **Bands Used**:
  - B4 (Red): 665nm
  - B8 (NIR): 842nm
  - B11 (SWIR): 1610nm
- **Cloud Filtering**: < 20% cloud cover
- **Spatial Resolution**: 10m
- **Free Tier**: Yes (for research/education)

### Open-Meteo (Weather)
- **Endpoints**:
  - `/v1/archive` (historical data)
  - `/v1/forecast` (7-day forecast)
- **Data Providers**: NOAA, DWD, Met Office, etc.
- **Update Frequency**: Hourly
- **Free Tier**: Unlimited for non-commercial
- **No API Key Required**: Yes

## 🌍 Geographic Coverage

- **Satellite Data**: Global (land areas)
- **Weather Data**: Global
- **Limitations**:
  - Ocean areas: No vegetation data
  - Polar regions: Limited coverage
  - Urban areas: May have noise
  - Cloud cover: Can delay data availability

## 📈 Performance Characteristics

### Response Times
- **Weather API**: 1-3 seconds
- **Satellite Query**: 5-15 seconds
- **PDF Generation**: 2-5 seconds
- **Total (typical)**: 10-25 seconds

### Accuracy
- **NDVI Accuracy**: ±0.05 (dependent on cloud cover)
- **Weather Accuracy**: Varies by region (generally high)
- **Area Calculation**: ±0.1% (WGS84 ellipsoid)

### Limitations
- **Sentinel-2 Revisit**: 5 days (may need to look back 30 days)
- **Cloud Cover**: Can obscure imagery
- **Resolution**: 10m (not suitable for small gardens)
- **Historical Data**: Limited to satellite mission duration

## 🔐 Security Considerations

### Data Privacy
- No user data stored (stateless API)
- No authentication required
- Reports generated on-demand
- PDFs sent as base64 (no server storage)

### API Security
- CORS configured for specific origins
- Input validation on all endpoints
- Rate limiting (recommended in production)
- HTTPS in production

### Credentials Management
- GEE credentials: Service account (not exposed)
- No API keys in frontend code
- Environment variables for sensitive data

## 🚀 Scalability

### Current Capacity (Free Tier)
- **Concurrent Users**: 10-20
- **Reports/Day**: ~100
- **Storage**: None (ephemeral)

### Scaling Options
1. **Horizontal Scaling**: Multiple Render instances
2. **Caching**: Redis for repeated queries
3. **CDN**: For static assets
4. **Background Jobs**: Queue for long-running tasks
5. **Database**: Store reports (Supabase/PostgreSQL)

### Bottlenecks
1. Google Earth Engine quota (10,000 requests/day)
2. Render free tier (sleeps after 15min)
3. PDF generation (CPU intensive)

Solutions:
- Cache satellite data by location/date
- Use background workers
- Implement request queuing

## 🎨 Customization Options

### Frontend Customization
```javascript
// Change map center
map.setView([your_lat, your_lng], zoom_level);

// Change map style
L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png').addTo(map);

// Change color scheme (in styles.css)
:root {
    --primary-color: #your-color;
}
```

### Backend Customization
```python
# Add custom crop types (analysis.py)
CROP_NDVI_THRESHOLDS = {
    'your_crop': {'excellent': 0.7, 'good': 0.5, ...}
}

# Change date ranges (satellite.py)
days_back = 14  # Instead of 30

# Add custom analysis logic (analysis.py)
def your_custom_analysis(data):
    # Your logic here
    pass
```

## 📱 Mobile Support

- Fully responsive design
- Touch-friendly map controls
- Mobile-optimized forms
- Adaptive layout for small screens
- Works on iOS and Android

## 🌐 Browser Compatibility

- Chrome 90+ ✅
- Firefox 88+ ✅
- Safari 14+ ✅
- Edge 90+ ✅
- Opera 76+ ✅

## 🔮 Future Enhancements

### Planned Features
- [ ] Multi-field comparison
- [ ] Historical NDVI trends (time series)
- [ ] Crop yield prediction
- [ ] Pest/disease detection (AI)
- [ ] Email notifications
- [ ] User accounts & saved farms
- [ ] Mobile app (React Native)
- [ ] Offline mode (PWA)
- [ ] Multiple language support

### Advanced Features
- [ ] Soil analysis integration
- [ ] Market price data
- [ ] Irrigation scheduling
- [ ] Fertilizer recommendations
- [ ] Integration with farm equipment
- [ ] Collaborative features (share reports)

## 📚 Resources

### Documentation
- Leaflet: https://leafletjs.com/reference.html
- FastAPI: https://fastapi.tiangolo.com/
- Google Earth Engine: https://developers.google.com/earth-engine
- Open-Meteo: https://open-meteo.com/en/docs

### Tutorials
- NDVI Calculation: https://eos.com/make-an-analysis/ndvi/
- Sentinel-2 Bands: https://sentinels.copernicus.eu/web/sentinel/user-guides/sentinel-2-msi/resolutions/spatial
- Agronomic Principles: FAO Agricultural Knowledge

### Community
- GEE Developers: https://groups.google.com/g/google-earth-engine-developers
- r/agriculture: https://reddit.com/r/agriculture
- Stack Overflow: Tag [google-earth-engine]

## 💡 Tips & Best Practices

### For Best Results
1. Draw accurate field boundaries
2. Provide planting date for better advice
3. Run reports regularly (weekly/monthly)
4. Compare NDVI over time
5. Act on high-risk warnings promptly

### Troubleshooting
- No satellite data? Try extending date range
- High cloud cover? Wait for clearer imagery
- Slow response? Server may be waking up (free tier)
- NDVI seems wrong? Verify field boundaries

### Performance Tips
- Limit polygon complexity (< 50 points)
- Clear browser cache if issues
- Use modern browser
- Stable internet connection

---

**Version**: 1.0.0  
**Last Updated**: January 2026  
**License**: MIT  
**Author**: Farm Monitor Team
