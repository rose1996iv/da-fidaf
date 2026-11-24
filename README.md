# DA-FIDAF — Drift-Aware Federated Intrusion Detection and Attribution Framework

- **Research Status:** `Active PhD Research — Experimental Validation and Development`
- **Repository Visibility Target:** Private
- **Documentation Platform:** MkDocs Material (`mkdocs.yml`)

> **A robust, privacy-preserving, and continually adaptive federated intrusion detection framework for heterogeneous IoT/IIoT networks under Non-IID data, concept drift, and adversarial threats.**

---

## Mandatory Status & Scientific Disclosures

| Area | Verified Current Status |
| --- | --- |
| **Phase 3B.2 Remediation** | **Conditional Pass** — engineering, integrity, statistical, and closed-loop ablation goals succeeded; experimental `E3 v2` (`client_val_loss_delta`) produced a net FAR regression and is **not approved as default**. |
| **Original Methodology Alignment** | **Insufficient Source Evidence** — the original approved PhD research proposal has not yet been located in the workspace (`GAP-01`). |
| **Local IDS Architecture** | Current codebase implements baseline `LinearLogisticIDS`. The `1D-CNN / TCN` model depicted in Draft Architecture Diagram 2 is **not yet implemented or validated**. |
| **Closed-Loop Attribution (`E6 v2`)** | Verified code-isolated quarantine improved selected `sign_flip` metrics, but **benign-client over-quarantine (`41%–45%` client-rounds)** remains an open limitation. |
| **Experiment E5 (Cross-Dataset)** | **Not Executed (`HOLD`)** — blocked pending validated semantic feature and label ontology. |
| **Privacy Guarantees** | Phase 3B (`490` runs) and Phase 3B.2 (`60` runs) executed **Non-DP baselines only** (`dp_enabled=False`, `secure_aggregation_active=False`). Do **not** claim formal deployment DP or Secure Aggregation guarantees. |
| **Dataset & Client Boundaries** | ToN-IoT windows **W1** and **W3 overlap ($\text{W1} \subset \text{W3}$)** and are not independent datasets. `K=10` partitions are **simulated logical gateways**, not physical edge deployments. |

---

## 1. Research Overview & Abstract

**DA-FIDAF** investigates how heterogeneous IoT and IIoT gateways can collaboratively train and adapt intrusion detection systems without centralizing raw network traffic, while addressing statistical Non-IID skew, temporal concept drift, and adversarial poisoning or Byzantine attacks. Rather than treating every outlying client update as malicious, DA-FIDAF explores multi-evidence drift–attack attribution to separate legitimate benign drift from malicious manipulation and guide risk-aware robust aggregation and continual adaptation.

Full framing: [docs/research/research_overview.md](docs/research/research_overview.md)

---

## 2. Problem Statement

Federated IDS in heterogeneous IoT/IIoT networks faces four coupled failure modes: (1) decentralized, privacy-sensitive traffic silos; (2) severe Non-IID label, feature, and quantity skew across gateways; (3) temporal covariate and attack-campaign shifts that can catastrophically invert linear decision boundaries; and (4) operational ambiguity between honest benign-drifted clients and adversarial poisoning or Byzantine clients.

Details: [docs/research/problem_statement.md](docs/research/problem_statement.md)

---

## 3. Research Objectives

1. **RO1:** Build a leak-free, chronologically disciplined, portable federated IDS pipeline for IoT traffic.
2. **RO2:** Quantify and mitigate Non-IID degradation across heterogeneous simulated IoT gateways (E1).
3. **RO3:** Evaluate drift monitoring and continual replay-assisted adaptation under strict temporal embargoes (E2).
4. **RO4:** Investigate multi-evidence drift–attack attribution separating benign drift from poisoning/Byzantine threats without excessive false attribution (E3).
5. **RO5:** Couple attribution decisions with risk-aware robust aggregation (`Accept` / `Downweight` / `Hold` / `Quarantine`) while controlling honest-client over-quarantine (E4, E6).
6. **RO6 *(Planned)*:** Evaluate formal privacy mechanisms (DP / Secure Aggregation) and cross-dataset generalization (E5, currently `HOLD`) once proposal alignment is confirmed.

Details: [docs/research/research_objectives.md](docs/research/research_objectives.md) · [docs/research/research_questions.md](docs/research/research_questions.md)

---

## 4. Research Scope

- **Evaluated to Date:** Real ToN-IoT network shards (`W1`: Shards `22+23`, `n=89,269`; `W3`: Shards `8–23` excl. duplicate Shard `16`, `n=191,738`; $\text{W1} \subset \text{W3}$), `K=10` simulated logical gateways, `n=5` seeds `[42, 101, 202, 303, 404]`, Non-DP baseline.
- **Audited Only (Not Yet Executed in E1–E6):** CICIoT2023 and Edge-IIoTset.
- **Out of Current Verified Scope:** Physical gateway hardware deployment, formal DP/SecAgg deployment guarantees, `1D-CNN / TCN` training, adaptive Byzantine adversaries (ALIE/Min-Max), and E5 cross-dataset transfer.

Details: [docs/research/scope_and_limitations.md](docs/research/scope_and_limitations.md)

---

## 5. Draft Framework Architecture

The two latest researcher draft diagrams outline an end-to-end pipeline spanning heterogeneous IoT/IIoT clients, local data preparation and IDS training (`1D-CNN / TCN` depicted in Draft Diagram 2), local drift monitoring, multi-evidence update analysis (update geometry, distribution-shift evidence, model behavior, historical client behavior), Drift–Attack Attribution (`Benign Drift` / `Uncertain` / `Malicious`), risk-aware aggregation (`Accept` / `Downweight` / `Hold` / `Quarantine`), continual drift adaptation feedback, and global IDS distribution.

> **Important:** These diagrams are treated strictly as **latest draft-level architecture evidence**, not proof of supervisor approval or verified implementation. Original diagram image files are not yet stored in `docs/architecture/figures/` (see [docs/architecture/figures/FIGURE_CATALOG.md](docs/architecture/figures/FIGURE_CATALOG.md)).

Details: [docs/architecture/system_architecture.md](docs/architecture/system_architecture.md)

---

## 6. Core Research Components (`src/dafidaf/`)

| Module | Role | Implementation Notes |
| --- | --- | --- |
| `src/dafidaf/data/` | Adapters, schemas, train-only preprocessing, chronological splits, logical gateway partitioning | Verified leak-free (`57/57` tests) |
| `src/dafidaf/models/` | `ModelInterface` & `LinearLogisticIDS` | Baseline linear IDS (`1D-CNN / TCN` pending) |
| `src/dafidaf/drift/` | PSI / KS / Page–Hinkley drift detectors and replay buffer | Baseline continual adaptation |
| `src/dafidaf/attribution/` | `DriftAttackAttributor` multi-evidence engine | v1 baseline; v2 `val_loss_delta` experimental only (high FAR) |
| `src/dafidaf/federated/` | `FederatedTrainer`, clients, `FedAvg`, `FedProx`, `Median`, `Trimmed Mean`, `Multi-Krum` | Closed-loop `attribution_filter` binary quarantine verified |
| `src/dafidaf/attacks/` | Simulated `label_flip`, `data_poisoning`, `backdoor`, `sign_flip` | Non-adaptive attacks only |
| `src/dafidaf/privacy/` | Prototype DP accounting/noise helpers | **Non-DP only in Phase 3B/3B.2**; SecAgg unimplemented |
| `src/dafidaf/orchestration/` | Config-driven runner, LF-canonical SHA-256 provenance, E5 `HOLD` gate | `60/60` Phase 3B.2 raw-byte SHA-256 verified |
| `src/dafidaf/visualization/` | IEEE Transactions-compatible Matplotlib plotting helpers | External-root containment enforced |

---

## 7. Repository Structure

```text
da-fidaf/
├── .github/                  # Least-privilege CI workflows, issue & PR templates
├── configs/                  # Path templates & E1–E6 experiment YAMLs
├── docs/                     # MkDocs Material research site & Phase 1–3B.2 reports
│   ├── research/             # Framing, objectives, questions, scope & limitations
│   ├── architecture/         # System architecture, component docs, FIG-01–FIG-10 catalog
│   ├── methodology/          # Original methodology alignment audit (8 reports)
│   ├── datasets/             # Inventory, provenance, preprocessing, data governance
│   ├── dataset/              # Historical Phase 1 (24 reports) & Phase 3 split audits
│   ├── experiments/          # Protocol, execution guide, Phase 3A/3B/3B.2 reports
│   ├── results/              # Results overview, limitations, verified Phase 3B.2 PNGs
│   ├── development/          # Installation, configuration, execution, testing guides
│   ├── repository/           # Baseline preservation, security, readiness, GitHub config
│   ├── security/             # Phase 2–3B security & Non-DP scope reports
│   └── references/           # Verified BibTeX bibliography & citation policy
├── manifests/                # Verified lightweight dataset metadata JSONs (no raw data)
├── src/dafidaf/              # Portable Python 3.12 research framework
├── tests/                    # 57 unit & synthetic integration tests
├── mkdocs.yml                # MkDocs Material configuration
├── requirements-docs.txt     # Isolated documentation dependencies
├── pyproject.toml / uv.lock  # Core Python 3.12 dependencies
└── CITATION.cff              # Research software citation metadata
```

Full inventory: [docs/repository/REPOSITORY_INVENTORY.md](docs/repository/REPOSITORY_INVENTORY.md)

---

## 8. Dataset Sources and Provenance

Raw datasets, archives, PCAPs, and experiment outputs **remain permanently outside Git** on read-only external storage (`DAFIDAF_DATA_ROOT` / `DAFIDAF_RUNS_ROOT`).

- **ToN-IoT** (Moustafa, 2021): Primary evaluated dataset (Shards `15`/`16` duplicate excluded; W1 $\subset$ W3 overlapping windows).
- **CICIoT2023** (Neto et al., 2023) & **Edge-IIoTset** (Ferrag et al., 2022): Audited in Phase 1; not yet executed in E1–E6.

Details: [docs/datasets/dataset_inventory.md](docs/datasets/dataset_inventory.md) · [docs/datasets/data_governance.md](docs/datasets/data_governance.md)

---

## 9. Installation and Environment Setup

Requires **Python `3.12.*`** (`.python-version`: `3.12.10`) and **`uv`**:

```powershell
uv sync
```

Build or preview documentation locally in an isolated docs environment (without altering core dependencies):

```powershell
python -m venv .venv-docs
.venv-docs\Scripts\python.exe -m pip install -r requirements-docs.txt
.venv-docs\Scripts\mkdocs.exe serve
```

Details: [docs/development/installation.md](docs/development/installation.md)

---

## 10. Configuration Instructions

Copy `.env.example` to `.env` (Git-ignored) and set external read-only dataset and run roots:

```dotenv
DAFIDAF_DATA_ROOT=<EXTERNAL_READONLY_DATASETS_DIR>
DAFIDAF_RUNS_ROOT=<EXTERNAL_EXPERIMENT_RUNS_DIR>
```

Verify configuration read-only:

```powershell
.venv\Scripts\python.exe -m dafidaf doctor
```

Details: [docs/development/configuration.md](docs/development/configuration.md)

---

## 11. Experiment Reproduction & Testing

Run lint and all `57` automated unit/integration tests (synthetic fixtures only; zero raw dataset required):

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"
.venv\Scripts\ruff.exe check src tests --no-cache
.venv\Scripts\python.exe -m pytest -v -p no:cacheprovider tests
```

Run a deterministic synthetic smoke test (`SYNTHETIC_TOY_GENERATOR`):

```powershell
.venv\Scripts\python.exe -m dafidaf.orchestration.cli run-e2e-synthetic --seed 42 --save
```

Full reproduction guide: [docs/development/running_experiments.md](docs/development/running_experiments.md) · [docs/experiments/EXPERIMENT_EXECUTION_GUIDE.md](docs/experiments/EXPERIMENT_EXECUTION_GUIDE.md)

---

## 12. Current Experimental Results (Phase 3B & Phase 3B.2)

- **E1 (W1 Score Inversion):** Saved W1 `seed=42` checkpoint confirmed `Train ROC-AUC = 0.933945 -> Val = 0.333538 -> Test = 0.320810` because `8/8` active flow-volume features inverted polarity between `xss`-heavy Train and `backdoor`-heavy Test (vs. W3 `0.8744 -> 0.8321`).
- **E3 (Attribution v2 Negative Net Result):** Leak-free `client_val_loss_delta` broke W3 `data_poisoning` blind spot (`Recall: 0.000 -> 0.400`), **but** regressed FAR to `0.400–0.575`, falsely flagged `4–8/15` benign-drifted clients, and degraded recall on `label_flip`, `backdoor`, and `sign_flip`. **Not approved as default.**
- **E6 (Genuine Closed-Loop Ablation):** Code-isolated quarantine under `sign_flip + FedAvg` yielded W1 `Macro-F1: 0.6256 -> 0.7493` (`+0.1237`) and W3 `ROC-AUC: 0.6294 -> 0.8257` (`+0.1963`), while disclosing honest Non-IID over-quarantine (`41%–45%` client-rounds vs. `20%` attackers).
- **Statistical Reanalysis (`n=5`):** Exact paired Student-$t$ ($df=4$) flipped **9 comparisons** from significant (bootstrap) to **non-significant**, including `E6_W3_closedloop_vs_noattr_auc` and `E4_W3_mkrum_vs_fedavg_signflip_auc`.
- **Integrity (`canonical_sha256_manifest.json`):** `578` files hashed (`470/470` original Phase 3B LF-verified; `60/60` Phase 3B.2 raw-byte LF-verified `100%`).

Full results & figures: [docs/results/results_overview.md](docs/results/results_overview.md) · [docs/results/figures/FIGURE_CATALOG.md](docs/results/figures/FIGURE_CATALOG.md)

---

## 13. Limitations and Known Issues

See [docs/results/limitations.md](docs/results/limitations.md) and [docs/methodology/DA_FIDAF_METHOD_GAP_REGISTER.md](docs/methodology/DA_FIDAF_METHOD_GAP_REGISTER.md) for the complete gap register (`GAP-01` through `GAP-08`).

---

## 14. Methodology Alignment Status

**Verdict:** **`INSUFFICIENT SOURCE EVIDENCE`** — No standalone original approved PhD research proposal document currently exists in the repository or adjacent workspaces (`GAP-01`). See [docs/methodology/DA_FIDAF_METHODOLOGY_ALIGNMENT_VERDICT.md](docs/methodology/DA_FIDAF_METHODOLOGY_ALIGNMENT_VERDICT.md).

---

## 15. Privacy and Security Disclosures

- **Privacy:** Current experimental results are **Non-DP only**; no formal DP or Secure Aggregation claims are made.
- **Security Hygiene:** Gitleaks v8 (`0` leaks), `dafidaf.repo_guard` (`10 MiB` cap, blocked raw-data/secret extensions), and read-only pre-commit/pre-push hooks are configured. See [SECURITY.md](SECURITY.md) and [docs/repository/REPOSITORY_SECURITY_AUDIT.md](docs/repository/REPOSITORY_SECURITY_AUDIT.md).

---

## 16. Citation, License, and Contribution

- **Citation:** See [CITATION.cff](CITATION.cff) and [docs/references/citation_policy.md](docs/references/citation_policy.md) (no invented DOI or ORCID).
- **License Status:** **No license granted yet** — licensing and institutional IP ownership are pending explicit researcher and institutional confirmation.
- **Contributing & Conduct:** See [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Contact details are intentionally omitted pending private repository ownership confirmation.
