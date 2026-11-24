# Local Intrusion Detection System (IDS) Model

!!! danger "Architecture Divergence Disclosure"
    - **Draft Architecture Diagram 2:** Explicitly depicts a **`1D-CNN / TCN`** (1D Convolutional Neural Network / Temporal Convolutional Network) as the local IDS model.
    - **Current Codebase (`src/dafidaf/models/logistic.py`):** Implements a baseline linear classifier (**`LinearLogisticIDS`**) conforming to `ModelInterface`.
    - **Status:** **`1D-CNN / TCN` is NOT implemented and NOT evaluated.** Current linear results must **never** be presented as `1D-CNN / TCN` results.

---

## 1. Current Verified Implementation (`LinearLogisticIDS`)

- Lightweight deterministic binary classifier implemented in pure NumPy/Python (`src/dafidaf/models/logistic.py`) for reproducible federated weight updates, checkpoint serialization, and fast multi-seed execution.
- Evaluated across `490` Phase 3B runs and `60` Phase 3B.2 runs on ToN-IoT windows W1 and W3.

---

## 2. Empirical Evidence of Linear Expressivity Bottleneck (Phase 3B.2 Workstream A)

Diagnostic inspection of the saved W1 `seed=42` checkpoint (`e1_W1_iid_fedavg_seed42/checkpoint_round_008.json`) proved why a linear hyperplane fails under severe chronological campaign shift:

| Window | Train ROC-AUC | Validation ROC-AUC | Test ROC-AUC |
| --- | ---: | ---: | ---: |
| **W1 (`Shards 22+23`, `seed=42`)** | `0.933945` | `0.333538` | `0.320810` |
| **W3 (`Shards 8–23`, `seed=42`)** | `0.874400` | — | `0.832135` |

- **Root Cause:** `8` of `8` active flow-volume features (`duration`, `src_bytes`, `dst_bytes`, `missed_bytes`, `src_pkts`, `src_ip_bytes`, `dst_pkts`, `dst_ip_bytes`) **inverted sign** between W1 Train (`69% xss`, high-volume HTTP flows) and W1 Test (`99.4% backdoor`, low-volume flows).
- **Implication (`GAP-02`):** A single linear boundary cannot separate multi-modal attack families straddling benign traffic on opposite sides. Implementing a non-linear `1D-CNN / TCN` (or proposal-confirmed neural backbone) via `ModelInterface` is strongly scientifically motivated for future Phase 4 work once the original approved PhD proposal is verified.

See [Phase 3B.2 E1 Domain-Shift Diagnostics](../experiments/phase3/PHASE_3B_2_E1_DOMAIN_SHIFT_DIAGNOSTICS.md).
