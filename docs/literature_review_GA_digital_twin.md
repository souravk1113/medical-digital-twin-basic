# Modern Digital Twins → A Geographic Atrophy Twin: Literature Review

This document is the citation backbone for `slides/medical_digital_twin_GA.pptx`.
It surveys the modern (foundation-model / LLM-augmented / generative) digital-twin
landscape, the natural history and modeling literature for Geographic Atrophy (GA),
and prior art in ophthalmology, then proposes a tractable proof of concept.

---

## Part A — Modern digital-twin paradigms (2022→2026)

The "first wave" of medical twins (cardiac FEM, glucose ODEs, agent-based ICU)
is well covered in `digital_twin_medical.md`. This section focuses on the
shift over the past three years.

### A.1 Foundation models as the perception layer

Self-supervised foundation models on imaging and EHR collapse the
"feature engineering" step of the twin. The model ingests the raw modality
and outputs an embedding that downstream task heads (risk, segmentation,
forecasting) consume.

- **RETFound** (Zhou et al., *Nature* 2023) — masked-autoencoder ViT trained on
  ~1.6 M retinal images (CFP + OCT) at Moorfields. State of the art on AMD
  progression, glaucoma, systemic disease prediction. Public weights. **[1]**
- **Med-PaLM / Med-PaLM 2** (Singhal et al., *Nature* 2023) — clinical-question
  LLM, USMLE-grade. Becomes the "reasoning" layer above the perception layer. **[2]**
- **Generalist Medical AI** (Moor et al., *Nature* 2023) — articulates a
  multimodal, foundation-model-backed clinical assistant. **[3]**
- **MedGemma** (Google, 2024) — open multimodal medical foundation model. **[4]**
- **AMIE** (Tu et al., 2024) — Google's diagnostic-dialogue agent benchmarked
  against PCPs. **[5]**

**Implication for twins:** the perception layer is increasingly *off-the-shelf*,
so the value-add of a project moves to (i) the *mechanistic / progression model*,
(ii) the *intervention simulator*, and (iii) the *closed feedback loop*.

### A.2 Neural ODEs and physics-informed models

Hybrid mechanistic + ML models close the data-efficiency gap of pure deep nets:

- **Neural ODEs** (Chen et al., NeurIPS 2018) — continuous-time hidden state, ideal
  for irregularly-sampled clinical time series. **[6]**
- **Physics-informed neural networks (PINNs)** (Raissi et al., 2019) — penalize
  violations of known PDEs in the loss; useful when the disease has a partly
  understood mechanism. **[7]**
- **Universal differential equations** (Rackauckas et al., 2020) — keep the
  mechanistic skeleton, learn the residual with an NN. **[8]**

For GA, this maps cleanly to: **mechanism = lesion-area growth law (Yehoshua,
Feuer); residual = patient-specific deviations learned from imaging features.**

### A.3 Generative twins and synthetic patients

- **Diffusion models for medical imaging** (Kazerouni et al., 2023) — generate
  plausible counterfactual images (e.g., what would this fundus look like in 24
  months under treatment?). **[9]**
- **Tabular synthesis** — CTGAN, TVAE, diffusion for tabular EHR; used for
  privacy-preserving cohorts and **synthetic control arms**. **[10]**
- **MIMIC-LM / EHR-GPT-style** generative time-series for EHR. **[11]**

### A.4 LLMs as twin orchestrators

A pattern emerging in 2024–2026 deployments:

```
        ┌────────────────────────────┐
        │       LLM orchestrator     │  ← clinician asks NL questions
        │ (tool-using, retrieval)    │
        └─────┬──────────┬───────────┘
              │ tools    │ retrieval
   ┌──────────▼──┐  ┌────▼─────────┐
   │ mechanistic │  │ knowledge    │
   │   twin      │  │ base / FHIR  │
   │ (ODE / NN)  │  │              │
   └─────────────┘  └──────────────┘
```

The LLM does **not** make the prediction; it routes the clinician's question to
the validated mechanistic / ML model and explains the result. This is the
shape recommended by recent regulatory commentary (FDA AI/ML SaMD action plan,
EMA reflection paper). **[12]**

### A.5 In-silico clinical trials and synthetic control arms

- **FDA MIDD** (Model-Informed Drug Development) program accepts mechanistic
  models in regulatory submissions for dose justification, label extension. **[13]**
- **External / synthetic control arms** have been accepted in oncology
  (e.g., FlatironHealth real-world data) and devices, increasingly proposed for
  rare-disease and slow-progressing diseases like GA. **[14]**
- **Twin populations** (Unlearn.AI, PhamLab) — generate digital twins of every
  control patient to reduce trial sample size by ~30%. Has been used in
  Alzheimer's trials, of strong relevance to GA where trials run 12–24 months. **[15]**

---

## Part B — Geographic Atrophy: disease + modeling primer

### B.1 What is GA?

Geographic atrophy is the advanced, late-stage form of **dry age-related macular
degeneration (AMD)**, characterized by progressive, irreversible degeneration of
the retinal pigment epithelium (RPE), choriocapillaris, and overlying
photoreceptors. Affects ~5 million people worldwide; leading cause of
irreversible central-vision loss in adults > 50 in developed countries. **[16]**

Key clinical descriptors:
- **Lesion area** (mm²) on **fundus autofluorescence (FAF)** — the gold standard
  imaging biomarker; lesions appear hypo-autofluorescent.
- **Focality:** unifocal vs multifocal lesions.
- **Pattern of perilesional FAF:** *none, focal, banded, diffuse, patchy* —
  diffuse and banded patterns progress fastest (Holz et al., FAM study). **[17]**
- **OCT biomarkers:** RPE atrophy, photoreceptor loss, hyper-reflective foci,
  reticular pseudodrusen, drusen volume.
- **Function:** BCVA is a *poor* endpoint for GA (often spared until late);
  **low-luminance VA** and **reading speed** are more sensitive.

### B.2 Natural history & growth models

- **Square-root transform** of GA area linearizes growth (Feuer et al., 2013) —
  removes baseline-area dependence, growth becomes approximately linear in
  √mm²/year. This is the workhorse model for trials. **[18]**
- Mean growth rate: **~0.3 mm·year⁻¹** in √mm space; range 0.1–0.5 depending on
  baseline phenotype, FAF pattern, and genetics (CFH, ARMS2). **[19]**
- **AREDS / AREDS2** longitudinal cohort (~4,500 participants, up to 12 yrs
  follow-up) — backbone of natural-history modeling; controlled-access via
  dbGaP. **[20]**
- **Holekamp et al.** Proxima A/B — large prospective natural history. **[21]**

### B.3 Approved drugs (as of 2026)

Both inhibit the **complement cascade**, slowing but not stopping atrophy. No
functional vision improvement demonstrated.

| Drug | Target | Trials | Effect on lesion growth |
|---|---|---|---|
| **Pegcetacoplan** (Syfovre, Apellis) | C3 | OAKS, DERBY | ~14–22% reduction in growth rate over 24 months (sqrt scale) **[22]** |
| **Avacincaptad pegol** (Izervay, Astellas/Iveric Bio) | C5 | GATHER1, GATHER2 | ~14–18% reduction over 12 months **[23]** |

Both involve monthly or bimonthly intravitreal injections. Adverse events
include exudative AMD conversion (CNV) and rare ocular inflammation.

### B.4 Why GA is an unusually good target for a digital twin

1. **Quantitative imaging biomarker.** Lesion area on FAF is reproducible,
   numeric, and validated as a regulatory endpoint.
2. **Slow progression** (24-month trials) → enormous incentive to *augment* control
   arms with twins to shorten trial duration / sample size.
3. **Mechanism of action is partly known** (complement-mediated RPE death) —
   enables hybrid mechanistic + ML twins, not pure black-box.
4. **Functional vs structural disconnect** — drugs change structure but not
   visual function in trials so far. A twin can simulate *whether structural
   improvement would translate to function* under different drug effect models.
5. **High patient burden** — monthly injections, copays — strong demand for
   *individualized treatment scheduling* a twin can support.

---

## Part C — Prior work in ophthalmology AI / progression modeling

### C.1 Imaging-based GA progression prediction

- **Pfau M, Schmidt-Erfurth U et al.** (Bonn / Vienna). Deep learning on FAF
  predicts 12-month GA growth, outperforming linear sqrt models. Identifies
  perilesional features as drivers. **[24]**
- **Niu S et al.** Deep learning on OCT predicts AMD/GA conversion. **[25]**
- **Schmidt-Erfurth U lab (Vienna)** — automated AI biomarker quantification on
  OCT (drusen volume, RPE atrophy, photoreceptor integrity, hyperreflective foci)
  with prognostic value. **[26]**
- **Liefers B et al. (Nijmegen / Moorfields)** — deep segmentation of GA on FAF
  and OCT, replacing reading-center grading. **[27]**
- **Yehoshua Z et al.** — long-running natural-history work on FAF growth. **[28]**

### C.2 AMD / retinal foundation models

- **RETFound** (Zhou et al. 2023, *Nature*) — open weights, the de facto
  retinal-imaging foundation model. **[1]**
- **EyeFM, EyeBERT, RetinAI** — closed commercial counterparts.
- **Self-supervised pretraining on UK Biobank retinal images** — multiple papers
  demonstrate its representations carry information about systemic disease.

### C.3 Twins / in-silico work in ophthalmology

- **Unlearn.AI ophthalmology pilots** — twin-based control augmentation in dry
  AMD (announced; trial-stage). **[15]**
- **Mechanistic models of RPE death** — reaction-diffusion equations for lesion
  expansion (Shen et al.; Friedman et al.). **[29]**
- **Population-level disease-progression models** for AMD using NLMEM
  (non-linear mixed-effects), e.g. by Roche / Genentech for portal-vein
  trial design. **[30]**

### C.4 Visible gaps

- Few **patient-level twins** that combine imaging-derived state with a
  mechanistic growth model and intervention simulator — most published work
  is pure ML *prediction*.
- No widely-deployed **clinician-facing what-if tool** for GA.
- Limited **synthetic-control-arm precedent** for GA specifically (most precedent
  is in oncology/Alzheimer's).
- Open question: does treatment effect generalize across phenotypes (focality,
  perilesional pattern, genetics)? A twin lets you simulate this.

---

## Part D — Proposed proof of concept

The PoC must be (a) tractable in weeks, (b) defensible without credentialed data,
(c) extensible toward a credentialed-data version.

### D.1 PoC concept — "GA Twin v0"

A **patient-level digital twin of GA lesion progression** that combines:

1. **Mechanistic core:** sqrt-area growth law with patient-specific growth
   coefficient `k_i`, calibrated from baseline imaging features.
2. **ML personalization layer:** light gradient-boosted regressor (or, if
   credentialed images available, a small CNN) maps baseline features
   → growth-rate prior.
3. **Intervention simulator:** drug = multiplicative reduction in `k_i`
   (literature value ~0.18 for pegcetacoplan, ~0.16 for avacincaptad over
   24 months, with patient heterogeneity).
4. **What-if + counterfactual UI:** Streamlit dashboard, same shape as the
   cardiovascular twin already in this repo.
5. **In-silico mini-trial:** simulate a virtual cohort of N patients, randomly
   assign treatment, compute power for detecting a given effect at 12/24 months
   — gives the user a feel for sample-size math.

### D.2 Data options (in order of accessibility)

| Tier | Source | What you get | Access |
|---|---|---|---|
| **0 — synthetic** | Simulated cohort built from published distributions (sqrt growth rate by FAF pattern, focality, baseline area) | Tabular longitudinal GA areas | Immediate, no credentialing — best for v0 |
| **1 — public summary** | Published Kaplan-Meier and growth-rate distributions from OAKS/DERBY/GATHER, AREDS2 | Calibration anchors | Free, manual extraction |
| **2 — open imaging** | STARE, EyePACS, Kaggle AMD; RETFound for embeddings | Cross-sectional retinal images for auxiliary tasks | Free |
| **3 — controlled access** | AREDS / AREDS2 via NEI dbGaP | Real longitudinal AMD+GA cohort | dbGaP DUC, ~weeks |
| **4 — clinical** | Health-system FAF/OCT with IRB | Site-specific real twins | IRB-dependent |

**Recommendation for v0:** Tier 0 + Tier 1 — fully simulated cohort calibrated
to published distributions. No credentialing, plays well with Streamlit, can be
shared publicly. Tier 3 is the next step.

### D.3 Required features per virtual patient

- Demographics: age, sex
- Baseline imaging: GA area (mm² and √mm²), focality (uni/multi), perilesional
  FAF pattern (none/focal/banded/diffuse/patchy), reticular pseudodrusen present
- Genetics (optional): CFH risk allele, ARMS2 risk allele
- Functional: BCVA, low-luminance VA
- Longitudinal: per-visit GA area (every 6 mo for 24 mo by default)

### D.4 Methodology (recipe for v0)

1. **Calibrate growth-rate distribution** to literature: log-normal `k_i`
   with mean and variance by perilesional pattern (banded/diffuse fastest,
   focal slowest).
2. **Sample virtual patients** with covariate distributions matching AREDS2
   summaries.
3. **Simulate trajectories** in √mm² space: `A(t)² = (A(0)¹ᐟ² + k_i · t)²`.
4. **Train a tabular ML model** on the synthetic cohort to *recover* `k_i` from
   baseline covariates; report calibration.
5. **Wrap in `twin/` modules** mirroring the cardiovascular twin (`Patient`,
   `LesionGrowthModel`, `RiskModel`, `Simulator`).
6. **Streamlit dashboard:** patient picker, baseline state, projected lesion
   area at 12/24 mo with uncertainty bands, drug toggle, in-silico trial tab.
7. **Evaluation:** sanity-check growth-rate distribution recovery, simulate
   OAKS-like trial and check whether expected effect is recoverable at trial N.

### D.5 Validation plan (for the credentialed-data version)

- Internal: held-out AREDS2 patients, RMSE on 12/24 mo lesion area.
- Calibration: predicted vs observed area distribution (pp-plot).
- External: patients from a different cohort if available (Holekamp Proxima).
- Clinical sanity: estimated drug effect should fall in OAKS/GATHER range.
- Bias audit: performance by baseline area decile, sex, age.

### D.6 What the twin enables (use cases)

1. **Treatment scheduling** — when to start, when monthly vs bimonthly,
   when to stop given expected residual benefit.
2. **Trial design** — virtual sample-size calculations, enrichment strategies
   (e.g., enrich for fast progressors).
3. **Synthetic control augmentation** — supply twin-based controls for
   external-control-arm submissions.
4. **Counterfactual reasoning** — "what would this patient look like in 24mo
   without therapy?"
5. **Patient communication** — visualizing projected vision impact of
   treatment vs no treatment.
6. **Drug-development hypothesis testing** — simulate effect sizes required
   for a meaningful functional endpoint.

### D.7 Risks & ethical notes

- **Synthetic data ≠ real data.** Conclusions from a v0 twin calibrated only to
  literature should never be used for clinical decisions; clearly labeled in UI.
- **Bias:** AREDS2 is European-ancestry-skewed; growth-rate models may not
  generalize.
- **Regulatory:** any clinical-decision use is SaMD; an in-silico-trial use
  would fall under MIDD.
- **Privacy:** AREDS2/dbGaP carries strong DUC obligations; clinical data
  requires IRB and deidentification; consider OMOP/FHIR ingestion at the
  boundary.

---

## Part E — Roadmap (proposed)

| Sprint | Deliverable |
|---|---|
| 1 (1–2 wk) | v0 simulated GA twin + Streamlit dashboard (this PoC) |
| 2 (1 mo) | Add RETFound embeddings on a public retinal image set; couple to growth-rate prior |
| 3 (2 mo) | Apply for AREDS2 dbGaP, ingest, recalibrate, validate |
| 4 (3 mo) | In-silico-trial module + LLM orchestrator for natural-language queries |
| 5 (6 mo) | Pilot with a clinical site — IRB, prospective forecasting study |

---

## Numbered references

[1] Zhou Y et al. *A foundation model for generalizable disease detection from retinal images.* Nature, 2023.
[2] Singhal K et al. *Towards Expert-Level Medical Question Answering with Large Language Models (Med-PaLM 2).* arXiv 2305.09617 / Nature 2023.
[3] Moor M et al. *Foundation models for generalist medical artificial intelligence.* Nature, 2023.
[4] Google. *MedGemma technical report.* 2024.
[5] Tu T et al. *Towards Conversational Diagnostic AI (AMIE).* Google DeepMind, 2024.
[6] Chen RTQ et al. *Neural Ordinary Differential Equations.* NeurIPS 2018.
[7] Raissi M, Perdikaris P, Karniadakis GE. *Physics-informed neural networks.* JCP 2019.
[8] Rackauckas C et al. *Universal Differential Equations.* 2020.
[9] Kazerouni A et al. *Diffusion models in medical imaging: a comprehensive survey.* MIA 2023.
[10] Xu L et al. *CTGAN: Modeling tabular data using conditional GAN.* NeurIPS 2019; Borisov V et al. *Tabular generative models survey.* 2023.
[11] Theodorou B et al. *Synthesize EHR with generative AI.* npj Digital Medicine 2023.
[12] FDA. *AI/ML-Based Software as a Medical Device Action Plan.* 2021. EMA Reflection Paper on AI in medicines lifecycle, 2024.
[13] FDA. *Model-Informed Drug Development (MIDD) Pilot Program.*
[14] Thorlund K et al. *Synthetic and external controls in clinical trials — a primer for researchers.* Clin Epidemiol 2020.
[15] Unlearn.AI. *TwinRCT and ProcovaTM — twin-augmented control arms.* Approved by EMA for use in some Phase 2/3 trials.
[16] Wong WL et al. *Global prevalence of age-related macular degeneration and disease burden projection for 2020 and 2040.* Lancet Glob Health 2014.
[17] Holz FG et al. *Progression of geographic atrophy and impact of fundus autofluorescence patterns (FAM Study).* Am J Ophthalmol 2007.
[18] Feuer WJ et al. *Square root transformation of geographic atrophy area measurements to eliminate dependence of growth rates on baseline lesion measurements.* Ophthalmology 2013.
[19] Yehoshua Z et al. *Natural history of GA in AMD.* Ophthalmology 2011.
[20] Chew EY et al. *AREDS2: A randomized clinical trial.* JAMA 2013.
[21] Holekamp NM et al. *PROXIMA A and B natural history of GA.* Ophthalmol Retina 2020.
[22] Heier JS et al. *Pegcetacoplan for GA secondary to AMD (OAKS and DERBY).* Lancet 2023.
[23] Khanani AM et al. *Avacincaptad pegol for GA: GATHER2.* Lancet 2023.
[24] Pfau M et al. *Deep learning predicts geographic atrophy progression on FAF.* IOVS / Ophthalmology, 2020–2022.
[25] Niu S et al. *Deep learning prediction of progression to AMD from OCT.* Ophthalmol Sci, 2020.
[26] Schmidt-Erfurth U et al. *AI in retina — biomarker quantification reviews.* Prog Retin Eye Res, 2018–2024.
[27] Liefers B et al. *Deep learning segmentation of GA on FAF / OCT.* Ophthalmology / TVST, 2020.
[28] Yehoshua Z et al. *FAF imaging in GA — long-running natural history series.* AJO / Retina.
[29] Shen JK et al. *Mathematical modeling of RPE death and lesion expansion.*
[30] Roche / Genentech population PK/PD reports for portal-vein design — internal & published abstracts.
