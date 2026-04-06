=============
Release notes
=============

0.7.1 (unreleased)
==================

-   Fixed the generated Read the Docs configuration, which was causing builds
    to fail.

-   When the pre-commit hook fails, it now reports that it updated
    :file:`.readthedocs.yml`.

0.7.0 (2026-04-02)
==================

-   Dropped support for Python 3.8 and 3.9, added official support for Python
    3.14.

-   Added a tox plugin that provides a ``docs`` environment.

-   Added a pre-commit hook to create or update ``.readthedocs.yml``.

-   Enabling the ``sphinx_scrapy`` extension now automatically enables
    ``sphinx.ext.autodoc``, ``sphinx.ext.viewcode``, ``sphinx_copybutton``, and
    ``sphinx_llms_txt``.

-   Added a "Copy as Markdown" button on HTML pages that copies each page's
    corresponding ``.md`` counterpart.

-   | Extended easy intersphinx configuration to
    | `coverage <https://coverage.readthedocs.io/en/latest>`_
    | `cryptography <https://cryptography.io/en/latest/>`_
    | `multidict <https://multidict.aio-libs.org/en/latest/>`_
    | `sphinx <https://www.sphinx-doc.org/en/master>`_
    | `tox <https://tox.wiki/en/latest/>`_

0.6.1 (2025-09-16)
==================

Fixed Python 3.8 support.


0.6.0 (2025-09-16)
==================

| Extended easy intersphinx configuration to:
| `pydantic <https://docs.pydantic.dev/latest/>`_


0.5.0 (2025-09-16)
==================

Change the minimum version of Python from 3.9 to 3.8.


0.4.0 (2025-09-16)
==================

| Extended easy intersphinx configuration to:
| `packaging <https://packaging.pypa.io/en/stable/>`_
| `pytest <https://docs.pytest.org/en/stable/>`_


0.3.0 (2025-09-02)
==================

| Extended easy intersphinx configuration to:
| `jinja <https://jinja.palletsprojects.com/en/latest/>`_
| `lxml <https://lxml.de/apidoc/>`_


0.2.0 (2025-06-16)
==================

| Extended easy intersphinx configuration to:
| `dateparser <https://dateparser.readthedocs.io/en/latest/>`_
| `form2request <https://form2request.readthedocs.io/en/latest/>`_
| `formasaurus <https://formasaurus.readthedocs.io/en/latest/>`_
| `python-scrapinghub <https://python-scrapinghub.readthedocs.io/en/latest/>`_
| `scrapy-spider-metadata <https://scrapy-spider-metadata.readthedocs.io/en/latest/>`_
| `scrapy-zyte-api <https://scrapy-zyte-api.readthedocs.io/en/latest/>`_
| `scrapy-zyte-smartproxy <https://scrapy-zyte-smartproxy.readthedocs.io/en/latest/>`_
| `scrapyd <https://scrapyd.readthedocs.io/en/latest/>`_
| `shub <https://shub.readthedocs.io/en/latest/>`_
| `shub-image <https://shub-image.readthedocs.io/en/latest/>`_
| `spidermon <https://spidermon.readthedocs.io/en/latest/>`_
| `url-matcher <https://url-matcher.readthedocs.io/en/stable/>`_
| `zyte-parsers <https://zyte-parsers.readthedocs.io/en/latest/>`_


0.1.0 (2025-06-14)
==================

Initial release.
