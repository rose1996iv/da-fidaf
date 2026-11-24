# DA-FIDAF — Git Baseline Preservation Report

- **Repository:** `da-fidaf`
- **Baseline Captured (UTC):** `2026-11-24T18:13:00Z`
- **External Machine-Readable Manifest:** `git_baseline_manifest.json` (stored outside Git under `<DAFIDAF_RUNS_ROOT>/repository-preparation/`)
- **Preservation Status:** **VERIFIED INTACT (100% PRESERVED)**

---

## 1. Captured Stage 7 Git Baseline Summary

| Metric | Verified Value | Policy Requirement | Status |
| --- | --- | --- | --- |
| Symbolic `HEAD` | `refs/heads/main` (unborn) | Branch `main` | **PASS** |
| Total Commits | `0` | `0` (no commit created) | **PASS** |
| Configured Remotes | `0` | `0` (no remote created) | **PASS** |
| Staged File Count | `22` | Exactly `22` | **PASS** |
| Total Staged Blob Bytes | `84,102` | Exactly `84,102` | **PASS** |
| Unstaged Diffs vs. Staged Index | `0` | `0` (no staged file modified on disk) | **PASS** |

---

## 2. Exact Staged Index Inventory (22 Frozen Files)

| # | Mode | Git Blob SHA-1 | Bytes | Repository Path |
| --- | --- | --- | ---: | --- |
| 1 | `100644` | `ed70d1cca6b25eac92b7618e03e91d485e5f8423` | `267` | `.env.example` |
| 2 | `100644` | `27412ff5512d17c01652f35506783271ea916d17` | `626` | `.gitattributes` |
| 3 | `100644` | `2c239cb0709c857430424b5fde39b78cd498b712` | `1,265` | `.gitignore` |
| 4 | `100644` | `554afbe9f1271b98dab72a64111cd86878bcb989` | `478` | `.gitleaks.toml` |
| 5 | `100644` | `c28d66f16c06ef2729cb6f446325f661fe0b7505` | `2,048` | `.pre-commit-config.yaml` |
| 6 | `100644` | `e4fba2183587225f216eeada4c78dfab6b2e65f5` | `5` | `.python-version` |
| 7 | `100644` | `44a4ff1dc58a95d7530647065c92eaec315b2e83` | `2,733` | `README.md` |
| 8 | `100644` | `67516d427242e1c610d27837e01ddb0f22616ac7` | `677` | `configs/paths.example.yaml` |
| 9 | `100644` | `01dfe29eabd9f4a6d55fceb0e0cb43717259787c` | `1,795` | `docs/PROJECT_STATUS.md` |
| 10 | `100644` | `bcff1d6ff659169cd6299c9f8ddb4b491d38e763` | `3,417` | `docs/REPOSITORY_POLICY.md` |
| 11 | `100644` | `8c3b4c69b9cefa414f0e4c45cea5ebf9477b0b43` | `3,734` | `docs/architecture/PORTABLE_ARCHITECTURE.md` |
| 12 | `100644` | `6343d61b417b74bb79e76e036330329ad23dd8c5` | `768` | `pyproject.toml` |
| 13 | `100644` | `46a997829003602c035e5f42b0390c27cdd9853c` | `442` | `src/dafidaf/__init__.py` |
| 14 | `100644` | `01546c2357a48997b99b8c0dd0011ad645a29c23` | `196` | `src/dafidaf/__main__.py` |
| 15 | `100644` | `ea0df79f5496e1ecf5cafab7979060c81fc7e387` | `9,048` | `src/dafidaf/cli.py` |
| 16 | `100644` | `3771e30458c137f412ed262435574ba01ec53f92` | `6,845` | `src/dafidaf/config.py` |
| 17 | `100644` | `cda31bbafbec1a770ab5b3fdb701843e8fffacc1` | `9,677` | `src/dafidaf/paths.py` |
| 18 | `100644` | `62f8c0b2556d01d9afbf77c548369fca98aee976` | `6,731` | `src/dafidaf/repo_guard.py` |
| 19 | `100644` | `09b6984c1e51d7548b19c035071a2750f429e322` | `6,602` | `tests/unit/test_config_and_paths.py` |
| 20 | `100644` | `35805095d675688549ef5f2ddb4de95b25986078` | `2,801` | `tests/unit/test_doctor_cli.py` |
| 21 | `100644` | `8193500f1375668ba314f7d496b6e300bc4f2e9a` | `2,199` | `tests/unit/test_repo_guard.py` |
| 22 | `100644` | `f795917607ef29665ca7b895007f7741f90f7d66` | `21,748` | `uv.lock` |
| **Total** | — | **22 immutable blobs** | **`84,102`** | — |

---

## 3. Handling of Staged Files Requiring Preparation Updates

Because repository preparation rules strictly prohibit modifying any of the original 22 staged files without explicit researcher authorization, the following **3 staged files** were **NOT modified in-place**. Instead, complete ready-to-apply proposed replacements were placed under `docs/repository/proposed_staged_updates/`:

| Original Staged File (Unmodified) | Proposed Replacement Path | Reason for Proposed Update | Action Required Before Publication |
| --- | --- | --- | --- |
| `README.md` (`44a4ff1d...`) | `docs/repository/proposed_staged_updates/README.proposed.md` | Replaces Stage 2 scaffolding overview with full 20-section PhD research landing page reflecting Phase 1–3B.2 results, limitations, and disclosures. | Researcher reviews and explicitly approves applying over `README.md`. |
| `.gitignore` (`2c239cb0...`) | `docs/repository/proposed_staged_updates/gitignore.proposed` | Preserves all existing ignore rules and adds `site/` (MkDocs Material build directory) plus local documentation preview artifacts. | Researcher reviews and explicitly approves applying over `.gitignore`. |
| `.gitattributes` (`27412ff5...`) | `docs/repository/proposed_staged_updates/gitattributes.proposed` | Preserves all existing LF/binary rules and adds explicit rules for `*.svg`, `*.eps`, `*.bib`, and `*.cff`. | Researcher reviews and explicitly approves applying over `.gitattributes`. |

---

## 4. Prohibited Git Commands Confirmed Not Executed

During local repository preparation, none of the following commands were executed:

- `git add`, `git reset`, `git restore`, `git checkout`, `git clean`
- `git commit`, `git push`, `git remote add`, `git branch`, `gh repo create`

All newly created documentation, metadata, and CI files remain strictly untracked in the working tree.
