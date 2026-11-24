# Troubleshooting

## 1. `dafidaf doctor` Exits with Warning (`MISSING ON DISK`)

- Confirm `.env` exists in the repository root (copied from `.env.example`) and points `DAFIDAF_DATA_ROOT` and `DAFIDAF_RUNS_ROOT` to existing external directories.
- Remember that `dafidaf doctor` is strictly read-only and never creates missing directories automatically.

## 2. `E5OntologyBlockedError` When Running `e5_cross_dataset_hold.yaml`

- This is expected fail-closed behavior. Experiment E5 is intentionally on **`HOLD`** pending formal cross-dataset semantic feature and label ontology validation (`GAP-05`).

## 3. Windows CRLF vs. LF Checksum Discrepancies on Historical Phase 3B Files

- Original Phase 3B `run_report.json` files (`470` files) were written prior to the `newline="\n"` fix in `src/dafidaf/orchestration/runner.py`.
- All `470/470` original Phase 3B files verify identically after LF normalization, and their exact raw on-disk SHA-256 hashes are recorded in `<DAFIDAF_RUNS_ROOT>/phase3b_2/canonical_sha256_manifest.json`.
- All Phase 3B.2 and subsequent runs write pure LF bytes with `100%` raw-byte sidecar matches.

## 4. `mkdocs: command not found`

- MkDocs Material is intentionally kept out of the core runtime `.venv` (`pyproject.toml`). Install `requirements-docs.txt` into a separate virtual environment (see [Installation](installation.md)).

## 5. `repo_guard check-files` Fails on Trailing Whitespace or Missing EOF Newline

- Strip trailing whitespace and ensure files end with a single LF newline (`\n`) before committing.
- Never place files larger than `10 MiB` (`10,485,760` bytes) or raw dataset extensions (`.csv`, `.pcap`, `.zip`, `.7z`) inside the repository.
