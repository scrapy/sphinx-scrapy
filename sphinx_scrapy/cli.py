from __future__ import annotations

import argparse
import sys
from pathlib import Path

from packaging.version import InvalidVersion, Version
from sphinx.cmd.build import main as sphinx_build

from .config import LATEST_RTD_PYTHON_VERSION, load_project_config


def build_docs(output_dir: Path | None) -> int:
    config = load_project_config()
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
