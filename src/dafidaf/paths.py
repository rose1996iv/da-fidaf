"""Portable, read-only path resolution for DA-FIDAF.

Precedence order (highest to lowest):
1. Environment variables (DAFIDAF_DATA_ROOT, DAFIDAF_RUNS_ROOT, DAFIDAF_SEVENZIP_EXE)
2. Local YAML configuration (configs/paths.local.yaml)
3. Example YAML configuration (configs/paths.example.yaml)
4. Safe repository-relative defaults (for repo-local paths only)

This module never creates directories, never hardcodes machine-specific drive
letters, and clearly distinguishes configured paths from paths that exist.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath

ENV_DATA_ROOT = "DAFIDAF_DATA_ROOT"
ENV_RUNS_ROOT = "DAFIDAF_RUNS_ROOT"
ENV_SEVENZIP_EXE = "DAFIDAF_SEVENZIP_EXE"

ALLOWED_ENV_KEYS: frozenset[str] = frozenset(
    {
        ENV_DATA_ROOT,
        ENV_RUNS_ROOT,
        ENV_SEVENZIP_EXE,
    }
)

_WINDOWS_DRIVE_RE = re.compile(r"^[A-Za-z]:[\\/]")
_PLACEHOLDER_RE = re.compile(r"^<[^>]+>$")


@dataclass(frozen=True, slots=True)
class ResolvedPath:
    """Represents a configured or unconfigured path and its read-only existence state."""

    name: str
    raw_value: str | None
    path: Path | None
    source: str
    configured: bool
    exists: bool
    is_dir: bool
    is_file: bool


@dataclass(frozen=True, slots=True)
class ProjectPaths:
    """Resolved portable paths for the DA-FIDAF workspace."""

    repo_root: Path
    dataset_root: ResolvedPath
    raw_datasets_dir: ResolvedPath
    processed_datasets_dir: ResolvedPath
    manifest_dir: ResolvedPath
    experiment_runs_dir: ResolvedPath
    sevenzip_exe: ResolvedPath


def is_placeholder_value(value: str | None) -> bool:
    """Return True if a config value is empty, whitespace, or an angle-bracket placeholder."""
    if value is None:
        return True
    stripped = value.strip()
    if not stripped:
        return True
    return bool(_PLACEHOLDER_RE.match(stripped))


def is_windows_absolute(raw: str) -> bool:
    """Detect Windows drive-letter or UNC absolute paths on any host OS."""
    return bool(_WINDOWS_DRIVE_RE.match(raw)) or raw.startswith("\\\\")


def normalize_path(raw: str, *, base_dir: Path | None = None) -> Path:
    """Convert a raw string path into a portable pathlib.Path without creating directories.

    - Recognizes POSIX absolute paths and Windows drive/UNC paths.
    - Expands user home (~).
    - Resolves relative paths against base_dir when provided.
    """
    cleaned = raw.strip()
    if is_windows_absolute(cleaned):
        # Preserve Windows path semantics via PureWindowsPath -> Path
        return Path(str(PureWindowsPath(cleaned)))

    candidate = Path(cleaned).expanduser()
    if candidate.is_absolute():
        return candidate
    if base_dir is not None:
        return base_dir / candidate
    return candidate


def _make_resolved_path(
    *,
    name: str,
    raw_value: str | None,
    source: str,
    base_dir: Path | None,
) -> ResolvedPath:
    if is_placeholder_value(raw_value):
        return ResolvedPath(
            name=name,
            raw_value=None,
            path=None,
            source="unconfigured",
            configured=False,
            exists=False,
            is_dir=False,
            is_file=False,
        )

    assert raw_value is not None
    resolved = normalize_path(raw_value, base_dir=base_dir)
    try:
        exists = resolved.exists()
        is_dir = resolved.is_dir() if exists else False
        is_file = resolved.is_file() if exists else False
    except OSError:
        exists = False
        is_dir = False
        is_file = False

    return ResolvedPath(
        name=name,
        raw_value=raw_value.strip(),
        path=resolved,
        source=source,
        configured=True,
        exists=exists,
        is_dir=is_dir,
        is_file=is_file,
    )


def find_repo_root(start: Path | None = None) -> Path:
    """Locate the DA-FIDAF repository root by walking upward for pyproject.toml or .git."""
    candidates: list[Path] = []
    if start is not None:
        candidates.append(start.resolve())
    else:
        candidates.append(Path.cwd().resolve())
        candidates.append(Path(__file__).resolve().parent)

    for origin in candidates:
        current = origin if origin.is_dir() else origin.parent
        for directory in (current, *current.parents):
            if (directory / "pyproject.toml").is_file() or (directory / ".git").exists():
                return directory

    return (start or Path.cwd()).resolve()


def _select_value(
    *,
    env_key: str | None,
    yaml_key: str,
    env: Mapping[str, str],
    local_paths: Mapping[str, str] | None,
    example_paths: Mapping[str, str] | None,
    default_value: str | None = None,
) -> tuple[str | None, str]:
    """Select the highest-precedence non-placeholder value and its source label."""
    if env_key is not None:
        env_val = env.get(env_key)
        if not is_placeholder_value(env_val):
            return env_val, "env"

    if local_paths is not None:
        local_val = local_paths.get(yaml_key)
        if not is_placeholder_value(local_val):
            return local_val, "local_config"

    if example_paths is not None:
        example_val = example_paths.get(yaml_key)
        if not is_placeholder_value(example_val):
            return example_val, "example_config"

    if default_value is not None:
        return default_value, "default"

    return None, "unconfigured"


def resolve_paths(
    *,
    repo_root: Path,
    env: Mapping[str, str],
    local_paths: Mapping[str, str] | None = None,
    example_paths: Mapping[str, str] | None = None,
) -> ProjectPaths:
    """Resolve all DA-FIDAF paths without touching or creating any directories."""
    root = repo_root.resolve()

    data_raw, data_src = _select_value(
        env_key=ENV_DATA_ROOT,
        yaml_key="dataset_root",
        env=env,
        local_paths=local_paths,
        example_paths=example_paths,
    )
    dataset_root = _make_resolved_path(
        name="dataset_root",
        raw_value=data_raw,
        source=data_src,
        base_dir=root,
    )

    raw_val, raw_src = _select_value(
        env_key=None,
        yaml_key="raw_datasets_dir",
        env=env,
        local_paths=local_paths,
        example_paths=example_paths,
    )
    if raw_val is not None and not is_windows_absolute(raw_val) and not Path(raw_val).is_absolute():
        if dataset_root.path is not None:
            raw_datasets_dir = _make_resolved_path(
                name="raw_datasets_dir",
                raw_value=raw_val,
                source=raw_src,
                base_dir=dataset_root.path,
            )
        else:
            raw_datasets_dir = _make_resolved_path(
                name="raw_datasets_dir",
                raw_value=None,
                source="unconfigured",
                base_dir=None,
            )
    else:
        raw_datasets_dir = _make_resolved_path(
            name="raw_datasets_dir",
            raw_value=raw_val,
            source=raw_src,
            base_dir=dataset_root.path,
        )

    proc_val, proc_src = _select_value(
        env_key=None,
        yaml_key="processed_datasets_dir",
        env=env,
        local_paths=local_paths,
        example_paths=example_paths,
    )
    if (
        proc_val is not None
        and not is_windows_absolute(proc_val)
        and not Path(proc_val).is_absolute()
    ):
        if dataset_root.path is not None:
            processed_datasets_dir = _make_resolved_path(
                name="processed_datasets_dir",
                raw_value=proc_val,
                source=proc_src,
                base_dir=dataset_root.path,
            )
        else:
            processed_datasets_dir = _make_resolved_path(
                name="processed_datasets_dir",
                raw_value=None,
                source="unconfigured",
                base_dir=None,
            )
    else:
        processed_datasets_dir = _make_resolved_path(
            name="processed_datasets_dir",
            raw_value=proc_val,
            source=proc_src,
            base_dir=dataset_root.path,
        )

    manifest_val, manifest_src = _select_value(
        env_key=None,
        yaml_key="manifest_dir",
        env=env,
        local_paths=local_paths,
        example_paths=example_paths,
        default_value="manifests",
    )
    manifest_dir = _make_resolved_path(
        name="manifest_dir",
        raw_value=manifest_val,
        source=manifest_src,
        base_dir=root,
    )

    runs_val, runs_src = _select_value(
        env_key=ENV_RUNS_ROOT,
        yaml_key="experiment_runs_dir",
        env=env,
        local_paths=local_paths,
        example_paths=example_paths,
        default_value="runs",
    )
    experiment_runs_dir = _make_resolved_path(
        name="experiment_runs_dir",
        raw_value=runs_val,
        source=runs_src,
        base_dir=root,
    )

    sevenzip_val, sevenzip_src = _select_value(
        env_key=ENV_SEVENZIP_EXE,
        yaml_key="sevenzip_exe",
        env=env,
        local_paths=local_paths,
        example_paths=example_paths,
    )
    sevenzip_exe = _make_resolved_path(
        name="sevenzip_exe",
        raw_value=sevenzip_val,
        source=sevenzip_src,
        base_dir=root,
    )

    return ProjectPaths(
        repo_root=root,
        dataset_root=dataset_root,
        raw_datasets_dir=raw_datasets_dir,
        processed_datasets_dir=processed_datasets_dir,
        manifest_dir=manifest_dir,
        experiment_runs_dir=experiment_runs_dir,
        sevenzip_exe=sevenzip_exe,
    )
