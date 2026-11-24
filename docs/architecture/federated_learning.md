# Federated Learning Architecture

- **Implementation Modules:** `src/dafidaf/federated/trainer.py`, `src/dafidaf/federated/client.py`, `src/dafidaf/federated/aggregation.py`
- **Engineering Spec:** [Federated Learning Specification](FEDERATED_LEARNING_SPECIFICATION.md)

---

## 1. Simulated Federation Topology

- **Clients:** `K = 10` simulated logical gateways (`sim_gw_01` through `sim_gw_10`) generated from chronological ToN-IoT training splits via `src/dafidaf/data/partitioning.py`.
- **Supported Heterogeneity Regimes (E1):**
  - `iid`: Uniform stratified partition.
  - `label_skew`: Dirichlet class skew ($\alpha \in \{0.5, 0.1\}$).
  - `quantity_skew`: Unequal client sample budgets.
  - `feature_skew` and `combined`: Joint heterogeneity partitions.
- **Optimization & Aggregation Baselines:** `FedAvg`, `FedProx` (proximal regularization), `Coordinate Median`, `Trimmed Mean`, and `Multi-Krum`.

---

## 2. Round Execution Flow (Verified Implementation)

1. Server broadcasts current global parameters $\theta^{(t)}$ to participating logical clients.
2. Each client performs local training (`local_epochs`) on its partition (with optional replay adaptation when drift triggers).
3. In adversarial arms (E3/E4/E6), designated simulated compromised clients inject label flips, feature-noise poisoning, backdoor triggers, or Byzantine sign flips (`src/dafidaf/attacks/simulators.py`).
4. Optional server-side `attribution_filter` (`Phase 3B.2` Workstream C) evaluates client updates and records `quarantined_attributed_clients` before aggregation.
5. Selected robust aggregator computes $\theta^{(t+1)}$ from the accepted client updates.
6. Validation and Test evaluation are kept strictly isolated (`TrainOnlyPreprocessor` fitted solely on training partitions).

---

## 3. Known Limitations

- Clients are **simulated/emulated logical partitions**, not physical IoT/IIoT gateway deployments.
- All Phase 3B and Phase 3B.2 experiments ran in **Non-DP mode** (`dp_enabled=False`, `secure_aggregation_active=False`).
- Communication and wall-clock telemetry reflect desktop Python 3.12 simulation, not embedded IoT hardware constraints (`GAP-08`).
