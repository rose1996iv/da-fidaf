# Research Overview

**DA-FIDAF** (*Drift-Aware Federated Intrusion Detection and Attribution Framework*) investigates how distributed Internet of Things (IoT) and Industrial IoT (IIoT) gateways can collaboratively train and maintain intrusion detection models without centralizing raw network traffic, while simultaneously coping with:

1. **Statistical heterogeneity (Non-IID data)** across diverse IoT devices and gateways.
2. **Temporal concept drift** caused by benign behavioral evolution and emerging attack campaigns.
3. **Adversarial participation**, including data poisoning, label flipping, backdoor injection, and Byzantine model manipulation.
4. **Privacy constraints** requiring decentralized training and future formal privacy mechanisms.

---

## Core Scientific Hypothesis

Standard Byzantine-robust federated learning (FL) aggregators treat any statistically outlying client update as malicious. In real IoT networks, however, **legitimate benign concept drift** (e.g., new device behaviors or shifting traffic patterns) also produces outlying model updates. Conversely, stealthy poisoning attacks can mimic benign distribution shifts.

DA-FIDAF investigates whether **multi-evidence drift–attack attribution**—combining update geometry, distribution-shift signals, model behavior, and historical client behavior—can distinguish benign drift from malicious manipulation and guide risk-aware aggregation and continual adaptation without excessive false quarantine of honest clients.

---

## Epistemic Status of Current Evidence

| Aspect | Current Status | Verification Basis |
| --- | --- | --- |
| Portable software architecture & leak-free data pipeline | **Verified** | `57/57` tests, Phase 2.2 audit, LF-canonical SHA-256 manifests |
| ToN-IoT real-data Non-DP baseline experiments (E1–E4, E6) | **Executed & Independently Audited** | `490` Phase 3B runs + `60` Phase 3B.2 targeted remediation runs |
| Linear baseline vs. temporal campaign shift (W1) | **Empirically Falsified for Linear IDS** | W1 `Train AUC = 0.9339 -> Test AUC = 0.3208` (`8/8` active features sign-inverted) |
| Single-round `client_val_loss_delta` attribution (E3 v2) | **Empirically Falsified as Default** | Reduced W3 `data_poisoning` blind spot (`0.00 -> 0.40`) but regressed FAR (`0.400–0.575`) |
| Closed-loop attribution quarantine (E6 v2) | **Promising with Over-Quarantine Caveat** | Improved selected `sign_flip` metrics but over-quarantined `41%–45%` client-rounds (`2–3` honest clients/round) |
| Draft `1D-CNN / TCN` local IDS & formal DP / SecAgg / E5 | **Not Yet Implemented / Executed** | Pending original approved PhD proposal alignment and Phase 4 authorization |
