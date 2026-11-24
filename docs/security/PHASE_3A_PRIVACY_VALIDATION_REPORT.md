# DA-FIDAF Phase 3A — Independent Privacy & Security Validation Report

## 1. Privacy Mechanism & Accountant Verification

Inspected `src/dafidaf/privacy/mechanisms.py` and `src/dafidaf/federated/trainer.py` against real ToN-IoT pilot parameters ($T = 5$ rounds, $\delta = 10^{-5}$, $C = 1.0$, $\sigma \in \{0.5, 1.0, 2.0\}$):

| `dp_scope` | $\sigma$ | $T$ | $\delta$ | Exact RDP $\epsilon_{\text{upper}}$ | `formal_deployment_dp_claim` | `secure_aggregation_active` |
| --- | --- | --- | --- | --- | --- | --- |
| `local_per_client` | `0.5` | 5 | `1e-5` | `31.459660` | `False` | `False` |
| `local_per_client` | `1.0` | 5 | `1e-5` | `13.229830` | `False` | `False` |
| `local_per_client` | `2.0` | 5 | `1e-5` | `5.989915` | `False` | `False` |
| `central_aggregate` | `0.5` | 5 | `1e-5` | `31.459660` | `False` | `False` |
| `central_aggregate` | `1.0` | 5 | `1e-5` | `13.229830` | `False` | `False` |
| `central_aggregate` | `2.0` | 5 | `1e-5` | `5.989915` | `False` | `False` |

---

## 2. Mathematical & Threat-Model Audit

1. **Sensitivity Assumptions:**
   - `local_per_client`: Each honest client's update is clipped to L2 norm $C$ (`clip_update_l2`) and perturbed with $\mathcal{N}(0, (\sigma C)^2 I)$ *before* any Byzantine `update_hook` runs. Valid under add/remove-one-client adjacency.
   - `central_aggregate`: Server clips each finite update to $C$, aggregates, and adds central Gaussian noise scaled to $C \cdot \max_i w_i$ (for `fedavg`, exact worst-case client weight sensitivity) or $C$ (conservative upper bound for robust aggregators).
2. **Sampling & Composition Assumptions:**
   - Exact RDP Gaussian composition ($\varepsilon_{\text{RDP}}(\alpha) = T \cdot \alpha / (2\sigma^2)$) with analytical Mironov (2017) Proposition 3 conversion to $(\epsilon, \delta)$-DP.
   - **No subsampling amplification is claimed** (conservative $q = 1.0$ bound, valid for any participation rate $q \le 1$).
3. **Explicit Limitations (Must Be Disclosed in All Research Outputs):**
   - **Non-Cryptographic PRNG:** `add_gaussian_dp_noise` uses Python's deterministic `random.Random` (Mersenne Twister) for reproducible simulation. It is **NOT** a cryptographic CSPRNG and cannot be claimed as production-grade deployment DP (`formal_deployment_dp_claim: False`).
   - **Secure Aggregation Inactive:** `SecureAggregationInterface` is an interface and threat model only (`secure_aggregation_active: False`).
   - **Robust Aggregator Central-DP Sensitivity Caveat:** While `fedavg` has exact central sensitivity $C \cdot \max_i w_i$, non-linear robust aggregators (`median`, `trimmed_mean`, `krum`, `multi_krum`) use a conservative `max_w = 1.0` noise scale in `central_aggregate` mode rather than smooth-sensitivity bounds.

---

## 3. Privacy Experiment Authorization Status

- **Simulation DP-Utility Tradeoff Experiments (E6):** **CONDITIONAL PASS** — Mathematically defensible RDP accounting for *simulation-grade* utility-vs-$\epsilon$ research curves under explicit disclosure (`formal_deployment_dp_claim: False`, `secure_aggregation_active: False`).
- **Production / Deployment Privacy or Secure Aggregation Claims:** **HOLD / NOT AUTHORIZED**.
