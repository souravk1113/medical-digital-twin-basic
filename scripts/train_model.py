"""Train and persist the digital twin's risk model."""
from __future__ import annotations
import json
import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from twin.risk_model import RiskModel  # noqa: E402

DATA = ROOT / "data" / "heart.csv"
MODEL_DIR = ROOT / "data"
MODEL = MODEL_DIR / "risk_model.joblib"
METRICS = MODEL_DIR / "metrics.json"


def main() -> int:
    if not DATA.exists():
        print(f"[train] missing {DATA} — run scripts/fetch_data.py first", file=sys.stderr)
        return 1
    df = pd.read_csv(DATA)
    print(f"[train] {len(df)} rows, prevalence={df['target'].mean():.3f}")

    m = RiskModel()
    metrics = m.fit(df)
    m.save(MODEL)
    METRICS.write_text(json.dumps(metrics, indent=2))
    print(f"[train] saved -> {MODEL}")
    print(json.dumps(metrics, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
