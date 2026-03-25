from __future__ import annotations

import argparse
import concurrent.futures
import shutil
import sys
from typing import TYPE_CHECKING

from packaging.version import InvalidVersion, Version
from sphinx.cmd.build import main as sphinx_build_main

from .config import LATEST_RTD_PYTHON_VERSION, load_project_config

if TYPE_CHECKING:
    from pathlib import Path


def _builder_settings(builder: str) -> list[str]:
    if builder == "markdown":
        return ["-D", "llms_txt_uri_template={base_url}{docname}.md"]
    if builder == "singlemarkdown":
        return [
            "-D", "llms_txt_uri_template={base_url}{docname}.md",
            "-D", "singlemarkdown_flavor=llm",
        ]
    return []


def _run_builder(builder: str, source_dir: Path, build_dir: Path) -> None:
    args = [
        "-b",
        builder,
        *_builder_settings(builder),
        str(source_dir),
        str(build_dir / builder),
    ]
    exit_code = sphinx_build_main(args)
    if exit_code != 0:
        msg = f"sphinx builder failed for '{builder}' with exit code {exit_code}"
        raise RuntimeError(msg)


def build_docs() -> int:
    config = load_project_config()
    docs_dir = config.root / "docs"
    if not docs_dir.is_dir():
        print("docs directory not found", file=sys.stderr)
        return 1

    sphinx_build_dir = docs_dir / "_build"
    sphinx_build_dir.mkdir(parents=True, exist_ok=True)

    builders = ["html", "markdown", "singlemarkdown"]

    with concurrent.futures.ProcessPoolExecutor(max_workers=len(builders)) as executor:
        futures = [
            executor.submit(
                _run_builder,
                builder,
                docs_dir,
                sphinx_build_dir,
            )
            for builder in builders
        ]
        for future in concurrent.futures.as_completed(futures):
            future.result()

    all_dir = sphinx_build_dir / "all"
    all_dir.mkdir(parents=True, exist_ok=True)

    shutil.copytree(sphinx_build_dir / "html", all_dir, dirs_exist_ok=True)
    shutil.copytree(sphinx_build_dir / "markdown", all_dir, dirs_exist_ok=True)
    shutil.copy2(sphinx_build_dir / "singlemarkdown" / "index.md", all_dir / "llms-full.txt")

    print("\nDocumentation generated in docs/_build/all.")
    return 0


def update_rtd_config() -> int:
    config = load_project_config()

    try:
        config_python_version = Version(config.python_version)
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
                "    - cp -a docs/_build/all/. $READTHEDOCS_OUTPUT/html/",
                "",
            ]
        ),
        encoding="utf-8",
    )
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
