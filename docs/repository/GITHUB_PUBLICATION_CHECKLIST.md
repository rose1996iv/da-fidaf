# DA-FIDAF — GitHub Private Repository Publication Checklist

> **Execution Policy:** Follow this checklist **only after** explicit researcher review and written authorization. No step below has been executed during local preparation.

---

## Phase 1 — Pre-Staging Researcher Approval

- [ ] Review `docs/repository/GIT_BASELINE_PRESERVATION_REPORT.md` and confirm the 22-file Stage 7 baseline (`84,102` bytes) is verified intact.
- [ ] Review `docs/repository/REPOSITORY_SECURITY_AUDIT.md` (`0` Gitleaks leaks, `0` raw datasets, `0` files `> 1 MiB`).
- [ ] Decide whether to apply the 3 proposed staged-file updates from `docs/repository/proposed_staged_updates/`:
  - [ ] Copy `README.proposed.md` -> `README.md`
  - [ ] Copy `gitignore.proposed` -> `.gitignore`
  - [ ] Copy `gitattributes.proposed` -> `.gitattributes`
- [ ] Update author name in `CITATION.cff` (and add `LICENSE` only once institutional ownership/licensing is confirmed).
- [ ] (Optional) Copy researcher's original draft architecture diagram files into `docs/architecture/figures/` and update `docs/architecture/figures/FIGURE_CATALOG.md`.
- [ ] (Optional) Build and preview MkDocs Material locally in an isolated `.venv-docs` environment:
  ```powershell
  python -m venv .venv-docs
  .venv-docs\Scripts\python.exe -m pip install -r requirements-docs.txt
  .venv-docs\Scripts\mkdocs.exe build --clean
  .venv-docs\Scripts\mkdocs.exe serve
  ```

---

## Phase 2 — Authorized Commit Preparation (Local Only)

- [ ] Re-run full local verification gate:
  ```powershell
  $env:PYTHONDONTWRITEBYTECODE = "1"
  .venv\Scripts\ruff.exe check src tests --no-cache
  .venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests
  gitleaks dir --redact --config .gitleaks.toml .
  ```
- [ ] Decide commit strategy:
  - **Option A (Two-commit history preserving Stage 7 verbatim):** Commit the existing 22 staged files first (`git commit -m "chore: initial portable DA-FIDAF Stage 7 baseline"`), then apply approved updates and stage Phases 1–3B.2 + documentation/CI in a second commit.
  - **Option B (Single initial commit):** Apply approved updates, stage all approved files (`git add ...`), inspect `git status` and `git diff --cached --stat`, confirm `.env` and `site/` are NOT staged, run `gitleaks git --staged --redact --config .gitleaks.toml .`, and commit.

---

## Phase 3 — Authorized Private GitHub Creation & First Push

- [ ] Create **Private** GitHub repository named `da-fidaf` (via GitHub Web UI or authenticated `gh repo create da-fidaf --private` without initializing remote README/license).
- [ ] Add remote `origin` (`git remote add origin <PRIVATE_REPO_URL>`).
- [ ] Verify pre-push checks (`gitleaks git --redact --config .gitleaks.toml .`, `pytest tests/unit`).
- [ ] Push `main` (`git push -u origin main`).
- [ ] Verify all 3 GitHub Actions workflows (`ci-tests-and-lint.yml`, `docs-build.yml`, `secret-scan.yml`) pass on GitHub Actions.
- [ ] Create the 22 canonical labels from `docs/repository/GITHUB_PROJECT_CONFIGURATION.md` and configure branch protection on `main`.
