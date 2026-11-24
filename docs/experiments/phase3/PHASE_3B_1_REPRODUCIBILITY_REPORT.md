# DA-FIDAF Phase 3B.1 — Independent Reproducibility & Integrity Report

---

## Finding [AUD-01] — HIGH: Windows CRLF Line-Ending Mismatch in All `470` `run_report.sha256` Files

- **Finding ID:** `AUD-01` | **Severity:** `HIGH` (Execution & Checksum Integrity)
- **Evidence File:** `I:\Projects\da-fidaf-runs\scripts\phase3b\common_phase3b.py` (lines 253–258) & all `470` `run_report.json` / `run_report.sha256` pairs under `I:\Projects\da-fidaf-runs\phase3b\`
- **Verification Method:** Recomputed raw-byte SHA-256 and LF-normalized SHA-256 across all `470` `run_report.json` files.
- **Original Reported vs. Independently Recalculated:**
  - `raw-byte SHA-256 matches`: **`0 / 470`** (ALL `470` files contain `\r\n` CRLF on disk!)
  - `LF-normalized SHA-256 matches`: **`470 / 470`** (`100%` content integrity confirmed; zero tampering or corruption!)
- **Root Cause:** `tmp.write_text(raw, encoding="utf-8")` on Windows translates `\n` to `\r\n`, while `hashlib.sha256(raw.encode("utf-8"))` hashed the pre-translation LF string. (Note: `src/dafidaf/orchestration/runner.py` `_write_run_report` has the same Windows `write_text` pattern.)
- **Scientific Implication:** External verification via `sha256sum -c` or PowerShell `Get-FileHash` fails on all `470` files even though the JSON contents are intact. Original files were NOT modified during this audit.
- **Recommended Action:** Always pass `newline="\n"` to `write_text()` and compute SHA-256 from the exact bytes written (`out_file.read_bytes()`) in both `common_phase3b.py` and `src/dafidaf/orchestration/runner.py`.

---

## Finding [AUD-07B] — LOW: Scope Narrowing of Phase 3B Bit-Exact Reproducibility Claim

- **Finding ID:** `AUD-07B` | **Severity:** `LOW`
- **Evidence File:** `I:\Projects\da-fidaf-runs\scripts\phase3b\run_phase3b_e3_e4_e6.py` (`verify_reproducibility`, lines 371–393)
- **Verification Method:** Audited exact assertions executed in `verify_reproducibility()`.
- **What Was Actually Verified:**
  - Two identical back-to-back runs of W1 (`iid`, `seed=42`, `4` rounds, `batch_size=128`) on the same Windows host produced bit-exact final `model.get_parameters()` (`True`) and bit-exact fixed-0.50 `macro_f1` (`0.47519`, `True`).
  - Independent checkpoint replay (`checkpoint_round_008.json` for `e1_W1_iid_fedavg_seed42`) reproduced exact `ROC-AUC = 0.320810` and `Macro-F1 = 0.699189`.
- **What Was NOT Verified (Narrowed Claim Scope):**
  - Per-sample raw prediction arrays were not saved or diffed across runs.
  - Reproducibility was not re-executed end-to-end for E2, E3, E4, E6, or across different OS/CPU architectures (where IEEE-754 libm `math.exp` rounding can differ in the last ULP).
  - Non-deterministic elements: `run_id` timestamps and `uuid4` nonces vary per run by design (to prevent overwrites); `train_wall_seconds` and `inference_ms_per_1k` vary with OS scheduling.
  - All PRNGs use explicitly seeded pure-Python `random.Random(seed)` and `hashlib.blake2b` (confirmed free of `PYTHONHASHSEED` dependence).
- **Recommended Action:** Narrow any publication claim to: *"Same-host single-process parameter and metric determinism verified on W1 IID seed 42; all experiment PRNGs are deterministically seeded."*
