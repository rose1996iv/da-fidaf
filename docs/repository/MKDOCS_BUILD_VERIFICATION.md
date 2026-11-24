# DA-FIDAF — Isolated MkDocs Material Build Verification

- **Environment:** Isolated `I:\Projects\da-fidaf\.venv-docs` (created from base Python `3.12.10`; core `.venv`, `pyproject.toml`, and `uv.lock` completely untouched; zero global packages installed).
- **Requirements File:** `requirements-docs.txt`
- **Installed Versions (`PIP_INSTALL_EXIT=0`):**
  - `mkdocs`: `1.6.1`
  - `mkdocs-material`: `9.7.7`
  - `pymdown-extensions`: `10.21.3`
- **Output Directory:** `site/` *(local verification artifact only; excluded from Git commits via `.venv-docs/` & `site/` rules in `gitignore.proposed`)*

---

## 1. Build History

| Run | Timestamp (UTC) | Command | Nav Entries | Exit Code | Warnings | Errors | Notes |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| **Run 1 (Initial Diagnostic)** | `2026-11-24T19:52:46Z` | `.venv-docs\Scripts\mkdocs.exe build --clean --strict` | `91` | `1` | `25` | `0` | All `25` warnings originated solely from root-relative links inside temporary draft `docs/repository/proposed_staged_updates/README.proposed.md`; `0` broken links in actual docs pages. |
| **Run 2 (Post `exclude_docs`)** | `2026-11-24T19:55:02Z` | `.venv-docs\Scripts\mkdocs.exe build --clean --strict` | `97` | **`0`** | **`0`** | **`0`** | Added `exclude_docs: repository/proposed_staged_updates/` and 6 pre-publication review reports; `183` files (`12.81 MiB`) built cleanly in `3.17s`. |
| **Run 3 (Final Approval Package)** | Verified in Final Verification Pass | `.venv-docs\Scripts\mkdocs.exe build --clean --strict` | `98` | **`0`** | **`0`** | **`0`** | Re-verified after adding `FINAL_CONFIGURATION_APPROVAL_SUMMARY.md` to `mkdocs.yml` and updating diff/checklist reports. |

> **Upstream Notice (Informational Only):** Material for MkDocs `9.7.7` prints an informational banner regarding future MkDocs 2.0 changes; `requirements-docs.txt` pins `mkdocs>=1.6.1,<2.0` and `mkdocs-material>=9.5.49,<10.0`.
