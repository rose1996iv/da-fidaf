# DA-FIDAF Phase 3B — Non-DP Scope, Exclusions & Limitations Statement

## 1. Authorized Phase 3B Privacy & Scope Boundaries

All Phase 3B experiments (E1, E2, E3, E4, and E6) executed strictly under the **user-authorized Non-DP Baseline Scope**:

| Control / Feature | Phase 3B Execution State | Formal Claim Status |
| --- | --- | --- |
| **Differential Privacy (`DPConfig.enabled`)** | **`False`** across all Phase 3B runs | **NO formal DP guarantee is claimed** from Phase 3B results |
| **Secure Aggregation (`SecureAggregationInterface`)** | **`secure_aggregation_active: False`** | **NOT IMPLEMENTED** — no cryptographic masking executed |
| **E5 Cross-Dataset Generalization** | **EXCLUDED / NOT AUTHORIZED** | Remains **`HOLD`** (`E5OntologyBlockedError`) pending ontology alignment |
| **External Datasets (`I:\IoT`)** | Strictly read-only | Zero extraction, modification, or archive repair performed |

---

## 2. Methodological & Scientific Limitations Disclosed

1. **Overlapping Temporal Windows (W1 $\subset$ W3):**
   - W1 (`Shards 22+23`, `Apr 27–29`, `stride=15`) is a subset of W3 (`Shards 8–23`, `Apr 24–29`, `stride=80`).
   - They are **NOT independent datasets** and were never pooled for statistical inference. All tables and figures keep W1 and W3 strictly separated.
2. **Deterministic Uniform Temporal Striding:**
   - To make pure-Python `LinearLogisticIDS` multi-seed sweeps computationally tractable across `15.3M` raw rows, W1 used uniform temporal `stride=15` (`89,269` rows) and W3 used uniform temporal `stride=80` (`191,738` rows), preserving exact UTC chronology, `300s`/`900s` embargoes, and `>= 500`/class floors in every Validation and Test split.
3. **Linear Model Capacity Under Campaign-Disjoint Attacks:**
   - ToN-IoT executes each attack family in a disjoint 1–2 day campaign window (`xss` in W1 Train vs. `backdoor`/`mitm` in W1 Test; `dos`/`ddos`/`scanning` in W3 Train vs. `ransomware`/`backdoor` in W3 Test). A linear logistic model (`LinearLogisticIDS`, 10 numeric features) exhibits domain-shift sensitivity (inverted linear slope on W1 `ROC-AUC ≈ 0.32`, calibration shift on W3 `FPR ≈ 0.99`), motivating non-linear neural backbones in future work.
4. **Simulated Logical Gateways (`sim_gw_01..10`):**
   - Because ToN-IoT network CSVs lack true IoT gateway device identities, all `K = 10` clients are explicitly marked `simulated_logical_gateway` (`sim_gw_*`).
5. **Synthetic Drift & Poisoning Interventions:**
   - All E2 synthetic schedules (`abrupt`, `gradual`, `recurring`), E3 poisoning (`label_flip`, `data_poisoning`, `backdoor`), and E4 Byzantine updates (`sign_flip`, `scaled_update`, `random_update`, `model_replacement`, `nan_poison`) were injected strictly in memory and explicitly labeled as synthetic interventions.
6. **Limited Seed Replication (`n = 5`):**
   - Five deterministic seeds (`[42, 101, 202, 303, 404]`) enable paired within-seed comparisons and bootstrap CIs, but `n = 5` has modest statistical power; findings with wide CIs should not be overstated.
