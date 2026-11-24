## Summary

- Concise description of changes and linked issue / gap ID (e.g., `GAP-02`, `GAP-03`).

## Research Integrity & Safety Checklist

- [ ] No raw datasets, PCAP/PCAPNG files, archives, `.env`, secrets, or files `> 10 MiB` are included.
- [ ] Historical Phase 1–3B.2 reports and external experiment artifacts remain unmodified.
- [ ] Experimental claims accurately disclose Non-DP scope, simulated logical gateways, overlapping W1/W3 windows, negative findings, and Student-$t$ ($df=4$) CIs where applicable.
- [ ] Experiment E5 (`HOLD`), formal DP/SecAgg claims, and unimplemented architectures (`1D-CNN / TCN`) are not misrepresented as verified.

## Verification Executed Locally

- [ ] `ruff check src tests --no-cache` passed (`exit 0`).
- [ ] `python -m pytest -q -p no:cacheprovider tests` passed (`exit 0`).
- [ ] `python -m dafidaf.repo_guard check-files <changed_files>` passed (`exit 0`).
- [ ] `gitleaks dir --redact --config .gitleaks.toml .` reported `0` leaks.
- [ ] Documentation links / `mkdocs build` checked (if `docs/` or `mkdocs.yml` changed).
