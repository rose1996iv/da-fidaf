# 14 — Benign Temporal Shift Analysis (DA-FIDAF Phase 1C)

- **Audit Timestamp (UTC):** `2026-11-24T03:46:13Z`
- **Data Sources:** All **23** `Processed_Network_dataset/Network_dataset_1..23.csv` files (`22,339,021` rows) cross-verified against deduplicated `SecuityEvents_GroundTruth_datasets/SecurityEvents_Network_datasets/` (`17` unique shards excluding duplicate shard `16`, `16,801,188` rows).
- **Leakage Rule:** All quantile bin edges, standardization means/stds, and MMD median bandwidths were fitted **exclusively on Period A**.

## 1. Verified Normal-Only Period Comparison (VERIFIED)

| Metric | Period A (`2019-04-02` – `2019-04-04`) | Period B (`2019-04-23` – `2019-04-29`) | Notes |
| :--- | ---: | ---: | :--- |
| **Verified Normal Rows (`label=0` & `type=normal`)** | `200,898` | `595,482` | `0` label/type mismatches; `21,542,641` attack rows excluded |
| **Unique Feature-Signature Normal Rows (Deduplicated)** | `27,441` | `272,165` | Period A: `86.3%` exact repetition; Period B: `54.3%` |
| **Unique 6-Tuples `(ts, src_ip, src_port, dst_ip, dst_port, proto)`** | `173,535` | `428,291` | `18,423` (A) & `30,244` (B) many-to-one keys |
| **6-Tuple Conflicts with Deduplicated Attack Ground Truth** | **`0`** (`0.00%`) | **`0`** (`0.00%`) | Clean label separation verified across `16,801,188` GT rows |
| **Missing Numeric Values (10 Candidate Features)** | `0` | `0` | `0.00%` missingness across all 10 numeric features |

## 2. Candidate Feature Inclusion & Exclusion Decisions

- **Included Numeric Features (10):** `duration`, `src_bytes`, `dst_bytes`, `missed_bytes`, `src_pkts`, `src_ip_bytes`, `dst_pkts`, `dst_ip_bytes`, `http_request_body_len`, `http_response_body_len`.
- **Audited Separately as Categorical Confounders (3):** `proto`, `service`, `conn_state`.
- **Excluded (Documented Reasons):**
  - `src_ip`, `dst_ip`, `src_port`, `dst_port`: host/session identifiers (severe IP memorization risk).
  - `ts`: raw capture timestamp (temporal leakage if fed as feature).
  - `label`, `type`: target variables.
  - Sparse protocol string/post-event fields (`dns_*`, `ssl_*`, `http_uri`, `http_user_agent`, `weird_*`).

## 3. Executive Finding on Benign Shift

- **Multivariate Shift (VERIFIED):** Unbiased RBF-kernel **`MMD^2 = 0.18897`** (`n_A = 800`, `n_B = 800`, 10 Period-A-standardized features, median bandwidth `sigma^2 = 2.4867`, seed `42`, `100` permutations -> **`p = 0.009901`**).
- **Univariate Shift (VERIFIED):** Substantial distribution shifts occur in `src_pkts` (`PSI = 1.5670`, `JSD = 0.2573` bits), `src_ip_bytes` (`PSI = 0.6907`, `JSD = 0.1203` bits), and `duration` (`PSI = 0.5025`, `JSD = 0.0878` bits), all remaining large after exact feature deduplication and statistically separated from zero under 1-hour time-block bootstrap 95% confidence intervals.
- **Critical Qualification:** As proven in Report 16, this shift is **heavily confounded** by a **295x jump in unique `src_ip`** (`79` -> `23,298`) and a **73x jump in `http` service share** (`0.14%` -> `10.25%`) across an 18-day capture gap. It must be reported as **observed temporal covariate shift under capture/campaign confounding**, not pure organic benign drift.
