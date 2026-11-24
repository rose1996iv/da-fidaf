# Problem Statement

Heterogeneous IoT and IIoT networks exhibit four tightly coupled operational challenges that undermine conventional centralized and federated intrusion detection systems (IDS):

1. **Data Decentralization and Privacy Constraints:** Raw traffic flows and packet captures across organizational or gateway silos cannot be freely pooled into a single centralized repository without creating privacy, bandwidth, and regulatory risks.
2. **Severe Non-IID Client Distributions:** Distinct IoT gateways observe skewed class ratios, distinct device profiles, and unequal sample volumes, degrading standard Federated Averaging (`FedAvg`) convergence and calibration.
3. **Confounded Concept Drift and Novel Attack Campaigns:** Network traffic evolves over time. As demonstrated empirically on ToN-IoT Window W1 (`Shards 22–23`), attack families appearing in chronological test windows (`backdoor`, `mitm`) can exhibit inverted feature polarity relative to earlier training campaigns (`xss`), causing linear models trained earlier to suffer catastrophic score inversion (`Train AUC = 0.9339 -> Test AUC = 0.3208`).
4. **Ambiguity Between Benign Drift and Adversarial Poisoning:** In federated IDS, both an honest gateway experiencing legitimate concept drift and a compromised gateway executing label flipping, backdoor injection, or Byzantine sign flipping produce anomalous updates. Naive Byzantine filters risk quarantining honest drifting gateways, while naive acceptance exposes the global IDS to model corruption.

---

## Authoritative Proposal Note

> **Status:** Draft research framing derived from repository documentation and Phase 1–3B.2 empirical findings. Exact alignment against the verbatim problem statement in the original approved PhD research proposal remains **Pending** (`INSUFFICIENT SOURCE EVIDENCE`; see [Source Inventory](../methodology/ORIGINAL_METHODOLOGY_SOURCE_INVENTORY.md)).
