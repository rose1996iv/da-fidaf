"""Minimal read-only CLI for DA-FIDAF (`python -m dafidaf doctor`).

Exit codes:
    0 - Environment and configuration healthy.
    1 - Fatal configuration or Python compatibility error.
    2 - Valid configuration structure, but warnings or incomplete local setup exist.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO

from dafidaf.config import ConfigError, DafidafConfig, load_config

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_WARNING = 2


@dataclass(frozen=True, slots=True)
class ToolStatus:
    """Read-only diagnostic status for an external CLI tool."""

    name: str
    available: bool
    executable: str | None
    version: str | None
    note: str | None = None


def _run_readonly_cmd(args: Sequence[str], *, cwd: Path | None = None) -> tuple[int, str]:
    """Run a short read-only version/branch command without shell expansion."""
    try:
        completed = subprocess.run(
            list(args),
            cwd=str(cwd) if cwd is not None else None,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        output = (completed.stdout or completed.stderr or "").strip()
        first_line = output.splitlines()[0].strip() if output else ""
        return completed.returncode, first_line
    except (OSError, subprocess.SubprocessError) as exc:
        return 1, str(exc)


def _check_git(repo_root: Path) -> tuple[ToolStatus, str | None]:
    git_exe = shutil.which("git")
    if git_exe is None:
        return ToolStatus("git", False, None, None, "git not found on PATH"), None

    ver_code, ver_out = _run_readonly_cmd([git_exe, "--version"])
    version = ver_out if ver_code == 0 and ver_out else None

    branch: str | None = None
    if (repo_root / ".git").exists():
        b_code, b_out = _run_readonly_cmd(
            [git_exe, "symbolic-ref", "--short", "HEAD"],
            cwd=repo_root,
        )
        if b_code == 0 and b_out:
            branch = b_out
        else:
            b_code2, b_out2 = _run_readonly_cmd(
                [git_exe, "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=repo_root,
            )
            if b_code2 == 0 and b_out2:
                branch = b_out2

    return ToolStatus("git", True, git_exe, version), branch


def _find_gitleaks_executable(environ: Mapping[str, str]) -> tuple[str | None, str | None]:
    """Locate gitleaks on PATH or via Windows WinGet Links shim without assuming PATH refresh."""
    on_path = shutil.which("gitleaks")
    if on_path is not None:
        return on_path, None

    if os.name == "nt":
        local_app_data = environ.get("LOCALAPPDATA")
        if local_app_data:
            winget_shim = Path(local_app_data) / "Microsoft" / "WinGet" / "Links" / "gitleaks.exe"
            if winget_shim.is_file():
                return (
                    str(winget_shim),
                    "found via WinGet Links shim (not yet on current session PATH)",
                )

    return None, "gitleaks not found on PATH or WinGet Links shim"


def _check_gitleaks(environ: Mapping[str, str]) -> ToolStatus:
    exe, note = _find_gitleaks_executable(environ)
    if exe is None:
        return ToolStatus("gitleaks", False, None, None, note)

    code, out = _run_readonly_cmd([exe, "version"])
    if code == 0 and out:
        return ToolStatus("gitleaks", True, exe, out, note)
    return ToolStatus("gitleaks", False, exe, None, f"failed to query version: {out}")


def _check_sevenzip(config: DafidafConfig) -> ToolStatus:
    sz = config.paths.sevenzip_exe
    if sz.configured and sz.path is not None:
        if not sz.exists:
            return ToolStatus(
                "7-zip",
                False,
                str(sz.path),
                None,
                f"configured via {sz.source}, but file does not exist",
            )
        code, out = _run_readonly_cmd([str(sz.path)])
        version = out if code == 0 and out else "executable present"
        return ToolStatus("7-zip", True, str(sz.path), version, f"configured via {sz.source}")

    on_path = shutil.which("7z") or shutil.which("7zz")
    if on_path is not None:
        code, out = _run_readonly_cmd([on_path])
        version = out if code == 0 and out else "executable present"
        return ToolStatus(
            "7-zip",
            True,
            on_path,
            version,
            "found on PATH (not explicitly configured)",
        )

    return ToolStatus(
        "7-zip",
        False,
        None,
        None,
        "not configured (set DAFIDAF_SEVENZIP_EXE in .env if needed)",
    )


def run_doctor(
    *,
    repo_root: Path | None = None,
    environ: Mapping[str, str] | None = None,
    stream: TextIO | None = None,
) -> int:
    """Execute read-only environment and configuration diagnostics."""
    out = sys.stdout if stream is None else stream
    env_source = os.environ if environ is None else environ

    has_error = False
    has_warning = False

    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    py_ok = sys.version_info.major == 3 and sys.version_info.minor == 12
    if not py_ok:
        has_error = True

    out.write("DA-FIDAF Environment Doctor (Read-Only)\n")
    out.write("=" * 42 + "\n")
    out.write(
        f"Python:          {py_ver} "
        f"({'COMPATIBLE with 3.12.*' if py_ok else 'INCOMPATIBLE: requires 3.12.*'})\n"
    )

    try:
        config = load_config(repo_root=repo_root, environ=env_source)
    except ConfigError as exc:
        out.write(f"Configuration:   ERROR - {exc}\n")
        return EXIT_ERROR

    paths = config.paths
    status = config.status

    out.write(f"Repository Root: {paths.repo_root}\n")

    git_status, branch = _check_git(paths.repo_root)
    if git_status.available:
        branch_label = branch if branch is not None else "unknown / not a git repo"
        git_ver = git_status.version or "available"
        out.write(f"Git:             OK ({git_ver}) | branch: {branch_label}\n")
    else:
        has_warning = True
        out.write(f"Git:             MISSING ({git_status.note})\n")

    out.write(
        "Config Sources:  "
        f".env={'loaded' if status.dotenv_loaded else 'absent'}, "
        f"paths.local.yaml={'loaded' if status.local_yaml_loaded else 'absent'}, "
        f"paths.example.yaml={'loaded' if status.example_yaml_loaded else 'absent'}\n"
    )

    ds = paths.dataset_root
    if ds.configured:
        ds_state = "EXISTS" if ds.exists else "MISSING ON DISK"
        if not ds.exists:
            has_warning = True
        out.write(f"Dataset Root:    CONFIGURED ({ds.source}) -> {ds.path} [{ds_state}]\n")
    else:
        has_warning = True
        out.write(
            "Dataset Root:    UNCONFIGURED "
            "(set DAFIDAF_DATA_ROOT in .env or configs/paths.local.yaml)\n"
        )

    runs = paths.experiment_runs_dir
    runs_state = "EXISTS" if runs.exists else "not created yet"
    out.write(f"Runs Root:       CONFIGURED ({runs.source}) -> {runs.path} [{runs_state}]\n")

    gl = _check_gitleaks(env_source)
    if gl.available:
        note_suffix = f" ({gl.note})" if gl.note else ""
        out.write(f"Gitleaks:        OK ({gl.version}) -> {gl.executable}{note_suffix}\n")
    else:
        has_warning = True
        out.write(f"Gitleaks:        MISSING ({gl.note})\n")

    sz = _check_sevenzip(config)
    if sz.available:
        out.write(f"7-Zip:           OK ({sz.note}) -> {sz.executable}\n")
    else:
        if config.paths.sevenzip_exe.configured:
            has_warning = True
            out.write(f"7-Zip:           MISSING ({sz.note}) -> {sz.executable}\n")
        else:
            out.write(f"7-Zip:           UNCONFIGURED ({sz.note})\n")

    if status.warnings:
        has_warning = True
        out.write("\nWarnings:\n")
        for warn in status.warnings:
            out.write(f"  - {warn}\n")

    if has_error:
        out.write("\nResult: ERROR (exit code 1)\n")
        return EXIT_ERROR
    if has_warning:
        out.write("\nResult: WARNINGS / INCOMPLETE LOCAL SETUP (exit code 2)\n")
        return EXIT_WARNING

    out.write("\nResult: OK (exit code 0)\n")
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dafidaf",
        description="DA-FIDAF portable research framework CLI.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser(
        "doctor",
        help="Run read-only environment, path, and tooling diagnostics.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "doctor":
        return run_doctor()
    parser.error(f"Unknown command: {args.command}")
    return EXIT_ERROR
