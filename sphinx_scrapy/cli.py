from __future__ import annotations

import argparse
import re
import sys
from importlib.metadata import version
from pathlib import Path

from packaging.version import InvalidVersion, Version
from sphinx.cmd.build import main as sphinx_build

from .config import LATEST_RTD_PYTHON_VERSION, ProjectConfig, load_project_config


def _check_docs_requirements(config: ProjectConfig) -> bool:
    found = [
        path
        for path in ("docs/requirements.in", "docs/requirements.txt")
        if (config.root / path).is_file()
    ]
    if found:
        print(
            f"Found {' and '.join(found)}. Move documentation dependencies "
            f"other than sphinx-scrapy to a docs dependency group in "
            f"pyproject.toml, and remove {' and '.join(found)}.",
            file=sys.stderr,
        )
        return False
    return True


def build_docs(output_dir: Path | None) -> int:
    config = load_project_config()
    if not _check_docs_requirements(config):
        return 1
    docs_dir = config.root / "docs"
    if not docs_dir.is_dir():
        print("docs directory not found", file=sys.stderr)
        return 1
    build_dir = docs_dir / "_build"
    args = [
        "-b",
        "html",
        "-d",
        str(build_dir / "doctrees"),
        "-j",
        "auto",
        str(docs_dir),
        str(output_dir or build_dir / "html"),
    ]
    if config.fail_on_warning:
        args += ["-W", "--keep-going"]
    return sphinx_build(args)


def update_rtd_config() -> int:
    config = load_project_config()
    if not _check_docs_requirements(config):
        return 1

    try:
        config_python_version = Version(str(config.python_version))
    except InvalidVersion:
        print(
            f"Invalid Python version in pyproject.toml: {config.python_version}",
            file=sys.stderr,
        )
        return 1

    if config_python_version > Version(LATEST_RTD_PYTHON_VERSION):
        print(
            f"Configured Python ({config.python_version}) is newer than the "
            f"latest Read the Docs supported Python version known to "
            f"sphinx-scrapy ({LATEST_RTD_PYTHON_VERSION}).",
            file=sys.stderr,
        )
        return 1

    output = config.root / ".readthedocs.yml"
    output.write_text(
        "\n".join(
            [
                "version: 2",
                "build:",
                "  os: ubuntu-24.04",
                "  tools:",
                f'    python: "{config.python_version}"',
                "  commands:",
                "    - pip install tox",
                "    - tox -e docs -- $READTHEDOCS_OUTPUT/html",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print("Updated .readthedocs.yml")

    tox_ini = config.root / "tox.ini"
    if tox_ini.is_file():
        text = tox_ini.read_text(encoding="utf-8")
        new_text = re.sub(
            r"(sphinx-scrapy(?:\[tox\])?)(?:==\S+|\s*@\s*git\+\S+)",
            rf"\g<1>=={version('sphinx-scrapy')}",
            text,
        )
        if new_text != text:
            tox_ini.write_text(new_text, encoding="utf-8")
            print("Updated tox.ini")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sphinx-scrapy")
    subparsers = parser.add_subparsers(dest="command", required=True)
    build_parser = subparsers.add_parser("build")
    build_parser.add_argument("output_dir", nargs="?", type=Path)
    subparsers.add_parser("update-rtd-config")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "build":
        return build_docs(args.output_dir)
    if args.command == "update-rtd-config":
        return update_rtd_config()
    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
