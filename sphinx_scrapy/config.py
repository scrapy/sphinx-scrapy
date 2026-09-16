from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from packaging.utils import canonicalize_name

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

LATEST_RTD_PYTHON_VERSION = "3.14"

_GITHUB_URL = re.compile(r"https?://github\.com/(?P<owner>[\w.-]+)/(?P<repo>[\w.-]+)")


@dataclass(frozen=True)
class ProjectConfig:
    root: Path
    python_version: str | None = None
    extras: set[str] = field(default_factory=set)
    project_id: str | None = None
    github_repo: str | None = None
    fail_on_warning: bool = True


def find_project_root(start: Path | None = None) -> Path:
    path = (start or Path.cwd()).resolve()
    for candidate in (path, *path.parents):
        if (candidate / "pyproject.toml").is_file():
            return candidate
    msg = "Could not find pyproject.toml in the current directory or parent directories"
    raise FileNotFoundError(msg)


def get_extras(pyproject_data: dict[str, Any]) -> set[str]:
    project_data = pyproject_data.get("project", {})
    optional_dependencies = project_data.get("optional-dependencies", {})
    return {str(key) for key in optional_dependencies}


def _get_github_repo(pyproject_data: dict[str, Any]) -> str | None:
    urls: dict[str, Any] = pyproject_data.get("project", {}).get("urls", {})
    # Repository URLs first, since other entries may point to a different
    # repository, e.g. a documentation page hosted elsewhere.
    keys = sorted(urls, key=lambda key: key.lower() not in {"repository", "source"})
    for key in keys:
        match = _GITHUB_URL.match(str(urls[key]))
        if match:
            owner, repo = match.group("owner", "repo")
            return f"{owner}/{repo.removesuffix('.git')}"
    return None


def normalize_project_id(project_id: str) -> str:
    return canonicalize_name(project_id.strip())


def load_project_config(start: Path | None = None) -> ProjectConfig:
    """Load project configuration from a :file:`pyproject.toml` if available.

    The file is searched for in *start* (CWD by default) and its parents. If
    there is none, return a minimal ``ProjectConfig`` containing only the
    resolved project root and leaving other fields empty/None.
    """
    try:
        project_root = find_project_root(start)
    except FileNotFoundError:
        resolved_root = (start or Path.cwd()).resolve()
        return ProjectConfig(root=resolved_root)

    pyproject_path = project_root / "pyproject.toml"
    with pyproject_path.open("rb") as fp:
        pyproject_data = tomllib.load(fp)
    tool_data = pyproject_data.get("tool", {})
    scrapy_data = tool_data.get("sphinx-scrapy", {})
    python_version = scrapy_data.get("python-version", LATEST_RTD_PYTHON_VERSION)
    fail_on_warning = bool(scrapy_data.get("fail-on-warning", True))
    extras = get_extras(pyproject_data)
    raw_project_id = pyproject_data.get("project", {}).get("name")
    project_id = None
    if raw_project_id is not None:
        normalized_project_id = normalize_project_id(str(raw_project_id))
        if normalized_project_id:
            project_id = normalized_project_id
    return ProjectConfig(
        root=project_root,
        python_version=str(python_version) if python_version is not None else None,
        extras=extras,
        project_id=project_id,
        github_repo=_get_github_repo(pyproject_data),
        fail_on_warning=fail_on_warning,
    )
