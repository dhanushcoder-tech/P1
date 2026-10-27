"""Explainable incident-candidate screening for sampled traffic-video counts.

Flags abrupt temporal drops in YOLO vehicle counts for human review. A count
change is not proof of an incident and may be caused by occlusion, camera motion,
lighting, or sampling variation.
"""
from __future__ import annotations
from typing import Any, Dict, Iterable, List

class IncidentDetector:
    """Flag abrupt drops in sampled vehicle counts as review candidates."""
    def __init__(self, min_absolute_drop: int = 5, min_relative_drop: float = 0.45):
        if min_absolute_drop < 1:
            raise ValueError("min_absolute_drop must be >= 1")
        if not 0 < min_relative_drop <= 1:
            raise ValueError("min_relative_drop must be in (0, 1]")
        self.min_absolute_drop = int(min_absolute_drop)
        self.min_relative_drop = float(min_relative_drop)

    def detect_from_decisions(self, decisions: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
        normalized = []
        for item in decisions:
            try:
                normalized.append({
                    "frame": int(item.get("frame", 0) or 0),
                    "timestamp": round(float(item.get("timestamp", 0) or 0), 2),
                    "vehicle_count": max(0, int(item.get("vehicle_count", 0) or 0)),
                })
            except (AttributeError, TypeError, ValueError):
                continue
        candidates = []
        for previous, current in zip(normalized, normalized[1:]):
            drop = previous["vehicle_count"] - current["vehicle_count"]
            baseline = previous["vehicle_count"]
            ratio = drop / baseline if baseline else 0.0
            if drop >= self.min_absolute_drop and ratio >= self.min_relative_drop:
                # Heuristic review score, NOT a calibrated probability.
                score = min(95, round(50 + 35 * ratio + min(10, drop)))
                candidates.append({
                    "frame": current["frame"], "timestamp": current["timestamp"],
                    "previous_count": previous["vehicle_count"],
                    "current_count": current["vehicle_count"], "drop": drop,
                    "drop_ratio_pct": round(ratio * 100, 1), "review_score": score,
                    "label": "Abrupt vehicle-count drop — review footage",
                    "reason": "Sampled YOLO count dropped sharply between controller decisions.",
                    "limitation": "Not proof of an accident, breakdown, or road blockage.",
                })
        return candidates
