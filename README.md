# Leopard Detection & Campus Alert — Streamlit UI prototype

## Run locally
1. Install Python 3.10 or newer.
2. From this folder, install dependencies:
   `pip install -r requirements.txt`
3. Start the dashboard:
   `streamlit run dashboard/app.py`

## What is included
- Dashboard metrics and zone/hour activity heatmap
- Zone-wise activity bar chart
- Recent sighting list and confidence indicators
- Live camera status placeholders and safe video preview
- Sighting table with CSV export
- Analytics page and media library for clips/snapshots

## Important
All sightings are **simulated demo records**. The dashboard does not run YOLO, access live CCTV, write to SQLite, or send WhatsApp alerts. Connect these UI sections to the project's FastAPI/SQLite backend and media output folders before operational use.

## Integration points
- Replace `load_sightings()` in `dashboard/app.py` with a query to `backend/sightings.db` or a request to FastAPI.
- Put confirmed MP4 clips in `media/clips/` and snapshots in `media/snapshots/`, or adapt the media lookup to the clip paths returned by your backend.
- The architecture's proposed confirmation logic (10 of 15 frames, average confidence >= 0.5, 5-minute cooldown) belongs in the detection/backend pipeline, not in this dashboard.
