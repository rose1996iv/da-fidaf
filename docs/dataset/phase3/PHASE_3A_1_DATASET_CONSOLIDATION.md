# DA-FIDAF Phase 3A.1 — ToN-IoT Dataset Consolidation & Selection Strategy

**Scope:** Complete read-only inventory of all `23` `Processed_Network_dataset` shards (`22,339,021` rows), `train_test_network.csv` (`211,043` rows), and `GroundTruth_Network_1–18.csv` (`17` unique shards excluding duplicate shard 16). Source: `manifests/ton_iot_temporal_audit.json` + Phase 3A/3A.1 direct disk verification under `I:\IoT`.

---

## 1. Complete 23-Shard Inventory (`Processed_Network_dataset`)

| Shard | Rows | Unique `ts` | Out-of-Order | UTC Window (`min_ts` .. `max_ts`) | Benign (`normal`) | Dominant Attack Classes |
| --- | --- | --- | --- | --- | --- | --- |
| `Network_dataset_1.csv` | 1,000,000 | 103,119 | 0 | `2019-04-02T09:45:58Z` .. `2019-04-23T13:23:00Z` | 208,679 | `scanning` (791,321) — *contains 18-day gap Apr 5–22* |
| `Network_dataset_2.csv` | 1,000,000 | 1,621 | 0 | `2019-04-23T13:23:00Z` .. `2019-04-23T13:50:14Z` | 5,717 | `scanning` (994,283) |
| `Network_dataset_3.csv` | 1,000,000 | 623 | 0 | `2019-04-23T13:50:14Z` .. `2019-04-23T14:00:36Z` | 2,820 | `scanning` (997,180) |
| `Network_dataset_4.csv` | 1,000,000 | 1,531 | 0 | `2019-04-23T14:00:36Z` .. `2019-04-24T03:20:51Z` | 6,256 | `scanning` (993,744) |
| `Network_dataset_5.csv` | 1,000,000 | 646 | 0 | `2019-04-24T03:20:51Z` .. `2019-04-24T03:31:36Z` | 3,657 | `scanning` (996,343) |
| `Network_dataset_6.csv` | 1,000,000 | 2,665 | 0 | `2019-04-24T03:31:36Z` .. `2019-04-24T04:16:00Z` | 13,473 | `scanning` (986,527) |
| `Network_dataset_7.csv` | 1,000,000 | 1,574 | 0 | `2019-04-24T04:16:00Z` .. `2019-04-24T06:12:48Z` | 7,499 | `scanning` (992,501) |
| `Network_dataset_8.csv` | 1,000,000 | 7,833 | 0 | `2019-04-24T06:12:48Z` .. `2019-04-24T20:13:13Z` | 21,306 | `scanning` (388,262), `dos` (590,432) |
| `Network_dataset_9.csv` | 1,000,000 | 8,303 | 0 | `2019-04-24T20:13:13Z` .. `2019-04-24T22:31:44Z` | 24,739 | `dos` (975,261) |
| `Network_dataset_10.csv` | 1,000,000 | 8,321 | 0 | `2019-04-24T22:31:44Z` .. `2019-04-25T00:50:26Z` | 30,002 | `dos` (969,998) |
| `Network_dataset_11.csv` | 1,000,000 | 11,242 | 0 | `2019-04-25T00:50:26Z` .. `2019-04-25T07:05:29Z` | 35,168 | `dos` (839,637), `injection` (125,195) |
| `Network_dataset_12.csv` | 1,000,000 | 18,157 | 2 | `2019-04-25T07:05:29Z` .. `2019-04-25T17:01:59Z` | 32,806 | `injection` (327,464), `ddos` (639,730) |
| `Network_dataset_13.csv` | 1,000,000 | 10,565 | 5 | `2019-04-25T17:01:59Z` .. `2019-04-25T19:59:08Z` | 917 | `ddos` (999,083) |
| `Network_dataset_14.csv` | 1,000,000 | 7,574 | 3 | `2019-04-25T19:59:08Z` .. `2019-04-25T22:06:21Z` | 583 | `ddos` (999,417) |
| `Network_dataset_15.csv` | 1,000,000 | 7,755 | 0 | `2019-04-25T22:06:21Z` .. `2019-04-26T00:16:43Z` | 1,060 | `ddos` (998,940) |
| `Network_dataset_16.csv` | 1,000,000 | 7,969 | 2 | `2019-04-26T00:16:43Z` .. `2019-04-26T02:30:34Z` | 1,891 | `ddos` (998,109) |
| `Network_dataset_17.csv` | 1,000,000 | 10,059 | 1 | `2019-04-26T02:30:34Z` .. `2019-04-26T05:27:11Z` | 33,711 | `ddos` (966,289) |
| `Network_dataset_18.csv` | 1,000,000 | 21,908 | 0 | `2019-04-26T05:27:11Z` .. `2019-04-26T17:54:05Z` | 49,436 | `ddos` (563,440), `password` (387,124) |
| `Network_dataset_19.csv` | 1,000,000 | 27,058 | 0 | `2019-04-26T17:54:05Z` .. `2019-04-27T01:25:17Z` | 12,708 | `password` (987,292) |
| `Network_dataset_20.csv` | 1,000,000 | 16,376 | 0 | `2019-04-27T01:25:17Z` .. `2019-04-27T07:57:43Z` | 21,082 | `password` (344,152), `xss` (634,766) |
| `Network_dataset_21.csv` | 1,000,000 | 11,308 | 1 | `2019-04-27T07:57:43Z` .. `2019-04-27T11:06:41Z` | 14,407 | `xss` (985,593) |
| `Network_dataset_22.csv` | 1,000,000 | 58,458 | 3 | `2019-04-27T11:06:41Z` .. `2019-04-28T21:05:32Z` | 234,988 | `xss` (488,585), `ransomware` (72,805), `backdoor` (203,622) |
| `Network_dataset_23.csv` | 339,021 | 47,990 | 4 | `2019-04-28T21:05:32Z` .. `2019-04-29T14:45:56Z` | 33,475 | `backdoor` (304,494), `mitm` (1,052) |

- **Total:** `22,339,021` rows (`0` invalid `ts`, `0` missing `ts`, `21` out-of-order transitions handled by stable sort).
- **Duplicate Ground-Truth Shard 15/16 Exclusion:** `GroundTruth_Network_15.csv` and `GroundTruth_Network_16.csv` are bit-for-bit identical (`SHA-256: d1d4cb491cb6edda3523f7424d24ea1afd4496a933e60b3ec357286f7f0f542f`, `1,000,000` duplicated rows); shard 16 is permanently excluded. Note: `Processed_Network_dataset` shards 15 and 16 are **distinct** chronological shards (`Apr 25 22:06..Apr 26 00:16` vs `Apr 26 00:16..02:30`).

---

## 2. Valid Multi-Shard Chronological Windows & Embargo Feasibility

Single-shard prefixes fail under 900s embargo (verified in Phase 3A.1: `Network_dataset_23.csv` 15k prefix `2,154s` -> `embargo=900s` raises empty Val/Test error; `embargo=300s` leaves only `3` benign Test flows).

| Candidate Window | Shards | Span | Total Rows | Benign (`normal`) | Attack | 300s & 900s Embargo Feasibility |
| --- | --- | --- | --- | --- | --- | --- |
| **Window W1 (Multi-Attack Balanced Tail)** | `22 + 23` | `51.6 hours` (`Apr 27 11:06Z` .. `Apr 29 14:45Z`) | `1,339,021` | `268,463` (`20.0%`) | `1,070,558` (`xss`, `ransomware`, `backdoor`, `mitm`) | **PASS** — Both 300s (`<0.4%` span) and 900s (`<1.0%` span) preserve >35,000 benign Val/Test rows |
| **Window W2 (Mid-Campaign Multi-Attack)** | `11 + 12 + 18` | Multi-day (`Apr 25–26`) | `3,000,000` | `117,410` (`3.9%`) | `2,882,590` (`dos`, `injection`, `ddos`, `password`) | **CONDITIONAL** — High attack dominance (`96.1%`); requires stratified/weighted calibration |
| **Window W3 (Full Period B Campaign)** | `8..23` (bounded temporal stride) | `5.35 days` (`Apr 24 06:12Z` .. `Apr 29 14:45Z`) | `15,339,021` | `547,427` | `14,791,594` (all 9 attack families) | **PASS** for E2 novel-attack emergence (Train Apr 24–26, Val Apr 27, Test Apr 28–29) |

---

## 3. Capture-Vantage Confounding & `train_test_network.csv` Suitability

1. **Period A (Apr 2–4) vs. Period B (Apr 23–29) Confounding:** An 18-day capture gap (`Apr 5–22`) separates normal-only Period A from attack-campaign Period B. Phase 1C and Phase 3A confirmed massive benign feature shift (`max_psi = 10.365`) across this gap caused by lab/capture changes, NOT purely organic environmental drift. Period A→B must NEVER be claimed as unconfounded organic drift.
2. **`train_test_network.csv` (`211,043` rows, `no ts`):**
   - **Suitability:** **SUITABLE for non-temporal E1, E4, and E6** (`50,000` normal + `161,043` attacks across all 9 attack classes) **ONLY when the full `211,043` rows are loaded** (or sampled via stratified full-file scan).
   - **Prohibited Usage:** Head-truncated `--max-rows` loading is strictly prohibited (first `5,000` rows are `100% backdoor`), and chronological E2 splitting is prohibited (`ts` absent).

---

## 4. Documented Dataset-Selection Strategy for E1–E6

| Exp | Primary Dataset Selection | Split Policy | Status |
| --- | --- | --- | --- |
| **E1** | `train_test_network.csv` (full `211,043` rows, stratified) + `W1` (`Shards 22+23`, chronological) | 70/15/15 stratified (non-temporal) + 70/15/15 chronological (`300s` embargo) | Ready for Phase 3B |
| **E2** | `Processed_Network_dataset` Window `W1` (`Shards 22+23`, `51.6h`) + `W3` (novel-attack emergence) | Chronological 70/15/15 with `300s` and `900s` embargo sensitivity + active-flow exclusion | Ready for Phase 3B |
| **E3** | Window `W1` (`Shards 22+23`) + explicit synthetic covariate drift & synthetic poisoning | Chronological 70/15/15 (`300s` embargo); synthetic interventions explicitly labeled | Ready for Phase 3B |
| **E4** | `train_test_network.csv` (full `211,043` rows) + Window `W1` (`Shards 22+23`) | Stratified & chronological (`300s` embargo); Byzantine attacks strictly in-memory | Ready for Phase 3B |
| **E5** | ToN-IoT + CICIoT2023 + Edge-IIoTset | **BLOCKED / HOLD** (`E5OntologyBlockedError`) | **HOLD** |
| **E6** | `train_test_network.csv` (full `211,043` rows) + Window `W1` (`Shards 22+23`) | Ablation & simulation-grade RDP DP-utility sweeps (`formal_deployment_dp_claim: False`) | Ready for Phase 3B |
