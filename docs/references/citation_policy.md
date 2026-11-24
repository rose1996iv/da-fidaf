# Citation Policy

## 1. Citing This Software Repository

Machine-readable citation metadata is maintained in the root `CITATION.cff` file. Because this repository is an active, private PhD research artifact without an assigned DOI or finalized license, **do not invent a DOI, ORCID, institutional endorsement, or publication venue**. Update `CITATION.cff` once a preprint, thesis chapter, or peer-reviewed paper is formally published.

---

## 2. Mandatory Third-Party Dataset Citations

Any publication using DA-FIDAF experimental protocols or results **must** cite the underlying dataset authors:

- **ToN-IoT:** Moustafa (2021), *Sustainable Cities and Society*, 72, 102994.
- **CICIoT2023 (when audited/used):** Neto et al. (2023), *Sensors*, 23(13), 5941.
- **Edge-IIoTset (when audited/used):** Ferrag et al. (2022), *IEEE Access*, 10, 40281–40306.

See `docs/references/bibliography.bib` for verified BibTeX entries.

---

## 3. Responsible Reporting of DA-FIDAF Results

When referencing Phase 3B or Phase 3B.2 results, always disclose:

- Non-DP baseline status (`dp_enabled=False`, `secure_aggregation_active=False`).
- Simulated logical gateway topology (`K=10`).
- Overlap between ToN-IoT windows W1 and W3 ($\text{W1} \subset \text{W3}$).
- Exact paired Student-$t$ ($df=4$) confidence intervals for `n=5` seed comparisons.
- Negative net remediation outcome for experimental `E3 v2` (`client_val_loss_delta`) and benign-client over-quarantine in `E6 v2`.
