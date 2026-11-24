# DA-FIDAF Phase 3B.2 — Canonical Integrity & Checksum Manifest Report (Workstream F)

- **Canonical Raw-Byte Manifest:** `I:\Projects\da-fidaf-runs\phase3b_2\canonical_sha256_manifest.json`
- **Hashing Convention:** `raw_bytes_on_disk_sha256` (`hashlib.sha256(path.read_bytes()).hexdigest()`)
- **Preservation Confirmed:** Zero original Phase 3B `run_report.json` files or `run_report.sha256` sidecars were rewritten or altered.

---

## 1. Original LF/CRLF Discrepancy Root Cause (Documented)

In Phase 3B (`common_phase3b.py`), `tmp.write_text(raw, encoding="utf-8")` omitted `newline="\n"` on Windows, causing Python to translate `\n` -> `\r\n` on disk while `hashlib.sha256(raw.encode("utf-8"))` hashed the pre-translation LF string.
- **Original Phase 3B `run_report.json` (`470` files):** `470 / 470` verified **`lf_normalized_matches_sidecar == True`** (`100%` content intact; zero corruption), and all `470` raw on-disk SHA-256 hashes are now recorded in `canonical_sha256_manifest.json`.

---

## 2. Remediated Production Code & Phase 3B.2 Verification

- Updated `src/dafidaf/orchestration/runner.py` (`_write_run_report`) to write `newline="\n"` and hash `out_file.read_bytes()` directly; verified by `test_lf_canonical_sha256_matches_raw_disk_bytes`.
- **New Phase 3B.2 `run_report.json` (`60` files):** **`60 / 60`** (`100%`) pure LF on disk with **`raw_matches_sidecar == True`**.
- **Total Files Hashed in Canonical Manifest:** **`578`** (`470` original Phase 3B run reports + `5` original master summaries + `43` original IEEE figure files + `60` new Phase 3B.2 run reports).
