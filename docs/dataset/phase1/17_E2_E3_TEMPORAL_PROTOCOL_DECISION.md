# 17 — E2 & E3 Temporal Protocol Decision (DA-FIDAF Phase 1C)

- **Audit Timestamp (UTC):** `2026-11-24T03:46:13Z`
- **Scope:** Final Phase 1C protocol recommendation and evidence-based E2/E3 feasibility decision (no splits created; no model training performed).

## 1. Recommended Three-Tier Temporal Evaluation Protocol

1. **Protocol A — Natural Chronological Baseline-vs-Campaign Evaluation (APPROVED WITH CONFOUNDING DISCLOSURE):**
   - Train baseline preprocessing and normal-traffic profile on **Period A (`2019-04-02`–`04`)**; evaluate false-positive rate (FPR) stability on **Period B (`2019-04-23`–`29`) normal traffic** separately from attack detection.
   - Explicitly document the **18-day capture gap**, deduplication sensitivity, and **295x `src_ip` / 73x `http` confounding**.
2. **Protocol B — Abrupt Novel Attack Emergence (APPROVED FOR BINARY & UNSEEN-ATTACK EVALUATION):**
   - Train on earlier chronological windows (`Apr 2–24`) and evaluate on later campaign windows (`Apr 25–26`, `Apr 27–29`) using a **`>= 300s` (5-min) or `900s` (15-min) embargo** plus active-flow end-time (`ts + duration`) exclusion.
   - Report binary intrusion detection (`label`) and unseen-attack recall separately; **never** claim this protocol alone proves benign concept drift.
3. **Protocol C — Controlled Synthetic Gradual / Recurring Drift (APPROVED AS COMPLEMENTARY SIMULATION):**
   - Because ToN-IoT has no continuous organic gradual or recurring drift, evaluate gradual/recurring drift via **explicitly labeled synthetic drift schedules** (specifying exact mechanism, onset round, duration, severity, and random seed in `configs/experiments/*.yaml`), strictly separated from natural-data metrics.

## 2. Final Phase 1C Reassessment of E2 and E3

### E2 — Stable vs. Gradual / Abrupt Concept Drift: **CONDITIONAL**
- **Natural benign covariate shift:** **VERIFIED OBSERVED, BUT CONFOUNDED** (`MMD^2 = 0.18897`, `p = 0.0099`; `src_pkts` `PSI = 1.57`; confounded by 295x `src_ip` & 73x `http` shift).
- **Natural label/prior shift:** **VERIFIED** (`0%` attack in Period A vs `97.3%` attack in Period B).
- **Conditional concept drift $P(y \mid x)$:** **UNVERIFIED** (cannot be isolated from unseen attack introduction and host composition shift).
- **Abrupt novel attack emergence:** **VERIFIED SUPPORTED** (Protocol B).
- **Synthetic gradual / recurring drift:** **SUPPORTED** (Protocol C, explicitly labeled simulated).
- **Verdict:** Remains **CONDITIONAL** (ready to execute once Phase 2 implements Protocols A+B+C with confounding disclosure; not `PASS` due to confounding and lack of organic gradual/recurring drift).

### E3 — Benign Drift vs. Poisoning Attacks: **HOLD -> CONDITIONAL (WITH STRICT SIMULATION & CONFOUNDING DISCLOSURE)**
- **Benign drift evidence:** Real benign covariate shift exists between Period A and Period B normal flows (`MMD^2 = 0.189`), enabling empirical benign-shift false-alarm stress testing — **but** it is confounded by testbed/campaign composition, not pure organic drift.
- **Poisoning evaluation:** Controlled FL poisoning (label-flip, gradient scaling, backdoor) can be independently evaluated with fixed seeds and known malicious-client ground truth.
- **Distinguishability & attribution:** Benign client shift vs. malicious Byzantine/poisoning updates can be quantitatively evaluated in FL simulation (client-update divergence, robust aggregation rejection rates, false-positive quarantine rates on Period-B-shifted benign clients), provided **all claims explicitly distinguish empirical confounded benign shift from simulated poisoning**.
- **Verdict:** Upgraded from `HOLD` to **CONDITIONAL** (not `PASS`): executable only under a versioned threat-and-drift contract that prohibits claiming unconfounded organic benign drift or real-world poisoning provenance.
