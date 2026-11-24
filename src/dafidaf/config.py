"""Typed, read-only configuration loader for DA-FIDAF.

Uses standard-library dataclasses, PyYAML, and python-dotenv.
Never mutates process environment variables and never exposes secrets.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

import yaml
from dotenv import dotenv_values

from dafidaf.paths import ALLOWED_ENV_KEYS, ProjectPaths, find_repo_root, resolve_paths

KNOWN_YAML_PATH_KEYS: frozenset[str] = frozenset(
    {
        "dataset_root",
        "raw_datasets_dir",
        "processed_datasets_dir",
        "manifest_dir",
        "experiment_runs_dir",
        "sevenzip_exe",
    }
)


class ConfigError(ValueError):
    """Raised when a DA-FIDAF configuration file is malformed or invalid."""


@dataclass(frozen=True, slots=True)
class ConfigStatus:
    """Non-sensitive metadata describing which configuration sources were loaded."""

    dotenv_path: Path
    dotenv_loaded: bool
    local_yaml_path: Path
    local_yaml_loaded: bool
    example_yaml_path: Path
    example_yaml_loaded: bool
    warnings: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class DafidafConfig:
    """Top-level resolved configuration for DA-FIDAF."""

    paths: ProjectPaths
    status: ConfigStatus


def _load_paths_yaml(yaml_path: Path) -> dict[str, str]:
    """Parse and validate a paths YAML file strictly using yaml.safe_load."""
    try:
        raw_text = yaml_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigError(f"Unable to read configuration file '{yaml_path}': {exc}") from exc

    try:
        parsed = yaml.safe_load(raw_text)
    except yaml.YAMLError as exc:
        raise ConfigError(f"Invalid YAML syntax in '{yaml_path}': {exc}") from exc

    if parsed is None:
        return {}
    if not isinstance(parsed, dict):
        raise ConfigError(
            f"Configuration file '{yaml_path}' must contain a top-level YAML mapping."
        )

    section = parsed.get("paths")
    if section is None:
        raise ConfigError(
            f"Configuration file '{yaml_path}' is missing required top-level 'paths' mapping."
        )
    if not isinstance(section, dict):
        raise ConfigError(
            f"Top-level 'paths' in '{yaml_path}' must be a YAML mapping, "
            f"got {type(section).__name__}."
        )

    validated: dict[str, str] = {}
    for key, value in section.items():
        if not isinstance(key, str):
            raise ConfigError(
                f"Invalid non-string key under 'paths' in '{yaml_path}': {key!r}."
            )
        if key not in KNOWN_YAML_PATH_KEYS:
            raise ConfigError(
                f"Unknown key '{key}' under 'paths' in '{yaml_path}'. "
                f"Allowed keys: {sorted(KNOWN_YAML_PATH_KEYS)}."
            )
        if value is None:
            continue
        if not isinstance(value, str):
            raise ConfigError(
                f"Path value for 'paths.{key}' in '{yaml_path}' must be a string, "
                f"got {type(value).__name__}."
            )
        validated[key] = value

    return validated


def _collect_allowlisted_env(
    *,
    dotenv_path: Path,
    environ: Mapping[str, str],
) -> tuple[dict[str, str], bool]:
    """Combine optional .env file and process environment for allowlisted keys only.

    Process environment variables take precedence over .env values.
    Unrelated environment variables (such as API tokens or credentials) are ignored.
    """
    merged: dict[str, str] = {}
    dotenv_loaded = False

    if dotenv_path.is_file():
        raw_dotenv = dotenv_values(dotenv_path)
        dotenv_loaded = True
        for key in ALLOWED_ENV_KEYS:
            val = raw_dotenv.get(key)
            if val is not None and val.strip():
                merged[key] = val.strip()

    for key in ALLOWED_ENV_KEYS:
        val = environ.get(key)
        if val is not None and val.strip():
            merged[key] = val.strip()

    return merged, dotenv_loaded


def load_config(
    *,
    repo_root: Path | None = None,
    environ: Mapping[str, str] | None = None,
    dotenv_file: Path | None = None,
    local_yaml_file: Path | None = None,
    example_yaml_file: Path | None = None,
) -> DafidafConfig:
    """Load and validate DA-FIDAF configuration in read-only mode.

    Args:
        repo_root: Optional explicit repository root. Auto-detected if omitted.
        environ: Optional environment mapping (defaults to os.environ).
        dotenv_file: Optional override path for `.env`.
        local_yaml_file: Optional override path for `configs/paths.local.yaml`.
        example_yaml_file: Optional override path for `configs/paths.example.yaml`.

    Returns:
        A validated, immutable DafidafConfig instance.
    """
    root = find_repo_root(repo_root)
    env_source = os.environ if environ is None else environ

    dotenv_path = dotenv_file if dotenv_file is not None else root / ".env"
    local_yaml_path = (
        local_yaml_file if local_yaml_file is not None else root / "configs" / "paths.local.yaml"
    )
    example_yaml_path = (
        example_yaml_file
        if example_yaml_file is not None
        else root / "configs" / "paths.example.yaml"
    )

    warnings: list[str] = []

    effective_env, dotenv_loaded = _collect_allowlisted_env(
        dotenv_path=dotenv_path,
        environ=env_source,
    )

    local_paths: dict[str, str] | None = None
    local_yaml_loaded = False
    if local_yaml_path.is_file():
        local_paths = _load_paths_yaml(local_yaml_path)
        local_yaml_loaded = True

    example_paths: dict[str, str] | None = None
    example_yaml_loaded = False
    if example_yaml_path.is_file():
        example_paths = _load_paths_yaml(example_yaml_path)
        example_yaml_loaded = True
    else:
        warnings.append(
            f"Example configuration file not found at '{example_yaml_path}'; "
            "falling back to repository-relative defaults."
        )

    if not dotenv_loaded and not local_yaml_loaded and not effective_env:
        warnings.append(
            "No machine-local configuration found (.env, configs/paths.local.yaml, or "
            "DAFIDAF_* environment variables). Using safe fallback defaults."
        )

    paths = resolve_paths(
        repo_root=root,
        env=effective_env,
        local_paths=local_paths,
        example_paths=example_paths,
    )

    status = ConfigStatus(
        dotenv_path=dotenv_path,
        dotenv_loaded=dotenv_loaded,
        local_yaml_path=local_yaml_path,
        local_yaml_loaded=local_yaml_loaded,
        example_yaml_path=example_yaml_path,
        example_yaml_loaded=example_yaml_loaded,
        warnings=tuple(warnings),
    )

    return DafidafConfig(paths=paths, status=status)
