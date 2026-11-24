# Research Questions

!!! note "Status"
    Draft working research questions aligned to Experiments E1–E6. Verbatim cross-checking against the original approved PhD proposal is **Pending** (`GAP-01`).

| ID | Working Research Question | Linked Experiment | Current Empirical Status |
| --- | --- | --- | --- |
| **RQ1** | How severely do Non-IID client heterogeneity and chronological attack-campaign shift degrade federated IoT intrusion detection performance? | **E1** | Executed on ToN-IoT W1 & W3 (Non-DP); severe W1 score inversion diagnosed (`Train AUC 0.9339 -> Test AUC 0.3208`). |
| **RQ2** | How effectively can drift monitoring and replay-assisted continual adaptation detect and recover from gradual and abrupt drift under strict temporal embargoes? | **E2** | Executed with controlled synthetic drift on W1 & W3 (`300s`/`900s` embargo checks); round-8 evaluation limit noted (`GAP-07`). |
| **RQ3** | Can multi-evidence update analysis accurately separate legitimate benign drift from poisoning and Byzantine attacks without inflating false alarms on benign-drifted clients? | **E3** | Executed (`v1` & `v2`). `v2` (`client_val_loss_delta`) exposed a W3 `data_poisoning` recall gain (`0.00 -> 0.40`) offset by severe FAR regression (`0.400–0.575`) — **not solved yet**. |
| **RQ4** | How do Byzantine-robust aggregation rules compare under poisoning and sign-flipping adversaries in Non-IID IoT federation? | **E4** | Executed on ToN-IoT W1 & W3 (`FedAvg`, `Coordinate Median`, `Trimmed Mean`, `Multi-Krum`); adaptive attacks (ALIE/Min-Max) remain pending. |
| **RQ5** | Does a unified ontology enable zero-shot or federated cross-dataset generalization across ToN-IoT, CICIoT2023, and Edge-IIoTset? | **E5** | **NOT EXECUTED (`HOLD`)** — blocked pending validated semantic feature and label ontology. |
| **RQ6** | What is the causal contribution and computational/communication overhead of closed-loop attribution-guided quarantine relative to unguided aggregation? | **E6** | Genuine closed-loop ablation verified in Phase 3B.2; selected gains observed under `sign_flip`, tempered by honest-client over-quarantine (`41%–45%`) and desktop-only timing telemetry. |
