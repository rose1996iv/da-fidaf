# DA-FIDAF — Repository Security and Data Governance Audit

- **Audit Date (UTC):** `2026-11-24`
- **Scanner:** Gitleaks `8.30.1` (`.gitleaks.toml`, extending all default v8 rules) + `dafidaf.repo_guard` (`10 MiB` cap, blocked extensions, whitespace/EOF checks) + full filesystem pattern audit.
- **Security Verdict:** **PASS FOR PRIVATE PUBLICATION (ZERO SECRETS / ZERO RAW DATASETS; LOW PORTABILITY HYGIENE NOTES DOCUMENTED)**

---

## 1. Secret & Credential Scan Summary

| Audit Target | Inspection Result | Risk Level |
| --- | --- | --- |
| `gitleaks dir --redact --config .gitleaks.toml .` | **`0` leaks found** (`exit 0`) | **CLEAR** |
| `gitleaks git --staged --redact --config .gitleaks.toml .` | **`0` leaks found** (`84.10 KB` scanned, `exit 0`) | **CLEAR** |
| `.env` (local machine file) | Contains ONLY `DAFIDAF_DATA_ROOT`, `DAFIDAF_RUNS_ROOT`, `DAFIDAF_SEVENZIP_EXE` (no API keys, passwords, Supabase credentials, or tokens). Verified strictly Git-ignored via `.gitignore:7:.env`. | **CLEAR (Git-Ignored)** |
| Private keys / certificates (`*.key`, `*.pem`, `*.p12`, `*.pfx`, `*.crt`) | `0` files present in repository | **CLEAR** |
| API keys / Supabase / DB passwords / sealing keys | `0` credentials present (`tests/unit/test_doctor_cli.py` uses synthetic dummy test strings only to assert non-leakage) | **CLEAR** |
| User profile paths (`C:\Users\...`) | `0` occurrences in tracked or newly created repository files | **CLEAR** |

---

## 2. Raw Dataset, Large File, and Artifact Containment Check

| Governance Check | Observed Result | Status |
| --- | --- | --- |
| Files `> 1 MiB` (excl. `.git/`, `.venv/`) | **`0` files** (largest single file is `fig_E2_01_drift_timeline_rev2.png` at `148,108` bytes / `145 KiB`) | **PASS** |
| Files `> 10 MiB` (`repo_guard` limit) | **`0` files** | **PASS** |
| Raw datasets / CSVs / PCAP / PCAPNG / archives (`.zip`, `.7z`, `.rar`, `.tar*`) | **`0` files** in repository; all remain read-only under external `DAFIDAF_DATA_ROOT` | **PASS** |
| Checkpoints / model weights (`.pt`, `.pth`, `.ckpt`, `.onnx`, `.pkl`, `.npy`) | **`0` files** in repository; remain under external `DAFIDAF_RUNS_ROOT` | **PASS** |
| Documentation figure copies (`docs/results/figures/*.png`) | `5` verified Phase 3B.2 preview PNGs (`522,331` bytes total / `0.50 MiB`); canonical external figures untouched | **PASS** |
| Damaged ToN-IoT archives & raw PCAP collections | Strictly excluded from Git and untouched on external disk | **PASS** |

---

## 3. Low-Severity Hygiene & Governance Notes (Non-Blocking for Private Repo)

1. **Historical Local Windows Drive Paths (`I:\IoT`, `I:\Projects\da-fidaf-runs`, `I:\Projects\da-fidaf`) — LOW:** Present across historical Phase 1–3B.2 audit reports (`74` references, zero usernames or secrets) and in `file:///` links inside `docs/methodology/ORIGINAL_METHODOLOGY_SOURCE_INVENTORY.md`. Preserved untouched to maintain historical audit integrity; all newly written documentation uses portable placeholders (`<DAFIDAF_DATA_ROOT>`, `<DAFIDAF_RUNS_ROOT>`) and relative Markdown links.
2. **`.gitignore` Coverage for MkDocs `site/` — LOW:** Existing staged `.gitignore` already excludes `.env`, `.venv/`, caches, datasets, PCAPs, checkpoints, and outputs, but does not yet exclude `site/` or `.venv-docs/`. Ready-to-apply update is provided in `docs/repository/proposed_staged_updates/gitignore.proposed` (not applied in-place to preserve the Stage 7 22-file staged baseline).
3. **No Public License File — GOVERNANCE:** Repository deliberately has no `LICENSE` file yet pending researcher and institutional IP confirmation. Keep GitHub visibility strictly **Private** until licensing and ownership are confirmed.
4. **Non-DP Privacy Scope Disclosure — SCIENTIFIC GOVERNANCE:** All Phase 3B / 3B.2 experiments ran with `dp_enabled=False` and `secure_aggregation_active=False`. No formal privacy guarantee is claimed.
