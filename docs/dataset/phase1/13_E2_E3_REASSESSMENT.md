# 13 — E2 and E3 Experiment Feasibility Reassessment (DA-FIDAF Phase 1B)

- **Audit Timestamp (UTC):** `2026-11-24T03:38:32Z`
- **Evidence Basis:** Direct full-stream audit of all `22,339,021` rows of ToN-IoT `Processed_Network_dataset` and all `30` `SecuityEvents_GroundTruth_datasets` CSVs.

## 1. Drift & Threat Taxonomy Distinction (VERIFIED)

| Phenomenon | Local ToN-IoT Evidence | Verdict |
| :--- | :--- | :---: |
| **Stable Benign Baseline Period** | `2019-04-02` – `2019-04-04` (`200,898` normal rows, `0` attacks) | **VERIFIED** |
| **Abrupt Attack-Induced Distribution Shift (Novel Attack Emergence)** | Daily staged introduction of new attack families across `2019-04-23` – `2019-04-29` (`scanning` -> `dos` -> `injection`/`ddos` -> `password` -> `xss` -> `ransomware`/`backdoor` -> `mitm`) | **VERIFIED** |
| **Gradual / Recurring Natural Concept Drift** | **18-day capture gap** (`Apr 5–22`); attack families are non-recurring single-window campaigns | **NOT SUPPORTED** naturally |
| **Natural Benign Environmental Drift** | Normal traffic exists in `Apr 2–4` (`200,898` rows) and `Apr 23–29` (`595,482` rows), separated by an 18-day gap; feature-distribution shift between those two normal windows is **UNVERIFIED** | **UNVERIFIED** (requires Phase 2 statistical shift test) |
| **Controlled Synthetic Drift** | Can be systematically injected in derived experiment pipelines (e.g., gradual covariate/label-prior shift across FL rounds) | **SUPPORTED** (must be explicitly labeled synthetic) |
| **Simulated FL Poisoning Attacks** | No native FL poisoning ground truth exists; must be simulated with fixed seeds and threat model | **SUPPORTED** (must be explicitly labeled simulated) |

## 2. Updated E2 and E3 Decisions

### E2 — Stable vs. Gradual / Abrupt Concept Drift: **HOLD -> CONDITIONAL**
- **Upgrade Rationale:** Phase 1B verified `100.00%` valid Unix timestamps (`22,339,021` rows) in `Processed_Network_dataset`, confirming both a **stable benign baseline (`Apr 2–4`)** and **abrupt novel-attack emergence (`Apr 23–29`)** suitable for Protocol A chronological binary/continual-adaptation drift evaluation.
- **Why NOT `PASS`:**
  1. Natural **gradual** and **recurring** drift are **not** supported by ToN-IoT's staged non-recurring campaign schedule; gradual/recurring regimes must either use explicitly labeled controlled synthetic drift or an additional continuous-capture temporal IoT benchmark.
  2. Requires stable-sorting (`21` minor out-of-order rows), deduplication, IP/port removal, and time-embargo split verification before execution.

### E3 — Benign Drift vs. Poisoning Attacks: **REMAINS HOLD**
- **Rationale:**
  1. Distinguishing **natural benign drift** from **poisoning attacks** requires first verifying whether statistically meaningful benign covariate shift actually occurs between `Apr 2–4` and `Apr 23–29` normal traffic (currently **UNVERIFIED**).
  2. No native poisoning ground truth exists; poisoning must be formally specified in a versioned experimental threat model (attack types, malicious client fraction, round schedule, seeds).
  3. E3 remains **HOLD** until: (a) benign normal-traffic distribution shift (`Apr 2–4` vs `Apr 23–29`) is empirically quantified, and (b) the versioned synthetic benign-drift + poisoning evaluation contract is approved.
