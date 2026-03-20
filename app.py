import streamlit as st
from storage import initialize_storage
initialize_storage()

st.set_page_config(
    page_title="MEC TimeTable AI",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="collapsed"
)

# Inject everything as one single markdown block
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Bebas+Neue&family=JetBrains+Mono:wght@400;700&display=swap');

* { margin:0; padding:0; box-sizing:border-box; }

html, body, [data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main,
.block-container {
    background:#0a0a0f !important;
    color:#e8e8f0 !important;
    font-family:'Space Grotesk',sans-serif !important;
    padding:0 !important;
    max-width:100% !important;
    overflow-x:hidden;
}

[data-testid="stHeader"],[data-testid="stToolbar"],
footer,#MainMenu,[data-testid="stSidebar"] { display:none !important; }

.hero {
    min-height:100vh;
    display:flex;
    flex-direction:column;
    align-items:center;
    justify-content:center;
    position:relative;
    overflow:hidden;
    padding:60px 24px 120px;
    background:#0a0a0f;
}
.hero::before {
    content:'';
    position:absolute;
    inset:0;
    background-image:
        linear-gradient(rgba(99,102,241,.07) 1px,transparent 1px),
        linear-gradient(90deg,rgba(99,102,241,.07) 1px,transparent 1px);
    background-size:60px 60px;
    animation:gridMove 20s linear infinite;
    pointer-events:none;
}
@keyframes gridMove { to { transform:translateY(60px); } }

.orb {
    position:absolute;
    border-radius:50%;
    filter:blur(80px);
    opacity:.2;
    pointer-events:none;
    animation:float 8s ease-in-out infinite;
}
.o1 { width:600px;height:600px;background:radial-gradient(#6366f1,transparent);top:-200px;left:-150px; }
.o2 { width:450px;height:450px;background:radial-gradient(#ec4899,transparent);bottom:-100px;right:-100px;animation-delay:3s; }
.o3 { width:350px;height:350px;background:radial-gradient(#10b981,transparent);top:40%;left:45%;animation-delay:5s; }

@keyframes float {
    0%,100% { transform:translate(0,0) scale(1); }
    33%      { transform:translate(30px,-20px) scale(1.05); }
    66%      { transform:translate(-20px,15px) scale(.97); }
}

.badge {
    display:inline-flex;
    align-items:center;
    gap:8px;
    background:rgba(99,102,241,.12);
    border:1px solid rgba(99,102,241,.35);
    border-radius:100px;
    padding:7px 20px;
    font-family:'JetBrains Mono',monospace;
    font-size:11px;
    letter-spacing:.1em;
    color:#a5b4fc;
    margin-bottom:36px;
    position:relative;
    z-index:2;
    animation:fadeUp .8s ease both;
}
.dot {
    width:7px;height:7px;
    background:#6366f1;
    border-radius:50%;
    box-shadow:0 0 8px #6366f1;
    animation:pulse 2s infinite;
}
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.4;transform:scale(1.4)} }

.hl {
    position:relative;
    z-index:2;
    text-align:center;
    margin-bottom:20px;
    animation:fadeUp 1s .2s ease both;
}
.hl-solid {
    font-family:'Bebas Neue',sans-serif;
    font-size:clamp(80px,13vw,150px);
    line-height:.88;
    letter-spacing:.03em;
    background:linear-gradient(135deg,#fff 30%,#a5b4fc 60%,#ec4899 90%);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
    background-clip:text;
}
.hl-outline {
    font-family:'Bebas Neue',sans-serif;
    font-size:clamp(80px,13vw,150px);
    line-height:.88;
    letter-spacing:.03em;
    color:transparent;
    -webkit-text-stroke:2px rgba(165,180,252,.3);
}
.hl-sub-title {
    font-family:'Space Grotesk',sans-serif;
    font-size:clamp(22px,3vw,32px);
    font-weight:300;
    color:rgba(200,200,220,.7);
    letter-spacing:.25em;
    text-transform:uppercase;
    text-align:center;
    margin-top:8px;
    position:relative;
    z-index:2;
    animation:fadeUp 1s .35s ease both;
}
.hl-powered {
    font-family:'JetBrains Mono',monospace;
    font-size:11px;
    color:rgba(165,180,252,.45);
    letter-spacing:.3em;
    text-transform:uppercase;
    text-align:center;
    margin-top:12px;
    position:relative;
    z-index:2;
    animation:fadeUp 1s .45s ease both;
}

.sub {
    font-size:17px;
    color:rgba(200,200,220,.55);
    max-width:480px;
    margin:24px auto 0;
    line-height:1.65;
    text-align:center;
    position:relative;
    z-index:2;
    animation:fadeUp 1s .4s ease both;
}

.stats {
    display:flex;
    gap:48px;
    justify-content:center;
    margin:48px 0;
    flex-wrap:wrap;
    position:relative;
    z-index:2;
    animation:fadeUp 1s .6s ease both;
}
.si { text-align:center; }
.sn {
    font-family:'Bebas Neue',sans-serif;
    font-size:52px;
    line-height:1;
    background:linear-gradient(135deg,#6366f1,#ec4899);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
    background-clip:text;
}
.sl {
    font-size:10px;
    letter-spacing:.18em;
    color:rgba(200,200,220,.35);
    text-transform:uppercase;
    margin-top:4px;
    font-family:'JetBrains Mono',monospace;
}
.sdiv { width:1px;height:52px;background:rgba(255,255,255,.08);align-self:center; }

.feats {
    display:flex;
    gap:14px;
    justify-content:center;
    flex-wrap:wrap;
    position:relative;
    z-index:2;
    margin-top:0;
    animation:fadeUp 1s 1s ease both;
}
.fc {
    background:rgba(255,255,255,.03);
    border:1px solid rgba(255,255,255,.07);
    border-radius:14px;
    padding:22px 20px;
    width:210px;
    text-align:center;
    transition:all .3s;
}
.fc:hover {
    background:rgba(99,102,241,.08);
    border-color:rgba(99,102,241,.3);
    transform:translateY(-4px);
}
.fi { font-size:26px;margin-bottom:10px; }
.ft { font-size:13px;font-weight:600;color:#e8e8f0;margin-bottom:5px; }
.fd { font-size:11px;color:rgba(200,200,220,.38);line-height:1.5; }

/* CTA button via Streamlit */
div[data-testid="stButton"] button {
    background:linear-gradient(135deg,#6366f1,#8b5cf6) !important;
    color:white !important;
    border:none !important;
    border-radius:14px !important;
    padding:18px 56px !important;
    font-family:'Space Grotesk',sans-serif !important;
    font-size:17px !important;
    font-weight:700 !important;
    letter-spacing:.03em !important;
    box-shadow:0 0 40px rgba(99,102,241,.35),0 8px 32px rgba(0,0,0,.4) !important;
    transition:all .3s !important;
    min-width:260px !important;
}
div[data-testid="stButton"] button:hover {
    transform:translateY(-3px) scale(1.02) !important;
    box-shadow:0 0 60px rgba(99,102,241,.55),0 16px 48px rgba(0,0,0,.5) !important;
}

.ticker {
    position:fixed;
    bottom:0;left:0;right:0;
    background:rgba(10,10,15,.92);
    border-top:1px solid rgba(99,102,241,.18);
    padding:9px 0;
    overflow:hidden;
    z-index:999;
    backdrop-filter:blur(12px);
}
.ti {
    display:flex;
    gap:64px;
    animation:tick 30s linear infinite;
    white-space:nowrap;
}
.ti span {
    font-family:'JetBrains Mono',monospace;
    font-size:11px;
    color:rgba(165,180,252,.45);
    letter-spacing:.08em;
}
.ti b { color:#6366f1; }
@keyframes tick { from{transform:translateX(0)} to{transform:translateX(-50%)} }

@keyframes fadeUp {
    from{opacity:0;transform:translateY(28px)}
    to{opacity:1;transform:translateY(0)}
}

/* spacer so button appears in hero */
.cta-zone { position:relative; z-index:2; margin:40px 0 48px; text-align:center; animation:fadeUp 1s .8s ease both; }
</style>

<div class="hero">
  <div class="orb o1"></div>
  <div class="orb o2"></div>
  <div class="orb o3"></div>

  <div class="badge"><div class="dot"></div>POWERED BY D3QN REINFORCEMENT LEARNING</div>

  <div class="hl">
    <div class="hl-solid">CHRONOAI</div>
  </div>
  <div class="hl-sub-title">Smart Timetable Generator</div>
  <div class="hl-powered">✦ Powered by AI ✦</div>

  <p class="sub">Model Engineering College's AI scheduling system.<br>42 divisions. Zero conflicts. Instant results.</p>

  <div class="stats">
    <div class="si"><div class="sn">42</div><div class="sl">Divisions</div></div>
    <div class="sdiv"></div>
    <div class="si"><div class="sn">313</div><div class="sl">Subjects</div></div>
    <div class="sdiv"></div>
    <div class="si"><div class="sn">100%</div><div class="sl">Placement</div></div>
    <div class="sdiv"></div>
    <div class="si"><div class="sn">0</div><div class="sl">Conflicts</div></div>
  </div>

  <div class="cta-zone" id="cta"></div>

  <div class="feats">
    <div class="fc"><div class="fi">🧠</div><div class="ft">D3QN Brain</div><div class="fd">Dueling Double Deep Q-Network learns optimal slot assignments</div></div>
    <div class="fc"><div class="fi">⚡</div><div class="ft">Instant Generation</div><div class="fd">Full college timetable generated in seconds, not hours</div></div>
    <div class="fc"><div class="fi">🔒</div><div class="ft">Hard Constraints</div><div class="fd">Zero teacher clashes, lab blocks enforced, Honours synced</div></div>
  </div>
</div>

<div class="ticker">
  <div class="ti">
    <span>🎓 <b>MEC</b> AI TIMETABLE &nbsp;·&nbsp;</span>
    <span>⚡ <b>D3QN</b> REINFORCEMENT LEARNING &nbsp;·&nbsp;</span>
    <span>📅 <b>S2 / S4 / S6 / S8</b> ALL SEMESTERS &nbsp;·&nbsp;</span>
    <span>🏫 <b>CS · EC · EE · ME · EB · EV · CU</b> DEPARTMENTS &nbsp;·&nbsp;</span>
    <span>✅ <b>ZERO</b> TEACHER CONFLICTS &nbsp;·&nbsp;</span>
    <span>🧠 <b>AI-POWERED</b> SCHEDULING ENGINE &nbsp;·&nbsp;</span>
    <span>🎓 <b>MEC</b> AI TIMETABLE &nbsp;·&nbsp;</span>
    <span>⚡ <b>D3QN</b> REINFORCEMENT LEARNING &nbsp;·&nbsp;</span>
    <span>📅 <b>S2 / S4 / S6 / S8</b> ALL SEMESTERS &nbsp;·&nbsp;</span>
    <span>🏫 <b>CS · EC · EE · ME · EB · EV · CU</b> DEPARTMENTS &nbsp;·&nbsp;</span>
    <span>✅ <b>ZERO</b> TEACHER CONFLICTS &nbsp;·&nbsp;</span>
    <span>🧠 <b>AI-POWERED</b> SCHEDULING ENGINE &nbsp;·&nbsp;</span>
  </div>
</div>
""", unsafe_allow_html=True)

# The CTA button — Streamlit renders this inside the page flow
col1, col2, col3 = st.columns([1,1,1])
with col2:
    if st.button("⚡  Launch Dashboard  →", use_container_width=True):
        st.switch_page("pages/dashboard.py")