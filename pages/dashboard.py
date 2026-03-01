import streamlit as st

st.set_page_config(layout="wide")

# =====================
# Custom CSS
# =====================
st.markdown("""
<style>

.stApp {
    background-color: #0f172a;
    color: white;
}

/* HERO SECTION */
.hero {
    padding: 80px 40px;
    border-radius: 20px;
    background: linear-gradient(135deg, #6d28d9, #9333ea, #c026d3);
    color: white;
    text-align: left;
}

.hero h1 {
    font-size: 55px;
    font-weight: 800;
}

.hero span {
    color: #fde047;
}

.hero p {
    font-size: 20px;
    margin-top: 15px;
    color: #f3f4f6;
}

/* STATS */
.stat-box {
    background: #1e293b;
    padding: 30px;
    border-radius: 15px;
    text-align: center;
    transition: 0.3s;
}

.stat-box:hover {
    transform: translateY(-5px);
    background: #334155;
}

.stat-number {
    font-size: 30px;
    font-weight: 700;
    color: #38bdf8;
}

.stat-label {
    font-size: 16px;
    color: #cbd5e1;
}

/* FEATURE CARDS */
.feature-card {
    background: #1e293b;
    padding: 30px;
    border-radius: 20px;
    margin-bottom: 20px;
    transition: 0.3s;
}

.feature-card:hover {
    transform: scale(1.02);
    background: #334155;
}

.feature-card h3 {
    color: #22d3ee;
    margin-bottom: 10px;
}

.feature-card p {
    color: #cbd5e1;
}

</style>
""", unsafe_allow_html=True)


# =====================
# HERO SECTION
# =====================
st.markdown("""
<div class="hero">
    <h1>Meet Your AI <span>Scheduling Assistant</span></h1>
    <p>Generate conflict-free university timetables in seconds. 
    Upload data, optimize scheduling, and visualize results beautifully.</p>
</div>
""", unsafe_allow_html=True)

st.write("")

# =====================
# STATS ROW
# =====================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-number">8</div>
        <div class="stat-label">Semesters</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-number">6</div>
        <div class="stat-label">Periods / Day</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-number">480+</div>
        <div class="stat-label">Subjects</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-number">99.9%</div>
        <div class="stat-label">Conflict-Free</div>
    </div>
    """, unsafe_allow_html=True)

st.write("\n\n")

# =====================
# FEATURES GRID
# =====================
st.markdown("## 🚀 AI-Powered Benefits")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-card">
        <h3>Conflict-Free Scheduling</h3>
        <p>Automatically eliminates teacher, room, and subject clashes 
        for optimized academic planning.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-card">
        <h3>Smart Recommendations</h3>
        <p>AI suggests better slot distributions based on constraints 
        and historical data.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <h3>Time & Cost Efficiency</h3>
        <p>Reduce manual scheduling effort from hours to seconds.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-card">
        <h3>Optimized Resource Allocation</h3>
        <p>Efficient distribution of teachers and classrooms.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <h3>Customizable Constraints</h3>
        <p>Define lab durations, semester-specific rules, 
        and teacher preferences easily.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-card">
        <h3>Real-Time Updates</h3>
        <p>Instantly regenerate schedules after modifications.</p>
    </div>
    """, unsafe_allow_html=True)

    # =====================
# SYSTEM MODULES SECTION
# =====================

st.write("\n\n")
st.markdown("## 🧭 System Modules")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-card">
        <h3>📚 Manage Subjects</h3>
        <p>Add, edit and manage subject data.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Manage Subjects", key="subjects", use_container_width=True):
        st.switch_page("pages/manage_subjects.py")

with col2:
    st.markdown("""
    <div class="feature-card">
        <h3>👩‍🏫 Manage Teachers</h3>
        <p>Maintain teacher records and assignments.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Manage Teachers", key="teachers", use_container_width=True):
        st.switch_page("pages/manage_teachers.py")

with col3:
    st.markdown("""
    <div class="feature-card">
        <h3>🏫 Manage Rooms</h3>
        <p>Configure classrooms and lab allocations.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Manage Rooms", key="rooms", use_container_width=True):
        st.switch_page("pages/manage_rooms.py")

col4, col5, col6 = st.columns(3)

with col4:
    st.markdown("""
    <div class="feature-card">
        <h3>📂 Upload Data</h3>
        <p>Upload CSV files for scheduling.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Upload", key="upload", use_container_width=True):
       st.switch_page("pages/upload_csv.py")

with col5:
    st.markdown("""
    <div class="feature-card">
        <h3>⚡ Generate Timetable</h3>
        <p>Run AI scheduling engine.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Generate", key="generate", use_container_width=True):
        st.switch_page("pages/generate.py")

with col6:
    st.markdown("""
    <div class="feature-card">
        <h3>📅 View Timetable</h3>
        <p>Visualize generated timetable.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open View", key="view", use_container_width=True):
        st.switch_page("pages/view.py")

        # =====================
# MODULE NAVIGATION
# =====================

st.write("\n\n")
st.markdown("## 🧭 Quick Access")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📚 Manage Subjects", use_container_width=True):
        st.switch_page("pages/manage_subjects.py")

with col2:
    if st.button("👩‍🏫 Manage Teachers", use_container_width=True):
        st.switch_page("pages/manage_teachers.py")

with col3:
    if st.button("🏫 Manage Rooms", use_container_width=True):
        st.switch_page("pages/manage_rooms.py")

col4, col5, col6 = st.columns(3)

with col4:
    if st.button("📂 Upload Data", use_container_width=True):
        st.switch_page("pages/upload_csv.py")

with col5:
    if st.button("⚡ Generate Timetable", use_container_width=True):
        st.switch_page("pages/generate.py")

with col6:
    if st.button("📅 View Timetable", use_container_width=True):
        st.switch_page("pages/view.py")