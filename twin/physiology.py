"""Mechanistic cardiovascular sub-model.

Simplified, *teaching-grade* dynamics inspired by:
- the 2-element Windkessel model for systemic arterial pressure, and
- standard pharmacodynamic decay/onset for medication effects.

These are NOT clinically validated — they exist to demonstrate how a
mechanistic core can sit inside a digital twin and respond to interventions.
"""
from __future__ import annotations
import numpy as np
from scipy.integrate import odeint


# Targets a "healthy adult" would equilibrate toward in absence of disease.
HEALTHY_SBP = 118.0
HEALTHY_DBP = 76.0
HEALTHY_HR = 70.0

# Time constants (days) — how quickly the body drifts toward equilibrium.
TAU_BP = 30.0       # blood pressure homeostasis / lifestyle response
TAU_CHOL = 60.0     # serum cholesterol response to statin / diet


class CardiovascularModel:
    """ODE-based forward simulator for one patient's vitals over days."""

    def __init__(self, patient):
        self.p = patient

    def derivatives(self, state, t, params):
        """dx/dt for the state vector [sbp, dbp, hr, chol].

        params dict provides intervention-dependent target values
        (e.g. statin lowers chol target; antihypertensive lowers sbp target).
        """
        sbp, dbp, hr, chol = state
        sbp_target = params["sbp_target"]
        dbp_target = params["dbp_target"]
        hr_target = params["hr_target"]
        chol_target = params["chol_target"]

        d_sbp = (sbp_target - sbp) / TAU_BP
        d_dbp = (dbp_target - dbp) / TAU_BP
        d_hr  = (hr_target  - hr ) / 14.0
        d_chol = (chol_target - chol) / TAU_CHOL
        return [d_sbp, d_dbp, d_hr, d_chol]

    def _intervention_targets(self, statin: bool, antihypertensive: bool,
                              lifestyle_score: float) -> dict:
        """Translate active interventions into ODE target setpoints.

        Effect sizes are illustrative ballpark values from the cardiovascular
        intervention literature:
          - moderate-intensity statin: ~20-30% LDL reduction (we apply on total chol scaled)
          - antihypertensive monotherapy: ~10 mmHg SBP, ~5 mmHg DBP
          - lifestyle (diet+exercise): up to ~5 mmHg SBP and ~10 mg/dL chol per unit score
        """
        baseline_sbp = max(self.p.trestbps, HEALTHY_SBP)
        baseline_chol = self.p.chol

        # statin pulls cholesterol toward a lower setpoint
        chol_drop = (0.22 * baseline_chol) if statin else 0.0
        chol_drop += 10.0 * lifestyle_score

        # antihypertensive + lifestyle on BP
        sbp_drop = (10.0 if antihypertensive else 0.0) + 5.0 * lifestyle_score
        dbp_drop = (5.0 if antihypertensive else 0.0) + 2.5 * lifestyle_score

        return {
            "sbp_target": max(HEALTHY_SBP, baseline_sbp - sbp_drop),
            "dbp_target": max(HEALTHY_DBP, baseline_sbp * 0.66 - dbp_drop),
            "hr_target": HEALTHY_HR + (3.0 if antihypertensive else 0.0)
                          - 2.0 * lifestyle_score,  # mild bradycardia from beta-blockers
            "chol_target": max(150.0, baseline_chol - chol_drop),
        }

    def simulate(self, days: int = 180, dt: float = 1.0,
                 statin: bool = False, antihypertensive: bool = False,
                 lifestyle_score: float = 0.0) -> np.ndarray:
        """Integrate the ODE forward and return a (T, 4) array [sbp,dbp,hr,chol]."""
        params = self._intervention_targets(statin, antihypertensive, lifestyle_score)
        x0 = [self.p.sbp, self.p.dbp, self.p.hr, self.p.chol]
        t = np.arange(0, days + dt, dt)
        sol = odeint(self.derivatives, x0, t, args=(params,))
        return t, sol
