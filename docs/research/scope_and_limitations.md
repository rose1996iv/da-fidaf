# Research Scope and Limitations

This page summarizes the exact boundaries of what current DA-FIDAF experimental evidence **does** and **does not** support.

---

## Mandatory Scientific Boundaries

| Boundary Area | Current Reality | Prohibited Claim |
| --- | --- | --- |
| **Dataset Scope** | Only **ToN-IoT** (`Processed_Network_dataset` windows W1 and W3) has been evaluated in full-scale experiments. | Do **not** claim multi-dataset generalization across CICIoT2023 or Edge-IIoTset. |
| **Window Independence** | **W1** (Shards 22–23, `n=89,269`) is a strict subset of **W3** (Shards 8–23, `n=191,738`). | Do **not** represent W1 and W3 as independent datasets or independent validation sets. |
| **Client Realism** | `K=10` partitions (`sim_gw_01`..`sim_gw_10`) are **simulated/emulated logical gateways**. | Do **not** claim physical IoT/IIoT gateway deployment or embedded hardware benchmarks. |
| **Privacy Guarantees** | All Phase 3B (`490`) and Phase 3B.2 (`60`) runs executed with `dp_enabled=False` and `secure_aggregation_active=False`. Prototype DP code uses non-cryptographic PRNG. | Do **not** claim formal deployment Differential Privacy or Secure Aggregation guarantees. |
| **Experiment E5** | `configs/experiments/e5_cross_dataset_hold.yaml` is enforced as `HOLD` and fails closed. | Do **not** report E5 as completed or partially executed. |
| **Model Architecture** | Implemented model is `LinearLogisticIDS`. Draft Diagram 2 depicts `1D-CNN / TCN`, which is **not yet implemented**. | Do **not** present current linear baseline results as `1D-CNN / TCN` performance. |
| **Attribution (`E3 v2`)** | `client_val_loss_delta` produced a severe FAR regression (`0.400–0.575`) and falsely flagged `4–8/15` benign-drifted clients. | Do **not** deploy `E3 v2` as default or claim benign-drift-safe attribution. |
| **Closed-Loop Quarantine (`E6 v2`)** | Quarantined `41%–45%` of client-rounds (`2–3` honest Non-IID clients/round) vs. `20%` attackers; W3 AUC gain (`+0.196`) is **not significant** under exact Student-$t$ ($df=4$). | Do **not** claim over-quarantine-free or statistically conclusive closed-loop superiority at `n=5`. |
| **Statistical Power** | `n=5` seeds (`[42, 101, 202, 303, 404]`); `9` comparisons flipped from significant (bootstrap) to non-significant (exact Student-$t$, $df=4$). | Do **not** rely on percentile bootstrap alone at `n=5` to assert significance. |
| **Proposal Alignment** | Original approved PhD research proposal has not been located in the workspace (`GAP-01`). | Do **not** claim verified compliance with the original approved PhD proposal. |

See also [Results Limitations](../results/limitations.md) and [Method Gap Register](../methodology/DA_FIDAF_METHOD_GAP_REGISTER.md).
