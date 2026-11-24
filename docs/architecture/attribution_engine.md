# Multi-Evidence Drift–Attack Attribution Engine

- **Implementation Module:** `src/dafidaf/attribution/engine.py` (`DriftAttackAttributor`)
- **Engineering Spec:** [Drift & Attack Attribution Specification](DRIFT_AND_ATTACK_ATTRIBUTION_SPECIFICATION.md)

---

## 1. Draft Conceptual Evidence Dimensions

The latest draft architecture diagrams specify four complementary evidence streams feeding Drift–Attack Attribution:

1. **Update Geometry:** Cosine alignment and update-norm ratios relative to the peer consensus update.
2. **Distribution-Shift Evidence:** Local covariate-shift signals (e.g., Population Stability Index / KS statistics).
3. **Model Behavior:** Client-update effect on held-out clean validation performance (explored experimentally in Phase 3B.2 Workstream B).
4. **Historical Client Behavior:** Multi-round behavioral consistency and drift/anomaly history *(only partially represented in current single-round heuristics)*.

Decisions map to three states: **`Benign Drift`**, **`Uncertain`**, and **`Malicious`**.

---

## 2. Phase 3B (v1) vs. Phase 3B.2 (v2 Experimental) Findings

| Attribution Variant | Mechanism | Observed Strength | Observed Limitation / Regression | Deployment Status |
| --- | --- | --- | --- | --- |
| **E3 v1 (Baseline)** | Geometry (cosine / norm) + PSI shift rules | High recall (`0.80`) on W3 `label_flip`, `backdoor`, `sign_flip` | Complete blind spot on W3 `data_poisoning` (`Recall = 0.000`); moderate FAR (`0.200–0.425`) | Baseline reference only |
| **E3 v2 (Phase 3B.2 Experimental)** | Adds leak-free `client_val_loss_delta` evaluated on clean Val subset (`n=1,000`) | Broke W3 `data_poisoning` blind spot (`Recall: 0.000 -> 0.400`, `TP=4/10`) | **Severe FAR regression (`0.400–0.575`)**; falsely flagged `4–8/15` benign-drifted clients; degraded recall on `label_flip` (`0.80 -> 0.00`), `backdoor` (`0.80 -> 0.20`), `sign_flip` (`0.80 -> 0.30`) | **DO NOT DEPLOY AS DEFAULT** |

!!! warning "Mandatory Scientific Disclosure"
    Phase 3B.2 Workstream B **empirically falsified** naive single-round `client_val_loss_delta` thresholding as a benign-drift-safe discriminator on real Non-IID ToN-IoT traffic because legitimate benign covariate shift also increases loss on a stationary clean validation probe. Future work must separate covariate-shift loss increases from adversarial corruption (`GAP-03`).

See [Phase 3B.2 E3 Attribution Improvement](../experiments/phase3/PHASE_3B_2_E3_ATTRIBUTION_IMPROVEMENT.md).
