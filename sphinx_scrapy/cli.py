from __future__ import annotations

import argparse
import sys

from packaging.version import InvalidVersion, Version
from sphinx_llm_friendly import build

from .config import LATEST_RTD_PYTHON_VERSION, load_project_config


def build_docs() -> int:
    config = load_project_config()
    docs_dir = config.root / "docs"
    if not docs_dir.is_dir():
        print("docs directory not found", file=sys.stderr)
        return 1
    output_dir = build(docs_dir, docs_dir / "_build")
    print(f"\nDocumentation generated in {output_dir.relative_to(config.root)}.")
    return 0


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
                "    - tox -e docs",
                "    - mkdir -p $READTHEDOCS_OUTPUT/html",
                "    - cp -a docs/_build/all/. $READTHEDOCS_OUTPUT/html/",
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
    subparsers.add_parser("build")
    subparsers.add_parser("update-rtd-config")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "build":
        return build_docs()
    if args.command == "update-rtd-config":
        return update_rtd_config()
    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
