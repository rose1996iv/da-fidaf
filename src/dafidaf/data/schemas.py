"""Canonical feature metadata, label ontology, and E5 cross-dataset governance."""

from __future__ import annotations

from dataclasses import dataclass

UNKNOWN_ATTACK_LABEL = "unknown_attack"


class E5OntologyBlockedError(RuntimeError):
    """Raised when unvalidated cross-dataset merging (E5) is attempted."""


@dataclass(frozen=True, slots=True)
class FeatureSpec:
    """Canonical semantic specification for a single feature."""

    name: str
    dtype: str
    description: str
    source_column: str
    unit: str | None
    missing_policy: str
    allowed_transform: str
    datasets: tuple[str, ...]
    leakage_risk: str


@dataclass(frozen=True, slots=True)
class LabelOntology:
    """Explicit label normalization ontology with unknown-class safety."""

    version: str
    dataset_id: str
    benign_tokens: frozenset[str]
    coarse_map: dict[str, str]
    verified_for_e5: bool = False

    def to_binary(self, raw_label: str) -> int:
        token = raw_label.strip().lower()
        if not token or token in ("-", "nan", "null", "none", "na", "n/a", "?"):
            raise ValueError(f"Missing or invalid raw label: {raw_label!r}")
        return 0 if token in self.benign_tokens else 1

    def to_coarse(self, raw_label: str) -> str:
        token = raw_label.strip().lower()
        if not token or token in ("-", "nan", "null", "none", "na", "n/a", "?"):
            raise ValueError(f"Missing or invalid raw label: {raw_label!r}")
        if token in self.benign_tokens:
            return "benign"
        return self.coarse_map.get(token, UNKNOWN_ATTACK_LABEL)


TON_IOT_LABEL_ONTOLOGY = LabelOntology(
    version="1.0.0",
    dataset_id="ToN-IoT",
    benign_tokens=frozenset({"normal", "benign", "0"}),
    coarse_map={
        "normal": "benign",
        "ddos": "dos_ddos",
        "dos": "dos_ddos",
        "scanning": "recon_scan",
        "injection": "web_injection",
        "xss": "web_injection",
        "mitm": "mitm_spoofing",
        "password": "credential_attack",
        "backdoor": "malware_backdoor",
        "ransomware": "malware_ransomware",
    },
    verified_for_e5=False,
)

CICIOT2023_LABEL_ONTOLOGY = LabelOntology(
    version="1.0.0",
    dataset_id="CICIoT2023",
    benign_tokens=frozenset({"benign", "normal", "0"}),
    coarse_map={
        "benign": "benign",
        "ddos-icmp_flood": "dos_ddos",
        "ddos-udp_flood": "dos_ddos",
        "ddos-tcp_flood": "dos_ddos",
        "ddos-syn_flood": "dos_ddos",
        "dos-udp_flood": "dos_ddos",
        "dos-tcp_flood": "dos_ddos",
        "dos-syn_flood": "dos_ddos",
        "mirai-greeth_flood": "botnet_mirai",
        "mirai-udpplain": "botnet_mirai",
        "mirai-greip_flood": "botnet_mirai",
        "recon-portscan": "recon_scan",
        "recon-osscan": "recon_scan",
        "vulnerabilityscan": "recon_scan",
        "mitm-arpspoofing": "mitm_spoofing",
        "dns_spoofing": "mitm_spoofing",
        "dictionarybruteforce": "credential_attack",
        "backdoor_malware": "malware_backdoor",
        "xss": "web_injection",
        "sqlinjection": "web_injection",
    },
    verified_for_e5=False,
)

EDGE_IIOT_LABEL_ONTOLOGY = LabelOntology(
    version="1.0.0",
    dataset_id="Edge-IIoTset",
    benign_tokens=frozenset({"normal", "benign", "0"}),
    coarse_map={
        "normal": "benign",
        "ddos_udp": "dos_ddos",
        "ddos_icmp": "dos_ddos",
        "ddos_http": "dos_ddos",
        "ddos_tcp": "dos_ddos",
        "port_scanning": "recon_scan",
        "vulnerability_scanner": "recon_scan",
        "fingerprinting": "recon_scan",
        "sql_injection": "web_injection",
        "xss": "web_injection",
        "uploading": "web_injection",
        "mitm": "mitm_spoofing",
        "password": "credential_attack",
        "backdoor": "malware_backdoor",
        "ransomware": "malware_ransomware",
    },
    verified_for_e5=False,
)


TON_IOT_NUMERIC_FEATURES: tuple[FeatureSpec, ...] = (
    FeatureSpec(
        "duration",
        "float",
        "Connection duration",
        "duration",
        "seconds",
        "median_train_only",
        "robust_scale",
        ("ToN-IoT",),
        "low",
    ),
    FeatureSpec(
        "src_bytes",
        "float",
        "Originator payload bytes",
        "src_bytes",
        "bytes",
        "median_train_only",
        "robust_scale",
        ("ToN-IoT",),
        "low",
    ),
    FeatureSpec(
        "dst_bytes",
        "float",
        "Responder payload bytes",
        "dst_bytes",
        "bytes",
        "median_train_only",
        "robust_scale",
        ("ToN-IoT",),
        "low",
    ),
    FeatureSpec(
        "missed_bytes",
        "float",
        "Missed content gap bytes",
        "missed_bytes",
        "bytes",
        "median_train_only",
        "robust_scale",
        ("ToN-IoT",),
        "low",
    ),
    FeatureSpec(
        "src_pkts",
        "float",
        "Originator packet count",
        "src_pkts",
        "packets",
        "median_train_only",
        "robust_scale",
        ("ToN-IoT",),
        "low",
    ),
    FeatureSpec(
        "src_ip_bytes",
        "float",
        "Originator IP bytes",
        "src_ip_bytes",
        "bytes",
        "median_train_only",
        "robust_scale",
        ("ToN-IoT",),
        "low",
    ),
    FeatureSpec(
        "dst_pkts",
        "float",
        "Responder packet count",
        "dst_pkts",
        "packets",
        "median_train_only",
        "robust_scale",
        ("ToN-IoT",),
        "low",
    ),
    FeatureSpec(
        "dst_ip_bytes",
        "float",
        "Responder IP bytes",
        "dst_ip_bytes",
        "bytes",
        "median_train_only",
        "robust_scale",
        ("ToN-IoT",),
        "low",
    ),
    FeatureSpec(
        "http_request_body_len",
        "float",
        "HTTP request body size",
        "http_request_body_len",
        "bytes",
        "median_train_only",
        "robust_scale",
        ("ToN-IoT",),
        "low",
    ),
    FeatureSpec(
        "http_response_body_len",
        "float",
        "HTTP response body size",
        "http_response_body_len",
        "bytes",
        "median_train_only",
        "robust_scale",
        ("ToN-IoT",),
        "low",
    ),
)


def assert_cross_dataset_ontology_ready(ontologies: tuple[LabelOntology, ...]) -> None:
    """Block E5 cross-dataset merging unless all ontologies are formally validated."""
    unverified = [o.dataset_id for o in ontologies if not o.verified_for_e5]
    if unverified:
        raise E5OntologyBlockedError(
            "E5 cross-dataset merging is HOLD: semantic feature/label ontology is not "
            f"validated for datasets: {', '.join(unverified)}. "
            "Do not merge datasets merely because column names match."
        )
