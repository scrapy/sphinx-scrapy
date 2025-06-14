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

Sphinx_ extension for documentation in the Scrapy_ ecosystem.

.. _Sphinx: https://www.sphinx-doc.org/
.. _Scrapy: https://scrapy.org/


Features
========

-   Automatic configuration of intersphinx_ for Python_, Scrapy_.

    Ready-to-use, easy-to-enable configuration for the following packages of
    the Scrapy_ ecosystem is also available:

    .. _intersphinx: https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html
    .. _Python: https://docs.python.org/

    | `attrs <https://www.attrs.org/en/stable/>`_
    | `cssselect <https://cssselect.readthedocs.io/en/latest>`_
    | `itemloaders <https://itemloaders.readthedocs.io/en/latest/>`_
    | `parsel <https://parsel.readthedocs.io/en/latest/>`_
    | `python-zyte-api <https://python-zyte-api.readthedocs.io/en/stable/>`_
    | `scrapy-poet <https://scrapy-poet.readthedocs.io/en/stable/>`_
    | `tenacity <https://tenacity.readthedocs.io/en/latest>`_
    | `twisted <https://docs.twisted.org/en/stable/>`_ (and `twistedapi <https://docs.twisted.org/en/stable/api/>`_)
    | `w3lib <https://w3lib.readthedocs.io/en/latest/>`_
    | `web-poet <https://web-poet.readthedocs.io/en/stable/>`_
    | `zyte <https://docs.zyte.com>`_
    | `zyte-common-items <https://zyte-common-items.readthedocs.io/en/latest>`_
    | `zyte-spider-templates <https://zyte-spider-templates.readthedocs.io/en/latest>`_

    To automatically configure intersphinx for any of those packages if
    installed, add to your ``conf.py`` file:

    .. code-block:: python

        scrapy_intersphinx_enable_installed = True

    You can also enable or disable the automatic intersphinx configuration of
    packages manually:

    .. code-block:: python

        scrapy_intersphinx_enable = [
            "parsel",
            "w3lib",
        ]
        scrapy_intersphinx_disable = [
            "scrapy",
        ]

-   Automatic configuration of Sphinx roles of the Scrapy documentation, so
    that you can easily link to Scrapy settings, request metadata keys, signals
    and commands:

    .. code-block:: rst

        :setting:`BOT_NAME`
        :setting:`LOG_LEVEL <scrapy:LOG_LEVEL>`
        :reqmeta:`download_slot`
        :signal:`spider_opened`
        :command:`crawl`


Setup
=====

#.  Install:

    .. code-block:: shell

        pip install sphinx-scrapy

#.  Add to your ``conf.py``:

    .. code-block:: python

        extensions = [
            "sphinx_scrapy",
        ]


Release notes
=============

See `Release notes`_ for a list of releases and their changes.

.. _Release notes: https://github.com/scrapy/sphinx-scrapy/blob/main/CHANGES.rst
