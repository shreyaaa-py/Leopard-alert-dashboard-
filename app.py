from pathlib import Path
from datetime import datetime, timedelta
import random

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ------------------------------------------------------------
# Leopard Detection & Campus Alert — Streamlit UI prototype
# Demo values below are simulated. Replace load_sightings() with
# your SQLite/FastAPI data source when integrating the backend.
# ------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]
CLIPS_DIR = ROOT / "media" / "clips"
SNAPSHOTS_DIR = ROOT / "media" / "snapshots"

ZONES = {
    "Zone A — Hostel Area": "CAM-01",
    "Zone B — North Forest": "CAM-02",
    "Zone C — Academic Block": "CAM-03",
    "Zone D — Library": "CAM-04",
    "Zone E — Sports Ground": "CAM-05",
    "Zone F — Southern Forest": "CAM-06",
    "Zone G — Residential": "CAM-07",
    "Zone H — Entrance": "CAM-08",
}

st.set_page_config(
    page_title="Leopard Detection & Campus Alert",
    page_icon="🐆",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
  html, body, [class*="css"] { font-family: Inter, sans-serif; }
  .stApp { background: #07111f; color: #e8eefb; }
  [data-testid="stSidebar"] { background: #0c192b; border-right: 1px solid #1d3552; }
  [data-testid="stMetric"] { background: linear-gradient(135deg,#111f33,#0d1a2b);
    border: 1px solid #203753; padding: 15px 17px; border-radius: 13px; }
  [data-testid="stMetricLabel"] { color: #aabbd7; }
  [data-testid="stMetricValue"] { color: #f4f7ff; }
  h1,h2,h3 { color: #f3f6ff !important; }
  .subtle { color:#9eb1d0; font-size:0.9rem; }
  .status { background:#0c332d; border:1px solid #17644f; color:#75edb7;
    padding:8px 12px; border-radius:10px; display:inline-block; font-weight:600; }
  .alert { background:#3a1722; border:1px solid #783146; padding:12px 14px; border-radius:10px; }
  .panel { background:#0e1c2e; border:1px solid #203753; padding:14px 16px; border-radius:13px; }
  div[data-testid="stDataFrame"] { border: 1px solid #203753; border-radius: 10px; }
  .small-note { color:#9eb1d0; font-size:0.78rem; }
</style>
""", unsafe_allow_html=True)

def load_sightings():
    """Return demo sightings; replace this function with a SQLite/API query."""
    random.seed(17)
    now = datetime.now()
    rows = []
    zone_names = list(ZONES.keys())
    weights = [0.9, 1.6, 0.7, 0.4, 0.5, 1.3, 0.6, 0.3]
    for i in range(60):
        zone = random.choices(zone_names, weights=weights, k=1)[0]
        ts = now - timedelta(hours=random.randint(1, 24 * 30), minutes=random.randint(0, 59))
        rows.append({
            "timestamp": ts,
            "zone": zone,
            "camera": ZONES[zone],
            "confidence": round(random.uniform(0.63, 0.98), 2),
            "duration_sec": random.randint(4, 38),
            "clip": None,
            "source": "SIMULATED DEMO",
        })
    # Add a few recent illustrative sightings.
    for zone, hours_ago, conf in [
        ("Zone B — North Forest", 2, .91),
        ("Zone F — Southern Forest", 5, .87),
        ("Zone D — Library", 10, .83),
        ("Zone A — Hostel Area", 14, .89),
    ]:
        rows.append({
            "timestamp": now - timedelta(hours=hours_ago),
            "zone": zone,
            "camera": ZONES[zone],
            "confidence": conf,
            "duration_sec": 15,
            "clip": None,
            "source": "SIMULATED DEMO",
        })
    return pd.DataFrame(rows).sort_values("timestamp", ascending=False)

df_all = load_sightings()

with st.sidebar:
    st.markdown("## 🐾 Leopard Alert")
    st.caption("Campus wildlife monitoring")
    page = st.radio(
        "Navigation",
        ["Dashboard", "Live Cameras", "Sightings", "Heatmap & Analytics", "Media Library"],
        label_visibility="collapsed",
    )
    st.divider()
    st.markdown("**System status**")
    st.markdown('<span class="status">● Demo dashboard online</span>', unsafe_allow_html=True)
    st.caption("Prototype data only — not connected to live CCTV.")
    st.divider()
    st.caption("Green Valley College · Wildlife · Safety · Community")

st.title("Leopard Detection & Campus Alert")
st.markdown('<div class="subtle">Safer campus · Smarter monitoring · Sighting analytics</div>', unsafe_allow_html=True)
st.write("")

# Shared filters
f1, f2, f3 = st.columns([1.3, 1.3, 1])
with f1:
    period = st.selectbox("Time period", ["Last 7 days", "Last 30 days", "All demo data"], index=0)
with f2:
    zone_filter = st.selectbox("Campus zone", ["All zones", *ZONES.keys()])
with f3:
    st.write("")
    show_demo = st.toggle("Show demo data", value=True, help="All current records are simulated placeholders.")

df = df_all.copy()
now = datetime.now()
if period == "Last 7 days":
    df = df[df["timestamp"] >= now - timedelta(days=7)]
elif period == "Last 30 days":
    df = df[df["timestamp"] >= now - timedelta(days=30)]
if zone_filter != "All zones":
    df = df[df["zone"] == zone_filter]
if not show_demo:
    df = df.iloc[0:0]

if not show_demo:
    st.info("Demo data is hidden. Connect the backend/database to display real sightings.")

if page == "Dashboard":
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Sightings in selected period", len(df), help="Count of records in the selected filters")
    c2.metric("Zones with activity", df["zone"].nunique(), f"of {len(ZONES)} zones")
    last_seen = df["timestamp"].max() if not df.empty else None
    c3.metric("Most recent sighting", last_seen.strftime("%d %b, %H:%M") if last_seen is not None else "No records")
    c4.metric("Alert pipeline", "Demo only", help="WhatsApp delivery is not connected in this UI prototype")

    left, right = st.columns([1.7, 1])
    with left:
        st.subheader("Campus activity heatmap")
        st.caption("Zone × hour-of-day activity. Replace illustrative data with recorded sightings.")
        if df.empty:
            st.info("No sightings match the selected filters.")
        else:
            heat = df.assign(hour=df["timestamp"].dt.hour).pivot_table(
                index="zone", columns="hour", values="confidence", aggfunc="count", fill_value=0
            )
            heat = heat.reindex(list(ZONES.keys()), fill_value=0)
            heat = heat.reindex(columns=list(range(24)), fill_value=0)
            fig = go.Figure(data=go.Heatmap(
                z=heat.values, x=[f"{h:02d}:00" for h in heat.columns], y=heat.index,
                colorscale=[[0, "#102b4b"], [0.25, "#1764a3"], [0.55, "#21b7a8"], [0.78, "#ffd34f"], [1, "#f04438"]],
                hovertemplate="Zone: %{y}<br>Hour: %{x}<br>Sightings: %{z}<extra></extra>",
                colorbar=dict(title="Sightings"),
            ))
            fig.update_layout(height=370, margin=dict(l=8,r=8,t=12,b=8), paper_bgcolor="#0e1c2e",
                              plot_bgcolor="#0e1c2e", font_color="#dce7fb")
            st.plotly_chart(fig, use_container_width=True)
    with right:
        st.subheader("Recent sightings")
        if df.empty:
            st.info("No recent sightings to show.")
        else:
            for _, row in df.head(5).iterrows():
                with st.container(border=True):
                    st.markdown(f"**{row['zone']}**")
                    st.caption(f"{row['timestamp']:%d %b %Y, %H:%M} · {row['camera']}")
                    st.progress(float(row["confidence"]), text=f"Confidence: {row['confidence']:.0%}")
                    st.caption(f"Duration: {row['duration_sec']} sec · {row['source']}")
    st.write("")
    a, b = st.columns([1, 1])
    with a:
        st.subheader("Zone-wise activity")
        counts = df["zone"].value_counts().reindex(list(ZONES.keys()), fill_value=0).rename_axis("Zone").reset_index(name="Sightings")
        fig = px.bar(counts, x="Zone", y="Sightings", color="Sightings", color_continuous_scale=["#2268d8", "#28c4a4"])
        fig.update_layout(height=300, margin=dict(l=5,r=5,t=10,b=5), paper_bgcolor="#0e1c2e",
                          plot_bgcolor="#0e1c2e", font_color="#dce7fb", coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
    with b:
        st.subheader("Recent clips")
        clip_files = sorted(CLIPS_DIR.glob("*")) if CLIPS_DIR.exists() else []
        videos = [p for p in clip_files if p.suffix.lower() in {".mp4", ".mov", ".webm"}]
        if videos:
            for clip in videos[:2]:
                st.markdown(f"**{clip.name}**")
                st.video(str(clip))
        else:
            st.info("No clips found yet. Add confirmed-sighting MP4 files to `media/clips/` or connect the backend clip paths.")
    st.caption("Safety note: use verified, timestamped backend records for operational decisions. Simulated data is for UI testing only.")

elif page == "Live Cameras":
    st.subheader("Camera status")
    st.info("The current architecture uses reference videos as camera stand-ins. This page is a UI placeholder until camera feeds are connected.")
    cam_cols = st.columns(2)
    for i, (zone, cam) in enumerate(ZONES.items()):
        with cam_cols[i % 2]:
            with st.container(border=True):
                st.markdown(f"**{cam} · {zone}**")
                st.markdown("🟡 Reference feed / connection pending")
                st.caption("Expected input: local video now; RTSP CCTV stream later.")
    st.subheader("Add a test clip")
    uploaded = st.file_uploader("Upload a video for preview (does not run leopard detection)", type=["mp4", "mov", "webm"])
    if uploaded:
        st.video(uploaded)
        st.warning("Preview only. This upload does not invoke the YOLO detection pipeline.")

elif page == "Sightings":
    st.subheader("Sighting records")
    st.caption("Filter records and export the current table. Demo rows are simulated.")
    if not df.empty:
        table = df.copy()
        table["timestamp"] = table["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
        table["confidence"] = (table["confidence"] * 100).round(1).astype(str) + "%"
        st.dataframe(table[["timestamp", "zone", "camera", "confidence", "duration_sec", "source"]],
                     use_container_width=True, hide_index=True)
        st.download_button("Download CSV", data=table.to_csv(index=False).encode("utf-8"),
                           file_name="leopard_sightings_demo.csv", mime="text/csv")
    else:
        st.info("No records match the current filters.")

elif page == "Heatmap & Analytics":
    st.subheader("Activity analysis")
    if df.empty:
        st.info("No records match the current filters.")
    else:
        x, y = st.columns(2)
        with x:
            hourly = df.assign(hour=df["timestamp"].dt.hour).groupby("hour").size().reindex(range(24), fill_value=0).rename("Sightings").reset_index()
            fig = px.line(hourly, x="hour", y="Sightings", markers=True, title="Sightings by hour")
            fig.update_layout(height=320, paper_bgcolor="#0e1c2e", plot_bgcolor="#0e1c2e", font_color="#dce7fb")
            st.plotly_chart(fig, use_container_width=True)
        with y:
            daily = df.assign(date=df["timestamp"].dt.date).groupby("date").size().rename("Sightings").reset_index()
            fig = px.bar(daily, x="date", y="Sightings", title="Sightings by date")
            fig.update_layout(height=320, paper_bgcolor="#0e1c2e", plot_bgcolor="#0e1c2e", font_color="#dce7fb")
            st.plotly_chart(fig, use_container_width=True)
        busiest = df["zone"].value_counts()
        if not busiest.empty:
            st.markdown(f"**Most active zone in this selection:** {busiest.index[0]} ({busiest.iloc[0]} records)")
        st.caption("Patterns are descriptive only. The architecture suggests risk prediction only after enough real historical data is collected.")

elif page == "Media Library":
    st.subheader("Confirmed-sighting clips and snapshots")
    st.caption("Expected folders: `media/clips/` and `media/snapshots/`.")
    clips = sorted(CLIPS_DIR.glob("*")) if CLIPS_DIR.exists() else []
    clips = [p for p in clips if p.suffix.lower() in {".mp4", ".mov", ".webm"}]
    snaps = sorted(SNAPSHOTS_DIR.glob("*")) if SNAPSHOTS_DIR.exists() else []
    snaps = [p for p in snaps if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}]
    m1, m2 = st.columns(2)
    m1.metric("Video clips found", len(clips))
    m2.metric("Snapshots found", len(snaps))
    if clips:
        for clip in clips:
            with st.container(border=True):
                st.markdown(f"**{clip.name}**")
                st.video(str(clip))
    else:
        st.info("No video files found. Add exported sighting clips to the clips folder.")
    if snaps:
        st.subheader("Snapshots")
        cols = st.columns(3)
        for i, snap in enumerate(snaps):
            cols[i % 3].image(str(snap), caption=snap.name, use_container_width=True)
