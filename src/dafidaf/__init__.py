"""DA-FIDAF portable research framework core package."""

from dafidaf.config import ConfigError, ConfigStatus, DafidafConfig, load_config
from dafidaf.paths import ProjectPaths, ResolvedPath, find_repo_root, resolve_paths

__all__ = [
    "__version__",
    "ConfigError",
    "ConfigStatus",
    "DafidafConfig",
    "ProjectPaths",
    "ResolvedPath",
    "find_repo_root",
    "load_config",
    "resolve_paths",
]

__version__ = "0.1.0"
