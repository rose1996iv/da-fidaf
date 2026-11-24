"""Workstream C: Synthetic concept drift, detectors, and continual adaptation."""

from dafidaf.drift.core import (
    AdaptationResult,
    ContinualAdapter,
    DriftDetectionResult,
    DriftSpec,
    FeatureDriftDetector,
    PageHinkleyDetector,
    apply_synthetic_drift,
)

__all__ = [
    "AdaptationResult",
    "ContinualAdapter",
    "DriftDetectionResult",
    "DriftSpec",
    "FeatureDriftDetector",
    "PageHinkleyDetector",
    "apply_synthetic_drift",
]
