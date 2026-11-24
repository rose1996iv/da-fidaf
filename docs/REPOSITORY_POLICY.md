# DA-FIDAF Repository Policy

These rules apply permanently to all code, configurations, manifests, documentation, and experiments in the DA-FIDAF repository.

## 1. Raw Datasets Must Never Be Committed

- Raw datasets, archives (`.zip`, `.7z`, `.tar*`), packet captures (`.pcap`, `.pcapng`), large tabular files (`.csv`, `.parquet`), and heavy intermediate artifacts must remain outside the Git repository.
- Original dataset files are strictly immutable and must never be silently modified, overwritten, or replaced.

## 2. Verified Provenance and Checksums Only

- Dataset provenance records, file sizes, and SHA-256 checksums may be written to `manifests/` **only after actual verification** on the target files.
- Never fabricate, estimate, or copy unverified metadata or checksums.

## 3. Zero Secrets in Git

- Never stage or commit `.env`, API keys, tokens, passwords, private keys, or sensitive local configuration.
- Machine-specific paths and credentials must remain strictly in Git-ignored local files (`.env`, `configs/paths.local.yaml`).
- Tracked templates (`.env.example`, `configs/paths.example.yaml`) must contain placeholders only.

## 4. Controlled GitHub Publishing & Safe Git Workflow

- No automated `git push`, remote creation, or publishing is permitted.
- Every commit and push must be preceded by explicit `git status`, `git diff --cached`, and secret-scanning verification.
- Repository-local Git hooks (`pre-commit` and `pre-push`) are managed via `.pre-commit-config.yaml` and installed into `.git/hooks/` without modifying global `core.hooksPath`.

## 5. Large-File Restrictions

- Files exceeding **10 MiB (`10,485,760` bytes)** are blocked from entering Git by both `check-added-large-files` (`--maxkb=10240`) and `dafidaf.repo_guard`.
- Git LFS is **not** used for raw datasets or large model artifacts.
- Any exception to the 10 MiB limit requires explicit prior review and must never permit raw datasets, archives, or secrets into version control.

## 6. Automated Security & Quality Checks (Gitleaks, Pre-Commit, Pre-Push)

- **Gitleaks (`.gitleaks.toml`):** Extends all official default v8 secret-detection rules. `.env` is never allowlisted as secret-free; it remains Git-ignored and untracked.
  - Directory scan: `gitleaks dir --redact --config .gitleaks.toml .`
  - Staged scan: `gitleaks git --staged --redact --config .gitleaks.toml .`
- **Pre-commit hooks:** Read-only YAML/TOML/JSON syntax validation, 10 MiB large-file check, private-key detection, blocked dataset/secret extension check, trailing-whitespace & EOF-newline check, Ruff lint check, and Gitleaks staged secret scan.
- **Pre-push hooks:** Gitleaks repository scan and `pytest` unit test suite.
- **Emergency bypass policy:** Bypassing hooks (`git commit --no-verify` or `git push --no-verify`) is strongly discouraged and permitted only for verified emergencies, with the justification documented explicitly in the commit message and followed by an immediate security audit.

## 7. Reproducibility and Portability

- All experiments must be driven by version-controlled configuration files recording random seeds, dataset versions, preprocessing settings, model parameters, and evaluation criteria.
- Source code and tracked configs must avoid hardcoded machine-specific absolute paths and drive letters, using `pathlib.Path` and centralized environment/config resolution for Windows and Linux portability.
