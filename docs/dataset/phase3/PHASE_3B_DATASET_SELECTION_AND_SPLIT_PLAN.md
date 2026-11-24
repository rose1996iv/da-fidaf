# DA-FIDAF — Phase 3B Dataset Selection & Split Plan

**Validation Mode:** Empirically measured split-level counts across all candidate ToN-IoT datasets and windows (strictly read-only; zero assumptions from aggregate totals).

---

## 1. Empirically Verified Split-Level Class Sufficiency

Minimum statistical floor required for Phase 3B: **`>= 500` benign AND `>= 500` attack flows in BOTH Validation and Test**.

### 1.1 Window W1 (`Network_dataset_22.csv` + `Network_dataset_23.csv`) — Full Exact Measurement
- **Total:** `1,339,021` rows (`268,463` benign = `20.05%`, `1,070,558` attack = `79.95%`), span `185,955s` (`51.65 hours`: `2019-04-27T11:06:41Z` .. `2019-04-29T14:45:56Z`).
- **Active-Flow Exclusion Verified:** Exactly `22` flows whose `[ts, ts + duration]` crossed a split boundary were detected and excluded under both `300s` and `900s` embargoes.

| Embargo | Split | Total Rows | Benign (`normal`) | Attack | Attack Families Present | Discarded (Embargo / Active) | Floor `>=500`? |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **`300s`** | Train | `937,302` | `229,948` | `707,354` | `xss` (488,585), `backdoor` (145,964), `ransomware` (72,805) | — | PASS |
| **`300s`** | Validation | `199,547` | **`10,927`** | **`188,620`** | `backdoor` (188,620) | `3,368` / `22` | **PASS** |
| **`300s`** | Test | `198,782` | **`27,425`** | **`171,357`** | `backdoor` (170,305), `mitm` (1,052 novel) | (included above) | **PASS** |
| **`900s`** | Train | `937,302` | `229,948` | `707,354` | `xss`, `backdoor`, `ransomware` | — | PASS |
| **`900s`** | Validation | `197,082` | **`10,757`** | **`186,325`** | `backdoor` (186,325) | `9,998` / `22` | **PASS** |
| **`900s`** | Test | `194,617` | **`27,257`** | **`167,360`** | `backdoor` (166,308), `mitm` (1,052 novel) | (included above) | **PASS** |

- **Verified UTC Boundaries (`300s`):** Train ends `2019-04-28T17:26:07Z`; Val `2019-04-28T17:31:07Z .. 2019-04-29T02:35:21Z`; Test starts `2019-04-29T02:40:21Z`.
- **Verified UTC Boundaries (`900s`):** Val starts `2019-04-28T17:41:07Z`; Test starts `2019-04-29T02:50:21Z`.

### 1.2 Window W3 (`Processed_Network_dataset` Shards `8..23`, Daily Chronological Split)
Derived from verified full-scan daily counts (`manifests/ton_iot_temporal_audit.json`, Period B only — excludes Period A 18-day capture gap):

| Split | Dates (UTC) | Benign (`normal`) | Attack | Attack Families Present | Floor `>=500`? |
| --- | --- | --- | --- | --- | --- |
| Train | `2019-04-24` .. `2019-04-26` | `262,642` | `13,907,611` | `scanning`, `dos`, `injection`, `ddos`, `password` | PASS |
| Validation | `2019-04-27` (with `300s`/`900s` gap) | **`48,578`** | **`2,658,325`** | `password`, `xss` | **PASS** |
| Test | `2019-04-28` .. `2019-04-29` (with `300s`/`900s` gap) | **`261,786`** | **`581,973`** | `ransomware`, `backdoor`, `mitm` (100% novel vs. Train) | **PASS** |

### 1.3 `train_test_network.csv` (Full `211,043` Rows, Non-Temporal Stratified 70/15/15)
- **Train:** `35,000` benign, `112,730` attack (`147,730` total).
- **Validation:** **`7,500`** benign, **`24,156`** attack (`31,656` total) — **PASS**.
- **Test:** **`7,500`** benign, **`24,157`** attack (`31,657` total) — **PASS**.
- **Mandatory Guard:** Full `211,043` rows MUST be loaded before stratified splitting; head-truncating (`--max-rows`) is prohibited due to strict class-grouped row ordering.

---

## 2. Duplicate Shard Exclusion & Confounding Controls

1. **Duplicate Ground-Truth Shard 16 Excluded:** `GroundTruth_Network_15.csv` and `GroundTruth_Network_16.csv` share identical SHA-256 (`d1d4cb491cb6edda3523f7424d24ea1afd4496a933e60b3ec357286f7f0f542f`). Shard 16 is permanently excluded. `Processed_Network_dataset` shards 15 and 16 are verified distinct chronological shards.
2. **Capture-Vantage Confounding Control:** Period A (`Apr 2–4`, `Network_dataset_1.csv`) is separated from Period B (`Apr 23–29`) by an 18-day capture gap (`Apr 5–22`) with `max_psi = 10.365`. Therefore, **W1 and W3 operate strictly within continuous Period B**, preventing 18-day capture-vantage confounding from being misreported as organic drift.
3. **Zero Identifier Leakage:** `src_ip`, `dst_ip`, `src_port`, `dst_port`, `ts`, `label`, `type` are excluded from model features (`TonIoTNetworkAdapter.excluded_columns`).

---

## 3. Final Dataset Assignment per Experiment

| Exp | Selected Dataset(s) | Justification | Status |
| --- | --- | --- | --- |
| **E1** | `train_test_network.csv` (full `211,043`, stratified) + `W1` (`Shards 22+23`, chronological `300s`) | Balanced 9-attack multi-class coverage (`train_test`) plus genuine chronological validation (`W1`) | Validated |
| **E2** | `W1` (`Shards 22+23`, `300s` & `900s` embargo) + `W3` (novel-attack emergence) | Verified `>10,700` benign & `>167,000` attack in Val/Test under both embargoes; zero Period A gap confounding | Validated |
| **E3** | `W1` (`Shards 22+23`, `300s` embargo) | Genuine chronological Train/Val/Test with sufficient benign support for clean attribution FAR measurement | Validated |
| **E4** | `train_test_network.csv` (full) + `W1` (`300s` embargo) | Evaluates Byzantine robustness under both balanced non-temporal and chronological imbalanced regimes | Validated |
| **E5** | ToN-IoT + CICIoT2023 + Edge-IIoTset | **BLOCKED / HOLD** (`E5OntologyBlockedError`) until cross-dataset ontology alignment is validated | **HOLD** |
| **E6** | `train_test_network.csv` (full) + `W1` (`300s` embargo) | Measures ablation & simulation-grade RDP overhead on real ToN-IoT workloads | Validated (`DP` conditional) |
