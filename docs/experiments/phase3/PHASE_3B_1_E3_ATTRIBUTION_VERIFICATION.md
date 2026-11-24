# DA-FIDAF Phase 3B.1 — E3 Independent Drift–Attack Attribution Verification

- **Scope:** All `40` E3 raw `run_report.json` files (`20` W1 + `20` W3; `400` total client-round verdict decisions audited).
- **Detector Isolation Verified (`PASS`):** Inspection of `run_phase3b_e3_e4_e6.py` lines 111–116 confirms `DriftAttackAttributor.attribute_round(round_id, client_updates, client_max_psi=client_psis)` uses strictly observable update vectors (`cosine_to_median`, `norm_ratio_to_median`, `isfinite`) and per-client feature PSI — **zero hidden attack labels** enter the model or attributor.

---

## 1. Independently Recomputed Per-Attack Confusion Matrices (Pooled Across `5` Seeds = `10` Malicious, `40` Benign Client Instances per Arm)

| Window & Arm | TP | FP | FN | TN | Unc (Mal / Ben) | Malicious Client Verdicts | Benign-Drifted (`15` inst) Verdicts |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **W1 `label_flip`** | 3 | 8 | 7 | 32 | 6 / 20 | `uncertain: 6`, `mal_model: 3`, `benign_drift: 1` | `benign_drift: 7`, `uncertain: 7`, `mal_byz: 1` |
| **W1 `data_poisoning`** | 3 | 11 | 7 | 29 | 6 / 18 | `uncertain: 6`, `mal_byz: 3`, `benign_drift: 1` | `benign_drift: 6`, `uncertain: 8`, `mal_byz: 1` |
| **W1 `backdoor`** | 1 | 8 | 9 | 32 | 8 / 18 | `uncertain: 8`, `mal_byz: 1`, `benign_drift: 1` | `benign_drift: 7`, `uncertain: 8` |
| **W1 `byzantine_sign_flip`** | 6 | 11 | 4 | 29 | 4 / 19 | `mal_byz: 4`, `mal_model: 2`, `uncertain: 4` | `benign_drift: 5`, `uncertain: 8`, `mal_byz: 2` |
| **W3 `label_flip`** | 8 | 17 | 2 | 23 | 1 / 15 | `mal_byz: 4`, `mal_model: 3`, `mal_poison: 1`, `benign_drift: 1`, `uncertain: 1` | `benign_drift: 6`, `uncertain: 7`, `mal_byz: 2` |
| **W3 `data_poisoning`** | **0** | 9 | **10** | 31 | 5 / 17 | **`benign_drift: 5`, `uncertain: 5`** | `benign_drift: 10`, `uncertain: 5` |
| **W3 `backdoor`** | 8 | 11 | 2 | 29 | 2 / 18 | `mal_model: 8`, `uncertain: 2` | `benign_drift: 7`, `uncertain: 7`, `mal_byz: 1` |
| **W3 `byzantine_sign_flip`** | 8 | 14 | 2 | 26 | 2 / 13 | `mal_byz: 6`, `mal_model: 2`, `uncertain: 2` | `benign_drift: 9`, `uncertain: 5`, `mal_byz: 1` |

---

## Finding [AUD-04] — MEDIUM: Feature-Noise Blind Spot, High Non-IID FAR, and Attack-Type Conflation

- **Finding ID:** `AUD-04` | **Severity:** `MEDIUM`
- **Evidence File:** `I:\Projects\da-fidaf-runs\phase3b\e3\*` & `PHASE_3B_1_EVIDENCE_MANIFEST.json` (`e3_per_attack_cm_audit`)
- **Verification Method:** Recomputed pooled per-attack confusion matrices and verdict histograms directly from all `40` raw `run_report.json` files.
- **Original Reported vs. Recalculated:** Exact match (`W3 data_poisoning Recall = 0.000`, `W3 label_flip FAR = 0.425`, `W1 FAR = 0.200–0.275`).
- **Three Specific Audit Diagnoses:**
  1. **Root Cause of W3 `data_poisoning` `0.00` Recall:** Adding Gaussian noise (`sigma = 3.0`) to `30%` of client features pushes per-client `feature_psi >= 0.25`, directly triggering `has_feat_drift = True`. Because `DriftAttackAttributor` suppresses `malicious_model_update` and `malicious_data_poisoning` whenever `has_feat_drift` is true, **all 10 poisoned instances** were routed to `benign_distribution_drift` (`5`) or `uncertain` (`5`).
  2. **Non-IID Benign Misclassification:** Honest Non-IID (`alpha = 0.5`) clients accounted for `8–17` false positives per 40 benign instances (`FAR = 20%–42.5%`), mostly among stationary honest minority-class clients rather than benign-drifted clients (drifted clients had lower FP rate `0/15` to `2/15`).
  3. **Malicious Detection vs. Attack-Type Classification:** On `W3 label_flip`, `8/10` attackers were detected as `malicious_*`, but only `1/8` received the specific `malicious_data_poisoning` label (`4` labeled `malicious_byzantine_update`, `3` `malicious_model_update`). Claims must explicitly frame E3 as **binary malicious-client detection**, NOT fine-grained attack-type classification.
- **Recommended Action:** Add server-side clean validation-loss delta probing (`val_loss_delta`) and multi-round temporal persistence before Phase 4 so feature-noise poisoning can be separated from beneficial covariate shift and Non-IID FAR reduced.
