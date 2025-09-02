from collections.abc import Generator

from sphinx.application import Sphinx
from sphinx.config import Config

INTERSPHINX_MAPPING = {
    "attrs": ("https://www.attrs.org/en/stable/", None),
    "cssselect": ("https://cssselect.readthedocs.io/en/latest", None),
    "dateparser": ("https://dateparser.readthedocs.io/en/latest/", None),
    "form2request": ("https://form2request.readthedocs.io/en/latest/", None),
    "formasaurus": ("https://formasaurus.readthedocs.io/en/latest/", None),
    "itemloaders": ("https://itemloaders.readthedocs.io/en/latest/", None),
    "jinja": ("https://jinja.palletsprojects.com/en/latest/", None),
    "lxml": ("https://lxml.de/apidoc/", None),
    "parsel": ("https://parsel.readthedocs.io/en/latest/", None),
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
    "spidermon": ("https://spidermon.readthedocs.io/en/latest/", None),
    "tenacity": ("https://tenacity.readthedocs.io/en/latest", None),
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

    app.setup_extension("sphinx.ext.intersphinx")
    app.connect("config-inited", update_config)

    # https://github.com/scrapy/scrapy/blob/dba37674e6eaa6c2030c8eb35ebf8127cd488062/docs/_ext/scrapydocs.py#L90C16-L110C6
    for crossref_type in ("setting", "signal", "command", "reqmeta"):
        app.add_crossref_type(
            directivename=crossref_type,
            rolename=crossref_type,
        )


def update_config(app: Sphinx, config: Config) -> None:
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
