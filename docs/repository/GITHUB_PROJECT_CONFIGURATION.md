# DA-FIDAF — GitHub Project & Label Configuration Specification

> **Status:** Prepared locally only. **No GitHub repository, remote, or remote labels have been created.** Apply these settings only after explicit researcher authorization to create the private `da-fidaf` repository.

---

## 1. Repository Settings Target

- **Repository Name:** `da-fidaf`
- **Visibility:** **Private**
- **Default Branch:** `main`
- **Branch Protection (Recommended post-initial push):** Require status checks (`CI — Lint, Repo Guard, and Tests`, `Docs — MkDocs Material Build Check`, `Security — Gitleaks Secret Scan`), block force pushes to `main`.
- **GitHub Pages:** Disabled by default for private pre-publication repository (enable only if intentionally authorized for private/internal docs viewing).

---

## 2. Canonical Issue & PR Label Specification (`22` Labels)

### Type Labels (`6`)

| Label | Hex Color | Description |
| --- | --- | --- |
| `bug` | `#d73a4a` | Defect in code, pipeline, tests, or reporting |
| `feature` | `#0075ca` | New framework capability or planned module |
| `research` | `#5319e7` | Scientific question, methodology review, or hypothesis |
| `documentation` | `#0e8a16` | MkDocs Material site, README, or research report update |
| `experiment` | `#1d76db` | Experimental design, execution protocol, or statistical audit |
| `security` | `#b60205` | Secret hygiene, data governance, or privacy/security check |

### Priority Labels (`4`)

| Label | Hex Color | Description |
| --- | --- | --- |
| `priority: critical` | `#b60205` | Publication or integrity blocker requiring immediate resolution |
| `priority: high` | `#d93f0b` | Major research or engineering gap |
| `priority: medium` | `#fbca04` | Moderate improvement or secondary refinement |
| `priority: low` | `#c2e0c6` | Minor polish or backlog item |

### Component Labels (`6`)

| Label | Hex Color | Description |
| --- | --- | --- |
| `component: attribution` | `#006b75` | Multi-evidence drift–attack attribution engine |
| `component: drift` | `#0052cc` | Local/global drift detection and continual adaptation |
| `component: aggregation` | `#5319e7` | Robust and risk-aware federated aggregation |
| `component: privacy` | `#b60205` | Differential Privacy and Secure Aggregation |
| `component: ids` | `#1d76db` | Local IDS architecture (`LinearLogisticIDS` / draft `1D-CNN / TCN`) |
| `component: federated-learning` | `#0e8a16` | Federated trainer, client simulation, and Non-IID partitioning |

### Research Phase Labels (`6`)

| Label | Hex Color | Description |
| --- | --- | --- |
| `phase: 1` | `#bfdadc` | Dataset discovery, integrity, and suitability audits |
| `phase: 2` | `#c5def5` | Core framework implementation and Phase 2.1/2.2 remediation |
| `phase: 3A` | `#d4c5f9` | Real-dataset pilot and consolidation |
| `phase: 3B` | `#e99695` | Full-scale E1–E4, E6 experiments and 3B.1 audit |
| `phase: 3B.2` | `#f9d0c4` | Targeted remediation, statistical reanalysis, and asset revision |
| `phase: 4` | `#fef2c0` | Future proposal-aligned architecture, DP/SecAgg, and E5 work |

---

## 3. Configured Local Templates & Workflows (Ready for First Push)

- Issue templates: `.github/ISSUE_TEMPLATE/bug_report.yml`, `feature_request.yml`, `research_question.yml`
- Pull request template: `.github/PULL_REQUEST_TEMPLATE.md`
- CI workflows (least-privilege `contents: read`, synthetic fixtures only, **not yet executed on GitHub**):
  - `.github/workflows/ci-tests-and-lint.yml`
  - `.github/workflows/docs-build.yml`
  - `.github/workflows/secret-scan.yml`
