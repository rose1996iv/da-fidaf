# Security Policy

## 1. Scope and Repository Status

**DA-FIDAF** is a private, offline PhD research framework for federated intrusion detection research. It is **not** production security software, and current Phase 3B / Phase 3B.2 experiments executed **Non-DP baselines only** without cryptographic Secure Aggregation.

## 2. Offensive Simulation Containment

Adversarial modules under `src/dafidaf/attacks/` (`label_flip`, `data_poisoning`, `backdoor`, `sign_flip`) exist solely to benchmark defensive attribution and Byzantine-robust aggregation in offline research simulations. They must never be repurposed against live networks or production systems.

## 3. Secret Hygiene and Data Governance

- Never commit `.env`, API keys, tokens, passwords, private keys, or machine-local credentials.
- Automated secret scanning is enforced via Gitleaks v8 (`.gitleaks.toml`) locally, in pre-commit/pre-push hooks (`.pre-commit-config.yaml`), and in GitHub Actions (`.github/workflows/secret-scan.yml`).
- Raw IoT datasets, PCAPs, and files exceeding `10 MiB` are blocked by `.gitignore` and `dafidaf.repo_guard`.

## 4. Reporting Security Issues

If a secret exposure, dependency vulnerability, or repository governance issue is discovered:

1. **Do not** reproduce raw secrets or credentials in issues, commit messages, or reports.
2. Report the file path and risk privately to the repository owner (formal security contact address pending private GitHub repository setup).
3. Block publication or pushes until the issue is remediated and re-verified with Gitleaks.
