from __future__ import annotations

import re
from functools import cache
from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING

from docutils import nodes
from sphinx.util.docutils import SphinxRole

from .config import load_project_config, normalize_project_id

if TYPE_CHECKING:
    from collections.abc import Generator

    from sphinx.application import Sphinx
    from sphinx.config import Config
    from sphinx.util.typing import ExtensionMetadata

    from .config import ProjectConfig

logger = getLogger(__name__)

INTERSPHINX_MAPPING = {
    "aiohttp": ("https://docs.aiohttp.org/en/stable/", None),
    "attrs": ("https://www.attrs.org/en/stable/", None),
    "coverage": ("https://coverage.readthedocs.io/en/latest/", None),
    "cryptography": ("https://cryptography.io/en/latest/", None),
    "cssselect": ("https://cssselect.readthedocs.io/en/latest/", None),
    "curl-cffi": ("https://curl-cffi.readthedocs.io/en/latest/", None),
    "dateparser": ("https://dateparser.readthedocs.io/en/latest/", None),
    "form2request": ("https://form2request.readthedocs.io/en/latest/", None),
    "formasaurus": ("https://formasaurus.readthedocs.io/en/latest/", None),
    "itemloaders": ("https://itemloaders.readthedocs.io/en/latest/", None),
    "jinja": ("https://jinja.palletsprojects.com/en/latest/", None),
    "lxml": ("https://lxml.de/apidoc/", None),
    "multidict": ("https://multidict.aio-libs.org/en/latest/", None),
    "niquests": ("https://niquests.readthedocs.io/en/latest/", None),
    "packaging": ("https://packaging.pypa.io/en/stable/", None),
    "parsel": ("https://parsel.readthedocs.io/en/latest/", None),
    "platformdirs": ("https://platformdirs.readthedocs.io/en/latest/", None),
    "pydantic": ("https://pydantic.dev/docs/validation/latest/", None),
    "pypug": ("https://packaging.python.org/en/latest/", None),
    "pytest": ("https://docs.pytest.org/en/stable/", None),
    "python": ("https://docs.python.org/3/", None),
    "python-scrapinghub": (
        "https://python-scrapinghub.readthedocs.io/en/latest/",
        None,
    ),
    "python-zyte-api": ("https://python-zyte-api.readthedocs.io/en/stable/", None),
    "scrapy": ("https://docs.scrapy.org/en/latest/", None),
    "scrapy-lint": ("https://scrapy-lint.readthedocs.io/en/latest/", None),
    "scrapy-poet": ("https://scrapy-poet.readthedocs.io/en/stable/", None),
    "scrapy-spider-metadata": (
        "https://scrapy-spider-metadata.readthedocs.io/en/latest/",
        None,
    ),
    "scrapy-zyte-api": ("https://scrapy-zyte-api.readthedocs.io/en/latest/", None),
    "scrapy-zyte-smartproxy": (
        "https://scrapy-zyte-smartproxy.readthedocs.io/en/latest/",
        None,
    ),
    "scrapyd": ("https://scrapyd.readthedocs.io/en/latest/", None),
    "shub": ("https://shub.readthedocs.io/en/latest/", None),
    "shub-image": ("https://shub-image.readthedocs.io/en/latest/", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
    "spidermon": ("https://spidermon.readthedocs.io/en/latest/", None),
    "tenacity": ("https://tenacity.readthedocs.io/en/latest/", None),
    "tox": ("https://tox.wiki/en/latest/", None),
    "twisted": ("https://docs.twisted.org/en/stable/", None),
    "twistedapi": ("https://docs.twisted.org/en/stable/api/", None),
    "url-matcher": ("https://url-matcher.readthedocs.io/en/latest/", None),
    "w3lib": ("https://w3lib.readthedocs.io/en/latest/", None),
    "web-poet": ("https://web-poet.readthedocs.io/en/stable/", None),
    "zyte": ("https://docs.zyte.com/", None),
    "zyte-common-items": ("https://zyte-common-items.readthedocs.io/en/latest/", None),
    "zyte-parsers": ("https://zyte-parsers.readthedocs.io/en/latest/", None),
    "zyte-spider-templates": (
        "https://zyte-spider-templates.readthedocs.io/en/latest/",
        None,
    ),
}

# By default, interphinx entries are configured if a same-name module is
# installed. Here you can set True to always configure the entry unless
# explicitly disabled, False to never configure the entry unless explicitly
# requested, or a string to use as the package name to check for.
PACKAGE_OVERRIDES = {
    "python": True,
    "python-zyte-api": "zyte-api",
    "scrapy": True,
    "twistedapi": "twisted",
    "zyte": False,
}

# Repositories that :gh: can target by name alone, e.g. :gh:`parsel#12`.
_GITHUB_OWNERS = {
    "scrapinghub": (
        "andi",
        "dateparser",
        "extruct",
        "price-parser",
        "python-scrapinghub",
        "scrapy-poet",
        "scrapyrt",
        "shub",
        "spidermon",
        "web-poet",
    ),
    "scrapy": (
        "cssselect",
        "form2request",
        "itemadapter",
        "itemloaders",
        "parsel",
        "protego",
        "queuelib",
        "scrapy",
        "scrapy-lint",
        "scrapyd",
        "scrapyd-client",
        "sphinx-scrapy",
        "w3lib",
    ),
    "scrapy-plugins": (
        "scrapy-playwright",
        "scrapy-splash",
        "scrapy-zyte-api",
        "scrapy-zyte-smartproxy",
    ),
    "zytedata": (
        "python-zyte-api",
        "scrapy-spider-metadata",
        "url-matcher",
        "zyte-common-items",
        "zyte-parsers",
        "zyte-spider-templates",
    ),
}
_GITHUB_REPO_OWNERS = {
    repo: owner for owner, repos in _GITHUB_OWNERS.items() for repo in repos
}

_GITHUB_REFERENCE = re.compile(
    r"(?:(?:(?P<owner>[\w.-]+)/)?(?P<repo>[\w.-]+)#)?(?P<number>\d+)"
)


def setup(app: Sphinx) -> ExtensionMetadata:
    app.add_config_value(
        "scrapy_intersphinx_enable", [], "env", types=frozenset({list})
    )
    app.add_config_value(
        "scrapy_intersphinx_enable_installed", False, "env", types=frozenset({bool})
    )
    app.add_config_value(
        "scrapy_intersphinx_disable", [], "env", types=frozenset({list})
    )

    for extension in (
        "sphinx.ext.autodoc",
        "sphinx.ext.intersphinx",
        "sphinx.ext.viewcode",
        "sphinx_copybutton",
        "sphinx_design",
        "sphinx_llm_friendly",
        "sphinx_sitemap",
        "sphinxcontrib.youtube",
    ):
        app.setup_extension(extension)

    app.add_role("gh", _GitHubRole())

    app.connect("builder-inited", set_better_defaults)
    app.connect("config-inited", update_config)

    # https://github.com/scrapy/scrapy/blob/dba37674e6eaa6c2030c8eb35ebf8127cd488062/docs/_ext/scrapydocs.py#L90C16-L110C6
    for crossref_type in ("setting", "signal", "command", "reqmeta", "stat"):
        app.add_crossref_type(
            directivename=crossref_type,
            rolename=crossref_type,
            indextemplate=f"pair: %s; {crossref_type}",
        )

    return {"parallel_read_safe": True}


class _GitHubRole(SphinxRole):
    """Link to a GitHub issue or pull request, given ``123`` for the current
    repository, or ``repo#123`` or ``owner/repo#123`` for a different one.
    """

    def run(self) -> tuple[list[nodes.Node], list[nodes.system_message]]:
        current_repo = _project_config(self.env.app.confdir).github_repo or ""
        match = _GITHUB_REFERENCE.fullmatch(self.text.strip())
        error = owner = repo = number = ""
        if not match:
            error = f"Unsupported GitHub reference: {self.text!r}"
        else:
            number = match["number"]
            repo = match["repo"] or current_repo.partition("/")[2]
            owner = (
                match["owner"]
                or _GITHUB_REPO_OWNERS.get(repo)
                or current_repo.partition("/")[0]
            )
            if not (owner and repo):
                error = (
                    f"Could not determine the repository of {self.text!r}; use "
                    f"the owner/repo#number syntax"
                )
            elif match["repo"] and f"{owner}/{repo}" == current_repo:
                error = (
                    f"{self.text!r} targets the current repository; use the "
                    f"number alone"
                )
        if error:
            message = self.inliner.reporter.error(error, line=self.lineno)
            problem = self.inliner.problematic(self.rawtext, self.rawtext, message)
            return [problem], [message]
        label = (
            f"#{number}" if f"{owner}/{repo}" == current_repo else f"{repo}#{number}"
        )
        # GitHub redirects the issue URL of a pull request to the pull request.
        url = f"https://github.com/{owner}/{repo}/issues/{number}"
        return [nodes.reference(self.rawtext, label, refuri=url)], []


@cache
def _project_config(confdir: str | Path) -> ProjectConfig:
    return load_project_config(Path(confdir))


def update_config(app: Sphinx, config: Config) -> None:
    configure_intersphinx(config)
    configure_sitemap(config, _project_config(app.confdir))


def set_better_defaults(app: Sphinx) -> None:
    manual_conf = getattr(app, "_raw_config", {})
    better_defaults = {
        "sitemap_excludes": ["genindex.html", "search.html"],
        "sitemap_url_scheme": "{link}",
    }
    for key, value in better_defaults.items():
        if key in manual_conf:
            continue
        setattr(app.config, key, value)


def configure_intersphinx(config: Config) -> None:
    known = set(INTERSPHINX_MAPPING)
    default = {k for k in INTERSPHINX_MAPPING if PACKAGE_OVERRIDES.get(k) is True}
    disabled = set(config.scrapy_intersphinx_disable)
    non_disabled = known - disabled
    requested = set(config.scrapy_intersphinx_enable)
    to_configure = (
        requested
        | (default - disabled)
        | (
            set(installed(non_disabled - requested - default))
            if config.scrapy_intersphinx_enable_installed
            else set()
        )
    )
    for k in to_configure:
        config.intersphinx_mapping[k] = INTERSPHINX_MAPPING[k]


def configure_sitemap(config: Config, project_config: ProjectConfig) -> None:
    if not config.html_baseurl:
        package: str | None = None
        if project_config.project_id:
            package = normalize_project_id(project_config.project_id)
        elif hasattr(config, "project"):
            package = normalize_project_id(re.sub(r"\s+", "-", str(config.project)))
        if not package:
            return
        if package in INTERSPHINX_MAPPING:
            base_url = INTERSPHINX_MAPPING[package][0]
        else:
            base_url = f"https://{package}.readthedocs.io/en/latest/"
        config.html_baseurl = base_url
    if not config.html_baseurl.endswith("/"):
        config.html_baseurl = config.html_baseurl + "/"
        logger.warning(
            "html_baseurl should end with a slash; automatically fixed to %r",
            config.html_baseurl,
        )


def installed(names: set[str]) -> Generator[str, None, None]:
    checked: dict[str, bool] = {}
    for name in names:
        if name in PACKAGE_OVERRIDES:
            package = PACKAGE_OVERRIDES[name]
            if package is False:
                continue
        if name in checked:
            if checked[name]:
                yield name
            continue
        module_name = name.replace("-", "_")
        try:
            __import__(module_name)
        except ImportError:
            checked[name] = False
            continue
        checked[name] = True
        yield name
