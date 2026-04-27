# Medical Digital Twin — demo

A small, runnable example of a **patient digital twin** for cardiovascular risk,
built on public EHR-style data (UCI Heart Disease, Cleveland).
It combines a mechanistic ODE for vitals with a calibrated ML risk model so you
can apply *what-if* interventions (statin, antihypertensive, lifestyle) and watch
the patient's state and risk evolve.

> **Teaching demo only, not a clinical tool.** See `docs/digital_twin_medical.md`
> for the literature review, methodology, and references.

## Repository layout

```
digital_twin/
├── docs/
│   ├── digital_twin_medical.md             # base literature review + methodology
│   └── literature_review_GA_digital_twin.md # modern DT + Geographic Atrophy survey
├── slides/
│   ├── build_deck.py                        # generates the pptx
│   └── medical_digital_twin_GA.pptx         # 41-slide deck (regenerable)
├── twin/                          # twin core (state, physiology, risk, simulator)
├── scripts/fetch_data.py          # download UCI Heart Disease (cached -> data/)
├── scripts/train_model.py         # fit + persist the risk model
├── app.py                         # Streamlit demo
├── requirements.txt
└── .venv/                         # local virtual environment
```

## Documents

- `docs/digital_twin_medical.md` — first-principles intro: definition,
  taxonomy, methodology, classical use cases.
- `docs/literature_review_GA_digital_twin.md` — modern foundation-model and
  LLM-based approaches, GA disease primer, ophthalmology prior art, proposed
  proof-of-concept and roadmap.
- `slides/medical_digital_twin_GA.pptx` — presentable 41-slide deck that walks
  from classical twins → modern paradigms → Geographic Atrophy → PoC proposal.
  Regenerate with `python slides/build_deck.py`.

## Quick start

The repository ships with a local `.venv/`. From a fresh shell:

```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# or bash / Git Bash
source .venv/Scripts/activate

pip install -r requirements.txt
python scripts/fetch_data.py        # writes data/heart.csv
python scripts/train_model.py       # writes data/risk_model.joblib + metrics.json
streamlit run app.py                # opens http://localhost:8501
```

## What the demo shows

| Architecture layer | In the demo |
|---|---|
| Data | UCI Heart Disease loaded via `ucimlrepo` (with offline URL fallback) |
| State | `Patient` dataclass holding the EHR-style state vector |
| Mechanistic model | Windkessel-inspired ODE for SBP/DBP/HR + cholesterol response |
| ML model | Calibrated gradient-boosted trees for CHD risk |
| Simulation | Forward integration over user-chosen horizon, baseline vs intervention |
| UI | Streamlit dashboard: cohort picker, state, risk gauge, what-if sandbox |

## Reading order

1. `docs/digital_twin_medical.md` — definition, taxonomy, methodology, use cases.
2. `twin/patient.py`, `twin/physiology.py`, `twin/risk_model.py`,
   `twin/simulator.py` — implementation in the same order as the architecture diagram.
3. `app.py` — how it all comes together as a clinician-facing tool.
