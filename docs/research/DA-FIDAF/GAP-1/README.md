# DA-FIDAF GAP-1 — Master Documentation Index

**Scope:** Centralized repository documentation index for `EXP-GAP-1` (`CompactMLP` Drift & Continual Adaptation: `E2` + `C3`) under `I:\Projects\da-fidaf\docs\research\DA-FIDAF\GAP-1\`.  
**Last Updated:** `2026-11-28`  
**Current GAP-1 Status:** **`COMPLETE & AUDITED (7/7 PASS) — APPEND-ONLY LEDGER ADDENDUM v1.1 FINALIZED (AWAITING GAP-2 AUTHORIZATION)`** *(All `320` confirmatory runs, `328/328` `.sha256` sidecars, and `66/66` statistical tests independently verified; pre-GAP-1 frozen ledgers untouched; `EXP-GAP-2`/`EXP-GAP-3` remain blocked pending explicit separate authorization)*  
**Verified Repository Baseline:** Branch `main` (pushed to `origin/main`; prior commit `66ffe19d86166e49fb3de8d90eb2ab29c1340954`).

---

## 1. Authoritative & Supporting GAP-1 Documents (Inside `docs/`)

| Relative Path (from repo root) | Document Purpose | Current Status | Version / Date | Classification | Verified SHA-256 |
|---|---|---|---|---|---|
| [`docs/research/DA-FIDAF/GAP-1/README.md`](README.md) | Master GAP-1 documentation index, provenance map, and status summary | Active | `v1.6` / `2026-11-28` | **Authoritative** *(Index)* | *(computed on save; self-referenced)* |
| [`docs/research/DA-FIDAF/GAP-1/EXP_GAP_1_Protocol_v5_0.md`](EXP_GAP_1_Protocol_v5_0.md) | Complete locked `EXP-GAP-1` protocol (`D1`–`D6`, `RD-1`–`RD-5`, `VER-1`/`VER-2` summary, claim boundaries; byte-identical canonical repo copy of verified `v5.0`) | Locked (`v5.0`) | `v5.0` / `2026-11-27` | **Authoritative** *(Protocol)* | `0ee5dbd15e2116ab0294bcd7d5f8a715837a97aa99cd761e024645f6e7899ad2` |
| [`docs/research/DA-FIDAF/GAP-1/GAP_1_REPOSITORY_AND_ARTIFACT_AUDIT_REPORT.md`](GAP_1_REPOSITORY_AND_ARTIFACT_AUDIT_REPORT.md) | Phase A audit of Git state, `docs/` tree, frozen ledger hashes, source file hashes, and discrepancies (`AUD-01`–`AUD-06`) | Completed | `v1.0` / `2026-11-28` | **Supporting** *(Audit Report)* | `e3ad71cebbd150cc58598668e1ef564decf15b4a72455e06e006e920cb04397a` |
| [`docs/research/DA-FIDAF/GAP-1/GAP_1_PROTOCOL_AND_DECISION_AUDIT_REPORT.md`](GAP_1_PROTOCOL_AND_DECISION_AUDIT_REPORT.md) | Phase B line-by-line audit of `v5.0` operational rules, cross-ledger consistency, observations (`OBS-B1`–`OBS-B5`), and locked `D1`–`D6` / `RD-1`–`RD-5` decision log | Completed (`PASS`) | `v1.0` / `2026-11-28` | **Authoritative** *(Decision Log & Protocol Audit)* | `084a4ec01ba8fe3e6439da83334107f348c521e38e74b1bb3dc54770f6fc76fd` |
| [`docs/research/DA-FIDAF/GAP-1/GAP_1_READ_ONLY_VERIFICATION_REPORT.md`](GAP_1_READ_ONLY_VERIFICATION_REPORT.md) | Phase C independent read-only verification report for `VER-1` (`200` reservoirs) and `VER-2` (`2,000` stream client-rounds, clean PSI FAR, ramp/recall checks) with explicit unverified boundaries | Completed (`PASS`) | `v1.0` / `2026-11-28` | **Authoritative** *(Verification Report)* | `1248bce48358195d2f8f3938d984403b32218c8ab2d05495f42c1fd7eb23478a` |
| [`docs/research/DA-FIDAF/GAP-1/GAP_1_DETERMINISM_PILOT_READINESS_AND_EXECUTION_PLAN.md`](GAP_1_DETERMINISM_PILOT_READINESS_AND_EXECUTION_PLAN.md) | Phase D readiness checklist, isolated implementation scope, exact `2`-run Determinism Pilot specification, fail-closed abort rules, rollback plan, and two-stage approval gate | Executed (Gate 1 & Gate 2 Complete) | `v1.0` / `2026-11-28` | **Supporting** *(Execution Plan)* | `cf88a1dc969f041681242194105eccbe54043719428ba202b45b233f80f51603` |
| [`docs/research/DA-FIDAF/GAP-1/GAP_1_DETERMINISM_PILOT_REPORT.md`](GAP_1_DETERMINISM_PILOT_REPORT.md) | Gate 1 Determinism Pilot (`VER-3`) verification report (`run_A` vs. `run_B`, bit-exact `0.000e+00` CUDA determinism on `GTX 1650`, `0` discrete mismatches, runtime diagnostics, isolation audit) | Completed (`PASS`) | `v1.0` / `2026-11-28` | **Authoritative** *(Pilot Verification Report)* | `cbd335405b91ad62821b8a443c66d53e2335891e854d77a975300523573c4ce9` |
| [`docs/research/DA-FIDAF/GAP-1/GAP_1_POST_PILOT_AUDIT_REPORT.md`](GAP_1_POST_PILOT_AUDIT_REPORT.md) | Independent read-only post-pilot audit recomputing raw `.npy`/`.npz`/`.json`/`.sha256` diffs (`0.000e+00`, `0` mismatches), verifying scope/isolation, and documenting minor non-blocking notes (`DISCREPANCY-1`–`NOTE-3`) | Completed (`AUDIT PASSED`) | `v1.0` / `2026-11-28` | **Authoritative** *(Post-Pilot Audit Report)* | `aaf15b19d115129a749299d160b5fc5a8b9e8f51f61a3d956951a2f98395b9bd` |
| [`docs/research/DA-FIDAF/GAP-1/GAP_1_GATE_2_READINESS_REPORT.md`](GAP_1_GATE_2_READINESS_REPORT.md) | Concise Gate 2 readiness check verifying `320`-run matrix, `20` Holm tests, `W1`/`W3` exact `StratifiedShuffleSplit` `ceil` counts, `pilot_slot` omission, and `trigger_rate` naming choice | Completed (Gate 2 Executed under Option B-Hybrid) | `v1.0` / `2026-11-28` | **Supporting** *(Gate 2 Readiness Report)* | `5d2e7e39763e061b7116eeb1400846b2566c18fc203cb43d5b52f7233cd980c2` |
| [`docs/research/DA-FIDAF/GAP-1/GAP_1_FINAL_EXPERIMENT_REPORT.md`](GAP_1_FINAL_EXPERIMENT_REPORT.md) | Gate 2 confirmatory experiment report (`20` base FL models + `320` trajectories, `20` pre-registered Holm + exact Wilcoxon tests, `W1` vs. `W3` findings, verified split counts & hashes) | Completed *(Independently Audited: `PASS`)* | `v1.0` / `2026-11-28` | **Authoritative** *(Final Experiment Report)* | `5ecd61238596d5cf6c1967753a0d6f6aa9024a6a92b5f56b1feea0c2a6c0946f` |
| [`docs/research/DA-FIDAF/GAP-1/GAP_1_POST_CONFIRMATORY_AUDIT_REPORT.md`](GAP_1_POST_CONFIRMATORY_AUDIT_REPORT.md) | Independent read-only post-confirmatory audit verifying all `320` raw runs, `20` base-model linkages, `328/328` `.sha256` sidecars, `66/66` paired/Wilcoxon/Holm stats, split counts, report fidelity, and Gate 1/ledger/Git isolation | Completed (`AUDIT PASSED`) | `v1.0` / `2026-11-28` | **Authoritative** *(Post-Confirmatory Audit Report)* | `625b0489658760f9c7474930513bb48d62e267ca20c6781ab4d312a66c25b7b9` |
| [`docs/research/DA-FIDAF/GAP-1/GAP_1_CROSS_STAGE_EVIDENCE_LEDGER_ADDENDUM_v1_1.md`](GAP_1_CROSS_STAGE_EVIDENCE_LEDGER_ADDENDUM_v1_1.md) | Append-only post-GAP-1 cross-stage evidence & claim ledger addendum (`Domain D7`, `U-B4-01`–`U-B4-07`, `2,325` cumulative disjoint runs, explicit confirmatory/exploratory/`NS` separation and `C1+C2+C3`/`GAP-2`/`GAP-3` boundaries) preserving both frozen ledgers byte-identical | Completed *(Reviewed & Verified)* | `v1.1` / `2026-11-28` | **Authoritative** *(Append-Only Ledger Addendum)* | `8de56f836a24309cec7365c15a5eff087c097921dc0650b6afac56a91dc60fa0` |

---

## 2. Preserved External, Archived & Superseded GAP-1 Artifacts (Not Modified)

| Artifact / Revision | Location | Status | Classification | Notes / Verified Hash |
|---|---|---|---|---|
| Pre-consolidation external `EXP_GAP_1_Protocol_v5_0.md` | `I:\Projects\da-fidaf-runs\phase4_phd_execution\exp_gap1_protocol\EXP_GAP_1_Protocol_v5_0.md` | Preserved untouched | **Archived** *(Pre-consolidation mirror)* | Byte-identical to repo `docs/` copy (`SHA-256: 0ee5dbd15e2116ab0294bcd7d5f8a715837a97aa99cd761e024645f6e7899ad2`). |
| Historical protocol drafts `v1.0` – `v4.0` | Conversation review transcript only (never saved as repo files) | Superseded by `v5.0` | **Superseded** | Resolved `U1` (`X_test` PSI leakage removed), `U2` (`p_min=0.06` simplex floor), `D4` (`q_min=3` state machine), `D5` (compute fairness), and `RD-1`–`RD-5`. |
| Frozen Unified Cross-Stage Evidence & Claim Ledger | `I:\Projects\da-fidaf-runs\phase4_phd_execution\unified_cross_stage_freeze\DA_FIDAF_Unified_Cross_Stage_Evidence_and_Claim_Ledger.md` | Immutable | **Authoritative** *(External Frozen Ledger)* | Verified unchanged (`SHA-256: f51eddcea12928c6ab465bd12a21e9c22f99b59a55d3a36a9cda210c09810d4f`). |
| Frozen Stage A4-Fix Evidence Freeze & Claim Ledger | `I:\Projects\da-fidaf-runs\phase4_phd_execution\stage_a4_evidence_freeze\Stage_A4_Fix_Evidence_Freeze_and_Claim_Ledger.md` | Immutable | **Authoritative** *(External Frozen Ledger)* | Verified unchanged (`SHA-256: 47f28614879b019f075cdfcc4e586998ad59588f584af11b6e6073bd5f6a7335`). |

---

## 3. Blocked Next Actions (Pending Explicit Separate User Authorization)

- **Next Research Gaps (`EXP-GAP-2` / `EXP-GAP-3`):** Protocol authoring and execution for `C1` attribution fidelity (`v3` `Hold`/`Downweight` logging & `n = 10` pre-registered audit) or `C2` 4-tier graduated response latency/overhead and closed-loop `E6` ablation remain blocked pending explicit separate authorization.

---

## 4. Non-Negotiable Scope & Evidence Boundaries

- `ToN-IoT W1` (`89,269`) is a strict chronological subset of `W3` (`191,738`); never pool them or treat them as independent datasets.
- `X_test` remains `100%` untouched for PSI fitting, threshold calibration, adaptation, and protocol selection.
- `VER-1` and `VER-2` are read-only data/PSI checks — they do **not** validate model accuracy, live Page-Hinkley FAR, or CUDA determinism (`<= 1e-6`).
- `E5` cross-dataset transfer remains on **`HOLD`**; `C1` attribution and `C2` 4-tier response telemetry belong to `EXP-GAP-2` / `EXP-GAP-3`.
