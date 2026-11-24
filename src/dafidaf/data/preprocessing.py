"""Leakage-free train-only preprocessing (imputation, scaling, missingness flags)."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PreprocessorConfig:
    """Configuration for train-only imputation and scaling."""

    impute_strategy: str = "median"  # "median" or "mean"
    scale_strategy: str = "robust"  # "robust" (IQR) or "standard" (z-score)
    add_missing_indicators: bool = True
    clip_abs_value: float = 20.0


@dataclass(frozen=True, slots=True)
class PreprocessorState:
    """Frozen parameters learned strictly from training data."""

    feature_names: tuple[str, ...]
    fill_values: tuple[float, ...]
    centers: tuple[float, ...]
    scales: tuple[float, ...]
    indicator_indices: tuple[int, ...]


class TrainOnlyPreprocessor:
    """Fits imputer and scaler strictly on training features, never on val/test."""

    def __init__(self, config: PreprocessorConfig | None = None) -> None:
        self.config = config or PreprocessorConfig()
        self._state: PreprocessorState | None = None

    @property
    def state(self) -> PreprocessorState:
        if self._state is None:
            raise RuntimeError("TrainOnlyPreprocessor must be fitted on training data first.")
        return self._state

    def fit(
        self,
        x_train: Sequence[Sequence[float | None]],
        feature_names: Sequence[str],
        *,
        split_name: str = "train",
    ) -> TrainOnlyPreprocessor:
        if split_name.strip().lower() != "train":
            raise RuntimeError(
                f"TrainOnlyPreprocessor.fit() refused on non-training split '{split_name}'."
            )
        if not x_train:
            raise ValueError("Cannot fit TrainOnlyPreprocessor on empty training data.")
        n_cols = len(feature_names)
        fill_vals: list[float] = []
        centers: list[float] = []
        scales: list[float] = []
        ind_indices: list[int] = []

        for j in range(n_cols):
            valid = [float(r[j]) for r in x_train if r[j] is not None and math.isfinite(r[j])]
            has_missing = len(valid) < len(x_train)
            if has_missing and self.config.add_missing_indicators:
                ind_indices.append(j)
            if not valid:
                fill_vals.append(0.0)
                centers.append(0.0)
                scales.append(1.0)
                continue

            sv = sorted(valid)
            m = len(sv)
            median = sv[m // 2] if m % 2 == 1 else 0.5 * (sv[m // 2 - 1] + sv[m // 2])
            mean = sum(sv) / m

            fill = median if self.config.impute_strategy == "median" else mean
            fill_vals.append(fill)

            if self.config.scale_strategy == "robust":
                q25 = sv[int(0.25 * (m - 1))]
                q75 = sv[int(0.75 * (m - 1))]
                iqr = q75 - q25
                center = median
                scale = (
                    iqr
                    if iqr > 1e-9
                    else (math.sqrt(sum((x - mean) ** 2 for x in sv) / max(1, m - 1)) or 1.0)
                )
            else:
                center = mean
                var = sum((x - mean) ** 2 for x in sv) / max(1, m - 1)
                scale = math.sqrt(var) if var > 1e-12 else 1.0

            centers.append(center)
            scales.append(scale)

        self._state = PreprocessorState(
            feature_names=tuple(feature_names),
            fill_values=tuple(fill_vals),
            centers=tuple(centers),
            scales=tuple(scales),
            indicator_indices=tuple(ind_indices),
        )
        return self

    def transform(self, x_rows: Sequence[Sequence[float | None]]) -> list[list[float]]:
        st = self.state
        n_cols = len(st.feature_names)
        clip = self.config.clip_abs_value
        out: list[list[float]] = []

        for row in x_rows:
            if len(row) != n_cols:
                raise ValueError(f"Expected {n_cols} features, got {len(row)}.")
            vec: list[float] = []
            miss_flags: list[float] = []
            for j in range(n_cols):
                raw = row[j]
                is_miss = raw is None or not math.isfinite(raw)
                val = st.fill_values[j] if is_miss else float(raw)
                scaled = (val - st.centers[j]) / st.scales[j]
                if scaled > clip:
                    scaled = clip
                elif scaled < -clip:
                    scaled = -clip
                vec.append(scaled)
                if j in st.indicator_indices:
                    miss_flags.append(1.0 if is_miss else 0.0)
            vec.extend(miss_flags)
            out.append(vec)
        return out

    def fit_transform(
        self,
        x_train: Sequence[Sequence[float | None]],
        feature_names: Sequence[str],
        *,
        split_name: str = "train",
    ) -> list[list[float]]:
        return self.fit(x_train, feature_names, split_name=split_name).transform(x_train)
