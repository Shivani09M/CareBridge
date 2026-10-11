
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="CareBridge | Recovery",
    page_icon="💙",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Styling ----------
st.markdown("""
<style>
.stApp {
    background: #f4f7fb;
}

[data-testid="stSidebar"] {
    background: #eaf2ff;
}

[data-testid="stSidebar"] * {
    color: #17365d;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #17365d !important;
}


[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span {
    color: #17365d !important;
}


[data-testid="stMetric"] {
    background: #ffffff !important;
    color: #17365d !important;
    padding: 18px;
    border-radius: 14px;
    border: 1px solid #e1e9f5;
}

[data-testid="stMetric"] label,
[data-testid="stMetric"] [data-testid="stMetricValue"],
[data-testid="stMetric"] [data-testid="stMetricLabel"],
[data-testid="stMetric"] [data-testid="stMetricDelta"] {
    color: #17365d !important;
}

.hero {
    background: linear-gradient(120deg, #1246a0, #2878d4);
    color: white;
    padding: 28px;
    border-radius: 18px;
    margin-bottom: 22px;
}
.hero h1 {
    color: white;
    margin-bottom: 8px;
}
.hero p {
    color: #edf5ff;
    margin-bottom: 0;
}
</style>
""", unsafe_allow_html=True)

# ---------- Session data ----------
if "checkins" not in st.session_state:
    st.session_state.checkins = []

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("# 💙 CareBridge")
    st.caption("Patient Recovery Monitoring")
    page = st.radio(
        "NAVIGATION",
        ["Overview", "Patient Check-In", "Patient Records"],
    )
    st.divider()
    st.caption("Prototype • For demonstration only")

# ---------- Header ----------
st.markdown("""
<div class="hero">
    <h1>CareBridge Dashboard</h1>
    <p>Recovery check-ins, clearer insights, and timely
    human review.</p>
</div>
""", unsafe_allow_html=True)

records = st.session_state.checkins
df = pd.DataFrame(records)

# ---------- Overview ----------
if page == "Overview":
    st.subheader("Recovery Overview")
    st.write("A quick summary of recorded check-ins.")

    total = len(records)
    patients = len(set(r["Patient ID"] for r in records))
    review_count = sum(
        r["Review Required"] for r in records
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Check-Ins", total)
    c2.metric("Patients Recorded", patients)
    c3.metric("Needs Human Review", review_count)

    st.divider()
    left, right = st.columns([3, 2])

    with left:
        st.subheader("Check-In Activity")
        if not df.empty:
            activity = df.groupby("Status").size()
            st.bar_chart(activity)
        else:
            st.info("Your chart will appear after the first check-in.")

    with right:
        st.subheader("Status Distribution")
        if not df.empty:
            distribution = df["Status"].value_counts()
            st.bar_chart(distribution)
        else:
            st.info("No recovery statuses recorded yet.")

    st.subheader("Latest Check-Ins")
    if not df.empty:
        st.dataframe(
            df.tail(5).iloc[::-1],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No check-ins yet. Open Patient Check-In to add one.")

    if review_count:
        st.warning(
            f"{review_count} check-in(s) report worsening symptoms. "
            "Arrange review by a qualified healthcare professional."
        )

# ---------- Patient Check-In ----------
elif page == "Patient Check-In":
    st.subheader("📝 New Patient Check-In")
    st.write("Use fictional details while testing this prototype.")

    with st.form("checkin_form", clear_on_submit=True):
        patient_id = st.text_input(
            "Patient ID",
            placeholder="e.g. DEMO001",
        )

        status = st.selectbox(
            "Recovery status",
            ["Improving", "Unchanged", "Worsening"],
        )

        notes = st.text_area(
            "Recovery notes",
            placeholder="Describe the reported recovery update...",
        )

        submitted = st.form_submit_button(
            "Save Check-In",
            type="primary",
            use_container_width=True,
        )

        if submitted:
            if not patient_id.strip():
                st.error("Please enter a Patient ID.")
            else:
                st.session_state.checkins.append({
                    "Time": datetime.now().strftime(
                        "%Y-%m-%d %H:%M"
                    ),
                    "Patient ID": patient_id.strip(),
                    "Status": status,
                    "Notes": notes.strip(),
                    "Review Required": status == "Worsening",
                })
                st.success("Check-in saved!")
                if status == "Worsening":
                    st.warning(
                        "This report is flagged for human review. "
                        "It is not a medical diagnosis."
                    )

# ---------- Patient Records ----------
elif page == "Patient Records":
    st.subheader("📋 Patient Records")
    st.write("Search and review the check-ins recorded in this session.")

    if not df.empty:
        search_id = st.text_input(
            "Search by Patient ID",
            placeholder="Enter an ID or leave blank",
        )

        status_filter = st.selectbox(
            "Filter by status",
            ["All", "Improving", "Unchanged", "Worsening"],
        )

        filtered = df.copy()

        if search_id.strip():
            filtered = filtered[
                filtered["Patient ID"].str.contains(
                    search_id.strip(),
                    case=False,
                    regex=False,
                )
            ]

        if status_filter != "All":
            filtered = filtered[
                filtered["Status"] == status_filter
            ]

        st.dataframe(
            filtered,
            use_container_width=True,
            hide_index=True,
        )

        csv = filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download filtered records (CSV)",
            data=csv,
            file_name="carebridge_records.csv",
            mime="text/csv",
        )
    else:
        st.info("No records available yet. Add a check-in first.")

st.divider()
st.caption(
    "CareBridge prototype • Use fictional data only. "
    "Not for clinical decision-making or emergency care."
)
