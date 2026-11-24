# DA-FIDAF Phase 3B.2 — E1 W1 Domain-Shift & Score-Inversion Diagnostics (Workstream A)

- **Evidence Source:** Saved W1 checkpoint `I:\Projects\da-fidaf-runs\phase3b\checkpoints\e1_W1_iid_fedavg_seed42\checkpoint_round_008.json` & W3 checkpoint `e1_W3_iid_fedavg_seed42\checkpoint_round_008.json`; `PHASE_3B_2_EVIDENCE_MANIFEST.json`.
- **Integrity Rule:** Scores were **NOT** reversed and labels were **NOT** modified.

---

## 1. Train -> Validation -> Test Trajectory (Proof of Campaign Domain Shift)

| Window | Train ROC-AUC | Val ROC-AUC | Test ROC-AUC | Test Fixed `0.50` Macro-F1 | Test Cal (`0.625`) Macro-F1 |
| --- | --- | --- | --- | --- | --- |
| **W1 (`Shards 22+23`, `seed=42`)** | **`0.933945`** | `0.333538` | `0.320810` | `0.5096` | `0.6992` |
| **W3 (`Shards 8–23`, `seed=42`)** | **`0.874400`** | — | **`0.832135`** | — | — |

The linear classifier converged strongly on W1 Train (`AUC = 0.9339`), ruling out training failure or label corruption.

---

## 2. Exact Per-Feature Sign Inversion (`XSS`-Heavy Train vs. `Backdoor`-Heavy Test)

| Feature | Learned Weight | Train `(Attack - Benign)` | Test `(Attack - Benign)` | Sign Inverted? |
| --- | --- | --- | --- | --- |
| `duration` | `+0.06019` | `+1.48702` | `-2.23648` | **YES** |
| `src_bytes` | `+0.49084` | `+1.94995` | `-1.00628` | **YES** |
| `dst_bytes` | `-0.00150` | `+0.56666` | `-1.61319` | **YES** |
| `missed_bytes` | `+0.01730` | `+0.04637` | `-0.04085` | **YES** |
| `src_pkts` | `+0.34197` | `+0.49792` | `-1.94355` | **YES** |
| `src_ip_bytes` | `+0.07987` | `+0.65430` | `-0.95235` | **YES** |
| `dst_pkts` | `+0.84521` | `+0.70917` | `-2.13025` | **YES** |
| `dst_ip_bytes` | `-0.57550` | `+0.12487` | `-1.87974` | **YES** |
| `http_request_body_len` | `-0.00235` | `0.00000` | `0.00000` | No |
| `http_response_body_len` | `+0.00156` | `+0.00497` | `0.00000` | No |

- **8 of 8 active flow-volume features inverted sign** between W1 Train (`69% xss` high-volume HTTP flows) and W1 Test (`99.4% backdoor` low-volume flows), directly inverting the linear hyperplane (`Test benign mean = 0.7689 > Test attack mean = 0.6415`, see revised figure `fig_E1_03_w1_domain_shift.pdf`).

---

## 3. Scientific Recommendation

A more expressive **non-linear classifier** (e.g., MLP / 1D-CNN / tree ensemble via `ModelInterface`) paired with **unsupervised/semi-supervised domain adaptation** is **strongly scientifically justified** for Phase 4. A single linear boundary cannot separate both high-volume (`xss`) and low-volume (`backdoor`) attack clusters that straddle the benign distribution on opposite sides.
