# DA-FIDAF — Architecture Alignment Audit

- **Authoritative Baseline Status:** Original approved proposal architecture diagram and equations are **MISSING** from `I:\Projects\da-fidaf` and `I:\IoT`. This audit compares the implemented repository architecture (`src/dafidaf/`) against the high-level attested scope (`README.md`) and downstream engineering blueprint (`PHASE_2_IMPLEMENTATION_BLUEPRINT.md`), clearly flagging every Category C engineering assumption.

---

## 1. Module-by-Module Architectural Assessment

1. **Data & Temporal Layer (`src/dafidaf/data/`):**
   - *Category B (Verified):* Read-only adapters (`TonIoT`, `CICIoT2023`, `Edge-IIoTset`), `flow_extract_v1` (PCAPNG/libpcap ZIP-stream SLL 113), `chronological_split` (`300s`/`900s` + active-flow exclusion), `TrainOnlyPreprocessor`, `E5OntologyBlockedError`.
   - *Category C (Inferred):* Using only 10 numeric ToN-IoT columns (excluding protocol/service/conn_state categorical encodings) and uniform temporal striding (`W1 stride=15`, `W3 stride=80`).
2. **Model Layer (`src/dafidaf/models/logistic.py`):**
   - *Category B (Verified):* Pure-Python `LinearLogisticIDS` behind `ModelInterface` (`88–96 B` parameters).
   - *Category C (Inferred & Empirically Insufficient):* Chosen to preserve `pyproject.toml`/`uv.lock` during Phase 2; Phase 3B.2 Workstream A proved `8/8` active flow features invert sign between W1 `xss` Train (`AUC=0.934`) and `backdoor` Test (`AUC=0.321`). Unlikely to match a PhD proposal's intended deep/non-linear IDS backbone.
3. **Federated & Aggregation Layer (`src/dafidaf/federated/`):**
   - *Category B (Verified):* `SimulatedClient` (`sim_` prefix), `FederatedTrainer` with `filter_finite_updates` and Phase 3B.2 `attribution_filter` closed-loop quarantine, 5 classical aggregators (`fedavg`, `median`, `trimmed_mean`, `krum`, `multi_krum`), FedProx proximal term.
   - *Category C (Inferred):* No custom DA-FIDAF reputation-weighted/adaptive aggregator beyond hard quarantine + classical robust aggregators.
4. **Drift, Attribution & Adaptation Layer (`src/dafidaf/drift/`, `src/dafidaf/attribution/`):**
   - *Category B (Verified):* `FeatureDriftDetector` (PSI/JSD), `PageHinkleyDetector`, `ContinualAdapter` (`replay`/`regularized`/`fine_tune`), `DriftAttackAttributor` (v1 geometric+PSI, v2 + `client_val_loss_delta`).
   - *Category C (Inferred):* Single-round rule-based attribution thresholds (`3.5x`, `6.0x`, `-0.25`, `0.025`). Phase 3B.2 empirically showed v2's `val_loss_delta` causes `4–8/15` benign-drifted clients to be misclassified as malicious (`FAR = 0.40–0.58`).
5. **Privacy Layer (`src/dafidaf/privacy/mechanisms.py`):**
   - *Category B (Verified):* Exact closed-form RDP Gaussian accountant (`local_per_client` & `central_aggregate`), `SecureAggregationInterface` (`active=False`), simulation-only Mersenne Twister PRNG (`formal_deployment_dp_claim: False`).
   - *Gap:* Privacy was explicitly disabled (`Non-DP baseline only`) in all Phase 3B and 3B.2 experiments.
