# DA-FIDAF — Drift, Adversarial Simulation & Attribution Specification

## 1. Research Problem

In federated IoT intrusion detection, benign network evolution (concept drift — e.g., new device firmware, seasonal traffic shifts) and adversarial compromise (data poisoning or Byzantine model updates) both produce anomalous client gradients. Naively discarding all anomalous updates harms continual adaptation to benign drift, whereas blindly accepting them enables poisoning. Workstream C (`src/dafidaf/drift/`, `src/dafidaf/attacks/`, `src/dafidaf/attribution/`) implements the full experimental and algorithmic stack to separate these regimes.

---

## 2. Concept Drift & Continual Adaptation (`src/dafidaf/drift/core.py`)

### 2.1 Synthetic Drift Injection (`DriftSpec`, `apply_synthetic_drift`)
Operates strictly in memory on copied feature/label arrays:
- **Temporal Dynamics**: `abrupt` (step transition), `gradual` (linear ramp across window), `recurring` (periodic oscillation).
- **Statistical Regimes**: `covariate` ($P(X)$ shift), `prior` ($P(Y)$ class balance shift), `conditional` ($P(Y|X)$ decision-boundary shift).

### 2.2 Drift Detection
- **`FeatureDriftDetector`**: Computes per-feature Population Stability Index (PSI) and Jensen-Shannon Divergence (JSD) against a frozen reference histogram fitted on Train data.
- **`PageHinkleyDetector`**: Online sequential change-point detector monitoring streaming validation loss or error rate (`delta`, `threshold`, `alpha`).

### 2.3 Continual Adaptation (`ContinualAdapter`)
Supports three adaptation strategies when benign drift is confirmed:
- `fine_tune`: Direct adaptation on recent post-drift batches.
- `replay`: Mixes a bounded reservoir of historical Train samples with new post-drift samples to mitigate catastrophic forgetting.
- `regularized`: Applies an L2 anchor penalty toward pre-drift weights (EWC-style quadratic anchor).
Tracks pre-adaptation vs. post-adaptation accuracy on both source (old) and target (drifted) distributions to quantify **forgetting** and **adaptation recovery**.

---

## 3. Adversarial Attack Simulators (`src/dafidaf/attacks/simulators.py`)

All attacks execute strictly in memory on client copies; disk datasets are never touched.

### 3.1 Data Poisoning (`PoisoningConfig`, `apply_data_poisoning`)
- `label_flip`: Flips target-class labels on a configurable fraction of a compromised client's local Train samples.
- `data_poisoning`: Injects targeted feature perturbations paired with corrupted labels.
- `backdoor`: Stamps a deterministic trigger pattern onto selected feature indices and reassigns labels to the attacker's target class.

### 3.2 Byzantine Model Updates (`ByzantineConfig`, `apply_byzantine_update`)
- `sign_flip`: Negates and optionally scales the honest client update ($\tilde{\Delta} = -s \cdot \Delta$).
- `scaled_update`: Amplifies update magnitude ($\tilde{\Delta} = s \cdot \Delta$).
- `random_update`: Replaces the update with seeded Gaussian noise.
- `model_replacement`: Scales update to override the honest aggregate toward a malicious target vector.

---

## 4. Drift vs. Attack Attribution Engine (`src/dafidaf/attribution/engine.py`)

`DriftAttackAttributor` evaluates each client update using four complementary signals bundled in `AttributionEvidence`:
1. **`cosine_similarity`**: Cosine alignment between the client's update vector and the robust cohort reference (coordinate-wise median of round updates).
2. **`norm_ratio`**: Ratio of the client's update L2 norm to the cohort median L2 norm.
3. **`feature_psi`**: Mean Population Stability Index of the client's current feature batch relative to its historical baseline.
4. **`val_loss_delta`**: Change in server-side validation loss when applying the client's update (when a clean validation probe is available).

### Decision Taxonomy (`AttributionDecision`)

| Label | Trigger Conditions (Summary) | Recommended Server Action |
| --- | --- | --- |
| `malicious_byzantine_update` | Strongly negative cosine alignment (`<= cosine_byzantine_max`) and extreme norm inflation (`>= norm_ratio_byzantine`) | Reject / quarantine update |
| `malicious_model_update` | Extreme norm inflation (`>= norm_ratio_byzantine`) with non-benign cosine alignment (`< cosine_benign_min`) | Reject / quarantine update |
| `malicious_data_poisoning` | Negative cosine alignment (`<= -0.55`) with elevated norm (`>= 1.5`) or severe validation loss degradation (`>= val_loss_poison_delta`) without commensurate benign covariate PSI | Reject / down-weight update |
| `benign_distribution_drift` | Elevated feature PSI (`>= psi_drift_threshold`) with non-hostile cosine alignment (`>= cosine_benign_min`) and bounded norm | Accept & trigger `ContinualAdapter` |
| `normal_aligned_update` | Aligned cosine similarity, bounded norm, low PSI | Standard aggregation |
| `uncertain_insufficient_evidence` | Ambiguous boundary signals | Down-weight / log for multi-round confirmation |

### Calibration Note (Non-IID Heterogeneity)
Under strong Dirichlet label skew (e.g., $\alpha = 0.5$) near model convergence, honest minority-class clients can exhibit temporarily elevated `norm_ratio` relative to a small median norm while remaining positively aligned (`cosine_similarity >= cosine_benign_min`). The engine explicitly requires misaligned cosine direction before classifying an update as `malicious_model_update` or `malicious_data_poisoning`, achieving `0.0` False Attribution Rate on the validated synthetic E2E benchmark while maintaining high malicious recall.
