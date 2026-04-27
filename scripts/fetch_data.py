"""Fetch the UCI Heart Disease (Cleveland) dataset.

Tries `ucimlrepo` first; falls back to a direct download from the
UCI archive (URL has been stable for two decades). Caches to data/heart.csv.
"""
from __future__ import annotations
import io
import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
OUT = DATA / "heart.csv"

COLUMNS = ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
           "thalach", "exang", "oldpeak", "slope", "ca", "thal", "target"]


def via_ucimlrepo() -> pd.DataFrame | None:
    try:
        from ucimlrepo import fetch_ucirepo
        ds = fetch_ucirepo(id=45)  # Heart Disease
        X = ds.data.features
        y = ds.data.targets
        df = pd.concat([X, y], axis=1)
        df.columns = [c.lower() for c in df.columns]
        if "num" in df.columns and "target" not in df.columns:
            df = df.rename(columns={"num": "target"})
        return df[COLUMNS]
    except Exception as e:
        print(f"[fetch] ucimlrepo path failed: {e}", file=sys.stderr)
        return None


def via_direct_url() -> pd.DataFrame | None:
    import urllib.request
    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data"
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            text = r.read().decode("utf-8")
        df = pd.read_csv(io.StringIO(text), header=None, names=COLUMNS, na_values="?")
        return df
    except Exception as e:
        print(f"[fetch] direct URL path failed: {e}", file=sys.stderr)
        return None


def clean(df: pd.DataFrame) -> pd.DataFrame:
    # Coerce numeric, drop rows with missing essentials, fill remaining with median
    for c in COLUMNS:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["age", "sex", "trestbps", "chol", "thalach", "target"])
    df = df.fillna(df.median(numeric_only=True))
    df["target"] = (df["target"] > 0).astype(int)  # binarise
    return df.reset_index(drop=True)


def main() -> int:
    df = via_ucimlrepo()
    if df is None:
        df = via_direct_url()
    if df is None:
        print("[fetch] FAILED — no data source available.", file=sys.stderr)
        return 1
    df = clean(df)
    df.to_csv(OUT, index=False)
    print(f"[fetch] saved {len(df)} patients -> {OUT}")
    print(df.head())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
