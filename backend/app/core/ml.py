"""Trusted local IsolationForest artifact loading and advisory scoring."""
from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path

@dataclass
class MLScore:
    available: bool
    suspicious: bool | None = None
    score: float | None = None
    reason: str | None = None
    metadata: dict | None = None

def score_features(artifact_path: Path, metadata_path: Path, values: list[float]) -> MLScore:
    if not artifact_path.is_file() or not metadata_path.is_file():
        return MLScore(available=False, reason="Trusted local ML artifact is missing.")
    try:
        import joblib
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        model = joblib.load(artifact_path)
        prediction = int(model.predict([values])[0])
        score = float(model.decision_function([values])[0])
    except (ImportError, OSError, ValueError, TypeError, KeyError) as exc:
        return MLScore(available=False, reason=f"ML artifact unavailable: {type(exc).__name__}")
    return MLScore(available=True, suspicious=prediction == -1, score=score, metadata=metadata)
