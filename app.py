"""Streamlit demo — patient cardiovascular digital twin.

Run from repo root:
    streamlit run app.py
"""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

from twin import Patient, RiskModel, TwinSimulator, Intervention

ROOT = Path(__file__).resolve().parent
DATA_CSV = ROOT / "data" / "heart.csv"
MODEL_PATH = ROOT / "data" / "risk_model.joblib"
METRICS_PATH = ROOT / "data" / "metrics.json"

st.set_page_config(page_title="Patient Digital Twin", layout="wide", page_icon=None)

# ----------------------------------------------------------------------------
# Caching
# ----------------------------------------------------------------------------
@st.cache_data
def load_cohort() -> pd.DataFrame:
    df = pd.read_csv(DATA_CSV)
    df.insert(0, "patient_id", range(1, len(df) + 1))
    return df


@st.cache_resource
def load_model() -> RiskModel:
    return RiskModel.load(MODEL_PATH)


@st.cache_data
def load_metrics() -> dict:
    return json.loads(METRICS_PATH.read_text()) if METRICS_PATH.exists() else {}


# ----------------------------------------------------------------------------
# Plot helpers
# ----------------------------------------------------------------------------
def risk_gauge(value: float, title: str = "10-yr CHD risk (model)") -> go.Figure:
    return go.Figure(go.Indicator(
        mode="gauge+number",
        value=value * 100,
        number={"suffix": "%"},
        title={"text": title, "font": {"size": 14}},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#1f77b4"},
            "steps": [
                {"range": [0, 20], "color": "#c8e6c9"},
                {"range": [20, 50], "color": "#fff59d"},
                {"range": [50, 100], "color": "#ef9a9a"},
            ],
        },
    )).update_layout(height=240, margin=dict(l=10, r=10, t=40, b=10))


def trajectory_plot(traj: pd.DataFrame, y: str, ylabel: str) -> go.Figure:
    fig = px.line(traj, x="t_days", y=y, color="intervention", markers=False)
    fig.update_layout(
        height=280,
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis_title="days",
        yaxis_title=ylabel,
        legend=dict(orientation="h", y=-0.25),
    )
    return fig


# ----------------------------------------------------------------------------
# Pre-flight: required artefacts must exist
# ----------------------------------------------------------------------------
if not DATA_CSV.exists() or not MODEL_PATH.exists():
    st.error(
        "Data or model artefacts missing.\n\n"
        "Run from a shell with the venv active:\n\n"
        "```\npython scripts/fetch_data.py\npython scripts/train_model.py\n```"
    )
    st.stop()

cohort = load_cohort()
risk = load_model()
metrics = load_metrics()
sim = TwinSimulator(risk)


# ----------------------------------------------------------------------------
# Sidebar — cohort + patient selection + model card
# ----------------------------------------------------------------------------
with st.sidebar:
    st.header("Cohort (UCI Heart Disease)")
    st.caption(f"{len(cohort)} patients, prevalence {cohort['target'].mean():.0%}")

    patient_id = st.selectbox(
        "Select patient",
        cohort["patient_id"].tolist(),
        format_func=lambda i: f"#{i:03d} — {int(cohort.loc[i-1,'age'])}y "
                              f"{'M' if cohort.loc[i-1,'sex']==1 else 'F'}",
    )

    st.divider()
    st.subheader("Risk model card")
    if metrics:
        c1, c2 = st.columns(2)
        c1.metric("AUROC", f"{metrics.get('auroc', 0):.3f}")
        c2.metric("Brier", f"{metrics.get('brier', 0):.3f}")
        st.caption(
            f"trained on {metrics.get('n_train','?')} pts, "
            f"tested on {metrics.get('n_test','?')}"
        )
    st.caption("Calibrated gradient-boosted trees (isotonic).")

    st.divider()
    with st.expander("About this demo"):
        st.markdown(
            "Implements a **patient cardiovascular digital twin** on public EHR-style "
            "data (UCI Heart Disease, Cleveland). The twin combines a mechanistic "
            "ODE for vitals with a calibrated ML risk model. See "
            "`docs/digital_twin_medical.md` for the methodology and references.\n\n"
            "**Teaching demo only — not for clinical use.**"
        )


# ----------------------------------------------------------------------------
# Main panel
# ----------------------------------------------------------------------------
st.title("Patient Cardiovascular Digital Twin")
st.caption(
    "Hybrid mechanistic + ML twin built on public EHR data. "
    "Pick a patient, apply an intervention, watch state and risk evolve."
)

row = cohort.iloc[patient_id - 1]
patient = Patient.from_row(row, patient_id=int(row["patient_id"]))

baseline_risk = risk.predict_proba(patient.feature_vector())

# ---- top row: state + risk gauge ----
col_state, col_gauge = st.columns([3, 2])

with col_state:
    st.subheader(f"State vector — patient #{patient.patient_id}")
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Age", f"{patient.age:.0f} y")
    s2.metric("Sex", "Male" if patient.sex == 1 else "Female")
    s3.metric("Resting SBP", f"{patient.trestbps:.0f} mmHg")
    s4.metric("Cholesterol", f"{patient.chol:.0f} mg/dL")
    s1.metric("Max HR", f"{patient.thalach:.0f} bpm")
    s2.metric("Chest pain type", int(patient.cp))
    s3.metric("ST depression", f"{patient.oldpeak:.1f}")
    s4.metric("Major vessels", int(patient.ca))

    if patient.diagnosis is not None:
        label = "diseased" if patient.diagnosis else "healthy"
        st.caption(f"Recorded diagnosis in dataset: **{label}**")

with col_gauge:
    st.plotly_chart(risk_gauge(baseline_risk, "Baseline model risk"),
                    width="stretch")


# ---- intervention sandbox ----
st.divider()
st.subheader("Intervention sandbox — what-if simulation")

ic1, ic2, ic3, ic4 = st.columns([1, 1, 1, 1])
with ic1:
    statin = st.toggle("Statin", value=False, help="~22% reduction in cholesterol")
with ic2:
    antihtn = st.toggle("Antihypertensive", value=False, help="~10 mmHg SBP drop")
with ic3:
    lifestyle = st.slider("Lifestyle score", 0.0, 1.0, 0.0, 0.1,
                          help="diet + exercise composite (0 = baseline, 1 = ideal)")
with ic4:
    horizon = st.slider("Horizon (days)", 60, 730, 365, 30)

interventions = [
    Intervention(label="Baseline (no Rx)"),
    Intervention(statin=statin, antihypertensive=antihtn,
                 lifestyle_score=lifestyle,
                 label="With selected interventions"),
]

traj = sim.compare(patient, interventions, days=horizon, dt_days=7)

# ---- trajectories ----
g1, g2 = st.columns(2)
with g1:
    st.plotly_chart(trajectory_plot(traj, "sbp", "systolic BP (mmHg)"),
                    width="stretch")
    st.plotly_chart(trajectory_plot(traj, "chol", "cholesterol (mg/dL)"),
                    width="stretch")
with g2:
    st.plotly_chart(trajectory_plot(traj, "hr", "heart rate (bpm)"),
                    width="stretch")
    st.plotly_chart(trajectory_plot(traj, "risk", "10-yr CHD risk (model)"),
                    width="stretch")

# ---- end-of-horizon delta ----
st.divider()
end = traj.groupby("intervention").tail(1).set_index("intervention")
if "With selected interventions" in end.index and "Baseline (no Rx)" in end.index:
    base = end.loc["Baseline (no Rx)", "risk"]
    treat = end.loc["With selected interventions", "risk"]
    delta = treat - base
    d1, d2, d3 = st.columns(3)
    d1.metric("Risk @ horizon (baseline)", f"{base*100:.1f}%")
    d2.metric("Risk @ horizon (treated)", f"{treat*100:.1f}%",
              delta=f"{delta*100:+.1f} pp", delta_color="inverse")
    rrr = (1 - treat / base) * 100 if base > 0 else 0
    d3.metric("Relative risk reduction", f"{rrr:.0f}%")

st.caption(
    "Equations and effect sizes are illustrative ballpark values; "
    "see `twin/physiology.py` and `docs/digital_twin_medical.md`."
)
