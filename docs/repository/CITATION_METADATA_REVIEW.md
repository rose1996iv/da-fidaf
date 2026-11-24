# DA-FIDAF — Citation Metadata Review (`CITATION.cff`)

- **Review Date (UTC):** `2026-11-24`
- **Target File:** `CITATION.cff` (Untracked new file; not part of the 22 frozen Stage 7 staged files)
- **License File Status:** **Absent by Researcher Decision** (`0` `LICENSE*` files exist in repository; no `license:` key in `CITATION.cff`)
- **Review Verdict:** **PASS — VERIFIED CLEAN (ZERO INVENTED IDENTIFIERS)**

---

## 1. Current Verified `CITATION.cff` Content

```yaml
cff-version: 1.2.0
title: "DA-FIDAF: Drift-Aware Federated Intrusion Detection and Attribution Framework"
message: >-
  This is an active PhD research repository under experimental validation and
  development. No DOI, license, or formal publication venue has been assigned
  yet. Update publication identifiers once formally assigned.
type: software
version: "0.1.0"
date-released: "2026-11-24"
authors:
  - given-names: "Joseph"
abstract: >-
  A portable, reproducible PhD research framework for investigating drift-aware
  federated intrusion detection, multi-evidence drift-versus-attack attribution,
  and robust aggregation in heterogeneous IoT/IIoT networks under Non-IID data,
  concept drift, and adversarial threats. Current evaluated results cover
  Non-DP baselines on overlapping ToN-IoT windows using simulated logical
  gateways.
keywords:
  - federated-learning
  - intrusion-detection
  - iot-security
  - concept-drift
  - poisoning-attribution
  - robust-aggregation
```

---

## 2. Compliance Verification Matrix

| Check | Requirement | Observed Result | Status |
| --- | --- | --- | --- |
| **YAML Validity** | Clean `yaml.safe_load` parse | Valid YAML 1.2 mapping | **PASS** |
| **CFF Schema Version** | Valid Citation File Format `1.2.0` required keys (`cff-version`, `message`, `title`, `authors`) | All required keys present and properly typed | **PASS** |
| **Author Field** | Set exactly to `Joseph` without inventing a surname | `authors: [{given-names: "Joseph"}]` (valid CFF 1.2.0 person object with single given name) | **PASS** |
| **Invented Identifiers** | Zero invented surname, ORCID, email, DOI, institutional affiliation, funding, or publication venue | Confirmed absent | **PASS** |
| **License Handling** | No license selected; no `LICENSE` file created | `license:` field omitted; `0` `LICENSE*` files on disk | **PASS** |
| **Scope Accuracy** | Accurately reflects active PhD research, Non-DP baseline, overlapping ToN-IoT windows, simulated gateways | Accurately disclosed in `message` and `abstract` | **PASS** |
