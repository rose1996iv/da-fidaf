"""Unit tests for portable path resolution and typed configuration loading."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from dafidaf.config import ConfigError, load_config
from dafidaf.paths import ENV_DATA_ROOT, ENV_RUNS_ROOT, ENV_SEVENZIP_EXE, is_windows_absolute


def _init_fake_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / "configs").mkdir(parents=True)
    (repo / "pyproject.toml").write_text("[project]\nname = 'da-fidaf'\n", encoding="utf-8")
    (repo / "configs" / "paths.example.yaml").write_text(
        "paths:\n"
        "  dataset_root: \"<SET_VIA_ENV_OR_LOCAL_CONFIG>\"\n"
        "  raw_datasets_dir: \"raw\"\n"
        "  processed_datasets_dir: \"processed\"\n"
        "  manifest_dir: \"manifests\"\n"
        "  experiment_runs_dir: \"runs\"\n",
        encoding="utf-8",
    )
    return repo


def test_env_variable_precedence_over_local_and_example(tmp_path: Path) -> None:
    repo = _init_fake_repo(tmp_path)
    local_data = tmp_path / "local_data"
    env_data = tmp_path / "env_data"
    env_runs = tmp_path / "env_runs"
    env_data.mkdir()

    (repo / "configs" / "paths.local.yaml").write_text(
        f"paths:\n"
        f"  dataset_root: \"{local_data.as_posix()}\"\n"
        f"  experiment_runs_dir: \"local_runs\"\n",
        encoding="utf-8",
    )
    (repo / ".env").write_text(
        f"{ENV_DATA_ROOT}={(tmp_path / 'dotenv_data').as_posix()}\n",
        encoding="utf-8",
    )

    cfg = load_config(
        repo_root=repo,
        environ={
            ENV_DATA_ROOT: str(env_data),
            ENV_RUNS_ROOT: str(env_runs),
        },
    )

    assert cfg.paths.dataset_root.configured is True
    assert cfg.paths.dataset_root.source == "env"
    assert cfg.paths.dataset_root.path == env_data
    assert cfg.paths.dataset_root.exists is True

    assert cfg.paths.experiment_runs_dir.source == "env"
    assert cfg.paths.experiment_runs_dir.path == env_runs
    assert cfg.paths.experiment_runs_dir.exists is False
    # Must not auto-create configured directories
    assert not env_runs.exists()


def test_local_config_precedence_over_example(tmp_path: Path) -> None:
    repo = _init_fake_repo(tmp_path)
    local_data = tmp_path / "external_datasets"
    local_data.mkdir()

    (repo / "configs" / "paths.local.yaml").write_text(
        f"paths:\n"
        f"  dataset_root: \"{local_data.as_posix()}\"\n"
        f"  raw_datasets_dir: \"immutable_raw\"\n"
        f"  experiment_runs_dir: \"custom_runs\"\n",
        encoding="utf-8",
    )

    cfg = load_config(repo_root=repo, environ={})

    assert cfg.status.local_yaml_loaded is True
    assert cfg.paths.dataset_root.source == "local_config"
    assert cfg.paths.dataset_root.path == local_data
    assert cfg.paths.raw_datasets_dir.path == local_data / "immutable_raw"
    assert cfg.paths.experiment_runs_dir.path == repo / "custom_runs"


def test_example_config_fallback_and_placeholder_handling(tmp_path: Path) -> None:
    repo = _init_fake_repo(tmp_path)

    cfg = load_config(repo_root=repo, environ={})

    assert cfg.status.example_yaml_loaded is True
    assert cfg.status.local_yaml_loaded is False
    assert cfg.paths.dataset_root.configured is False
    assert cfg.paths.dataset_root.path is None
    assert cfg.paths.dataset_root.source == "unconfigured"
    assert cfg.paths.manifest_dir.source == "example_config"
    assert cfg.paths.manifest_dir.path == repo / "manifests"
    assert cfg.paths.experiment_runs_dir.source == "example_config"
    assert cfg.paths.experiment_runs_dir.path == repo / "runs"


def test_missing_all_configuration_files_safe_fallback(tmp_path: Path) -> None:
    repo = tmp_path / "bare_repo"
    repo.mkdir()
    (repo / "pyproject.toml").write_text("[project]\nname = 'da-fidaf'\n", encoding="utf-8")

    cfg = load_config(repo_root=repo, environ={})

    assert cfg.status.dotenv_loaded is False
    assert cfg.status.local_yaml_loaded is False
    assert cfg.status.example_yaml_loaded is False
    assert len(cfg.status.warnings) >= 1
    assert cfg.paths.dataset_root.configured is False
    assert cfg.paths.manifest_dir.source == "default"
    assert cfg.paths.manifest_dir.path == repo / "manifests"


def test_relative_and_absolute_path_resolution(tmp_path: Path) -> None:
    repo = _init_fake_repo(tmp_path)
    abs_proc = tmp_path / "separate_processed"

    (repo / "configs" / "paths.local.yaml").write_text(
        f"paths:\n"
        f"  dataset_root: \"../relative_data\"\n"
        f"  raw_datasets_dir: \"raw_sub\"\n"
        f"  processed_datasets_dir: \"{abs_proc.as_posix()}\"\n",
        encoding="utf-8",
    )

    cfg = load_config(repo_root=repo, environ={})

    assert cfg.paths.dataset_root.path == repo / "../relative_data"
    assert cfg.paths.raw_datasets_dir.path == (repo / "../relative_data") / "raw_sub"
    assert cfg.paths.processed_datasets_dir.path == abs_proc


def test_windows_style_path_handling(tmp_path: Path) -> None:
    repo = _init_fake_repo(tmp_path)
    win_data = r"Z:\ResearchData\IoT_Benchmarks"
    win_7z = r"C:\Tools\7-Zip\7z.exe"

    assert is_windows_absolute(win_data) is True
    assert is_windows_absolute("relative/path") is False

    cfg = load_config(
        repo_root=repo,
        environ={
            ENV_DATA_ROOT: win_data,
            ENV_SEVENZIP_EXE: win_7z,
        },
    )

    assert cfg.paths.dataset_root.configured is True
    assert cfg.paths.dataset_root.raw_value == win_data
    assert cfg.paths.sevenzip_exe.configured is True
    assert cfg.paths.sevenzip_exe.raw_value == win_7z


@pytest.mark.parametrize(
    "bad_yaml",
    [
        "paths: [not, a, mapping]\n",
        "- just a list\n",
        "other_key:\n  dataset_root: /tmp\n",
        "paths:\n  unknown_field: /tmp\n",
        "paths:\n  dataset_root: 12345\n",
        "paths:\n  dataset_root: [unterminated\n",
    ],
)
def test_invalid_configuration_raises_config_error(tmp_path: Path, bad_yaml: str) -> None:
    repo = _init_fake_repo(tmp_path)
    (repo / "configs" / "paths.local.yaml").write_text(bad_yaml, encoding="utf-8")

    with pytest.raises(ConfigError):
        load_config(repo_root=repo, environ={})


def test_no_hardcoded_drive_letters_in_source_code() -> None:
    src_dir = Path(__file__).resolve().parents[2] / "src" / "dafidaf"
    drive_pattern = re.compile(r"""['"][A-Za-z]:\\""")
    for py_file in src_dir.rglob("*.py"):
        content = py_file.read_text(encoding="utf-8")
        assert not drive_pattern.search(content), f"Hardcoded Windows drive path in {py_file}"
