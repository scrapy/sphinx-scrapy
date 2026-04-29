from __future__ import annotations

import argparse
from collections.abc import Callable
import concurrent.futures
import re
import shutil
import sys
from http import HTTPStatus
from typing import TYPE_CHECKING
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, urlunsplit
from urllib.request import Request, urlopen

from packaging.version import InvalidVersion, Version
from sphinx.cmd.build import main as sphinx_build_main

from . import INTERSPHINX_MAPPING
from .config import LATEST_RTD_PYTHON_VERSION, load_project_config, normalize_project_id

if TYPE_CHECKING:
    from pathlib import Path


URL_PATTERN = re.compile(r"https?://[^\s<>()\[\]{}\"']+")
MARKDOWN_LINK_PATTERN = re.compile(
    r"(?P<prefix>!?\[[^\]]*\]\()"
    r"(?P<target>[^)\s]+)"
    r"(?P<title>\s+\"[^\"]*\")?"
    r"(?P<suffix>\))"
)


def _intersphinx_base_urls() -> tuple[str, ...]:
    bases = {url for url, _inventory in INTERSPHINX_MAPPING.values()}
    return tuple(sorted(bases, key=len, reverse=True))


def _project_docs_base_url(project_id: str | None) -> str | None:
    if not project_id:
        return None
    normalized_project_id = normalize_project_id(project_id)
    if not normalized_project_id:
        return None
    if normalized_project_id in INTERSPHINX_MAPPING:
        return INTERSPHINX_MAPPING[normalized_project_id][0]
    return f"https://{normalized_project_id}.readthedocs.io/en/latest/"


def _split_wrapped_markdown_target(target: str) -> tuple[str, str, str]:
    if len(target) >= 2 and target.startswith("<") and target.endswith(">"):
        return "<", target[1:-1], ">"
    return "", target, ""


def _rewrite_markdown_links(
    content: str,
    rewrite_target: Callable[[str], str],
) -> str:
    in_fence = False
    fence_char = ""
    rewritten_lines: list[str] = []

    def replacement(match: re.Match[str]) -> str:
        target = match.group("target")
        rewritten_target = rewrite_target(target)
        if rewritten_target == target:
            return match.group(0)

        title = match.group("title") or ""
        return (
            f"{match.group('prefix')}"
            f"{rewritten_target}"
            f"{title}"
            f"{match.group('suffix')}"
        )

    for line in content.splitlines(keepends=True):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            marker = stripped[0]
            if not in_fence:
                in_fence = True
                fence_char = marker
            elif marker == fence_char:
                in_fence = False
                fence_char = ""
            rewritten_lines.append(line)
            continue

        if in_fence:
            rewritten_lines.append(line)
            continue

        rewritten_lines.append(MARKDOWN_LINK_PATTERN.sub(replacement, line))

    return "".join(rewritten_lines)


def _rewrite_llms_link_target(
    target: str,
    docs_host: str,
    docs_path_prefix: str,
) -> str:
    wrapper_prefix, wrapped_target, wrapper_suffix = (
        _split_wrapped_markdown_target(target)
    )
    parts = urlsplit(wrapped_target)

    if parts.scheme or parts.netloc:
        if parts.scheme not in {"http", "https"}:
            return target
        if parts.netloc.lower() != docs_host:
            return target

    if not parts.path.endswith(".md"):
        return target

    clean_path = parts.path.lstrip("/")
    while clean_path.startswith("./"):
        clean_path = clean_path[2:]
    if clean_path.startswith("../"):
        return target

    if docs_path_prefix and not clean_path.startswith(docs_path_prefix):
        clean_path = f"{docs_path_prefix}{clean_path}"

    rewritten_target = urlunsplit(("", "", clean_path, parts.query, parts.fragment))
    return f"{wrapper_prefix}{rewritten_target}{wrapper_suffix}"


def _rewrite_llms_links_to_docs_path(
    output_dir: Path,
    docs_base_url: str | None,
) -> None:
    llms_path = output_dir / "llms.txt"
    if docs_base_url is None or not llms_path.is_file():
        return

    docs_parts = urlsplit(docs_base_url)
    docs_host = docs_parts.netloc.lower()
    docs_path = docs_parts.path.strip("/")
    docs_path_prefix = f"{docs_path}/" if docs_path else ""

    content = llms_path.read_text(encoding="utf-8")
    rewritten = _rewrite_markdown_links(
        content,
        lambda target: _rewrite_llms_link_target(target, docs_host, docs_path_prefix),
    )
    if rewritten != content:
        llms_path.write_text(rewritten, encoding="utf-8")


def _iter_markdown_outputs(output_dir: Path) -> list[Path]:
    files = sorted(output_dir.rglob("*.md"))
    for filename in ("llms.txt", "llms-full.txt"):
        path = output_dir / filename
        if path.is_file():
            files.append(path)
    return files


def _matching_base_url(url: str, base_urls: tuple[str, ...]) -> str | None:
    for base_url in base_urls:
        if url.startswith(base_url):
            return base_url
    return None


def _supports_markdown(base_url: str) -> bool:
    probe_url = f"{base_url.rstrip('/')}/index.md"
    headers = {"User-Agent": "sphinx-scrapy"}
    for method in ("HEAD", "GET"):
        request = Request(probe_url, headers=headers, method=method)  # noqa: S310
        try:
            with urlopen(request, timeout=5) as response:  # noqa: S310
                return HTTPStatus.OK <= response.status < HTTPStatus.BAD_REQUEST
        except HTTPError as error:
            if method == "HEAD" and error.code in {
                HTTPStatus.METHOD_NOT_ALLOWED,
                HTTPStatus.NOT_IMPLEMENTED,
            }:
                continue
            return False
        except URLError:
            return False
    return False


def _rewrite_url_to_markdown(url: str, enabled_base_urls: set[str], base_urls: tuple[str, ...]) -> str:
    base_url = _matching_base_url(url, base_urls)
    if not base_url or base_url not in enabled_base_urls:
        return url

    parts = urlsplit(url)
    path = parts.path
    if not path.endswith(".html"):
        return url
    new_path = f"{path[:-5]}.md"

    return urlunsplit((parts.scheme, parts.netloc, new_path, parts.query, parts.fragment))


def _rewrite_intersphinx_links_to_markdown(output_dir: Path) -> None:
    target_files = _iter_markdown_outputs(output_dir)
    if not target_files:
        return

    base_urls = _intersphinx_base_urls()
    file_contents: dict[Path, str] = {}
    candidate_base_urls: set[str] = set()

    for file in target_files:
        content = file.read_text(encoding="utf-8")
        file_contents[file] = content
        for match in URL_PATTERN.finditer(content):
            url = match.group(0)
            if ".html" not in url:
                continue
            base_url = _matching_base_url(url, base_urls)
            if base_url is not None:
                candidate_base_urls.add(base_url)

    if not candidate_base_urls:
        return

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=min(8, len(candidate_base_urls))
    ) as executor:
        availability = {
            base_url: executor.submit(_supports_markdown, base_url)
            for base_url in candidate_base_urls
        }
        enabled_base_urls = {
            base_url
            for base_url, future in availability.items()
            if future.result()
        }

    if not enabled_base_urls:
        return

    for file, content in file_contents.items():
        rewritten = URL_PATTERN.sub(
            lambda match: _rewrite_url_to_markdown(
                match.group(0),
                enabled_base_urls,
                base_urls,
            ),
            content,
        )
        if rewritten != content:
            file.write_text(rewritten, encoding="utf-8")


def _builder_settings(builder: str) -> list[str]:
    if builder == "html":
        return ["-D", "llms_txt_uri_template={docname}.md"]
    if builder == "singlemarkdown":
        return [
            "-D", "llms_txt_uri_template={docname}.md",
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
    docs_base_url = _project_docs_base_url(config.project_id)
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
    _rewrite_intersphinx_links_to_markdown(all_dir)
    _rewrite_llms_links_to_docs_path(all_dir, docs_base_url)

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
