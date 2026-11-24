# DA-FIDAF — Option A Two-Commit Plan (Prepared Only — NOT Executed)

- **Strategy Selected by Researcher:** **Option A — Two-Commit History**
- **Target Branch:** `main`
- **Target Remote:** Private GitHub repository `da-fidaf` *(not yet created)*
- **Execution Status:** **NOT EXECUTED** (`0` commits, `0` remotes, `22` original staged files untouched, `0` unstaged diffs)

---

## 1. Commit 1 — Historical Stage 7 Baseline (`22` Files)

**Suggested Commit Message:**
```text
chore: establish Stage 7 research baseline
```

**Execution Action (Only After Explicit Researcher Authorization):**
Run `git commit -m "chore: establish Stage 7 research baseline"` directly against the existing untouched 22-file staged index (`84,102` bytes).

| # | Repository Path | Current Git Status | Bytes |
| --- | --- | --- | ---: |
| 1 | `.env.example` | **Already staged** | `267` |
| 2 | `.gitattributes` | **Already staged** | `626` |
| 3 | `.gitignore` | **Already staged** | `1,265` |
| 4 | `.gitleaks.toml` | **Already staged** | `478` |
| 5 | `.pre-commit-config.yaml` | **Already staged** | `2,048` |
| 6 | `.python-version` | **Already staged** | `5` |
| 7 | `README.md` | **Already staged** | `2,733` |
| 8 | `configs/paths.example.yaml` | **Already staged** | `677` |
| 9 | `docs/PROJECT_STATUS.md` | **Already staged** | `1,795` |
| 10 | `docs/REPOSITORY_POLICY.md` | **Already staged** | `3,417` |
| 11 | `docs/architecture/PORTABLE_ARCHITECTURE.md` | **Already staged** | `3,734` |
| 12 | `pyproject.toml` | **Already staged** | `768` |
| 13 | `src/dafidaf/__init__.py` | **Already staged** | `442` |
| 14 | `src/dafidaf/__main__.py` | **Already staged** | `196` |
| 15 | `src/dafidaf/cli.py` | **Already staged** | `9,048` |
| 16 | `src/dafidaf/config.py` | **Already staged** | `6,845` |
| 17 | `src/dafidaf/paths.py` | **Already staged** | `9,677` |
| 18 | `src/dafidaf/repo_guard.py` | **Already staged** | `6,731` |
| 19 | `tests/unit/test_config_and_paths.py` | **Already staged** | `6,602` |
| 20 | `tests/unit/test_doctor_cli.py` | **Already staged** | `2,801` |
| 21 | `tests/unit/test_repo_guard.py` | **Already staged** | `2,199` |
| 22 | `uv.lock` | **Already staged** | `21,748` |

---

## 2. Commit 2 — Research Framework, Phase 1–3B.2 Documentation, and Repository Foundation (`194` Files Planned)

**Suggested Commit Message:**
```text
docs: establish professional DA-FIDAF research repository
```

> **Pre-Commit-2 Prerequisite:** Before staging Commit 2, (1) apply the approved replacement for `README.md`, (2) apply the **revised** `.gitignore` (adding `!.github/workflows/secret-scan.yml`, `.venv-docs/`, `site/`, and removing the temporary header banner), (3) apply the **revised** `.gitattributes` (removing the temporary header banner), and (4) optionally integrate the researcher's two PNG diagrams into `docs/architecture/figures/source/`.

### 2.1 Proposed Replacements for Stage 7 Root Files (`3` Files)

| Repository Path | Current Git Status | Action for Commit 2 |
| --- | --- | --- |
| `README.md` (from `docs/repository/proposed_staged_updates/README.proposed.md`) | **Proposed replacement** *(Currently `Already staged`)* | Apply after Commit 1 (`APPROVE` recommended) |
| `.gitignore` (from `docs/repository/proposed_staged_updates/gitignore.proposed` + `!.github/workflows/secret-scan.yml` fix) | **Proposed replacement** *(Currently `Already staged`)* | Apply revised version after Commit 1 (`REVISE` required first) |
| `.gitattributes` (from `docs/repository/proposed_staged_updates/gitattributes.proposed`, clean header) | **Proposed replacement** *(Currently `Already staged`)* | Apply revised version after Commit 1 (`REVISE` minor header cleanup) |

### 2.2 Complete Untracked Files Planned for Commit 2 (`191` Files)

#### Root Documentation, Metadata & GitHub Configuration (`14` Files — All `Untracked`)
- `CITATION.cff` (`Untracked`)
- `CHANGELOG.md` (`Untracked`)
- `CONTRIBUTING.md` (`Untracked`)
- `CODE_OF_CONDUCT.md` (`Untracked`)
- `SECURITY.md` (`Untracked`)
- `mkdocs.yml` (`Untracked`)
- `requirements-docs.txt` (`Untracked`)
- `.github/ISSUE_TEMPLATE/bug_report.yml` (`Untracked`)
- `.github/ISSUE_TEMPLATE/feature_request.yml` (`Untracked`)
- `.github/ISSUE_TEMPLATE/research_question.yml` (`Untracked`)
- `.github/PULL_REQUEST_TEMPLATE.md` (`Untracked`)
- `.github/workflows/ci-tests-and-lint.yml` (`Untracked`)
- `.github/workflows/docs-build.yml` (`Untracked`)
- `.github/workflows/secret-scan.yml` (`Untracked` — currently masked by Stage 7 `.gitignore:16:*secret*`; unmasked once revised `.gitignore` is applied!)

#### Experiment Configurations & Verified Lightweight Manifests (`9` Files — All `Untracked`)
- `configs/experiments/e1_iid_vs_noniid.yaml` (`Untracked`)
- `configs/experiments/e2_concept_drift.yaml` (`Untracked`)
- `configs/experiments/e3_benign_drift_vs_poisoning.yaml` (`Untracked`)
- `configs/experiments/e4_byzantine_robust_agg.yaml` (`Untracked`)
- `configs/experiments/e5_cross_dataset_hold.yaml` (`Untracked`)
- `configs/experiments/e6_ablation_overhead.yaml` (`Untracked`)
- `manifests/dataset_inventory.json` (`Untracked`)
- `manifests/ton_iot_drift_analysis.json` (`Untracked`)
- `manifests/ton_iot_temporal_audit.json` (`Untracked`)

#### Phase 2–3B.2 Source Code (`28` Files — All `Untracked`)
- `src/dafidaf/attacks/__init__.py`, `src/dafidaf/attacks/simulators.py` (`Untracked`)
- `src/dafidaf/attribution/__init__.py`, `src/dafidaf/attribution/engine.py` (`Untracked`)
- `src/dafidaf/data/__init__.py`, `adapters.py`, `flow_extract.py`, `partitioning.py`, `preprocessing.py`, `provenance.py`, `schemas.py` (`Untracked`)
- `src/dafidaf/drift/__init__.py`, `src/dafidaf/drift/core.py` (`Untracked`)
- `src/dafidaf/evaluation/__init__.py`, `src/dafidaf/evaluation/metrics.py` (`Untracked`)
- `src/dafidaf/federated/__init__.py`, `aggregation.py`, `client.py`, `trainer.py` (`Untracked`)
- `src/dafidaf/models/__init__.py`, `src/dafidaf/models/logistic.py` (`Untracked`)
- `src/dafidaf/orchestration/__init__.py`, `cli.py`, `runner.py` (`Untracked`)
- `src/dafidaf/privacy/__init__.py`, `src/dafidaf/privacy/mechanisms.py` (`Untracked`)
- `src/dafidaf/visualization/__init__.py`, `src/dafidaf/visualization/ieee_plots.py` (`Untracked`)

#### Phase 2–3B.2 Test Suite (`7` Files — All `Untracked`)
- `tests/integration/test_phase2_end_to_end.py` (`Untracked`)
- `tests/unit/test_phase2_2_remediation.py` (`Untracked`)
- `tests/unit/test_phase3b_2_remediation.py` (`Untracked`)
- `tests/unit/test_visualization_ieee.py` (`Untracked`)
- `tests/unit/test_workstream_a_data.py` (`Untracked`)
- `tests/unit/test_workstream_b_federated.py` (`Untracked`)
- `tests/unit/test_workstream_c_drift_attacks_attribution.py` (`Untracked`)

#### Documentation Tree (`133` Files — All `Untracked`)
- **Landing (`1`):** `docs/index.md`
- **Research (`6`):** `docs/research/problem_statement.md`, `research_contributions.md`, `research_objectives.md`, `research_overview.md`, `research_questions.md`, `scope_and_limitations.md`
- **Architecture (`18`):** `docs/architecture/DATA_PIPELINE_SPECIFICATION.md`, `DRIFT_AND_ATTACK_ATTRIBUTION_SPECIFICATION.md`, `EVALUATION_PROTOCOL.md`, `FEDERATED_LEARNING_SPECIFICATION.md`, `IEEE_VISUALIZATION_SPECIFICATION.md`, `PHASE_2_1_REMEDIATION_PLAN.md`, `PHASE_2_2_ACCEPTANCE_GATE_REPORT.md`, `PHASE_2_2_REMEDIATION_REPORT.md`, `PHASE_2_IMPLEMENTATION_BLUEPRINT.md`, `PHASE_2_IMPLEMENTATION_REPORT.md`, `PHASE_2_MODULE_STATUS.md`, `attribution_engine.md`, `drift_adaptation.md`, `federated_learning.md`, `local_ids.md`, `risk_aware_aggregation.md`, `system_architecture.md`, `figures/FIGURE_CATALOG.md`
- **Methodology Alignment (`8`):** `docs/methodology/DA_FIDAF_ARCHITECTURE_ALIGNMENT_AUDIT.md`, `DA_FIDAF_EXPERIMENT_ALIGNMENT_AUDIT.md`, `DA_FIDAF_METHODOLOGY_ALIGNMENT_VERDICT.md`, `DA_FIDAF_METHODOLOGY_TRACEABILITY_MATRIX.md`, `DA_FIDAF_METHOD_GAP_REGISTER.md`, `DA_FIDAF_ORIGINAL_METHODOLOGY_SPECIFICATION.md`, `DA_FIDAF_ORIGINAL_METHOD_REMEDIATION_BLUEPRINT.md`, `ORIGINAL_METHODOLOGY_SOURCE_INVENTORY.md`
- **Datasets Hubs (`4`):** `docs/datasets/data_governance.md`, `dataset_inventory.md`, `dataset_provenance.md`, `preprocessing.md`
- **Historical Phase 1 & Phase 3 Dataset Audits (`28`):** `docs/dataset/PHASE_1_TRANSITION_READINESS.md`, `docs/dataset/phase1/01_DATASET_INVENTORY.md` through `24_PHASE_1_RESEARCH_READINESS_GATE.md`, `docs/dataset/phase3/PHASE_3A_1_DATASET_CONSOLIDATION.md`, `PHASE_3A_TON_IOT_INTEGRITY_REPORT.md`, `PHASE_3B_DATASET_SELECTION_AND_SPLIT_PLAN.md`
- **Experiments (`36`):** `docs/experiments/EXPERIMENT_EXECUTION_GUIDE.md`, `experimental_protocol.md`, `phase3a/index.md`, `phase3b/index.md`, `phase3b_2/index.md`, plus all `31` Phase 3A / 3A.1 / 3B / 3B.1 / 3B.2 reports under `docs/experiments/phase3/` (`PHASE_3A_1_E1_DIAGNOSTIC_AUDIT.md`, `PHASE_3A_1_E2_DIAGNOSTIC_AUDIT.md`, `PHASE_3A_PILOT_RESULTS.md`, `PHASE_3A_PIPELINE_VALIDATION_REPORT.md`, `PHASE_3B_1_E1_METRIC_VERIFICATION.md`, `PHASE_3B_1_E2_DRIFT_VERIFICATION.md`, `PHASE_3B_1_E3_ATTRIBUTION_VERIFICATION.md`, `PHASE_3B_1_E4_BYZANTINE_VERIFICATION.md`, `PHASE_3B_1_E6_ABLATION_VERIFICATION.md`, `PHASE_3B_1_FIGURE_AUDIT.md`, `PHASE_3B_1_INDEPENDENT_AUDIT_REPORT.md`, `PHASE_3B_1_REPRODUCIBILITY_REPORT.md`, `PHASE_3B_1_STATISTICAL_REANALYSIS.md`, `PHASE_3B_2_E1_DOMAIN_SHIFT_DIAGNOSTICS.md`, `PHASE_3B_2_E3_ATTRIBUTION_IMPROVEMENT.md`, `PHASE_3B_2_E6_ABLATION_VALIDATION.md`, `PHASE_3B_2_INDEPENDENT_REVIEW.md`, `PHASE_3B_2_INTEGRITY_MANIFEST_REPORT.md`, `PHASE_3B_2_PUBLICATION_ASSET_REVISION.md`, `PHASE_3B_2_REMEDIATION_REPORT.md`, `PHASE_3B_2_STATISTICAL_REANALYSIS.md`, `PHASE_3B_E1_RESULTS.md`, `PHASE_3B_E2_RESULTS.md`, `PHASE_3B_E3_RESULTS.md`, `PHASE_3B_E4_RESULTS.md`, `PHASE_3B_E6_RESULTS.md`, `PHASE_3B_EXECUTION_REPORT.md`, `PHASE_3B_EXPERIMENT_DESIGN.md`, `PHASE_3B_FIGURE_AND_TABLE_STANDARD.md`, `PHASE_3B_FINAL_EXPERIMENT_PROTOCOL.md`, `PHASE_3B_STATISTICAL_ANALYSIS_PLAN.md`)
- **Results & Verified PNGs (`8`):** `docs/results/limitations.md`, `results_overview.md`, `figures/FIGURE_CATALOG.md`, `figures/fig_E1_02_f1_comparison_rev2.png`, `figures/fig_E1_03_w1_domain_shift.png`, `figures/fig_E2_01_drift_timeline_rev2.png`, `figures/fig_E3_02_attribution_v2.png`, `figures/fig_E6_02_genuine_ablation.png`
- **Development (`5`):** `docs/development/configuration.md`, `installation.md`, `running_experiments.md`, `testing.md`, `troubleshooting.md`
- **References (`2`):** `docs/references/bibliography.bib`, `citation_policy.md`
- **Security Reports (`5`):** `docs/security/PHASE_2_1_INDEPENDENT_TECHNICAL_AUDIT.md`, `PHASE_2_2_SECURITY_REVIEW.md`, `PHASE_2_SECURITY_REVIEW.md`, `PHASE_3A_PRIVACY_VALIDATION_REPORT.md`, `PHASE_3B_NON_DP_SCOPE_AND_LIMITATIONS.md`
- **Repository Governance & Pre-Publication Reviews (`12`):** `docs/repository/ARCHITECTURE_DIAGRAM_INTEGRATION_REPORT.md`, `CITATION_METADATA_REVIEW.md`, `GIT_BASELINE_PRESERVATION_REPORT.md`, `GITHUB_PROJECT_CONFIGURATION.md`, `GITHUB_PUBLICATION_CHECKLIST.md`, `MKDOCS_BUILD_VERIFICATION.md`, `OPTION_A_COMMIT_PLAN.md`, `PRE_PUBLICATION_FILE_DIFF_REVIEW.md`, `PRE_PUBLICATION_FINAL_CHECKLIST.md`, `REPOSITORY_INVENTORY.md`, `REPOSITORY_RELEASE_READINESS.md`, `REPOSITORY_SECURITY_AUDIT.md`

### 2.3 Pending Optional Additions (Not Yet on Disk)

| Expected Path | Current Status | Notes |
| --- | --- | --- |
| `docs/architecture/figures/source/DA-FIDAF_Draft_Framework_v1.png` | **Excluded (Missing on disk)** | Include in Commit 2 once copied by researcher and verified. |
| `docs/architecture/figures/source/DA-FIDAF_Trustworthy_Adaptive_Framework_v2.png` | **Excluded (Missing on disk)** | Include in Commit 2 once copied by researcher and verified. |

---

## 3. Explicitly Excluded Paths (Must NEVER Be Committed)

| Path / Directory | Current Git Status | Reason for Exclusion |
| --- | --- | --- |
| `.env` | **Excluded** (Git-ignored) | Machine-local paths; never version-control. |
| `.venv/` | **Excluded** (Git-ignored) | Local Python runtime virtual environment. |
| `.venv-docs/` | **Excluded** *(Add to revised `.gitignore`)* | Isolated MkDocs Material documentation virtual environment. |
| `site/` | **Excluded** *(Add to revised `.gitignore`)* | Generated MkDocs static HTML output; never publish to repo branch. |
| `docs/repository/proposed_staged_updates/README.proposed.md` | **Excluded** (Temporary staging draft) | Remove or exclude once approved changes are applied to root `README.md`. |
| `docs/repository/proposed_staged_updates/gitignore.proposed` | **Excluded** (Temporary staging draft) | Remove or exclude once revised `.gitignore` is applied. |
| `docs/repository/proposed_staged_updates/gitattributes.proposed` | **Excluded** (Temporary staging draft) | Remove or exclude once revised `.gitattributes` is applied. |
| `I:\IoT` (external dataset root) | **Excluded** (External read-only) | Raw IoT datasets, damaged archives, and PCAP/PCAPNG files. |
| `I:\Projects\da-fidaf-runs` (external runs root) | **Excluded** (External artifacts) | `470` Phase 3B + `60` Phase 3B.2 runs, checkpoints, PDF/EPS bundles. |
| `LICENSE` | **Excluded** (Absent by decision) | Researcher selected no license file pending institutional confirmation. |
