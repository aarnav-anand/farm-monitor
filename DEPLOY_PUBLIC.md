# How to Upload Farm Monitor to the Public (Free)

You have two parts: **backend API** (Python) and **frontend website** (HTML/JS). Deploy both, then connect them.

---

## 1. Put your code on GitHub

If you haven’t already:

```bash
cd "C:\Users\Dell\Desktop\Farm Monitor"
git init
git add .
git commit -m "Initial commit"
# Create a new repo at github.com, then:
git remote add origin https://github.com/YOUR_USERNAME/farm-monitor.git
git branch -M main
git push -u origin main
```

**Important:** Don’t commit secrets. Your `.gitignore` should include `gee-credentials.json`, `.env`, and `venv/`.

---

## 2. Deploy the backend (Render.com)

1. Sign up at **https://render.com** (free).
2. **New +** → **Web Service**.
3. Connect your GitHub repo and select it.
4. Set:
   - **Name:** `farm-monitor-api` (or any name)
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Free
5. **Environment** (in Render dashboard):
   - Add **Secret File**: name `gee-credentials.json`, paste the contents of your local `backend/gee-credentials.json`.
   - If your code reads from a path, set **GEE_CREDENTIALS_PATH** to the path Render gives (e.g. `/etc/secrets/gee-credentials.json`), or match what your app expects.
   - **If the build fails** (e.g. pandas/numpy errors): add **Environment Variable** `PYTHON_VERSION` = `3.11.9` (the app uses Python 3.11; Render’s default 3.13 is not supported by pandas 2.2).
6. Create the service. Wait for the first deploy (a few minutes).
7. Copy your backend URL, e.g. **`https://farm-monitor-api.onrender.com`**.

**Free tier note:** The app sleeps after ~15 minutes of no traffic. The first request after that can take 30–60 seconds (“waking up”).

---

## 3. Deploy the frontend (Vercel or Netlify)

### Option A – Vercel

1. Sign up at **https://vercel.com** (free, use GitHub).
2. **Add New** → **Project** → import your GitHub repo.
3. Set **Root Directory** to **`frontend`**.
4. **Framework Preset:** Other / None. Leave build command blank.
5. Deploy. You’ll get a URL like **`https://farm-monitor-xxx.vercel.app`**.

### Option B – Netlify

1. Sign up at **https://netlify.com** (free, use GitHub).
2. **Add new site** → **Import from Git** → choose your repo.
3. **Base directory:** `frontend`. **Publish directory:** `.` (or leave default).
4. Deploy. You’ll get a URL like **`https://something.netlify.app`**.

---

## 4. Point the frontend to your backend

The site in the browser must call your **public backend URL**, not `localhost`.

**Edit `frontend/js/api.js`** and set `PRODUCTION_API_URL` to your Render URL:

```javascript
const PRODUCTION_API_URL = 'https://farm-monitor-api.onrender.com'; // your Render URL
```

- **Local:** When you open the app from `http://localhost:5500`, it will still use `http://localhost:8000`.
- **Production:** When users open your Vercel/Netlify URL, the app will use your Render URL.

Then commit and push:

```bash
git add frontend/js/api.js
git commit -m "Use production API URL"
git push
```

Vercel/Netlify will redeploy automatically. Your public site will now use the backend.

---

## 5. Checklist

- [ ] Repo on GitHub (no `gee-credentials.json` or `.env` committed).
- [ ] Backend on Render, env/secret for GEE set, health check works:  
  `https://YOUR-APP.onrender.com/api/health`
- [ ] Frontend on Vercel or Netlify, root = `frontend`.
- [ ] `frontend/js/api.js` `baseURL` = your Render URL (or use the host-based logic above).
- [ ] Open the frontend URL, draw a polygon, generate report — no “can’t connect” errors.

---

## More detail

- **Full deployment options (custom domain, CORS, scaling):** see **`docs/DEPLOYMENT.md`**.
- **Backend env vars and GEE:** see **`docs/DEPLOYMENT.md`** “Environment Variables” and “GEE Credentials”.

Once the checklist is done, your Farm Monitor site is public and usable by anyone with the link.
