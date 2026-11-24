# Contributing to DA-FIDAF

DA-FIDAF is an active **private PhD research repository**. External public contributions are not currently solicited until research validation, methodology alignment, and licensing are finalized.

## Internal Research & Engineering Standards

All changes proposed within this repository must adhere to:

1. **Zero Raw Data or Secrets in Git:** Never add raw IoT datasets, PCAP/PCAPNG files, archives, experiment output directories, `.env` files, API keys, tokens, or credentials.
2. **Scientific Integrity:** Never fabricate, interpolate, or silently alter measured experimental results. Clearly distinguish draft conceptual diagrams, synthetic smoke tests, simulated logical gateways, and real-dataset findings.
3. **Preserve Historical Artifacts:** Do not overwrite historical Phase 1–3B.2 reports or original external experiment outputs under `<DAFIDAF_RUNS_ROOT>`.
4. **Code Quality & Verification:** Before requesting review, run:
   - `ruff check src tests --no-cache`
   - `python -m pytest -q -p no:cacheprovider tests`
   - `python -m dafidaf.repo_guard check-files <changed_files>`
   - `gitleaks dir --redact --config .gitleaks.toml .`
5. **Explicit Authorization Gates:** Do not execute Experiment E5 (`HOLD`), claim formal DP/SecAgg deployment guarantees, or start Phase 4 architectural changes without explicit researcher authorization.
6. **Pull Requests & Issues:** Use the templates under `.github/ISSUE_TEMPLATE/` and `.github/PULL_REQUEST_TEMPLATE.md`.
