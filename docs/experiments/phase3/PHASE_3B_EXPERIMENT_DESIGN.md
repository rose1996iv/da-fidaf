# DA-FIDAF — Phase 3B Full Experiment Execution Design

**Status:** Design Specification Only — **Phase 3B is NOT automatically authorized.** Requires explicit user approval before launching full runs.

---

## 1. Experiment Matrix & Dataset Selection

| Exp | Objective | Primary Dataset & Window | Split Policy | Clients (`sim_gw_`) | Seeds | Baselines vs. DA-FIDAF |
| --- | --- | --- | --- | --- | --- | --- |
| **E1** | IID vs. Non-IID Heterogeneity | `train_test_network.csv` (full `211,043` rows) + `W1` (`Shards 22+23`, `51.6h`) | 70/15/15 stratified (`train_test`) & chronological `300s` embargo (`W1`) | `K = 10` | `5` (`42, 101, 202, 303, 404`) | FedAvg vs. FedProx ($\mu \in \{0.01, 0.05, 0.1\}$) across `iid`, `label_skew` ($\alpha \in \{0.5, 0.1\}$), `quantity_skew`, `combined` |
| **E2** | Concept Drift & Continual Adaptation | `W1` (`Shards 22+23`, `51.6h`) + `W3` (novel-attack emergence, `Apr 24–29`) | Chronological 70/15/15; embargo sensitivity `300s` & `900s`; active-flow exclusion | `K = 10` | `5` | Static FL vs. `fine_tune` vs. `regularized` vs. `replay` under natural emergence + labeled synthetic gradual/recurring drift |
| **E3** | Benign Drift vs. Poisoning Attribution | `W1` (`Shards 22+23`) | Chronological 70/15/15 (`300s` embargo) | `K = 10` (`2` malicious) | `5` | No attribution vs. `DriftAttackAttributor` under labeled synthetic covariate shift vs. `label_flip`, `data_poisoning`, `backdoor` |
| **E4** | Byzantine Robust Aggregation | `train_test_network.csv` (full `211,043` rows) + `W1` | Stratified & chronological (`300s` embargo) | `K = 10` (`f = 2`, $n \ge 2f+3$) | `5` | `fedavg`, `median`, `trimmed_mean`, `krum`, `multi_krum` under `sign_flip`, `scaled_update`, `random_update`, `model_replacement`, `NaN` |
| **E5** | Cross-Dataset Generalization | ToN-IoT + CICIoT2023 + Edge-IIoTset | **BLOCKED / HOLD** (`E5OntologyBlockedError`) | N/A | N/A | Blocked until validated cross-dataset feature & label ontology alignment is approved |
| **E6** | Ablation & DP-Utility Overhead | `train_test_network.csv` (full `211,043` rows) + `W1` | Stratified & chronological (`300s` embargo) | `K = 10` | `5` | `full_dafidaf` vs. 4 ablations + simulation-grade RDP DP sweep ($\sigma \in \{0.5, 1.0, 2.0\}$, $\delta=10^{-5}$; `formal_deployment_dp_claim: False`, `secure_aggregation_active: False`) |

---

## 2. Mandatory Statistical & Data-Sufficiency Thresholds

1. **Minimum Class Support:** Every Validation and Test split MUST contain at least **`500` benign flows and `500` attack flows** before computing FPR, FNR, or Macro-F1 (eliminating the Phase 3A 3-benign quantization failure).
2. **Threshold Calibration Discipline:** Report threshold-free `ROC-AUC` and `PR-AUC` alongside both default `0.50` and Validation-tuned thresholds (maximize Validation Macro-F1 or target Validation FPR $\le 5\%$; never tune on Test).
3. **Multi-Seed Statistical Rigor:** Minimum **`n = 5` deterministic seeds** per condition; report mean, SD, and 95% bootstrap CI (`summarize_multi_seed`, `paired_effect_size_and_ci`). Never compute CIs for $n < 3$.
4. **No Head-Truncation Bias:** Never apply `--max-rows` to class-grouped `train_test_network.csv`.
5. **Runtime & Memory Guardrails:** Pure-Python `LinearLogisticIDS` on `211k` rows × `10` rounds × `5` seeds is CPU-bound; bound per-shard chronological subsampling to deterministic stratified/time-strided `50,000–100,000` rows per window (or migrate to vectorized NumPy/PyTorch in Phase 3B if approved) and store all outputs under `I:\Projects\da-fidaf-runs\`.
6. **Governance Holds Preserved:**
   - **E5 remains `HOLD`** until cross-dataset ontology alignment is formally validated.
   - **Privacy claims remain `CONDITIONAL`** (simulation-grade RDP with Mersenne Twister PRNG; Secure Aggregation inactive).
