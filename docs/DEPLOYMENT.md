# Farm Monitor - Deployment Guide

## Zero-Cost Deployment Strategy

This guide shows how to deploy the Farm Monitor application using completely free hosting services.

## Architecture Overview

```
┌─────────────────┐
│   Vercel/       │  Frontend (Static Files)
│   Netlify       │  HTML/CSS/JS
└────────┬────────┘
         │
         │ HTTPS
         │
┌────────▼────────┐
│   Render.com    │  Backend API (Python/FastAPI)
│   Free Tier     │  Sleeps after 15min inactivity
└────────┬────────┘
         │
         ├────────► Google Earth Engine (Satellite Data)
         ├────────► Open-Meteo API (Weather Data)
         └────────► PDF Generation (In-Memory)
```

## Part 1: Backend Deployment (Render.com)

### Prerequisites
- GitHub account
- Render.com account (sign up at https://render.com)
- GEE credentials JSON file

### Step 1: Prepare Repository

1. Create new GitHub repository:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/farm-monitor.git
   git push -u origin main
   ```

2. **Important**: Add `.gitignore`:
   ```
   # Python
   venv/
   __pycache__/
   *.pyc
   *.pyo
   *.egg-info/
   
   # Credentials
   gee-credentials.json
   .env
   
   # IDE
   .vscode/
   .idea/
   
   # OS
   .DS_Store
   Thumbs.db
   ```

### Step 2: Configure for Render

Create `backend/render.yaml`:
```yaml
services:
  - type: web
    name: farm-monitor-api
    env: python
    region: oregon
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.9.16
      - key: GEE_CREDENTIALS
        sync: false
```

### Step 3: Deploy to Render

1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: farm-monitor-api
   - **Region**: Choose closest to your users
   - **Branch**: main
   - **Root Directory**: backend
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free

5. Click "Advanced" → "Add Environment Variable"
   - Add `GEE_CREDENTIALS` as secret file:
     - Copy entire content of `gee-credentials.json`
     - Save as secret file
   
6. Click "Create Web Service"

### Step 4: Wait for Deployment

- First deployment takes 5-10 minutes
- Watch logs for any errors
- Once deployed, you'll get a URL like: `https://farm-monitor-api.onrender.com`

### Step 5: Test Deployment

```bash
# Test health endpoint
curl https://your-app.onrender.com/api/health

# Should return JSON with status: healthy
```

### Important: Free Tier Limitations

⚠️ **Render Free Tier Constraints:**
- Service **sleeps after 15 minutes** of inactivity
- First request after sleep takes 50-90 seconds (cold start)
- 750 hours/month free compute
- Automatic HTTPS included

**UX Solution**: Add loading message in frontend:
```javascript
"Waking up server (free tier), this may take 30-60 seconds..."
```

## Part 2: Frontend Deployment (Vercel)

### Option A: Deploy to Vercel

1. Go to https://vercel.com
2. Sign up with GitHub
3. Click "Add New Project"
4. Import your GitHub repository
5. Configure:
   - **Root Directory**: frontend
   - **Framework Preset**: None (Vanilla HTML)
   - **Build Command**: (leave empty)
   - **Output Directory**: (leave empty)
   - **Install Command**: (leave empty)

6. **Environment Variables**: None needed for frontend

7. Click "Deploy"

8. **Update API URL**:
   - After deployment, edit `frontend/js/api.js`
   - Change `baseURL` to your Render backend URL
   - Commit and push:
     ```javascript
     const API_CONFIG = {
         baseURL: 'https://your-app.onrender.com',
         timeout: 120000
     };
     ```
   - Vercel will auto-redeploy

### Option B: Deploy to Netlify

1. Go to https://app.netlify.com
2. Sign up with GitHub
3. Click "Add new site" → "Import an existing project"
4. Choose GitHub → Select repository
5. Configure:
   - **Base directory**: frontend
   - **Build command**: (leave empty)
   - **Publish directory**: . (dot)

6. Click "Deploy site"

7. Update API URL in `api.js` (same as Vercel)

### Option C: Deploy to GitHub Pages

1. Create `frontend/.nojekyll` (empty file)

2. Update repository settings:
   - Go to Settings → Pages
   - Source: Deploy from branch
   - Branch: main
   - Folder: /frontend

3. Update API URL in `api.js`

4. Access at: `https://yourusername.github.io/farm-monitor/`

## Part 3: Environment Variables Management

### Backend Environment Variables on Render

1. Dashboard → Your Service → Environment
2. Add these variables:

```
GEE_CREDENTIALS_PATH=gee-credentials.json
ALLOWED_ORIGINS=https://your-frontend.vercel.app
ENVIRONMENT=production
```

3. **Secrets Management**:
   - For GEE credentials, use "Secret Files"
   - Don't paste credentials in plain text environment variables

### How to Handle GEE Credentials Securely

**Method 1: Secret File (Recommended)**
```
1. Render Dashboard → Environment → Add Secret File
2. Name: gee-credentials.json
3. Paste entire JSON content
4. File will be mounted at /etc/secrets/gee-credentials.json
```

Update `backend/services/satellite.py`:
```python
credentials_path = os.environ.get(
    'GEE_CREDENTIALS_PATH',
    '/etc/secrets/gee-credentials.json'
)
```

**Method 2: Environment Variable**
```python
# In satellite.py
import json
import os

gee_json = os.environ.get('GEE_CREDENTIALS_JSON')
if gee_json:
    credentials = json.loads(gee_json)
    # Use credentials dict
```

Then in Render:
```
GEE_CREDENTIALS_JSON={"type":"service_account",...}
```

## Part 4: Custom Domain (Optional)

### For Frontend (Vercel)

1. Vercel Dashboard → Your Project → Settings → Domains
2. Add your domain: `farm.yourdomain.com`
3. Update DNS records as instructed
4. Vercel provides free SSL automatically

### For Backend (Render)

1. Render Dashboard → Your Service → Settings → Custom Domain
2. Add: `api.yourdomain.com`
3. Update DNS:
   ```
   Type: CNAME
   Name: api
   Value: your-app.onrender.com
   ```
4. Free SSL included

## Part 5: Monitoring & Logging

### Render Logs

```bash
# View live logs
render logs --service farm-monitor-api --tail

# Or via dashboard:
# Dashboard → Your Service → Logs
```

### Vercel Logs

- Dashboard → Project → Deployments → Click deployment → View Function Logs

### Error Tracking (Free Tier)

**Sentry** (recommended):
```bash
pip install sentry-sdk
```

```python
# In main.py
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=0.1,
    environment="production"
)
```

## Part 6: Performance Optimization

### Backend Optimizations

1. **Enable Caching**:
```python
# Add to main.py
from functools import lru_cache

@lru_cache(maxsize=100)
def get_weather_cached(lat, lng, date):
    # Cache weather data
    pass
```

2. **Optimize GEE Queries**:
```python
# Reduce date range
days_back = 14  # Instead of 30

# Increase cloud threshold for faster results
.filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 30))
```

3. **Background Tasks**:
```python
# For email sending
from fastapi import BackgroundTasks

@app.post("/generate-report")
async def generate(request, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_email, ...)
```

### Frontend Optimizations

1. **Add Service Worker** (Progressive Web App):
```javascript
// sw.js
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request);
    })
  );
});
```

2. **Lazy Load Map**:
```javascript
// Load Leaflet only when needed
const loadLeaflet = async () => {
  if (!window.L) {
    await import('https://unpkg.com/leaflet@1.9.4/dist/leaflet.js');
  }
};
```

3. **Compress Assets**:
- Minify CSS: Use cssnano or clean-css
- Minify JS: Use terser or uglify-js
- Compress images: Use TinyPNG

## Part 7: Continuous Deployment

### Automatic Deployments

Both Vercel and Render support auto-deploy:

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Update feature"
   git push
   ```

2. **Automatic Build**:
   - Render detects changes → rebuilds backend
   - Vercel detects changes → rebuilds frontend

### Deployment Checklist

Before each deployment:

- [ ] Test locally (`http://localhost:8000` and `http://localhost:8080`)
- [ ] Update `CHANGELOG.md`
- [ ] Check for security vulnerabilities: `pip check`
- [ ] Update requirements if needed: `pip freeze > requirements.txt`
- [ ] Test API endpoints
- [ ] Verify environment variables
- [ ] Check error logs
- [ ] Test on mobile devices
- [ ] Update documentation

## Part 8: Scaling Beyond Free Tier

When you outgrow free tier:

### Backend Scaling (Render)
- **Starter Plan** ($7/month):
  - No sleep
  - 512MB RAM
  - Always-on server

- **Standard Plan** ($25/month):
  - 2GB RAM
  - Better performance
  - More compute hours

### Alternative Backends
- **Railway.app**: $5/month starter
- **Fly.io**: Free tier available
- **Heroku**: $7/month for Eco dynos
- **DigitalOcean**: $4/month droplet

### Database (Optional)
If you want to store reports:

**Supabase** (PostgreSQL):
- Free: 500MB database
- $25/month: 8GB + more features

**MongoDB Atlas**:
- Free: 512MB storage
- Shared cluster

## Part 9: Troubleshooting Deployment

### Common Issues

**1. Backend won't start**
```
Check logs:
- Render Dashboard → Logs
- Look for Python errors
- Verify requirements.txt is complete
- Check Python version
```

**2. CORS errors**
```python
# In main.py, update:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**3. GEE authentication fails**
```
- Verify secret file is uploaded correctly
- Check file path matches code
- Ensure service account has permissions
- Re-download credentials from Google Cloud
```

**4. API timeout**
```
- Increase timeout in frontend
- Optimize backend queries
- Use background tasks for long operations
- Consider caching
```

**5. Build failures**
```
- Check requirements.txt syntax
- Verify Python version compatibility
- Check for platform-specific dependencies
- Review build logs carefully
```

## Part 10: Post-Deployment

### Monitor Application

1. **Set up uptime monitoring**:
   - UptimeRobot (free): https://uptimerobot.com
   - Monitor: `https://your-api.onrender.com/api/health`

2. **Analytics** (optional):
   - Google Analytics
   - Plausible (privacy-friendly)
   - Fathom

3. **User feedback**:
   - Add feedback form
   - Monitor error logs
   - Track usage patterns

### Backup Strategy

1. **Code**: Always in GitHub
2. **Credentials**: Store securely offline
3. **Generated reports**: 
   - Either email to users
   - Or store in Supabase Storage (free 1GB)

## Cost Summary

**Monthly Costs (Free Tier)**:
- Render backend: $0 (750 hours/month)
- Vercel frontend: $0 (100GB bandwidth)
- Google Earth Engine: $0 (for research/education)
- Open-Meteo: $0 (unlimited)
- Domain (optional): ~$12/year
- **Total: $0/month** (or $1/month if you buy domain)

**With Paid Tiers**:
- Render Starter: $7/month
- Vercel Pro: $20/month
- Domain: $12/year
- **Total: ~$28/month**

---

## Quick Deploy Commands

```bash
# One-time setup
git init
git add .
git commit -m "Initial deployment"
git remote add origin https://github.com/username/farm-monitor.git
git push -u origin main

# Then:
# 1. Deploy backend on Render (connect GitHub)
# 2. Deploy frontend on Vercel (connect GitHub)
# 3. Update API_CONFIG.baseURL in frontend/js/api.js
# 4. Commit and push → auto-deploy

# For updates:
git add .
git commit -m "Update description"
git push  # Auto-deploys to both services
```

🚀 **Your farm monitoring application is now live and accessible worldwide!**

## Support

- Render Support: https://render.com/docs
- Vercel Support: https://vercel.com/docs
- GEE Forum: https://groups.google.com/g/google-earth-engine-developers

---

Last updated: 2024
