# Services & APIs Used by Farm Monitor

This document lists every external service and API the product uses, and clarifies free plans vs paid / auto-upgrade behavior.

---

## All APIs & Services Used

| Service / API | Where used | Purpose | Free plan? |
|--------------|------------|---------|------------|
| **Open-Meteo** | `backend/services/weather.py` | Weather: historical + forecast (temperature, precipitation, evapotranspiration) | ✅ Yes – free, no API key, no sign-up required |
| **Google Earth Engine (GEE)** | `backend/services/satellite.py` | Satellite imagery (Sentinel-2), NDVI/NDMI | ✅ Yes – free for non-commercial/research; requires Google account + (for service account) Google Cloud project |
| **OpenStreetMap (OSM)** | `frontend/js/map.js` | Map tiles (`tile.openstreetmap.org`) | ✅ Yes – free; [usage policy](https://operations.osmfoundation.org/policies/tiles/) applies (no heavy commercial abuse) |
| **Leaflet** | `frontend/index.html`, `frontend/js/map.js` | Map UI and drawing (via unpkg CDN) | ✅ Yes – open source (BSD), free |
| **Leaflet-Draw** | `frontend/index.html`, `frontend/js/map.js` | Polygon drawing on map (via unpkg CDN) | ✅ Yes – open source, free |
| **ReportLab** | `backend/services/pdf_gen.py` | PDF report generation | ✅ Yes – Python library (BSD), no external API |
| **Pillow** | `backend/services/pdf_gen.py` | Image handling in PDFs | ✅ Yes – Python library (HPND), no external API |

**Not implemented (mentioned only in comments):**

- **SendGrid / Mailgun** – `main.py` has a placeholder for “send email”; no integration. If you add one, those services have free tiers but can become paid if you exceed limits or choose a paid plan.

---

## Does anything NOT offer a free plan?

**No.** Every service/API actually used in the codebase has a free tier or is free to use under their terms:

- **Open-Meteo**: free, no API key.
- **Google Earth Engine**: free for non-commercial/research use.
- **OpenStreetMap tiles**: free under OSM tile usage policy.
- **Leaflet / Leaflet-Draw**: open source, free.
- **ReportLab / Pillow**: libraries, no external paid API.

So nothing in this codebase is “paid-only” by design.

---

## Does anything auto-switch to a paid plan “without asking”?

**Hosting (Render, Vercel, Netlify)** – **No.** They do not automatically move you to a paid plan. You stay on the free tier until you explicitly upgrade. Free tiers have limits (e.g. Render sleeps after inactivity, Vercel/Netlify have bandwidth/build limits); if you hit limits, requests may fail or get rate-limited, but you are not charged.

**Google Cloud (used for GEE service account)** – **Only if you turn on billing.**  
To use a **service account** for Earth Engine you create a Google Cloud project. By default the project can be “no billing” for GEE usage. If you **enable billing** on that project and then use other Google Cloud services or exceed free quotas, you can incur charges. So:

- **GEE itself**: free for allowed use; no automatic charge.
- **Google Cloud project**: free tier exists; you are only charged if billing is enabled and you use billable resources or exceed free quotas.

**Recommendation:** For GEE-only use, keep the Google Cloud project without a billing account (or use a billing account but monitor usage). Do not enable billing “just in case” if you want to stay strictly free.

**Open-Meteo** – Free tier; they do not auto-upgrade you to a paid plan. No credit card required for the free API.

**OpenStreetMap** – No “plan”; usage is governed by their tile policy. They don’t charge; they may ask you to stop or use your own tile server if you abuse the tiles.

---

## Summary

- **All APIs used by this product** are listed in the table above; all have free options.
- **Nothing in the codebase** is a paid-only service.
- **Nothing** (including Render, Vercel, Netlify) **automatically switches you to a paid plan**; the only place where “unexpected” charges could happen is **Google Cloud** if you enable billing and use billable resources.
- **Email (SendGrid/Mailgun)** is not implemented; if you add it later, check that provider’s free tier and overage behavior.

For a fully free setup: use Open-Meteo and OSM as-is; use GEE with a Google Cloud project without billing (or with billing disabled for this project); deploy frontend/backend on Render/Vercel/Netlify free tiers and do not click “Upgrade” unless you intend to pay.
