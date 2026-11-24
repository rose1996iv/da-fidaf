"""Unit tests for the read-only `dafidaf doctor` CLI."""

from __future__ import annotations

import io
from pathlib import Path

from dafidaf.cli import EXIT_ERROR, EXIT_WARNING, run_doctor
from dafidaf.paths import ENV_DATA_ROOT, ENV_RUNS_ROOT


def _make_temp_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "da-fidaf-test"
    (repo / "configs").mkdir(parents=True)
    (repo / "pyproject.toml").write_text("[project]\nname = 'da-fidaf'\n", encoding="utf-8")
    (repo / "configs" / "paths.example.yaml").write_text(
        "paths:\n"
        "  dataset_root: \"<SET_VIA_ENV_OR_LOCAL_CONFIG>\"\n"
        "  experiment_runs_dir: \"runs\"\n",
        encoding="utf-8",
    )
    return repo


def test_doctor_is_strictly_readonly(tmp_path: Path) -> None:
    repo = _make_temp_repo(tmp_path)
    nonexistent_data = tmp_path / "does_not_exist_data"
    nonexistent_runs = tmp_path / "does_not_exist_runs"

    before_entries = sorted(p.relative_to(tmp_path) for p in tmp_path.rglob("*"))
    buffer = io.StringIO()

    code = run_doctor(
        repo_root=repo,
        environ={
            ENV_DATA_ROOT: str(nonexistent_data),
            ENV_RUNS_ROOT: str(nonexistent_runs),
        },
        stream=buffer,
    )

    after_entries = sorted(p.relative_to(tmp_path) for p in tmp_path.rglob("*"))
    assert before_entries == after_entries
    assert not nonexistent_data.exists()
    assert not nonexistent_runs.exists()
    assert code == EXIT_WARNING
    assert "MISSING ON DISK" in buffer.getvalue()


def test_doctor_never_prints_sensitive_env_or_dotenv_values(tmp_path: Path) -> None:
    repo = _make_temp_repo(tmp_path)
    fake_secret_env = "SUPER_SECRET_TOKEN_XYZ_987654321"
    fake_secret_dotenv = "DOTENV_PRIVATE_PASSWORD_ABC_123456"

    (repo / ".env").write_text(
        f"GITHUB_TOKEN={fake_secret_dotenv}\n"
        f"API_SECRET_KEY={fake_secret_dotenv}\n",
        encoding="utf-8",
    )

    buffer = io.StringIO()
    run_doctor(
        repo_root=repo,
        environ={
            "OPENAI_API_KEY": fake_secret_env,
            "AWS_SECRET_ACCESS_KEY": fake_secret_env,
            "DB_PASSWORD": fake_secret_env,
        },
        stream=buffer,
    )

    output = buffer.getvalue()
    assert fake_secret_env not in output
    assert fake_secret_dotenv not in output
    assert "OPENAI_API_KEY" not in output
    assert "GITHUB_TOKEN" not in output


def test_doctor_returns_error_on_invalid_yaml(tmp_path: Path) -> None:
    repo = _make_temp_repo(tmp_path)
    (repo / "configs" / "paths.local.yaml").write_text(
        "paths: [invalid_list_not_mapping]\n",
        encoding="utf-8",
    )

    buffer = io.StringIO()
    code = run_doctor(repo_root=repo, environ={}, stream=buffer)

    assert code == EXIT_ERROR
    assert "ERROR" in buffer.getvalue()
