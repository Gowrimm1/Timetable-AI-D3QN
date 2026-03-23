import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard · MEC AI", layout="wide", page_icon="⚡",
                   initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Bebas+Neue&family=JetBrains+Mono:wght@400;700&display=swap');

* { box-sizing: border-box; }
html, body, [data-testid="stAppViewContainer"] {
    background: #0a0a0f !important;
    color: #e8e8f0 !important;
    font-family: 'Space Grotesk', sans-serif !important;
}
[data-testid="stHeader"] { display: none !important; }
[data-testid="stSidebar"] {
    background: #0f0f1a !important;
    border-right: 1px solid rgba(99,102,241,0.15) !important;
}
[data-testid="stSidebar"] * { color: #e8e8f0 !important; }

/* Nav links */
[data-testid="stSidebarNav"] a {
    color: rgba(200,200,220,0.6) !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 14px !important;
    border-radius: 8px !important;
    transition: all 0.2s !important;
    padding: 8px 12px !important;
}
[data-testid="stSidebarNav"] a:hover,
[data-testid="stSidebarNav"] a[aria-selected="true"] {
    background: rgba(99,102,241,0.15) !important;
    color: #a5b4fc !important;
}

.block-container { padding: 2rem 2.5rem !important; max-width: 100% !important; }

/* ── PAGE HEADER ─────────────────────────────────────── */
.page-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 32px;
    padding-bottom: 24px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}
.page-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 48px;
    letter-spacing: 0.05em;
    background: linear-gradient(135deg, #fff 40%, #a5b4fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
}
.page-subtitle {
    font-size: 13px;
    color: rgba(200,200,220,0.4);
    font-family: 'JetBrains Mono', monospace;
    margin-top: 4px;
    letter-spacing: 0.05em;
}
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(16,185,129,0.1);
    border: 1px solid rgba(16,185,129,0.3);
    border-radius: 100px;
    padding: 8px 20px;
    font-size: 13px;
    color: #6ee7b7;
    font-family: 'JetBrains Mono', monospace;
}
.status-pill::before {
    content: '';
    width: 8px; height: 8px;
    background: #10b981;
    border-radius: 50%;
    box-shadow: 0 0 8px #10b981;
    animation: blink 2s infinite;
}
@keyframes blink {
    0%,100% { opacity:1; } 50% { opacity:0.3; }
}

/* ── KPI CARDS ───────────────────────────────────────── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 32px;
}
.kpi-card {
    background: linear-gradient(135deg, rgba(255,255,255,0.04), rgba(255,255,255,0.01));
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 24px;
    position: relative;
    overflow: hidden;
    transition: all 0.3s;
}
.kpi-card:hover {
    border-color: rgba(99,102,241,0.3);
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(99,102,241,0.1);
}
.kpi-card::after {
    content: '';
    position: absolute;
    top: 0; right: 0;
    width: 80px; height: 80px;
    border-radius: 0 16px 0 80px;
    background: var(--accent);
    opacity: 0.06;
}
.kpi-icon { font-size: 22px; margin-bottom: 12px; }
.kpi-num {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 44px;
    line-height: 1;
    color: var(--accent-color);
}
.kpi-label {
    font-size: 12px;
    color: rgba(200,200,220,0.45);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-top: 4px;
    font-family: 'JetBrains Mono', monospace;
}
.kpi-trend {
    font-size: 11px;
    color: #6ee7b7;
    margin-top: 8px;
    font-family: 'JetBrains Mono', monospace;
}

/* ── DEPT GRID ───────────────────────────────────────── */
.dept-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 80px;
}
.dept-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 18px;
    display: flex;
    align-items: center;
    gap: 14px;
    cursor: pointer;
    transition: all 0.25s;
}
.dept-card:hover {
    background: rgba(99,102,241,0.08);
    border-color: rgba(99,102,241,0.25);
    transform: translateX(4px);
}
.dept-dot {
    width: 40px; height: 40px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    flex-shrink: 0;
}
.dept-name {
    font-weight: 600;
    font-size: 14px;
    color: #e8e8f0;
}
.dept-sub {
    font-size: 11px;
    color: rgba(200,200,220,0.4);
    margin-top: 2px;
    font-family: 'JetBrains Mono', monospace;
}

/* ── QUICK ACTIONS ───────────────────────────────────── */
.action-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin-bottom: 32px;
}
.action-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 28px 24px;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s;
    position: relative;
    overflow: hidden;
}
.action-card:hover {
    background: rgba(99,102,241,0.08);
    border-color: rgba(99,102,241,0.3);
    transform: translateY(-3px);
    box-shadow: 0 12px 40px rgba(99,102,241,0.15);
}
.action-icon {
    font-size: 36px;
    margin-bottom: 14px;
    display: block;
}
.action-title {
    font-size: 16px;
    font-weight: 600;
    color: #e8e8f0;
    margin-bottom: 6px;
}
.action-desc {
    font-size: 12px;
    color: rgba(200,200,220,0.4);
    line-height: 1.5;
}
.action-arrow {
    position: absolute;
    bottom: 16px; right: 20px;
    font-size: 18px;
    color: rgba(165,180,252,0.3);
    transition: all 0.3s;
}
.action-card:hover .action-arrow {
    color: #6366f1;
    transform: translate(3px, -3px);
}

/* ── SECTION HEADERS ─────────────────────────────────── */
.section-head {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 16px;
}
.section-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 22px;
    letter-spacing: 0.05em;
    color: #e8e8f0;
}
.section-line {
    flex: 1;
    height: 1px;
    background: rgba(255,255,255,0.06);
}

/* ── STREAMLIT BUTTON OVERRIDES ──────────────────────── */
.stButton > button {
    background: rgba(99,102,241,0.12) !important;
    color: #a5b4fc !important;
    border: 1px solid rgba(99,102,241,0.25) !important;
    border-radius: 10px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    transition: all 0.3s !important;
}
.stButton > button:hover {
    background: rgba(99,102,241,0.25) !important;
    border-color: rgba(99,102,241,0.5) !important;
    transform: translateY(-1px) !important;
}
</style>
""", unsafe_allow_html=True)

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <div>
        <div class="page-title">DASHBOARD</div>
        <div class="page-subtitle">MODEL ENGINEERING COLLEGE · AI TIMETABLE SYSTEM</div>
    </div>
    <div class="status-pill">SYSTEM ONLINE</div>
</div>
""", unsafe_allow_html=True)

# ── KPI Cards ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="kpi-grid">
    <div class="kpi-card" style="--accent:rgba(99,102,241,0.3); --accent-color:#a5b4fc;">
        <div class="kpi-icon">🏫</div>
        <div class="kpi-num">42</div>
        <div class="kpi-label">Total Divisions</div>
        <div class="kpi-trend">▲ All departments covered</div>
    </div>
    <div class="kpi-card" style="--accent:rgba(236,72,153,0.3); --accent-color:#f9a8d4;">
        <div class="kpi-icon">📚</div>
        <div class="kpi-num">313</div>
        <div class="kpi-label">Subject Records</div>
        <div class="kpi-trend">▲ S2 · S4 · S6 · S8</div>
    </div>
    <div class="kpi-card" style="--accent:rgba(16,185,129,0.3); --accent-color:#6ee7b7;">
        <div class="kpi-icon">✅</div>
        <div class="kpi-num">100%</div>
        <div class="kpi-label">Placement Rate</div>
        <div class="kpi-trend">▲ Zero unscheduled subjects</div>
    </div>
    <div class="kpi-card" style="--accent:rgba(245,158,11,0.3); --accent-color:#fcd34d;">
        <div class="kpi-icon">⚡</div>
        <div class="kpi-num">0</div>
        <div class="kpi-label">Conflicts</div>
        <div class="kpi-trend">▲ Hard constraints enforced</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Quick Actions ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="section-head">
    <div class="section-title">QUICK ACTIONS</div>
    <div class="section-line"></div>
</div>
<div class="action-grid">
    <div class="action-card">
        <span class="action-icon">📤</span>
        <div class="action-title">Upload & Generate</div>
        <div class="action-desc">Upload your SubAllotment CSV and generate timetables for all semesters instantly</div>
        <div class="action-arrow">↗</div>
    </div>
    <div class="action-card">
        <span class="action-icon">📅</span>
        <div class="action-title">View Timetables</div>
        <div class="action-desc">Browse generated schedules by division, semester, or department</div>
        <div class="action-arrow">↗</div>
    </div>
    <div class="action-card">
        <span class="action-icon">👩‍🏫</span>
        <div class="action-title">Manage Faculty</div>
        <div class="action-desc">Add, edit, or view faculty details and subject assignments</div>
        <div class="action-arrow">↗</div>
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("📤  Upload CSV & Generate", use_container_width=True):
        st.switch_page("pages/upload_csv.py")
with col2:
    if st.button("📅  View Timetables", use_container_width=True):
        st.switch_page("pages/timetable_viewer.py")
with col3:
    if st.button("👩‍🏫  Manage Teachers", use_container_width=True):
        st.switch_page("pages/manage_teachers.py")

st.markdown("<br>", unsafe_allow_html=True)

# ── Departments ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="section-head">
    <div class="section-title">DEPARTMENTS</div>
    <div class="section-line"></div>
</div>
<div class="dept-grid">
    <div class="dept-card">
        <div class="dept-dot" style="background:rgba(99,102,241,0.15)">💻</div>
        <div>
            <div class="dept-name">Computer Science</div>
            <div class="dept-sub">CS2A-CB · CS4A-CB · CS6A-CB · CS8A-CB</div>
        </div>
    </div>
    <div class="dept-card">
        <div class="dept-dot" style="background:rgba(236,72,153,0.15)">📡</div>
        <div>
            <div class="dept-name">Electronics & Comm</div>
            <div class="dept-sub">EC2A-B · EC4A-B · EC6A-B · EC8A-B</div>
        </div>
    </div>
    <div class="dept-card">
        <div class="dept-dot" style="background:rgba(16,185,129,0.15)">⚡</div>
        <div>
            <div class="dept-name">Electrical Eng</div>
            <div class="dept-sub">EE2 · EE4 · EE6 · EE8 · EEE</div>
        </div>
    </div>
    <div class="dept-card">
        <div class="dept-dot" style="background:rgba(245,158,11,0.15)">⚙️</div>
        <div>
            <div class="dept-name">Mechanical Eng</div>
            <div class="dept-sub">ME2 · ME4 · ME6 · ME8</div>
        </div>
    </div>
    <div class="dept-card">
        <div class="dept-dot" style="background:rgba(139,92,246,0.15)">🔬</div>
        <div>
            <div class="dept-name">Biomedical Eng</div>
            <div class="dept-sub">EB2 · EB4 · EB6 · EB8</div>
        </div>
    </div>
    <div class="dept-card">
        <div class="dept-dot" style="background:rgba(6,182,212,0.15)">🌿</div>
        <div>
            <div class="dept-name">Electronics (EV)</div>
            <div class="dept-sub">EV2 · EV4 · EV6</div>
        </div>
    </div>
    <div class="dept-card">
        <div class="dept-dot" style="background:rgba(248,113,113,0.15)">🎓</div>
        <div>
            <div class="dept-name">Computer Sci (CU)</div>
            <div class="dept-sub">CU2 · CU4 · CU6 · CU8</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 40px 0 80px; color: rgba(200,200,220,0.2);
            font-family:'JetBrains Mono',monospace; font-size:11px; letter-spacing:0.1em;">
    MEC AI TIMETABLE SYSTEM &nbsp;·&nbsp; BUILT WITH D3QN + STABLE BASELINES3
    &nbsp;·&nbsp; MODEL ENGINEERING COLLEGE, THRIKKAKARA
</div>
""", unsafe_allow_html=True)