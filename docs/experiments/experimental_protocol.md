# Experimental Protocol Overview (E1–E6)

**Primary Protocol References:** [Phase 3B Final Experiment Protocol](phase3/PHASE_3B_FINAL_EXPERIMENT_PROTOCOL.md) · [Experiment Execution Guide](EXPERIMENT_EXECUTION_GUIDE.md) · [Statistical Analysis Plan](phase3/PHASE_3B_STATISTICAL_ANALYSIS_PLAN.md)

---

## 1. Experiment Matrix & Execution Status

| Experiment | Focus | Dataset / Data Source | Privacy Mode | Status |
| --- | --- | --- | --- | --- |
| **E1** | IID vs. Non-IID Heterogeneity (`FedAvg`, `FedProx`, `label_skew`, `quantity_skew`, `combined`) | Real ToN-IoT W1 & W3 (overlapping) | Non-DP only | **Completed & Diagnosed** (W1 score inversion proved in 3B.2) |
| **E2** | Gradual & Abrupt Concept Drift + Replay Adaptation (`300s`/`900s` embargo) | Controlled synthetic drift (`is_synthetic=True`) on real ToN-IoT W1 & W3 | Non-DP only | **Completed** (Round-8 limit & embedded embargo JSONs noted) |
| **E3** | Benign Drift vs. Poisoning Attribution (`label_flip`, `data_poisoning`, `backdoor`, `byzantine_sign_flip`) | Real ToN-IoT W1 & W3 + simulated attacks & benign shift | Non-DP only | **Completed (v1 & v2)** — v2 (`val_loss_delta`) had negative net FAR regression |
| **E4** | Byzantine-Robust Aggregation (`FedAvg`, `Median`, `Trimmed Mean`, `Multi-Krum`) | Real ToN-IoT W1 & W3 + simulated attacks | Non-DP only | **Completed** (Adaptive attacks ALIE/Min-Max pending) |
| **E5** | Cross-Dataset Generalization (ToN-IoT / CICIoT2023 / Edge-IIoTset) | Multi-dataset silos | N/A | **NOT EXECUTED (`HOLD`)** — fails closed (`E5OntologyBlockedError`) |
| **E6** | Closed-Loop Attribution Ablation & Overhead | Real ToN-IoT W1 & W3 + `sign_flip` (`f=2/10`) | Non-DP only | **Completed (3B.2 Genuine Closed-Loop)** — over-quarantine (`41%–45%`) disclosed |

---

## 2. Standard Reproducibility Parameters

- **Random Seeds (`n=5`):** `[42, 101, 202, 303, 404]` (independent unit of statistical analysis).
- **Federation Scale:** `K = 10` simulated logical gateways (`sim_gw_01`..`sim_gw_10`).
- **Primary Statistical Test:** Exact two-sided paired **Student-$t$ 95% CI ($df = 4, t_{0.975, 4} = 2.776445$)** + Cohen's $d_z$; 5,000-resample percentile bootstrap reported only as supplementary (Phase 3B.2 Workstream D).
- **Run Provenance:** LF-canonical `run_report.json` paired with raw-byte `run_report.sha256` sidecars and `canonical_sha256_manifest.json` (`578` files hashed).
