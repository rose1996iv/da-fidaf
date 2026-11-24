# DA-FIDAF — Evaluation Protocol

## 1. Metric Suite (`src/dafidaf/evaluation/metrics.py`)

### 1.1 Intrusion Detection Metrics (`compute_classification_metrics`)
Because IoT intrusion datasets are heavily class-imbalanced, accuracy alone is insufficient. Every experiment reports:
- **Macro-F1** (primary classification metric)
- **PR-AUC** (Precision-Recall Area Under Curve — sensitive to minority-class performance)
- **ROC-AUC** (Receiver Operating Characteristic Area Under Curve)
- **FPR** (False Positive Rate — critical for operational SOC alert fatigue)
- **FNR** (False Negative Rate — missed intrusion rate)
- **Precision, Recall, Accuracy**, and full confusion counts (`tp`, `fp`, `tn`, `fn`)

### 1.2 Attribution Metrics (`compute_attribution_metrics`)
For E3/E4 drift-vs-attack attribution experiments:
- **False Attribution Rate (FAR)**: Fraction of benign or benign-drifted clients wrongly flagged as malicious.
- **Malicious Recall**: Fraction of Byzantine / poisoned clients correctly flagged as malicious.
- **Drift Precision / Recall**: Accuracy of identifying `benign_distribution_drift` clients.
- **Uncertain Rate**: Fraction of updates routed to `uncertain_insufficient_evidence`.

### 1.3 Multi-Seed Statistical Rigor (`summarize_multi_seed`, `paired_effect_size_and_ci`)
- Every real-dataset experiment (E1–E4, E6) is configured for **multiple deterministic seeds** (minimum 3–5 seeds).
- Reports `mean`, `std`, `min`, `max`, and 95% confidence intervals.
- Compares baselines vs. DA-FIDAF using paired differences, Cohen's $d_z$ effect size, and bootstrap/t-based 95% confidence intervals.

---

## 2. Leakage-Free Evaluation Rules

1. **Temporal Ordering**: Train precedes Validation, which precedes Test, separated by a 300s or 900s buffer gap with active-flow exclusion (`ts + duration` crossing a boundary is dropped).
2. **Pre-Adaptation vs. Post-Adaptation Separation**: The converged global FL model is evaluated on the clean chronological Test split *before* running `ContinualAdapter` on drifted streams; post-adaptation metrics are reported separately on both source (forgetting) and drifted (recovery) evaluation sets.
3. **Train-Only Fitting**: `TrainOnlyPreprocessor` and `FeatureDriftDetector` reference histograms are fitted strictly on Train data.

---

## 3. Experiment Matrix (E1–E6)

| Experiment | Objective | Primary Metrics | Status |
| --- | --- | --- | --- |
| **E1** (`e1_iid_vs_noniid.yaml`) | IID vs. Non-IID (Dirichlet label/feature/quantity skew) + FedAvg vs. FedProx | Macro-F1, PR-AUC, FPR, convergence rounds | Code & Config Ready |
| **E2** (`e2_concept_drift.yaml`) | Abrupt/gradual/recurring drift detection + continual adaptation | Detection delay, recovery Macro-F1, forgetting | Code & Config Ready |
| **E3** (`e3_benign_drift_vs_poisoning.yaml`) | Separating benign covariate drift from label-flip/backdoor poisoning | FAR, Malicious Recall, Drift Precision | Code & Config Ready |
| **E4** (`e4_byzantine_robust_agg.yaml`) | FedAvg vs. Median / Trimmed Mean / Krum / Multi-Krum under Byzantine attacks | Robust Macro-F1, attack impact, FPR | Code & Config Ready |
| **E5** (`e5_cross_dataset_hold.yaml`) | Cross-dataset generalization (ToN-IoT ↔ CICIoT2023 ↔ Edge-IIoTset) | Cross-domain Macro-F1 | **HOLD** (`E5OntologyBlockedError`) |
| **E6** (`e6_ablation_overhead.yaml`) | DP-SGD privacy-utility tradeoff & component ablation overhead | Macro-F1 vs. $(\epsilon, \delta)$, wall-clock overhead | Code & Config Ready |
