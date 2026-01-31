# How to Test Backend + Frontend Locally

## 1. Start the backend (Terminal 1)

From the project root:

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Or on Windows double‑click `backend\start.bat`.

**Expected:** Server runs at **http://localhost:8000**. You should see:
- `Server: http://localhost:8000`
- `Docs: http://localhost:8000/docs`

Optional: open http://localhost:8000/docs to confirm the API and try endpoints.

---

## 2. Start the frontend (Terminal 2)

Use a **different port** (e.g. 5500) so it doesn’t conflict with the backend:

```bash
cd frontend
python -m http.server 5500
```

**Expected:** Static server at **http://localhost:5500**.

---

## 3. Open the app in the browser

1. Go to **http://localhost:5500** (the frontend).
2. The app will call the backend at **http://localhost:8000** (configured in `frontend/js/api.js`).

---

## 4. Run a full flow test

1. On the map: click the **polygon tool** (⬟), then click points to draw a field and double‑click to close.
2. Fill **Farm name** and **Crop type** (email and planting date optional).
3. Click **Generate Report**.
4. Check:
   - Loading modal and steps.
   - Either the success modal with PDF download, or a clear error message (no `[object Object]`).

---

## Quick check that backend is used

- **Backend not running:** "Generate Report" will show a connection error (e.g. “Unable to connect to the server”).
- **Backend running:** Request goes to `http://localhost:8000/api/generate-report`; check the **Network** tab in DevTools (F12) to see the request and response.

---

## Port summary

| Service   | URL                     | Port |
|----------|-------------------------|------|
| Backend  | http://localhost:8000   | 8000 |
| Frontend | http://localhost:5500   | 5500 |

Frontend `api.js` uses `baseURL: 'http://localhost:8000'`; change it only if your backend runs elsewhere (e.g. production).
