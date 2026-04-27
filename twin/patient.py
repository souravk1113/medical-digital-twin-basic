"""Patient state object — the 'object + state' layer of the digital twin."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Optional
import pandas as pd


@dataclass
class Patient:
    """A patient's instantaneous state.

    Fields mirror the UCI Heart Disease (Cleveland) feature set so we can
    initialise a twin directly from an EHR row, plus a few derived quantities.
    """
    patient_id: int
    age: float
    sex: int                 # 1 = male, 0 = female
    cp: int                  # chest pain type 0..3
    trestbps: float          # resting systolic BP (mmHg)
    chol: float              # serum cholesterol (mg/dL)
    fbs: int                 # fasting blood sugar > 120 mg/dL (1/0)
    restecg: int             # resting ECG result 0..2
    thalach: float           # max heart rate achieved
    exang: int               # exercise-induced angina (1/0)
    oldpeak: float           # ST depression induced by exercise
    slope: int               # slope of peak exercise ST segment 0..2
    ca: int                  # number of major vessels colored by fluoroscopy 0..3
    thal: int                # 1 = normal, 2 = fixed defect, 3 = reversible defect
    diagnosis: Optional[int] = None  # observed label (0 = no disease, 1 = disease)

    # Derived / simulated state (not in EHR but maintained by the twin)
    hr: float = 75.0          # current heart rate
    sbp: float = 120.0        # current systolic BP
    dbp: float = 80.0         # current diastolic BP
    on_statin: bool = False
    on_antihypertensive: bool = False
    lifestyle_score: float = 0.0  # 0 = baseline, +1 = improved diet/exercise

    history: list = field(default_factory=list)

    @classmethod
    def from_row(cls, row: pd.Series, patient_id: int) -> "Patient":
        """Build a Patient from one row of the UCI dataframe."""
        return cls(
            patient_id=patient_id,
            age=float(row["age"]),
            sex=int(row["sex"]),
            cp=int(row["cp"]),
            trestbps=float(row["trestbps"]),
            chol=float(row["chol"]),
            fbs=int(row["fbs"]),
            restecg=int(row["restecg"]),
            thalach=float(row["thalach"]),
            exang=int(row["exang"]),
            oldpeak=float(row["oldpeak"]),
            slope=int(row["slope"]),
            ca=int(row["ca"]),
            thal=int(row["thal"]),
            diagnosis=int(row["target"]) if "target" in row and pd.notna(row["target"]) else None,
            sbp=float(row["trestbps"]),
            dbp=float(row["trestbps"]) * 0.66,
            hr=float(row["thalach"]) * 0.55,
        )

    def feature_vector(self) -> dict:
        """Return the EHR-style features used by the risk model.

        Reflects current twin state (sbp, chol after intervention) rather than
        the original record, so what-if simulations propagate to the model.
        """
        return {
            "age": self.age,
            "sex": self.sex,
            "cp": self.cp,
            "trestbps": self.sbp,
            "chol": self.chol,
            "fbs": self.fbs,
            "restecg": self.restecg,
            "thalach": self.thalach,
            "exang": self.exang,
            "oldpeak": self.oldpeak,
            "slope": self.slope,
            "ca": self.ca,
            "thal": self.thal,
        }

    def snapshot(self, t: float) -> dict:
        """Append the current state to history and return it."""
        snap = {"t": t, "hr": self.hr, "sbp": self.sbp, "dbp": self.dbp,
                "chol": self.chol, "lifestyle_score": self.lifestyle_score}
        self.history.append(snap)
        return snap

    def to_dict(self) -> dict:
        d = asdict(self)
        d.pop("history", None)
        return d
