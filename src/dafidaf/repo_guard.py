"""Read-only repository guard and cross-platform Gitleaks hook wrapper for DA-FIDAF.

This utility is invoked by pre-commit and pre-push hooks without modifying files.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

DEFAULT_MAX_BYTES = 10 * 1024 * 1024  # 10 MiB

BLOCKED_EXACT_NAMES: frozenset[str] = frozenset(
    {
        ".env",
        "paths.local.yaml",
    }
)

BLOCKED_DATASET_AND_ARTIFACT_SUFFIXES: frozenset[str] = frozenset(
    {
        ".zip",
        ".7z",
        ".rar",
        ".tar",
        ".tgz",
        ".gz",
        ".bz2",
        ".xz",
        ".pcap",
        ".pcapng",
        ".cap",
        ".parquet",
        ".feather",
        ".arrow",
        ".pt",
        ".pth",
        ".ckpt",
        ".safetensors",
        ".onnx",
        ".h5",
        ".hdf5",
        ".pkl",
        ".pickle",
        ".joblib",
        ".key",
        ".pem",
        ".p12",
        ".pfx",
    }
)

TEXT_CHECK_SUFFIXES: frozenset[str] = frozenset(
    {
        ".py",
        ".md",
        ".yaml",
        ".yml",
        ".toml",
        ".json",
        ".txt",
        ".sh",
        ".cfg",
        ".ini",
    }
)

TEXT_CHECK_EXACT_NAMES: frozenset[str] = frozenset(
    {
        ".gitignore",
        ".gitattributes",
        ".python-version",
        ".env.example",
    }
)


def check_file_policy(
    file_path: Path,
    *,
    max_bytes: int = DEFAULT_MAX_BYTES,
    repo_root: Path | None = None,
) -> list[str]:
    """Validate a single file against DA-FIDAF size, dataset, and formatting policies.

    Strictly read-only: never modifies the file.
    """
    violations: list[str] = []
    if not file_path.is_file():
        return violations

    rel_posix = (
        file_path.resolve().relative_to(repo_root.resolve()).as_posix()
        if repo_root is not None
        else file_path.as_posix()
    )
    name = file_path.name
    lower_name = name.lower()
    suffix = file_path.suffix.lower()

    if lower_name in BLOCKED_EXACT_NAMES or (
        lower_name.startswith(".env.") and lower_name != ".env.example"
    ):
        violations.append(f"{rel_posix}: blocked local/secret config file must not be committed")

    if suffix in BLOCKED_DATASET_AND_ARTIFACT_SUFFIXES:
        violations.append(
            f"{rel_posix}: blocked dataset/archive/checkpoint/key extension '{suffix}'"
        )

    if suffix == ".csv" and not rel_posix.startswith("manifests/"):
        violations.append(
            f"{rel_posix}: raw CSV files outside 'manifests/' must remain external to Git"
        )

    size_bytes = file_path.stat().st_size
    if size_bytes > max_bytes:
        size_mib = size_bytes / (1024 * 1024)
        limit_mib = max_bytes / (1024 * 1024)
        violations.append(
            f"{rel_posix}: file size {size_mib:.2f} MiB exceeds {limit_mib:.2f} MiB limit"
        )

    if suffix in TEXT_CHECK_SUFFIXES or name in TEXT_CHECK_EXACT_NAMES:
        raw_bytes = file_path.read_bytes()
        if raw_bytes:
            if not raw_bytes.endswith(b"\n"):
                violations.append(f"{rel_posix}: missing trailing newline at end of file")
            try:
                text = raw_bytes.decode("utf-8")
            except UnicodeDecodeError:
                violations.append(f"{rel_posix}: text file is not valid UTF-8")
            else:
                for lineno, line in enumerate(text.splitlines(), start=1):
                    if line.endswith((" ", "\t")):
                        violations.append(
                            f"{rel_posix}:{lineno}: trailing whitespace detected"
                        )
                        break

    return violations


def find_gitleaks_executable() -> str | None:
    """Locate gitleaks on PATH or via Windows WinGet Links shim."""
    on_path = shutil.which("gitleaks")
    if on_path:
        return on_path
    if os.name == "nt":
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            shim = Path(local_app_data) / "Microsoft" / "WinGet" / "Links" / "gitleaks.exe"
            if shim.is_file():
                return str(shim)
    return None


def _run_gitleaks(mode: str, config_path: Path) -> int:
    exe = find_gitleaks_executable()
    if exe is None:
        sys.stderr.write(
            "ERROR: gitleaks executable not found on PATH or WinGet Links shim.\n"
        )
        return 1

    if mode == "staged":
        cmd = [exe, "git", "--staged", "--redact", "--config", str(config_path), "."]
    elif mode == "dir":
        cmd = [exe, "dir", "--redact", "--config", str(config_path), "."]
    elif mode == "pre-push":
        has_head = (
            subprocess.run(
                ["git", "rev-parse", "--verify", "HEAD"],
                capture_output=True,
                check=False,
            ).returncode
            == 0
        )
        if has_head:
            cmd = [exe, "git", "--redact", "--config", str(config_path), "."]
        else:
            cmd = [exe, "dir", "--redact", "--config", str(config_path), "."]
    else:
        sys.stderr.write(f"ERROR: unsupported gitleaks mode '{mode}'.\n")
        return 1

    completed = subprocess.run(cmd, check=False)
    return completed.returncode


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="DA-FIDAF read-only repository guard.")
    sub = parser.add_subparsers(dest="action", required=True)

    check_p = sub.add_parser("check-files", help="Check files for size, dataset, and text rules.")
    check_p.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    check_p.add_argument("files", nargs="*")

    gl_p = sub.add_parser("gitleaks", help="Run Gitleaks using repo config.")
    gl_p.add_argument("--mode", choices=("staged", "dir", "pre-push"), required=True)
    gl_p.add_argument("--config", default=".gitleaks.toml")

    args = parser.parse_args(argv)

    if args.action == "check-files":
        root = Path.cwd().resolve()
        all_violations: list[str] = []
        for raw in args.files:
            p = Path(raw)
            if not p.is_absolute():
                p = root / p
            all_violations.extend(
                check_file_policy(p, max_bytes=args.max_bytes, repo_root=root)
            )
        if all_violations:
            for item in all_violations:
                sys.stderr.write(f"POLICY VIOLATION: {item}\n")
            return 1
        return 0

    if args.action == "gitleaks":
        return _run_gitleaks(args.mode, Path(args.config))

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
