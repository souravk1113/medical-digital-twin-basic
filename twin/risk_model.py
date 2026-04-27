"""Data-driven risk model — the ML half of the hybrid twin.

Trained on UCI Heart Disease (Cleveland) to estimate probability of
coronary heart disease given a patient's current EHR features.
The twin queries this every time vitals change (e.g. after a simulated
intervention) so the risk gauge is *responsive* to the mechanistic state.
"""
from __future__ import annotations
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, brier_score_loss
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler


FEATURES = ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
            "thalach", "exang", "oldpeak", "slope", "ca", "thal"]


class RiskModel:
    """Calibrated gradient-boosted classifier for CHD risk."""

    def __init__(self):
        self.pipe = None
        self.metrics = {}

    def fit(self, df: pd.DataFrame, random_state: int = 42) -> dict:
        X = df[FEATURES].copy()
        y = (df["target"] > 0).astype(int)  # binarise multi-class label

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, stratify=y, test_size=0.25, random_state=random_state
        )

        base = Pipeline([
            ("impute", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
            ("gbm", GradientBoostingClassifier(
                n_estimators=200, max_depth=3, learning_rate=0.05,
                random_state=random_state)),
        ])
        # Probability calibration via isotonic regression on a held-out fold
        self.pipe = CalibratedClassifierCV(base, method="isotonic", cv=5)
        self.pipe.fit(X_train, y_train)

        proba = self.pipe.predict_proba(X_test)[:, 1]
        self.metrics = {
            "auroc": float(roc_auc_score(y_test, proba)),
            "brier": float(brier_score_loss(y_test, proba)),
            "n_train": int(len(X_train)),
            "n_test": int(len(X_test)),
            "prevalence": float(y.mean()),
        }
        return self.metrics

    def predict_proba(self, features: dict | pd.DataFrame) -> float:
        if isinstance(features, dict):
            features = pd.DataFrame([features])[FEATURES]
        elif isinstance(features, pd.DataFrame):
            features = features[FEATURES]
        return float(self.pipe.predict_proba(features)[0, 1])

    def save(self, path: str | Path) -> None:
        joblib.dump({"pipe": self.pipe, "metrics": self.metrics}, path)

    @classmethod
    def load(cls, path: str | Path) -> "RiskModel":
        obj = joblib.load(path)
        m = cls()
        m.pipe = obj["pipe"]
        m.metrics = obj["metrics"]
        return m
