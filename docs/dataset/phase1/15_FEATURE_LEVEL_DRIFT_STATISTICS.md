# 15 — Feature-Level Drift Statistics (DA-FIDAF Phase 1C)

- **Audit Timestamp (UTC):** `2026-11-24T03:46:13Z`
- **Methodology:** Period-A-only 10-quantile bin edges (`eps = 1e-6`), base-2 Jensen-Shannon divergence (JSD, bounded `[0, 1]`), 1D Wasserstein distance (`cap = 20,000`, seed `42`), Period-A-scaled Standardized Mean Difference (`SMD = (mean_B - mean_A) / std_A`), 1-hour UTC time-block bootstrap (`B = 200`, seed `42`) to account for temporal autocorrelation, and Holm-Bonferroni family-wise error correction across all 10 features.

## 1. Feature-Level Shift Table (Retained vs. Deduplicated — VERIFIED)

| Feature | PSI (Retained) | PSI (Dedup) | JSD bits (Retained) | JSD 95% Block-Boot CI | SMD (`std_A`) | SMD 95% Block-Boot CI | `p_holm` (SMD) | Practical Assessment |
| :--- | ---: | ---: | ---: | :--- | ---: | :--- | ---: | :--- |
| `src_pkts` | **`1.5670`** | **`1.6166`** | **`0.2573`** | `[0.1683, 0.3742]` | `+0.0438` | `[+0.0077, +0.1109]` | `0.0000` | **Large, robust shift** (distribution shape & body) |
| `src_ip_bytes` | **`0.6907`** | **`0.9682`** | **`0.1203`** | `[0.0763, 0.2266]` | `+0.0138` | `[-0.0053, +0.0386]` | `0.8800` | **Large shape shift** (mean stable; quantiles shifted) |
| `duration` | **`0.5025`** | **`0.4700`** | **`0.0878`** | `[0.0198, 0.2562]` | `-0.0252` | `[-0.0332, -0.0171]` | `0.0000` | **Large, robust shift** (shorter tails in Period B) |
| `dst_pkts` | `0.4612` | `0.1814` | `0.0799` | `[0.0214, 0.1681]` | `+0.0151` | `[-0.0084, +0.0517]` | `0.8800` | **Moderate, duplicate-sensitive** |
| `dst_ip_bytes` | `0.3627` | `0.1622` | `0.0624` | `[0.0162, 0.1251]` | `+0.0587` | `[+0.0169, +0.1139]` | `0.0000` | **Moderate, duplicate-sensitive** |
| `dst_bytes` | `0.1874` | `0.1990` | `0.0328` | `[0.0094, 0.0902]` | `+0.2207` | `[-0.0040, +0.7658]` | `0.6500` | **Moderate tail/variance shift** (heavy-tailed) |
| `src_bytes` | `0.0095` | `0.1323` | `0.0017` | `[0.0000, 0.0209]` | `-0.0033` | `[-0.0121, +0.0087]` | `0.8800` | **Small retained; masked by Period A repetition** |
| `missed_bytes` | `0.0000` | `0.0000` | `0.0000` | `[0.0000, 0.0000]` | `+0.0328` | `[-0.0166, +0.1355]` | `0.8800` | **Zero-inflated (>99% zero); bin collapse** |
| `http_request_body_len` | `0.0000` | `0.0000` | `0.0000` | `[0.0000, 0.0000]` | `-0.0073` | `[-0.0163, -0.0013]` | `0.0000` | **Zero-inflated; statistically sig. but negligible effect** |
| `http_response_body_len` | `0.0000` | `0.0000` | `0.0000` | `[0.0000, 0.0000]` | `-0.0049` | `[-0.0114, -0.0004]` | `0.0000` | **Zero-inflated; statistically sig. but negligible effect** |

*(Full quantile tables `min/p10/p50/p90/p99/max/zero_pct` and exact Wasserstein-1 values are recorded in `manifests/ton_iot_drift_analysis.json`.)*

## 2. Statistical Significance vs. Practical Effect Size

1. **Zero-Inflation Artifact:** `http_request_body_len` and `http_response_body_len` achieve `p_holm = 0.0` solely because large hourly sample sizes detect tiny mean differences (`|SMD| < 0.008`), while `PSI = 0.0` and `JSD = 0.0` confirm negligible practical shift in the bulk distribution.
2. **Shape Shift Without Mean Shift:** Conversely, `src_ip_bytes` has a non-significant mean difference (`SMD = +0.0138`, `p_holm = 0.88`), yet exhibits a **large distributional shift** (`PSI = 0.6907`, `dedup PSI = 0.9682`, `JSD = 0.1203` bits with 95% CI `[0.0763, 0.2266]` strictly above zero).
3. **Multivariate Confirmation:** RBF-kernel `MMD^2 = 0.18897` (`p = 0.009901`) confirms that joint feature distributions differ substantially across Period A and Period B even after Period-A-only standardization.
