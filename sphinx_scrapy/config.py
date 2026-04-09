from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

LATEST_RTD_PYTHON_VERSION = "3.14"


@dataclass(frozen=True)
class ProjectConfig:
    root: Path
    python_version: str | None = None
    extras: set[str] = field(default_factory=set)
    project_id: str | None = None


def find_project_root(start: Path | None = None) -> Path:
    path = (start or Path.cwd()).resolve()
    for candidate in (path, *path.parents):
        if (candidate / "pyproject.toml").is_file():
            return candidate
    msg = "Could not find pyproject.toml in the current directory or parent directories"
    raise FileNotFoundError(msg)


def get_extras(pyproject_data: dict[str, object]) -> set[str]:
    project_data = pyproject_data.get("project", {})
    optional_dependencies = project_data.get("optional-dependencies", {})
    return {str(key) for key in optional_dependencies}


def load_project_config(root: Path | None = None) -> ProjectConfig:
    """Load project configuration from a pyproject.toml if available.

    If no pyproject.toml can be found (starting from ``root`` or CWD),
    return a minimal ``ProjectConfig`` containing only the resolved
    project root and leaving other fields empty/None.
    """
    try:
        project_root = root or find_project_root()
    except FileNotFoundError:
        resolved_root = (root or Path.cwd()).resolve()
        return ProjectConfig(root=resolved_root)

    pyproject_path = project_root / "pyproject.toml"
    with pyproject_path.open("rb") as fp:
        pyproject_data = tomllib.load(fp)
    tool_data = pyproject_data.get("tool", {})
    scrapy_data = tool_data.get("sphinx-scrapy", {})
    python_version = scrapy_data.get("python-version", LATEST_RTD_PYTHON_VERSION)
    extras = get_extras(pyproject_data)
    project_id = pyproject_data.get("project", {}).get("name")
    return ProjectConfig(
        root=project_root,
        python_version=str(python_version) if python_version is not None else None,
        extras=extras,
        project_id=str(project_id) if project_id is not None else None,
    )
