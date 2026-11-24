# DA-FIDAF — Original Methodology Specification (Strictly Evidenced Only)

> [!CAUTION]
> **Missing Primary Source Notice:** The original approved research proposal document could not be located anywhere in `I:\Projects\da-fidaf` or `I:\IoT` (see [ORIGINAL_METHODOLOGY_SOURCE_INVENTORY.md](file:///I:/Projects/da-fidaf/docs/methodology/ORIGINAL_METHODOLOGY_SOURCE_INVENTORY.md)). This specification records **ONLY** elements verifiably attested in secondary on-disk documents (`README.md`, `06_DAFIDAF_EXPERIMENT_SUITABILITY.md`, and the research title) and explicitly marks every unverified methodological detail as **`UNVERIFIABLE — MISSING ORIGINAL PROPOSAL`**. Nothing is invented.

---

## Category A — Verifiably Attested Research Scope (Secondary Evidence Only; No Proposal Page/Equation Citations Available)

| Component | Attested Scope | Secondary Source Reference | Proposal Section / Page / Equation |
| --- | --- | --- | --- |
| **Research Title & Mission** | Robust, privacy-preserving, continually adaptive federated IDS for heterogeneous IoT under Non-IID data, concept drift, and adversarial threats | `README.md` L5–16; user prompt header | **MISSING (Original proposal not located)** |
| **Target Datasets** | ToN-IoT, CICIoT2023, Edge-IIoTset | `I:\IoT\_dataset_audit\06_DAFIDAF_EXPERIMENT_SUITABILITY.md` L3–10 | **MISSING (Original proposal not located)** |
| **Federated Learning Under Non-IID** | Collaborative FL across heterogeneous IoT clients (E1: IID vs. Non-IID) | `README.md` L12; `06_DAFIDAF_EXPERIMENT_SUITABILITY.md` L5 | **MISSING (Exact FL algorithm/backbone unverified)** |
| **Concept Drift & Continual Adaptation** | Gradual/abrupt drift detection and continual adaptation (E2) | `README.md` L13; `06_DAFIDAF_EXPERIMENT_SUITABILITY.md` L6 | **MISSING (Exact detector/adaptation equations unverified)** |
| **Benign Drift vs. Poisoning Attribution** | Distinguishing benign distribution drift from poisoning attacks (E3) | `06_DAFIDAF_EXPERIMENT_SUITABILITY.md` L7 | **MISSING (Exact attribution formulation unverified)** |
| **Byzantine Resilience & Robust Aggregation** | Adaptive/Byzantine clients & robust aggregation (E4) | `README.md` L14–15; `06_DAFIDAF_EXPERIMENT_SUITABILITY.md` L8 | **MISSING (Exact aggregator specification unverified)** |
| **Cross-Dataset Generalization** | Cross-dataset evaluation across CICIoT2023, ToN-IoT, Edge-IIoTset (E5) | `README.md` L11; `06_DAFIDAF_EXPERIMENT_SUITABILITY.md` L9 | **MISSING (Exact cross-dataset protocol unverified)** |
| **Privacy-Preserving Learning** | Privacy-preserving collaborative learning | `README.md` L16 | **MISSING (Exact DP / SecAgg / HE / FL privacy design unverified)** |
| **Ablation & Systems Overhead** | Component ablation & compute/comm overhead (E6) | `06_DAFIDAF_EXPERIMENT_SUITABILITY.md` L10 | **MISSING (Exact target hardware/metrics unverified)** |

---

## Unverifiable Specification Details (Require Original Proposal Upload)

The following core methodology details **CANNOT be verified** without the original approved proposal document:
1. Proposed IDS model architecture (e.g., MLP, 1D-CNN, LSTM, Transformer, Autoencoder, Graph Neural Network, or linear baseline).
2. Exact mathematical objective function, drift-attribution score equation, and continual learning mechanism.
3. Exact privacy mechanism specified in the proposal (Local DP, Central DP, Secure Aggregation, Homomorphic Encryption, or hybrid).
4. Exact proposed robust aggregation rule (custom DA-FIDAF adaptive aggregator vs. Krum/Trimmed-Mean/Median).
5. Exact evaluation dataset splits, multi-class vs. binary target formulation, and statistical acceptance thresholds.
