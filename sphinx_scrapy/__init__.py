from __future__ import annotations

import re
from logging import getLogger
from typing import TYPE_CHECKING

from .config import load_project_config

if TYPE_CHECKING:
    from collections.abc import Generator

    from sphinx.application import Sphinx
    from sphinx.config import Config

logger = getLogger(__name__)

INTERSPHINX_MAPPING = {
    "attrs": ("https://www.attrs.org/en/stable/", None),
    "coverage": ("https://coverage.readthedocs.io/en/latest", None),
    "cryptography": ("https://cryptography.io/en/latest/", None),
    "cssselect": ("https://cssselect.readthedocs.io/en/latest", None),
    "dateparser": ("https://dateparser.readthedocs.io/en/latest/", None),
    "form2request": ("https://form2request.readthedocs.io/en/latest/", None),
    "formasaurus": ("https://formasaurus.readthedocs.io/en/latest/", None),
    "itemloaders": ("https://itemloaders.readthedocs.io/en/latest/", None),
    "jinja": ("https://jinja.palletsprojects.com/en/latest/", None),
    "lxml": ("https://lxml.de/apidoc/", None),
    "multidict": ("https://multidict.aio-libs.org/en/latest/", None),
    "packaging": ("https://packaging.pypa.io/en/stable/", None),
    "parsel": ("https://parsel.readthedocs.io/en/latest/", None),
    "pydantic": ("https://docs.pydantic.dev/latest/", None),
    "pytest": ("https://docs.pytest.org/en/stable/", None),
    "python": ("https://docs.python.org/3", None),
    "python-scrapinghub": (
        "https://python-scrapinghub.readthedocs.io/en/latest/",
        None,
    ),
    "python-zyte-api": ("https://python-zyte-api.readthedocs.io/en/stable", None),
    "scrapy": ("https://docs.scrapy.org/en/latest", None),
    "scrapy-poet": ("https://scrapy-poet.readthedocs.io/en/stable", None),
    "scrapy-spider-metadata": (
        "https://scrapy-spider-metadata.readthedocs.io/en/latest/",
        None,
    ),
    "scrapy-zyte-api": ("https://scrapy-zyte-api.readthedocs.io/en/latest", None),
    "scrapy-zyte-smartproxy": (
        "https://scrapy-zyte-smartproxy.readthedocs.io/en/latest/",
        None,
    ),
    "scrapyd": ("https://scrapyd.readthedocs.io/en/latest/", None),
    "shub": ("https://shub.readthedocs.io/en/latest/", None),
    "shub-image": ("https://shub-image.readthedocs.io/en/latest/", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master", None),
    "spidermon": ("https://spidermon.readthedocs.io/en/latest/", None),
    "tenacity": ("https://tenacity.readthedocs.io/en/latest", None),
    "tox": ("https://tox.wiki/en/latest/", None),
    "twisted": ("https://docs.twisted.org/en/stable/", None),
    "twistedapi": ("https://docs.twisted.org/en/stable/api/", None),
    "url-matcher": ("https://url-matcher.readthedocs.io/en/latest", None),
    "w3lib": ("https://w3lib.readthedocs.io/en/latest", None),
    "web-poet": ("https://web-poet.readthedocs.io/en/stable", None),
    "zyte": ("https://docs.zyte.com", None),
    "zyte-common-items": ("https://zyte-common-items.readthedocs.io/en/latest", None),
    "zyte-parsers": ("https://zyte-parsers.readthedocs.io/en/latest/", None),
    "zyte-spider-templates": (
        "https://zyte-spider-templates.readthedocs.io/en/latest",
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


COPY_AS_MARKDOWN_BUTTON_JS = """
(function () {
    var COPY_ICON = String.fromCodePoint(0x1F4CB);
    var SUCCESS_ICON = String.fromCodePoint(0x2713);
    var ERROR_ICON = String.fromCodePoint(0x26A0);

    function makeLabel(icon, text) {
        return icon + ' ' + text;
    }

    function markdownPathFromCurrentPage(pathname) {
        if (pathname.endsWith('.html')) {
            return pathname.slice(0, -5) + '.md';
        }
        if (pathname.endsWith('/')) {
            return pathname + 'index.md';
        }
        var lastPart = pathname.split('/').pop() || '';
        if (!lastPart.includes('.')) {
            return pathname + '.md';
        }
        return pathname + '.md';
    }

    async function copyToClipboard(text) {
        if (navigator.clipboard && window.isSecureContext) {
            await navigator.clipboard.writeText(text);
            return;
        }
        var textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.setAttribute('readonly', 'readonly');
        textarea.style.position = 'fixed';
        textarea.style.left = '-9999px';
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
    }

    function setTemporaryLabel(button, label) {
        var previousLabel = button.textContent;
        button.textContent = label;
        window.setTimeout(function () {
            button.textContent = previousLabel;
            button.disabled = false;
        }, 1000);
    }

    async function onButtonClick(button) {
        button.disabled = true;
        button.textContent = '...';
        try {
            var mdPath = markdownPathFromCurrentPage(window.location.pathname);
            var response = await fetch(mdPath, { credentials: 'same-origin' });
            if (!response.ok) {
                throw new Error('Unable to fetch markdown source');
            }
            var markdown = await response.text();
            await copyToClipboard(markdown);
            setTemporaryLabel(button, makeLabel(SUCCESS_ICON, 'Copied'));
        } catch (_error) {
            setTemporaryLabel(button, makeLabel(ERROR_ICON, 'Error'));
        }
    }

    function addStyles() {
        var style = document.createElement('style');
        style.textContent = [
            '.scrapy-copy-as-markdown {',
            '  position: fixed;',
            '  right: 1rem;',
            '  bottom: 1rem;',
            '  z-index: 1000;',
            '  border: 1px solid #c9d4de;',
            '  border-radius: 0.45rem;',
            '  background: #ffffff;',
            '  color: #233a50;',
            '  font: inherit;',
            '  font-size: 0.875rem;',
            '  line-height: 1;',
            '  padding: 0.55rem 0.7rem;',
            '  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);',
            '  cursor: pointer;',
            '}',
            '.scrapy-copy-as-markdown:hover {',
            '  background: #f3f7fb;',
            '}',
            '.scrapy-copy-as-markdown:disabled {',
            '  opacity: 0.75;',
            '  cursor: default;',
            '}',
        ].join('\\n');
        document.head.appendChild(style);
    }

    function addButton() {
        if (!document.body || document.querySelector('.scrapy-copy-as-markdown')) {
            return;
        }

        addStyles();
        var button = document.createElement('button');
        button.type = 'button';
        button.className = 'scrapy-copy-as-markdown';
        button.title = 'Copy this page as Markdown';
        button.setAttribute('aria-label', 'Copy this page as Markdown');
        button.textContent = makeLabel(COPY_ICON, 'Copy as Markdown');
        button.addEventListener('click', function () {
            onButtonClick(button);
        });
        document.body.appendChild(button);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', addButton);
    } else {
        addButton();
    }
})();
"""


def setup(app: Sphinx) -> None:
    app.add_config_value(
        "scrapy_intersphinx_enable", [], "env", types=frozenset({list})
    )
    app.add_config_value(
        "scrapy_intersphinx_enable_installed", False, "env", types=frozenset({bool})
    )
    app.add_config_value(
        "scrapy_intersphinx_disable", [], "env", types=frozenset({list})
    )
    app.add_config_value("sitemap_url_scheme", "{link}", "env", types=frozenset({str}))

    for extension in (
        "sphinx.ext.autodoc",
        "sphinx.ext.intersphinx",
        "sphinx.ext.viewcode",
        "sphinx_copybutton",
        "sphinx_llms_txt",
        "sphinx_sitemap",
    ):
        app.setup_extension(extension)
    app.connect("builder-inited", add_copy_as_markdown_button)
    app.connect("config-inited", update_config)

    # https://github.com/scrapy/scrapy/blob/dba37674e6eaa6c2030c8eb35ebf8127cd488062/docs/_ext/scrapydocs.py#L90C16-L110C6
    for crossref_type in ("setting", "signal", "command", "reqmeta"):
        app.add_crossref_type(
            directivename=crossref_type,
            rolename=crossref_type,
        )


def add_copy_as_markdown_button(app: Sphinx) -> None:
    if app.builder.format != "html":
        return
    app.add_js_file(None, body=COPY_AS_MARKDOWN_BUTTON_JS)


def update_config(app: Sphinx, config: Config) -> None:
    configure_intersphinx(config)
    configure_sitemap(config)


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


def configure_sitemap(config: Config) -> None:
    if not config.html_baseurl:
        package: str | None = None
        project_config = load_project_config()
        if project_config.project_id:
            package = project_config.project_id
        elif hasattr(config, "project", None):
            package = re.sub(r"[\s_]+", "-", str(config.project)).lower()
        if not package:
            return
        if package in INTERSPHINX_MAPPING:
            base_url = INTERSPHINX_MAPPING[package][0]
        else:
            base_url = f"https://{package}.readthedocs.io/en/latest/"
        config.html_baseurl = base_url
    if not config.html_baseurl.endswith("/"):
        config.html_baseurl = config.html_baseurl + "/"
        logger.warning("html_baseurl should end with a slash; automatically fixed to %r", config.html_baseurl)


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
