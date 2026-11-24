"""Unit tests for the read-only repository guard (large-file, dataset, and formatting checks)."""

from __future__ import annotations

from pathlib import Path

from dafidaf.repo_guard import DEFAULT_MAX_BYTES, check_file_policy


def test_large_file_exceeding_threshold_is_blocked(tmp_path: Path) -> None:
    oversized = tmp_path / "artifact.bin"
    oversized.write_bytes(b"0" * 2048)

    violations = check_file_policy(oversized, max_bytes=1024, repo_root=tmp_path)
    assert any("exceeds" in v for v in violations)


def test_file_within_threshold_is_allowed(tmp_path: Path) -> None:
    small_doc = tmp_path / "notes.md"
    small_doc.write_text("# Clean Markdown\n", encoding="utf-8")

    violations = check_file_policy(small_doc, max_bytes=DEFAULT_MAX_BYTES, repo_root=tmp_path)
    assert violations == []


def test_blocked_dataset_and_secret_extensions(tmp_path: Path) -> None:
    blocked_files = [
        tmp_path / ".env",
        tmp_path / "capture.pcap",
        tmp_path / "archive.zip",
        tmp_path / "raw_data.csv",
        tmp_path / "model.pt",
        tmp_path / "private.pem",
    ]
    for path in blocked_files:
        path.write_bytes(b"dummy\n")
        violations = check_file_policy(path, repo_root=tmp_path)
        assert violations, f"Expected policy violation for {path.name}"


def test_curated_manifest_csv_is_allowed(tmp_path: Path) -> None:
    manifest_dir = tmp_path / "manifests"
    manifest_dir.mkdir()
    summary_csv = manifest_dir / "summary.csv"
    summary_csv.write_text("dataset,status\nexample,ok\n", encoding="utf-8")

    violations = check_file_policy(summary_csv, repo_root=tmp_path)
    assert violations == []


def test_trailing_whitespace_and_eof_detected_without_modifying_file(tmp_path: Path) -> None:
    sample = tmp_path / "sample.py"
    original = "x = 1   \ny = 2"
    sample.write_text(original, encoding="utf-8")

    violations = check_file_policy(sample, repo_root=tmp_path)
    assert any("trailing whitespace" in v for v in violations)
    assert any("missing trailing newline" in v for v in violations)
    # Strictly read-only: file must remain unmodified
    assert sample.read_text(encoding="utf-8") == original
