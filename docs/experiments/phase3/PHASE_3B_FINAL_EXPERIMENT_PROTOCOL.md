# DA-FIDAF — Phase 3B Final Experiment Protocol

- **Protocol Status:** Validated Design Specification — **Execution is NOT authorized automatically.**
- **Seeds (All Experiments):** `5` independent deterministic seeds: `[42, 101, 202, 303, 404]`.
- **Simulated Clients:** `K = 10` simulated logical gateways (`sim_gw_01` .. `sim_gw_10`, explicitly disclosed as `simulated_logical_gateway`).
- **Preprocessing:** `TrainOnlyPreprocessor` fitted strictly on Train (`split_name="train"`), frozen for Validation and Test.

---

## 1. E1 — Heterogeneous Federated Learning (IID vs. Non-IID)

- **Datasets:** `train_test_network.csv` (full `211,043`, stratified 70/15/15) and `W1` (`Shards 22+23`, chronological 70/15/15, `300s` embargo).
- **Partition Regimes (Strictly Inside Train):**
  - `iid`: Class-stratified uniform split across `K = 10` clients.
  - `label_skew`: Dirichlet allocation with $\alpha \in \{0.5, 0.1\}$; record per-client `(n_total, n_benign, n_attack, benign_fraction)`.
  - `quantity_skew`: Log-normal volume imbalance ($\sigma = 0.8$).
  - `combined`: Joint Dirichlet ($\alpha = 0.5$) + log-normal quantity skew.
- **Sample-Weighting Investigation:** Compare standard sample-weighted `FedAvg` ($w_k = n_k / N$) against `FedProx` ($\mu \in \{0.01, 0.05, 0.1\}$) and uniform-weighted FedAvg ($w_k = 1/K$) to quantify and mitigate the Phase 3A benign-rich client underrepresentation failure.
- **Validation-Only Threshold Calibration:** Evaluate test metrics at BOTH fixed `0.50` threshold AND $\tau^*_{\text{val}}$ selected exclusively on the Validation split (maximizing Validation Macro-F1; Test remains strictly untouched until final evaluation).
- **Metrics:** Class-wise Precision/Recall/F1 (Class 0 benign & Class 1 attack), Macro-F1, ROC-AUC, PR-AUC, FPR, FNR, per-round validation BCE loss.

---

## 2. E2 — Concept Drift Detection & Continual Adaptation

- **Datasets:** `W1` (`Shards 22+23`, `300s` and `900s` embargo sensitivity) + `W3` (natural novel-attack emergence).
- **Strict Drift Taxonomy:**
  - **Covariate Shift ($P_t(X)$ changes, $P(Y|X)$ fixed):** Monitored via `FeatureDriftDetector` (PSI/JSD). **PSI alone is NEVER claimed as proof of conditional concept drift.**
  - **Prior / Label Shift ($P_t(Y)$ changes):** Tracked via class-proportion shifts across chronological windows.
  - **Conditional Concept Drift ($P_t(Y|X)$ changes):** Monitored via `PageHinkleyDetector` on streaming validation error/loss + ground-truth conditional accuracy degradation.
- **Intervention Arms (Explicitly Separated):**
  1. **Natural Chronological:** `W1` (`mitm` emergence in Test) & `W3` (`ransomware`/`backdoor`/`mitm` emergence).
  2. **Controlled Synthetic Interventions (`is_synthetic=True`):** `stable` (control), `abrupt` (step at onset round), `gradual` (linear ramp over 4 rounds), and `recurring` (periodic oscillation, period 3) across `covariate_shift`, `prior_shift`, and `conditional_concept_drift`.
- **Adaptation Baselines:** Static FL (no adaptation) vs. `fine_tune` vs. `regularized` vs. `replay` (`ContinualAdapter`).
- **Metrics:** Detection delay (rounds from onset to alarm), False Alarm Rate (alarms during `stable` control rounds), Recovery time (rounds to restore >=95% pre-drift Macro-F1), and Catastrophic Forgetting (`forgetting_delta` on prior replay split).

---

## 3. E3 & E4 — Adversarial Attacks, Attribution & Robust Aggregation

- **Threat Model & Attacker Capabilities:**
  - **Compromised Proportion:** $f = 2$ of $K = 10$ simulated clients (`20%`, satisfying Krum/Multi-Krum precondition $n \ge 2f + 3$: $10 \ge 7$), active from `round = 2` through final round (`sim_gw_01`, `sim_gw_02`).
  - **E3 (Benign Drift vs. Poisoning Attribution on `W1`):**
    - Benign drift arm: `sim_gw_03..05` receive labeled synthetic covariate shift (`is_synthetic=True`).
    - Poisoning arms (strictly in-memory): `label_flip` (`30%`), `data_poisoning` (Gaussian noise $\sigma=3.0$, `30%`), `backdoor` (trigger `5.0` on `f0,f1`, target `0`, `20%`).
    - Ground-truth attribution labels (`malicious` vs `benign_drifted` vs `normal`) are held strictly outside `DriftAttackAttributor.attribute_round()` and used only by `compute_attribution_metrics()`.
  - **E4 (Byzantine Robust Aggregation on `train_test_network.csv` + `W1`):**
    - Byzantine attacks (in-memory): `sign_flip` ($-8\times$), `scaled_update` ($+8\times$), `random_update` (deterministic `blake2b`-seeded Gaussian $\sigma=2.0$), `model_replacement`, and `NaN`/`Inf` poisoning.
    - Aggregators compared: `fedavg`, `median`, `trimmed_mean` (`trim_ratio=0.2`), `krum` (`f=2`), `multi_krum` (`f=2`).
    - Documented limitations: Median/Trimmed-Mean/Krum degrade under extreme Non-IID ($\alpha=0.1$) where honest updates naturally diverge.

---

## 4. E5 — Cross-Dataset Generalization (`HOLD`)

- **Status:** **BLOCKED / HOLD** (`E5OntologyBlockedError`). Will not execute in Phase 3B until a formally reviewed cross-dataset semantic feature and attack ontology alignment is approved.

---

## 5. E6 — System Ablation, Overhead & Conditional Privacy Trade-offs

- **Ablation Matrix:** `full_dafidaf`, `without_drift_detection`, `without_robust_aggregation`, `without_attribution`, `without_continual_adaptation`.
- **Efficiency & Systems Telemetry:**
  - Communication bytes per round & total communication volume (`total_bytes_communicated`).
  - Per-round training wall time & end-to-end inference latency (ms / 1,000 flows).
  - Peak resident memory (`tracemalloc` peak MB) & serialized model parameter size (bytes).
  - Utility vs. robustness trade-off (Macro-F1 retention under attack vs. clean overhead).
- **Conditional Privacy Sweep:** Simulation-grade RDP Gaussian DP ($\sigma \in \{0.5, 1.0, 2.0\}$, $\delta = 10^{-5}$, $C = 1.0$; both `local_per_client` and `central_aggregate`). All outputs explicitly retain `formal_deployment_dp_claim: False` (Mersenne Twister PRNG) and `secure_aggregation_active: False`.
