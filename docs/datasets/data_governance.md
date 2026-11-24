# Data Governance Policy

DA-FIDAF enforces strict separation between version-controlled research code/documentation and immutable external data artifacts.

---

## Mandatory Governance Rules

1. **External Storage Only:** Raw datasets, extracted CSV shards, archives (`.zip`, `.7z`, `.rar`, `.tar*`), packet captures (`.pcap`, `.pcapng`), and raw experiment output directories (`<DAFIDAF_RUNS_ROOT>`) must **never** enter Git.
2. **Read-Only Immutability:** Source files under `DAFIDAF_DATA_ROOT` are strictly read-only. Never modify, extract in-place, or repair damaged source archives inside the dataset root.
3. **Automated Guardrails:** Both `.gitignore` and `python -m dafidaf.repo_guard check-files --max-bytes 10485760` block blocked dataset/secret extensions and files exceeding `10 MiB` (`10,485,760` bytes).
4. **No Private or Unverified Sharing:** Do not redistribute third-party IoT datasets or publish private supervisor/institutional documents without verifying ownership and licensing permissions.
5. **Verified Metadata Only:** Checksums, row counts, and split statistics written into `manifests/` or documentation must come exclusively from measured execution on actual files—never estimated or fabricated.

See [Repository Policy](../REPOSITORY_POLICY.md) and [Repository Security Audit](../repository/REPOSITORY_SECURITY_AUDIT.md).
