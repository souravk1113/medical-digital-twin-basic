"""Twin simulator — couples the mechanistic vitals model with the ML risk model.

This is the 'simulation layer' from the architecture diagram in
docs/digital_twin_medical.md. It:
  - applies an Intervention (or none) to a Patient,
  - integrates the cardiovascular ODE forward in time,
  - re-evaluates risk along the trajectory so the user sees how risk evolves.
"""
from __future__ import annotations
from dataclasses import dataclass
import copy
import numpy as np
import pandas as pd

from .patient import Patient
from .physiology import CardiovascularModel
from .risk_model import RiskModel


@dataclass
class Intervention:
    statin: bool = False
    antihypertensive: bool = False
    lifestyle_score: float = 0.0   # 0..1
    label: str = "no intervention"


class TwinSimulator:
    def __init__(self, risk_model: RiskModel):
        self.risk = risk_model

    def simulate(self, patient: Patient, intervention: Intervention,
                 days: int = 365, dt_days: int = 7) -> pd.DataFrame:
        """Forward-simulate vitals + risk under a given intervention.

        Returns a tidy DataFrame with one row per snapshot time.
        """
        # work on a copy so the source patient isn't mutated
        p = copy.deepcopy(patient)
        cvm = CardiovascularModel(p)
        t, sol = cvm.simulate(
            days=days, dt=dt_days,
            statin=intervention.statin,
            antihypertensive=intervention.antihypertensive,
            lifestyle_score=intervention.lifestyle_score,
        )

        rows = []
        for i, ti in enumerate(t):
            sbp, dbp, hr, chol = sol[i]
            p.sbp, p.dbp, p.hr, p.chol = sbp, dbp, hr, chol
            risk = self.risk.predict_proba(p.feature_vector())
            rows.append({
                "t_days": float(ti),
                "sbp": sbp, "dbp": dbp, "hr": hr, "chol": chol,
                "risk": risk,
                "intervention": intervention.label,
            })
        return pd.DataFrame(rows)

    def compare(self, patient: Patient, interventions: list[Intervention],
                days: int = 365, dt_days: int = 7) -> pd.DataFrame:
        """Run several interventions and return their stacked trajectories."""
        return pd.concat(
            [self.simulate(patient, iv, days=days, dt_days=dt_days) for iv in interventions],
            ignore_index=True,
        )
