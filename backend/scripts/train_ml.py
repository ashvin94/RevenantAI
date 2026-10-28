"""Train a trusted IsolationForest on seeded synthetic normal telemetry."""
from __future__ import annotations
import json
from datetime import UTC, datetime
from pathlib import Path
import joblib
import numpy as np
from sklearn.ensemble import IsolationForest

ROOT = Path(__file__).resolve().parents[1]
SEED = 42

def main() -> None:
    rng = np.random.default_rng(SEED)
    normal = np.column_stack([np.clip(rng.normal(45, 8, 1200), 1, None), rng.binomial(1, .03, 1200), np.ones(1200), np.ones(1200)])
    train, holdout = normal[:1000], normal[1000:]
    faults = np.column_stack([rng.normal(180, 20, 100), rng.integers(1, 4, 100), np.full(100, 2), np.full(100, 2)])
    model = IsolationForest(n_estimators=150, contamination=.02, random_state=SEED).fit(train)
    metadata = {
        "artifact_trust": "generated_locally_by_scripts/train_ml.py", "dataset": "synthetic",
        "features": ["duration_ms", "retry_no", "active_reservations", "stock_delta"], "seed": SEED,
        "train_normal_samples": 1000, "holdout_normal_samples": 200, "synthetic_fault_samples": 100,
        "synthetic_holdout_false_positive_rate": float(np.mean(model.predict(holdout) == -1)),
        "synthetic_fault_recall": float(np.mean(model.predict(faults) == -1)),
        "trained_at": datetime.now(UTC).isoformat(),
        "limitations": "Synthetic demo metrics only; no claim of production generalization."
    }
    artifacts = ROOT / "artifacts"; artifacts.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, artifacts / "isolation_forest.joblib")
    (artifacts / "isolation_forest.metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps(metadata, indent=2))

if __name__ == "__main__": main()
