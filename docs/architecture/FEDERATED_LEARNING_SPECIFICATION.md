# DA-FIDAF — Federated Learning & Privacy Specification

## 1. Architecture Overview

Workstream B implements a deterministic, reproducible synchronous Federated Learning (FL) engine in pure Python 3.12 (`src/dafidaf/models/`, `src/dafidaf/privacy/`, `src/dafidaf/federated/`).

```
SimulatedClient (sim_gw_XX)
   └─ Local SGD / FedProx (LinearLogisticIDS)
        └─ Delta = w_local - w_global
             ├─ [Optional] Adversarial Hook (Byzantine / Data Poisoning)
             ├─ [Optional] L2 Clipping + Gaussian DP Noise + PrivacyAccountant
             └─ DriftAttackAttributor (Workstream C)
                  └─ Robust Server Aggregation (FedAvg / Median / TrimmedMean / Krum / Multi-Krum)
                       └─ Updated Global Model + Round Telemetry
```

---

## 2. Model Interface (`src/dafidaf/models/logistic.py`)

- **`ModelInterface`**: Minimal protocol (`get_weights`, `set_weights`, `fit_local`, `predict_proba`, `predict`, `evaluate_loss`) enabling future drop-in PyTorch neural architectures in Phase 3 without changing the FL trainer or aggregators.
- **`LinearLogisticIDS`**: Numerically stable binary logistic regression IDS with:
  - Clipped sigmoid (`[-35.0, 35.0]`) to prevent overflow.
  - Deterministic L2 regularization (`l2_reg`).
  - **FedProx** proximal penalty $\frac{\mu}{2}\|w - w_{\text{global}}\|_2^2$ when `proximal_mu > 0.0` to stabilize non-IID client updates.

---

## 3. Client Abstraction (`src/dafidaf/federated/client.py`)

- **`SimulatedClient`** encapsulates a single federated gateway's local Train partition.
- **Identity Guard**: Enforces that `client_id` begins with `sim_` (e.g., `sim_gw_00`), preventing any misrepresentation of simulated partitions as physical IoT devices.
- Returns structured `ClientUpdate` objects containing `client_id`, parameter `delta`, `num_samples`, `local_loss`, and optional feature-distribution summaries for drift attribution.

---

## 4. Server Aggregation (`src/dafidaf/federated/aggregation.py`)

| Aggregator | Function | Byzantine Tolerance | Notes |
| --- | --- | --- | --- |
| FedAvg | `fedavg` | None (`f = 0`) | Sample-size weighted average baseline |
| Coordinate-wise Median | `coordinate_median` | Up to `< 50%` per coordinate | Resistant to unbounded scaling attacks |
| Coordinate-wise Trimmed Mean | `trimmed_mean` | Trims `trim_ratio` top & bottom | Smooth robust alternative to Median |
| Krum | `krum` | `n >= 2f + 3` enforced | Selects single update with smallest sum of `n - f - 2` nearest squared distances |
| Multi-Krum | `multi_krum` | `n >= 2f + 3` enforced | Averages top `m` Krum-ranked updates |

All robust aggregators validate input dimensions and raise `ValueError` when Byzantine tolerance preconditions (such as `n >= 2f + 3` for Krum/Multi-Krum) are violated.

---

## 5. Privacy Mechanisms & Threat Model (`src/dafidaf/privacy/mechanisms.py`)

### 5.1 Implemented: User-Level Differential Privacy (DP-SGD / DP-FedAvg)
- **`clip_update_l2(delta, max_norm)`**: Bounds each client update's L2 sensitivity to $C = \text{max\_norm}$.
- **`add_gaussian_dp_noise(delta, noise_multiplier, max_norm, rng)`**: Adds isotropic Gaussian noise $\mathcal{N}(0, (\sigma C)^2 I)$ deterministically seeded via `rng`.
- **`PrivacyAccountant`**: Tracks cumulative composition across communication rounds and reports `(epsilon, delta)` bounds along with noise multiplier $\sigma$, clip norm $C$, and sampling rate $q$.

### 5.2 Honest Status: Secure Aggregation (`SecureAggregationInterface`)
- `SecureAggregationInterface` documents the honest-but-curious server threat model and exposes the protocol hooks (`setup_masks`, `mask_update`, `unmask_aggregate`).
- **`secure_aggregation_active` is explicitly `False`** in Phase 2. No cryptographic pairwise masking or secret sharing is executed; any experiment telemetry records `secure_aggregation_active: false` to prevent overclaiming.

---

## 6. Federated Trainer (`src/dafidaf/federated/trainer.py`)

`FederatedTrainer` orchestrates `num_rounds` of synchronous FL:
1. Broadcasts current global weights to participating `SimulatedClient` instances.
2. Collects local updates (with optional `update_hook` for Byzantine simulation or attribution inspection).
3. Applies optional per-client L2 clipping + Gaussian DP noise and updates `PrivacyAccountant`.
4. Aggregates updates using the configured aggregator (`fedavg`, `coordinate_median`, `trimmed_mean`, `krum`, `multi_krum`).
5. Logs per-round validation metrics and optionally writes JSON round checkpoints to `DAFIDAF_RUNS_ROOT`.
