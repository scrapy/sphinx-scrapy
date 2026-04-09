=============
sphinx-scrapy
=============

|version| |python_version|

.. |version| image:: https://img.shields.io/pypi/v/sphinx-scrapy.svg
   :target: https://pypi.org/pypi/sphinx-scrapy
   :alt: PyPI version

.. |python_version| image:: https://img.shields.io/pypi/pyversions/sphinx-scrapy.svg
   :target: https://pypi.org/pypi/sphinx-scrapy
   :alt: Supported Python versions

`Sphinx <https://www.sphinx-doc.org/>`_ extension for documentation in the
`Scrapy <https://scrapy.org/>`_ ecosystem.

Features
========

-   Provides a ``docs`` `tox <https://tox.readthedocs.io/en/latest/>`_
    environment.

-   Generates a `Read the Docs <https://readthedocs.org/>`_ configuration.

-   Enables `commonly-used Sphinx extensions <#sphinx-extensions>`_.

-   Configures `sphinx.ext.intersphinx`_ for `Python
    <https://docs.python.org/>`_ and Scrapy_, and streamlines configuration for
    `additional packages <#intersphinx-packages>`_.

-   Allows you to easily link to Scrapy settings, request metadata keys,
    signals and commands:

    .. code-block:: rst

        :setting:`BOT_NAME`
        :setting:`LOG_LEVEL <scrapy:LOG_LEVEL>`
        :reqmeta:`download_slot`
        :signal:`spider_opened`
        :command:`crawl`

Setup
=====

#.  Configure in ``pyproject.toml`` the Python version for documentation
    builds, e.g.:

    .. code-block:: toml

        [tool.sphinx-scrapy]
        python-version = "3.14"
    
    It must be `supported by Read the Docs
    <https://docs.readthedocs.com/platform/latest/config-file/v2.html#build-tools-python>`_.

#.  Add to ``docs/requirements.txt``:

    .. code-block::

        sphinx-scrapy==0.7.2

#.  Add to ``docs/conf.py``:

    .. code-block:: python

        extensions = [
            "sphinx_scrapy",
        ]

    To automatically configure `sphinx.ext.intersphinx`_ for installed
    `supported packages <#intersphinx-packages>`_, set:

    .. code-block:: python

        scrapy_intersphinx_enable_installed = True

    You can also enable or disable the automatic `sphinx.ext.intersphinx`_
    configuration of packages manually:

    .. code-block:: python

        scrapy_intersphinx_enable = [
            "parsel",
            "w3lib",
        ]
        scrapy_intersphinx_disable = [
            "scrapy",
        ]

    The ``html_baseurl`` option for `sitemap generation
    <https://sphinx-sitemap.readthedocs.io/en/latest/getting-started.html#usage>`_
    is generated automatically based on the project name (``pyproject.toml`` or
    ``conf.py``) and known documentation URLs (the same used for easy
    intersphinx configuration) with a fallback to
    https://<project>.readthedocs.io/en/latest/. You can alternatively define
    the setting yourself in ``conf.py``.

#.  Add to ``docs/.gitignore``:

    .. code-block::

        /_build/

#.  Add to ``.pre-commit-config.yaml``:

    .. code-block:: yaml

        repos:
        - repo: https://github.com/scrapy/sphinx-scrapy
            rev: 0.8.0
            hooks:
            - id: sphinx-scrapy

#.  Add to ``tox.ini``:

    .. code-block:: ini

        [tox]
        requires =
            sphinx-scrapy[tox]==0.8.0
        envlist = …,docs

    .. note:: ``docs`` in ``envlist`` is required.

You can now build the docs with:

.. code-block:: bash

    tox -e docs

.. _sphinx-extensions:

Sphinx extensions
=================

The following Sphinx extensions are automatically enabled when you enable
``sphinx_scrapy``:

-   `sphinx.ext.autodoc
    <https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html>`_

-   `sphinx.ext.intersphinx`_

-   `sphinx.ext.viewcode
    <https://www.sphinx-doc.org/en/master/usage/extensions/viewcode.html>`_

-   `sphinx_copybutton <https://sphinx-copybutton.readthedocs.io/en/latest/>`_

-   `sphinx_llms_txt <https://sphinx-llms-txt.readthedocs.io/en/latest/>`_

.. _intersphinx-packages:

Intersphinx packages
====================

``scrapy_intersphinx_enable`` supports the following packages:

| `attrs <https://www.attrs.org/en/stable/>`_
| `coverage <https://coverage.readthedocs.io/en/latest>`_
| `cryptography <https://cryptography.io/en/latest/>`_
| `cssselect <https://cssselect.readthedocs.io/en/latest>`_
| `dateparser <https://dateparser.readthedocs.io/en/latest/>`_
| `form2request <https://form2request.readthedocs.io/en/latest/>`_
| `formasaurus <https://formasaurus.readthedocs.io/en/latest/>`_
| `itemloaders <https://itemloaders.readthedocs.io/en/latest/>`_
| `jinja <https://jinja.palletsprojects.com/en/latest/>`_
| `lxml <https://lxml.de/apidoc/>`_
| `multidict <https://multidict.aio-libs.org/en/latest/>`_
| `packaging <https://packaging.pypa.io/en/stable/>`_
| `parsel <https://parsel.readthedocs.io/en/latest/>`_
| `pydantic <https://docs.pydantic.dev/latest/>`_
| `pytest <https://docs.pytest.org/en/stable/>`_
| `python-scrapinghub <https://python-scrapinghub.readthedocs.io/en/latest/>`_
| `python-zyte-api <https://python-zyte-api.readthedocs.io/en/stable/>`_
| `scrapy-poet <https://scrapy-poet.readthedocs.io/en/stable/>`_
| `scrapy-spider-metadata <https://scrapy-spider-metadata.readthedocs.io/en/latest/>`_
| `scrapy-zyte-api <https://scrapy-zyte-api.readthedocs.io/en/latest/>`_
| `scrapy-zyte-smartproxy <https://scrapy-zyte-smartproxy.readthedocs.io/en/latest/>`_
| `scrapyd <https://scrapyd.readthedocs.io/en/latest/>`_
| `shub <https://shub.readthedocs.io/en/latest/>`_
| `shub-image <https://shub-image.readthedocs.io/en/latest/>`_
| `sphinx <https://www.sphinx-doc.org/en/master>`_
| `spidermon <https://spidermon.readthedocs.io/en/latest/>`_
| `tenacity <https://tenacity.readthedocs.io/en/latest>`_
| `tox <https://tox.wiki/en/latest/>`_
| `twisted <https://docs.twisted.org/en/stable/>`_ (and `twistedapi <https://docs.twisted.org/en/stable/api/>`_)
| `url-matcher <https://url-matcher.readthedocs.io/en/stable/>`_
| `w3lib <https://w3lib.readthedocs.io/en/latest/>`_
| `web-poet <https://web-poet.readthedocs.io/en/stable/>`_
| `zyte <https://docs.zyte.com>`_
| `zyte-common-items <https://zyte-common-items.readthedocs.io/en/latest>`_
| `zyte-parsers <https://zyte-parsers.readthedocs.io/en/latest/>`_
| `zyte-spider-templates <https://zyte-spider-templates.readthedocs.io/en/latest>`_

Release notes
=============

See the `release notes
<https://github.com/scrapy/sphinx-scrapy/blob/main/CHANGES.rst>`_ for a list of
releases and their changes.

.. _sphinx.ext.intersphinx: https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html