"""Reproducible YAML-driven experiment orchestration and Gate D synthetic smoke-test."""

from __future__ import annotations

import hashlib
import json
import os
import random
import uuid
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

import dafidaf
from dafidaf.attacks.simulators import (
    ByzantineConfig,
    PoisoningConfig,
    apply_byzantine_update,
    apply_data_poisoning,
)
from dafidaf.attribution.engine import DriftAttackAttributor
from dafidaf.data.adapters import (
    CICIoT2023Adapter,
    DatasetAdapter,
    EdgeIIoTsetAdapter,
    TonIoTNetworkAdapter,
)
from dafidaf.data.partitioning import (
    TemporalSplitConfig,
    chronological_split,
    partition_fl_clients,
)
from dafidaf.data.preprocessing import PreprocessorConfig, TrainOnlyPreprocessor
from dafidaf.data.provenance import build_provenance
from dafidaf.data.schemas import (
    CICIOT2023_LABEL_ONTOLOGY,
    EDGE_IIOT_LABEL_ONTOLOGY,
    TON_IOT_LABEL_ONTOLOGY,
    assert_cross_dataset_ontology_ready,
)
from dafidaf.drift.core import (
    ContinualAdapter,
    DriftSpec,
    FeatureDriftDetector,
    apply_synthetic_drift,
)
from dafidaf.evaluation.metrics import (
    compute_attribution_metrics,
    compute_classification_metrics,
    summarize_multi_seed,
)
from dafidaf.federated.client import ClientUpdate, SimulatedClient
from dafidaf.federated.trainer import FederatedConfig, FederatedTrainer
from dafidaf.models.logistic import LinearLogisticIDS
from dafidaf.privacy.mechanisms import DPConfig

SUPPORTED_AGGREGATIONS = frozenset({"fedavg", "median", "trimmed_mean", "krum", "multi_krum"})
SUPPORTED_PARTITIONS = frozenset({"iid", "label_skew", "feature_skew", "quantity_skew", "combined"})
SUPPORTED_ABLATIONS = frozenset(
    {
        "full_dafidaf",
        "without_drift_detection",
        "without_robust_aggregation",
        "without_attribution",
        "without_continual_adaptation",
    }
)
SUPPORTED_YAML_KEYS = frozenset(
    {
        "experiment_id",
        "name",
        "status",
        "reason",
        "seed",
        "seeds_multi_run",
        "datasets",
        "temporal_protocol",
        "federation",
        "preprocessing",
        "dp",
        "drift_interventions",
        "interventions",
        "byzantine",
        "ablations",
        "ablation",
        "telemetry",
        "disclosure",
        "required_before_unblock",
    }
)


def _unique_run_id(prefix: str, seed: int) -> str:
    ts_tag = datetime.now(tz=UTC).strftime("%Y%m%dT%H%M%S_%fZ")
    nonce = uuid.uuid4().hex[:6]
    return f"{ts_tag}_{prefix}_seed{seed}_{nonce}"


def _write_run_report(runs_root: Path, run_id: str, payload: dict[str, object]) -> Path:
    run_dir = runs_root / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    raw_txt = json.dumps(payload, indent=2) + "\n"
    out_file = run_dir / "run_report.json"
    tmp_file = run_dir / ".run_report.json.tmp"
    tmp_file.write_text(raw_txt, encoding="utf-8", newline="\n")
    os.replace(tmp_file, out_file)
    sha_txt = hashlib.sha256(out_file.read_bytes()).hexdigest() + "  run_report.json\n"
    (run_dir / "run_report.sha256").write_text(sha_txt, encoding="utf-8", newline="\n")
    return run_dir


def _select_adapter(primary_spec: str) -> DatasetAdapter:
    low = primary_spec.strip().lower()
    if low.startswith("ton-iot") or low.startswith("ton_iot"):
        return TonIoTNetworkAdapter()
    if low.startswith("ciciot2023") or low.startswith("ciciot"):
        return CICIoT2023Adapter()
    if low.startswith("edge-iiot") or low.startswith("edge_iiot"):
        return EdgeIIoTsetAdapter()
    raise ValueError(f"Unsupported dataset family in YAML datasets.primary: {primary_spec!r}")


def generate_synthetic_iot_dataset(
    *,
    n_samples: int = 1200,
    n_features: int = 8,
    seed: int = 42,
) -> tuple[list[list[float | None]], list[int], list[float], list[float], tuple[str, ...]]:
    """Generate deterministic timestamped synthetic IoT-like flow data for smoke tests ONLY."""
    rng = random.Random(seed)
    base_ts = 1_554_198_358.0
    feat_names = tuple(f"synth_f{j}" for j in range(n_features))
    x_rows: list[list[float | None]] = []
    y_rows: list[int] = []
    timestamps: list[float] = []
    durations: list[float] = []

    for i in range(n_samples):
        ts = base_ts + i * 10.0
        y = 1 if rng.random() < 0.35 else 0
        shift = 1.6 if y == 1 else -1.0
        row: list[float | None] = [
            round(rng.gauss(shift if j < 3 else 0.0, 0.9), 5) for j in range(n_features)
        ]
        if i % 40 == 0:
            row[n_features - 1] = None  # Intentional missingness to verify train-only imputation
        x_rows.append(row)
        y_rows.append(y)
        timestamps.append(ts)
        durations.append(round(rng.uniform(0.01, 5.0), 3))

    return x_rows, y_rows, timestamps, durations, feat_names


@dataclass(frozen=True, slots=True)
class SyntheticE2EResult:
    """Complete output of a synthetic smoke-test DA-FIDAF pipeline run."""

    run_id: str
    run_dir: str | None
    test_metrics: dict[str, object]
    attribution_metrics: dict[str, object]
    drift_detected: bool
    forgetting_delta: float
    total_comm_bytes: int
    provenance: dict[str, object]


def run_synthetic_e2e_experiment(
    *,
    runs_root: Path | None = None,
    seed: int = 42,
    n_clients: int = 10,
    rounds: int = 5,
    aggregation: str = "trimmed_mean",
    partition_strategy: str = "label_skew",
) -> SyntheticE2EResult:
    """Execute synthetic end-to-end DA-FIDAF smoke test (explicitly NOT real-data evidence)."""
    x_raw, y_raw, timestamps, durations, feat_names = generate_synthetic_iot_dataset(
        n_samples=1200, n_features=8, seed=seed
    )

    split = chronological_split(
        timestamps,
        durations,
        TemporalSplitConfig(embargo_seconds=300.0, exclude_active_end_time=True),
    )

    x_train_raw = [x_raw[i] for i in split.train_indices]
    x_val_raw = [x_raw[i] for i in split.val_indices]
    x_test_raw = [x_raw[i] for i in split.test_indices]

    pre = TrainOnlyPreprocessor()
    x_train_all = pre.fit_transform(x_train_raw, feat_names, split_name="train")
    x_val = pre.transform(x_val_raw)
    x_test = pre.transform(x_test_raw)
    y_train_all = [y_raw[i] for i in split.train_indices]
    y_val = [y_raw[i] for i in split.val_indices]
    y_test = [y_raw[i] for i in split.test_indices]

    local_train_idxs = list(range(len(split.train_indices)))
    part = partition_fl_clients(
        local_train_idxs,
        y_train_all,
        n_clients=n_clients,
        strategy=partition_strategy,
        seed=seed,
        timestamps=[timestamps[i] for i in split.train_indices],
        val_start_ts=split.val_start_ts,
    )

    clients = [
        SimulatedClient(
            cid,
            [x_train_all[i] for i in idxs],
            [y_train_all[i] for i in idxs],
        )
        for cid, idxs in part.client_indices.items()
    ]

    byz_cfg = ByzantineConfig(
        attack_type="sign_flip",
        malicious_clients=("sim_gw_01", "sim_gw_02"),
        scale_factor=8.0,
        active_from_round=2,
        seed=seed,
    )

    def hook(r_id: int, upd: ClientUpdate) -> ClientUpdate:
        return apply_byzantine_update(r_id, upd, byz_cfg)

    n_feat_out = len(x_train_all[0])
    model = LinearLogisticIDS(n_features=n_feat_out, seed=seed)
    fl_cfg = FederatedConfig(
        rounds=rounds,
        local_epochs=2,
        batch_size=32,
        lr=0.1,
        aggregation=aggregation,
        trim_ratio=0.2,
        num_byzantine=2,
        seed=seed,
    )
    trainer = FederatedTrainer(model, clients, fl_cfg, update_hook=hook)
    history = trainer.run(x_val=x_val, y_val=y_val)

    detector = FeatureDriftDetector(psi_threshold=0.25).fit_reference(x_train_all)
    drift_spec = DriftSpec(
        schedule="abrupt", mechanism="covariate_shift", onset_round=rounds, severity=2.0, seed=seed
    )
    x_drifted, y_drifted, _ = apply_synthetic_drift(x_val, y_val, drift_spec, round_id=rounds)
    drift_res = detector.detect(x_drifted)

    client_psis = {c.client_id: 0.02 for c in clients}
    client_psis["sim_gw_03"] = drift_res.max_psi
    attributor = DriftAttackAttributor()
    last_round = history[-1]
    decisions = attributor.attribute_round(
        last_round.round_id,
        last_round.client_updates,
        client_max_psi=client_psis,
    )
    attr_metrics = compute_attribution_metrics(
        set(byz_cfg.malicious_clients),
        [(d.client_id, d.verdict) for d in decisions],
    )

    scores = model.predict_proba(x_test)
    preds = [1 if s >= 0.5 else 0 for s in scores]
    test_metrics = compute_classification_metrics(y_test, preds, scores)

    adapter = ContinualAdapter(strategy="replay")
    adapt_res = adapter.adapt(
        model, x_drifted, y_drifted, x_train_all[:200], y_train_all[:200], seed=seed
    )

    prov = build_provenance(
        dataset_id="synthetic_iot_e2e",
        source_file="in_memory_generator",
        source_sha256=None,
        seed=seed,
        temporal_split_policy="chronological_70_15_15_active_endtime",
        embargo_seconds=300.0,
        client_partition_strategy=partition_strategy,
    ).to_dict()

    run_id = _unique_run_id("synthetic_e2e", seed)
    run_dir_str: str | None = None
    total_comm = sum(r.total_bytes_communicated for r in history)

    if runs_root is not None:
        report_payload: dict[str, object] = {
            "run_id": run_id,
            "data_source": "SYNTHETIC_TOY_GENERATOR",
            "is_synthetic_smoke_test": True,
            "code_version": getattr(dafidaf, "__version__", "unknown"),
            "test_metrics": test_metrics.to_dict(),
            "attribution_metrics": asdict(attr_metrics),
            "drift_detected": drift_res.drift_detected,
            "drift_max_psi": drift_res.max_psi,
            "adaptation": asdict(adapt_res),
            "total_comm_bytes": total_comm,
            "privacy": trainer.accountant.summary(),
            "provenance": prov,
        }
        run_dir = _write_run_report(runs_root, run_id, report_payload)
        run_dir_str = str(run_dir)

    return SyntheticE2EResult(
        run_id=run_id,
        run_dir=run_dir_str,
        test_metrics=test_metrics.to_dict(),
        attribution_metrics=asdict(attr_metrics),
        drift_detected=drift_res.drift_detected,
        forgetting_delta=adapt_res.forgetting_delta,
        total_comm_bytes=total_comm,
        provenance=prov,
    )


def _stratified_split_indices(
    labels: list[int],
    *,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    seed: int = 42,
) -> tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]:
    rng = random.Random(seed)
    by_cls: dict[int, list[int]] = {0: [], 1: []}
    for i, y in enumerate(labels):
        by_cls.setdefault(y, []).append(i)
    tr: list[int] = []
    va: list[int] = []
    te: list[int] = []
    for idxs in by_cls.values():
        shuf = list(idxs)
        rng.shuffle(shuf)
        n = len(shuf)
        n_tr = max(1, int(round(n * train_ratio)))
        n_va = max(1, int(round(n * val_ratio)))
        if n_tr + n_va >= n:
            n_va = max(1, (n - n_tr) // 2)
            n_tr = max(1, n - n_va - 1)
        tr.extend(shuf[:n_tr])
        va.extend(shuf[n_tr : n_tr + n_va])
        te.extend(shuf[n_tr + n_va :])
    if not tr or not va or not te:
        raise ValueError("Insufficient samples to construct non-empty train/val/test splits.")
    return tuple(sorted(tr)), tuple(sorted(va)), tuple(sorted(te))


def _run_single_real_seed(
    *,
    exp_id: str,
    cfg: dict[str, Any],
    dataset_csv: Path,
    allowed_root: Path | None,
    seed: int,
    max_rows: int | None,
    runs_root: Path | None,
) -> dict[str, object]:
    datasets_cfg = cfg.get("datasets")
    if not isinstance(datasets_cfg, dict) or not datasets_cfg.get("primary"):
        raise ValueError("YAML must define 'datasets.primary' for real-dataset execution.")
    adapter = _select_adapter(str(datasets_cfg["primary"]))
    ds = adapter.load(dataset_csv, max_rows=max_rows, allowed_root=allowed_root)

    fed_cfg = cfg.get("federation", {})
    if not isinstance(fed_cfg, dict):
        raise ValueError("'federation' section in YAML must be a mapping.")
    n_clients = int(fed_cfg.get("n_clients", 10))
    rounds = int(fed_cfg.get("rounds", 10))
    local_epochs = int(fed_cfg.get("local_epochs", 2))
    batch_size = int(fed_cfg.get("batch_size", 32))
    lr = float(fed_cfg.get("lr", 0.05))
    proximal_mu = float(fed_cfg.get("proximal_mu", 0.0))
    aggregation = str(fed_cfg.get("aggregation", "fedavg"))
    trim_ratio = float(fed_cfg.get("trim_ratio", 0.2))
    partition_strategy = str(fed_cfg.get("partition_strategy", "label_skew"))
    dirichlet_alpha = float(fed_cfg.get("dirichlet_alpha", 0.5))

    if aggregation not in SUPPORTED_AGGREGATIONS:
        raise ValueError(f"Unsupported aggregation strategy in YAML: {aggregation!r}")
    if partition_strategy not in SUPPORTED_PARTITIONS:
        raise ValueError(f"Unsupported partition_strategy in YAML: {partition_strategy!r}")

    ablation = str(cfg.get("ablation", "full_dafidaf"))
    if ablation not in SUPPORTED_ABLATIONS:
        raise ValueError(f"Unsupported ablation mode in YAML: {ablation!r}")
    if ablation == "without_robust_aggregation":
        aggregation = "fedavg"

    # Temporal split when timestamps exist; explicit stratified fallback otherwise
    temp_cfg = cfg.get("temporal_protocol", {})
    if not isinstance(temp_cfg, dict):
        raise ValueError("'temporal_protocol' in YAML must be a mapping.")
    embargo_s = float(temp_cfg.get("embargo_seconds", 300.0))
    exclude_active = bool(temp_cfg.get("exclude_active_end_time", True))
    split_ratios = temp_cfg.get("split_ratios", [0.70, 0.15, 0.15])
    if len(split_ratios) != 3:
        raise ValueError("temporal_protocol.split_ratios must have exactly 3 values.")

    if ds.timestamps is not None:
        split = chronological_split(
            ds.timestamps,
            ds.durations,
            TemporalSplitConfig(
                train_ratio=float(split_ratios[0]),
                val_ratio=float(split_ratios[1]),
                test_ratio=float(split_ratios[2]),
                embargo_seconds=embargo_s,
                exclude_active_end_time=exclude_active,
            ),
        )
        tr_idx, va_idx, te_idx = split.train_indices, split.val_indices, split.test_indices
        val_start_ts: float | None = split.val_start_ts
        split_policy = "chronological_embargo_active_endtime"
    else:
        tr_idx, va_idx, te_idx = _stratified_split_indices(
            list(ds.binary_labels),
            train_ratio=float(split_ratios[0]),
            val_ratio=float(split_ratios[1]),
            seed=seed,
        )
        val_start_ts = None
        split_policy = "stratified_no_timestamps_available"

    pre_cfg_raw = cfg.get("preprocessing", {})
    if not isinstance(pre_cfg_raw, dict):
        raise ValueError("'preprocessing' in YAML must be a mapping.")
    pre = TrainOnlyPreprocessor(
        PreprocessorConfig(
            impute_strategy=str(pre_cfg_raw.get("imputation", "median")),
            scale_strategy=str(pre_cfg_raw.get("scaling", "robust")),
        )
    )
    x_tr = pre.fit_transform([ds.features[i] for i in tr_idx], ds.feature_names, split_name="train")
    x_va = pre.transform([ds.features[i] for i in va_idx])
    x_te = pre.transform([ds.features[i] for i in te_idx])
    y_tr = [ds.binary_labels[i] for i in tr_idx]
    y_va = [ds.binary_labels[i] for i in va_idx]
    y_te = [ds.binary_labels[i] for i in te_idx]

    feat_scores = [r[0] for r in x_tr] if partition_strategy == "feature_skew" else None
    part = partition_fl_clients(
        list(range(len(tr_idx))),
        y_tr,
        n_clients=n_clients,
        strategy=partition_strategy,
        seed=seed,
        dirichlet_alpha=dirichlet_alpha,
        feature_scores=feat_scores,
        timestamps=[ds.timestamps[i] for i in tr_idx] if ds.timestamps is not None else None,
        val_start_ts=val_start_ts,
    )

    # Optional in-memory data poisoning on specified simulated clients
    poison_spec: dict[str, Any] | None = None
    interventions = cfg.get("interventions", {})
    if isinstance(interventions, dict) and interventions.get("poisoning_simulations"):
        p_list = interventions["poisoning_simulations"]
        if isinstance(p_list, list) and p_list:
            poison_spec = p_list[0]

    poison_clients: set[str] = set()
    if poison_spec is not None:
        poison_clients = set(str(c) for c in poison_spec.get("affected_clients", []))

    clients: list[SimulatedClient] = []
    for cid, idxs in part.client_indices.items():
        cx = [x_tr[i] for i in idxs]
        cy = [y_tr[i] for i in idxs]
        if poison_spec is not None and cid in poison_clients:
            pcfg = PoisoningConfig(
                attack_type=str(poison_spec.get("attack_type", "label_flip")),
                poison_fraction=float(poison_spec.get("poison_fraction", 0.3)),
                affected_clients=tuple(sorted(poison_clients)),
                seed=seed,
            )
            cx, cy, _ = apply_data_poisoning(cx, cy, pcfg)
        clients.append(SimulatedClient(cid, cx, cy))

    # Optional Byzantine attack hook
    byz_raw = cfg.get("byzantine")
    byz_cfg: ByzantineConfig | None = None
    if isinstance(byz_raw, dict):
        mal_list = tuple(str(c) for c in byz_raw.get("malicious_clients", []))
        atk_type = str(
            byz_raw.get("attack_type")
            or (byz_raw.get("attack_grid", ["sign_flip"])[0] if byz_raw.get("attack_grid") else "")
            or "sign_flip"
        )
        byz_cfg = ByzantineConfig(
            attack_type=atk_type,
            malicious_clients=mal_list,
            scale_factor=float(byz_raw.get("scale_factor", 8.0)),
            active_from_round=int(byz_raw.get("active_from_round", 2)),
            seed=seed,
        )

    def _hook(r_id: int, upd: ClientUpdate) -> ClientUpdate:
        return apply_byzantine_update(r_id, upd, byz_cfg) if byz_cfg is not None else upd

    dp_raw = cfg.get("dp", {})
    if not isinstance(dp_raw, dict):
        raise ValueError("'dp' in YAML must be a mapping.")
    dp_cfg = DPConfig(
        enabled=bool(dp_raw.get("enabled", False)),
        max_grad_norm=float(dp_raw.get("max_grad_norm", 1.0)),
        noise_multiplier=float(dp_raw.get("noise_multiplier", 0.0)),
        delta=float(dp_raw.get("delta", 1e-5)),
        dp_scope=str(dp_raw.get("dp_scope", "local_per_client")),
    )

    num_byz = len(byz_cfg.malicious_clients) if byz_cfg is not None else 1
    model = LinearLogisticIDS(n_features=len(x_tr[0]), seed=seed)
    fl_cfg = FederatedConfig(
        rounds=rounds,
        local_epochs=local_epochs,
        batch_size=batch_size,
        lr=lr,
        proximal_mu=proximal_mu,
        aggregation=aggregation,
        trim_ratio=trim_ratio,
        num_byzantine=num_byz,
        seed=seed,
        dp=dp_cfg,
    )
    trainer = FederatedTrainer(model, clients, fl_cfg, update_hook=_hook if byz_cfg else None)
    history = trainer.run(x_val=x_va, y_val=y_va)

    # Evaluate converged global model on held-out test set
    scores = model.predict_proba(x_te)
    preds = [1 if s >= 0.5 else 0 for s in scores]
    test_metrics = compute_classification_metrics(y_te, preds, scores)

    # Optional drift detection & continual adaptation (respecting ablation flags)
    drift_detected = False
    drift_max_psi: float | None = None
    forgetting_delta: float | None = None
    drift_raw = cfg.get("drift_interventions", {})
    if ablation != "without_drift_detection":
        det = FeatureDriftDetector(psi_threshold=0.25).fit_reference(x_tr)
        x_eval_drift, y_eval_drift = x_va, y_va
        if isinstance(drift_raw, dict) and drift_raw.get("synthetic_protocol_c"):
            d0 = drift_raw["synthetic_protocol_c"][0]
            spec = DriftSpec(
                schedule=str(d0.get("schedule", "gradual")),
                mechanism=str(d0.get("mechanism", "covariate_shift")),
                onset_round=int(d0.get("onset_round", max(1, rounds // 2))),
                duration_rounds=int(d0.get("duration_rounds", 3)),
                severity=float(d0.get("severity", 1.5)),
                seed=seed,
            )
            x_eval_drift, y_eval_drift, _ = apply_synthetic_drift(x_va, y_va, spec, round_id=rounds)
        dres = det.detect(x_eval_drift)
        drift_detected = dres.drift_detected
        drift_max_psi = dres.max_psi
        if ablation != "without_continual_adaptation" and drift_detected:
            adap = ContinualAdapter(strategy="replay").adapt(
                model,
                x_eval_drift,
                y_eval_drift,
                x_tr[: min(200, len(x_tr))],
                y_tr[: min(200, len(y_tr))],
                seed=seed,
            )
            forgetting_delta = adap.forgetting_delta

    # Optional attribution evaluation (respecting ablation flags)
    attr_summary: dict[str, object] | None = None
    if ablation != "without_attribution":
        attributor = DriftAttackAttributor()
        decs = attributor.attribute_round(history[-1].round_id, history[-1].client_updates)
        true_mal = set(byz_cfg.malicious_clients) if byz_cfg else set(poison_clients)
        attr_summary = asdict(
            compute_attribution_metrics(true_mal, [(d.client_id, d.verdict) for d in decs])
        )

    prov = build_provenance(
        dataset_id=ds.dataset_id,
        source_file=ds.source_path,
        source_sha256=ds.source_sha256,
        seed=seed,
        temporal_split_policy=split_policy,
        embargo_seconds=embargo_s if ds.timestamps is not None else None,
        client_partition_strategy=partition_strategy,
    ).to_dict()

    run_id = _unique_run_id(f"{exp_id.lower()}_{ds.dataset_id.lower()}", seed)
    total_comm = sum(r.total_bytes_communicated for r in history)
    payload: dict[str, object] = {
        "run_id": run_id,
        "experiment_id": exp_id,
        "data_source": "REAL_DATASET",
        "is_synthetic_smoke_test": False,
        "code_version": getattr(dafidaf, "__version__", "unknown"),
        "dataset_id": ds.dataset_id,
        "source_file": ds.source_path,
        "source_sha256": ds.source_sha256,
        "seed": seed,
        "split_policy": split_policy,
        "model": "LinearLogisticIDS",
        "aggregation": aggregation,
        "partition_strategy": partition_strategy,
        "ablation": ablation,
        "rows_loaded": len(ds.features),
        "dropped_invalid_ts": ds.dropped_invalid_ts,
        "dropped_invalid_label": ds.dropped_invalid_label,
        "test_metrics": test_metrics.to_dict(),
        "attribution_metrics": attr_summary,
        "drift_detected": drift_detected,
        "drift_max_psi": drift_max_psi,
        "forgetting_delta": forgetting_delta,
        "total_comm_bytes": total_comm,
        "privacy": trainer.accountant.summary(),
        "provenance": prov,
    }
    if runs_root is not None:
        run_dir = _write_run_report(runs_root, run_id, payload)
        payload["run_dir"] = str(run_dir)
    else:
        payload["run_dir"] = None
    return payload


def run_experiment_from_yaml(
    config_path: Path,
    *,
    runs_root: Path | None = None,
    dataset_csv: Path | None = None,
    allowed_root: Path | None = None,
    max_rows: int | None = None,
    multi_seed: bool = False,
    synthetic_smoke_test: bool = False,
) -> dict[str, object]:
    """Load a versioned YAML experiment config and execute real-data or explicit smoke test."""
    cfg = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(cfg, dict):
        raise ValueError(f"Experiment YAML must be a mapping, got {type(cfg).__name__}.")

    unknown_keys = sorted(set(cfg.keys()) - SUPPORTED_YAML_KEYS)
    if unknown_keys:
        raise ValueError(f"Unsupported top-level keys in experiment YAML: {unknown_keys}")

    exp_id = str(cfg.get("experiment_id", "unknown"))
    if exp_id.upper() == "E5" or str(cfg.get("status", "")).upper() == "HOLD":
        assert_cross_dataset_ontology_ready(
            (TON_IOT_LABEL_ONTOLOGY, CICIOT2023_LABEL_ONTOLOGY, EDGE_IIOT_LABEL_ONTOLOGY)
        )

    fed = cfg.get("federation", {})
    if not isinstance(fed, dict):
        raise ValueError("'federation' section in YAML must be a mapping.")

    if synthetic_smoke_test:
        agg = str(fed.get("aggregation", "trimmed_mean"))
        part_strat = str(fed.get("partition_strategy", "label_skew"))
        if agg not in SUPPORTED_AGGREGATIONS:
            raise ValueError(f"Unsupported aggregation strategy in YAML: {agg!r}")
        if part_strat not in SUPPORTED_PARTITIONS:
            raise ValueError(f"Unsupported partition_strategy in YAML: {part_strat!r}")
        res = run_synthetic_e2e_experiment(
            runs_root=runs_root,
            seed=int(cfg.get("seed", 42)),
            n_clients=int(fed.get("n_clients", 10)),
            rounds=int(fed.get("rounds", 5)),
            aggregation=agg,
            partition_strategy=part_strat,
        )
        return {
            "experiment_id": exp_id,
            "mode": "synthetic_smoke_test",
            "result": asdict(res),
        }

    # Real-dataset path (NEVER silently substitutes synthetic data)
    csv_path = dataset_csv
    if csv_path is None:
        ds_block = cfg.get("datasets", {})
        if isinstance(ds_block, dict) and ds_block.get("csv_path"):
            csv_path = Path(str(ds_block["csv_path"]))
    if csv_path is None:
        raise ValueError(
            f"Real-dataset execution for '{exp_id}' requires --dataset-csv (or datasets.csv_path "
            "in YAML). Refusing silent fallback to synthetic data; pass --synthetic-smoke-test "
            "explicitly to run a synthetic smoke test."
        )

    seeds: list[int] = (
        [int(s) for s in cfg.get("seeds_multi_run", [cfg.get("seed", 42)])]
        if multi_seed
        else [int(cfg.get("seed", 42))]
    )
    seed_results = [
        _run_single_real_seed(
            exp_id=exp_id,
            cfg=cfg,
            dataset_csv=csv_path,
            allowed_root=allowed_root,
            seed=s,
            max_rows=max_rows,
            runs_root=runs_root,
        )
        for s in seeds
    ]
    macro_f1s = [float(r["test_metrics"]["macro_f1"]) for r in seed_results]  # type: ignore[index]
    return {
        "experiment_id": exp_id,
        "mode": "real_dataset",
        "seeds": seeds,
        "multi_seed_macro_f1": asdict(summarize_multi_seed(macro_f1s)),
        "runs": seed_results,
    }
