# DA-FIDAF — Original Methodology Source Inventory

- **Audit Date (UTC):** `2026-11-24`
- **Search Scope (Strictly Read-Only):** `I:\Projects\da-fidaf\**`, `I:\Projects\*` (depth 2), and `I:\IoT\**` (full depth for `.pdf`, `.docx`, `.doc`, `.pptx`, `.tex`, `.md`, `.txt`, and `*proposal*`/`*synopsis*`/`*thesis*`/`*dafidaf*`).
- **Critical Finding:** **NO original approved PhD research proposal document (PDF, DOCX, LaTeX, or authoritative proposal Markdown) was found anywhere in the repository or dataset workspaces.**

---

## 1. Search Result: Authoritative Primary Source (MISSING)

| Expected Authoritative Artifact | Status | Evidence |
| --- | --- | --- |
| Original Approved PhD Research Proposal / Synopsis (`.pdf` / `.docx` / `.tex`) | **NOT LOCATED (MISSING)** | Full recursive search across `I:\Projects\da-fidaf` and `I:\IoT` returned zero proposal/synopsis/thesis files. |
| Original Architecture Diagram / Mathematical Formulation Document | **NOT LOCATED (MISSING)** | Zero original architecture figures or formal proposal equations exist on disk. |
| Original Approved Experimental Design Specification (Pre-Phase 1) | **NOT LOCATED (MISSING)** | Only downstream engineering audits/blueprints created during Phases 1–3 exist on disk. |

---

## 2. Secondary / Downstream Sources Located on Disk

Because the primary proposal document is absent, ONLY the following secondary project artifacts were located and inspected:

| Source File | Type | Authority Level | Verifiable Content |
| --- | --- | --- | --- |
| [README.md](file:///I:/Projects/da-fidaf/README.md) | Repo overview (Stage 2) | Secondary | Names DA-FIDAF, lists 6 high-level research scope bullets (heterogeneous IoT, Non-IID FL, concept drift/continual adaptation, adversarial/Byzantine resilience, robust aggregation, privacy-preserving collaborative learning). Contains zero model architectures, equations, or detailed protocols. |
| [06_DAFIDAF_EXPERIMENT_SUITABILITY.md](file:///I:/IoT/_dataset_audit/06_DAFIDAF_EXPERIMENT_SUITABILITY.md) | Pre-Phase-1 dataset audit | Secondary | Lists experiment labels `E1` (IID vs Non-IID), `E2` (gradual/abrupt drift), `E3` (benign drift vs poisoning), `E4` (adaptive/Byzantine clients), `E5` (cross-dataset generalization), `E6` (ablation/overhead) and dataset families (CICIoT2023, ToN-IoT, Edge-IIoTset). |
| [PHASE_2_IMPLEMENTATION_BLUEPRINT.md](file:///I:/Projects/da-fidaf/docs/architecture/PHASE_2_IMPLEMENTATION_BLUEPRINT.md) | Engineering blueprint | Downstream (Agent-authored) | 10-module software plan derived from Phase 1 dataset audits — **NOT** the original research proposal. |
| `docs/architecture/*_SPECIFICATION.md` & `docs/experiments/phase3/*` | Implementation specs & reports | Downstream (Agent-authored) | Documents what was engineered and executed in Phases 2–3B.2 — MUST NOT be treated as the original approved proposal. |
| Prompt-transmitted research title | User prompt metadata | Secondary (Title only) | *"A Robust, Privacy-Preserving and Continually Adaptive Federated Intrusion Detection Framework for Heterogeneous IoT Networks under Non-IID Data, Concept Drift and Adversarial Threats."* |

---

## 3. Source Evidence Sufficiency Determination

- **Primary Source Sufficiency:** **INSUFFICIENT SOURCE EVIDENCE**.
- **Rule Enforced:** No architecture, loss function, neural network backbone, cryptographic protocol, or hyperparameter from the unlocated original proposal is invented or assumed in any companion deliverable.
