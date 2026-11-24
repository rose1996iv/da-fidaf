# Changelog

All notable engineering and research milestones for **DA-FIDAF** are recorded in this file.

## [Unreleased] — Local Private GitHub Preparation (`2026-11-24`)

### Added
- MkDocs Material documentation configuration (`mkdocs.yml`), isolated documentation dependencies (`requirements-docs.txt`), and structured research documentation tree (`docs/research/`, `docs/datasets/`, `docs/results/`, `docs/development/`, `docs/references/`, `docs/repository/`).
- Architecture and results figure catalogs (`FIG-01`–`FIG-10`), including 5 lightweight documentation copies of verified Phase 3B.2 IEEE figures under `docs/results/figures/`.
- Repository metadata (`CITATION.cff`, `CHANGELOG.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`) and GitHub issue/PR templates plus least-privilege CI workflows (`.github/`).
- Git baseline preservation report, external machine-readable baseline manifest, security audit, release readiness report, and publication checklist.
- Proposed replacements for frozen Stage 7 staged files (`README.md`, `.gitignore`, `.gitattributes`) staged safely under `docs/repository/proposed_staged_updates/` pending researcher authorization.

### Verified Prior Research Phases (Preserved Untouched)
- **Phase 3B.2 (Conditional Pass):** LF-canonical raw-byte SHA-256 hashing (`60/60`), W1 domain-shift diagnosis (`8/8` active feature sign inversions), honest negative-net evaluation of experimental `E3 v2` (`client_val_loss_delta`), code-isolated closed-loop `E6 v2` quarantine ablation (with over-quarantine disclosed), paired Student-$t$ ($df=4$) reanalysis (`9` verdict shifts), revised IEEE figures (`36` files), and `578`-file canonical checksum manifest.
- **Methodology Alignment Audit (`INSUFFICIENT SOURCE EVIDENCE`):** Documented missing original approved PhD proposal (`GAP-01`) and 8-item gap register without fabricating proposal claims.
- **Phase 3B & 3B.1:** `490` authorized Non-DP ToN-IoT runs across E1–E4 and E6 (`E5` on `HOLD`) plus independent audit.
- **Phase 3A & 3A.1:** Real-dataset pilot validation and 23-shard ToN-IoT consolidation.
- **Phase 2 / 2.1 / 2.2:** Modular Python 3.12 framework (`src/dafidaf/`), independent technical audit, and remediation (`57` passing tests, Ruff clean).
- **Phase 1:** 24-report dataset discovery, integrity, schema, temporal provenance, and readiness audit across ToN-IoT, CICIoT2023, and Edge-IIoTset.
- **Stages 1–6 (Frozen Git Baseline):** 22 staged files (`84,102` bytes) on branch `main`, Gitleaks v8, pre-commit/pre-push hooks, and portable `dafidaf doctor` core.
