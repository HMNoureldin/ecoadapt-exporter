Project files and maintenance
=============================

Runtime and entry point
-----------------------

.. list-table::
   :header-rows: 1

   * - File
     - Purpose
   * - ``src/ecoadapt_exporter/__init__.py``
     - Package marker and overview; no automatic connections or API re-exports.
   * - ``src/ecoadapt_exporter/decoder.py``
     - Numeric decoding and order/type enums; see :doc:`api/decoder`.
   * - ``src/ecoadapt_exporter/registers.py``
     - Register definitions, units, addressing, and metadata codecs; see :doc:`api/registers`.
   * - ``src/ecoadapt_exporter/models.py``
     - Immutable measurements and metadata; see :doc:`api/models`.
   * - ``src/ecoadapt_exporter/transport.py``
     - Abstract transport and PyModbus adapter; see :doc:`api/transport`.
   * - ``src/ecoadapt_exporter/ecoadapt.py``
     - Device-specific reads; see :doc:`api/ecoadapt`.
   * - ``src/ecoadapt_exporter/sender.py``
     - Sender interface, protocol callbacks, and JSON sending; see :doc:`api/sender`.
   * - ``src/ecoadapt_exporter/exporter.py``
     - Requests and periodic orchestration; see :doc:`api/exporter`.
   * - ``app/exporter-ecoadapt.py``
     - CLI composition and reactor lifecycle; see :doc:`scripts`.

Development and tests
---------------------

``dev/server.py`` and ``dev/test_sender.py`` provide the receiver and manual
sender check described in :doc:`scripts`. Every test module, the package marker,
and ``tests/fakes.py`` are covered in :doc:`testing`.

Configuration and documentation
-------------------------------

.. list-table::
   :header-rows: 1

   * - File or directory
     - Purpose
   * - ``requirements.txt``
     - Runtime pins for PyModbus, Autobahn, and Twisted.
   * - ``requirements-dev.txt``
     - Includes runtime requirements and pins pytest.
   * - ``requirements-docs.txt``
     - Sphinx 5.3.0 and Read the Docs theme 1.3.0 for Python 3.7.
   * - ``pytest.ini``
     - Test discovery and source import-path configuration.
   * - ``.gitignore``
     - Excludes virtual environments, Python caches, and generated documentation.
   * - ``README.md``
     - Repository overview, setup commands, design rationale, and PoC limitations.
   * - ``docs/conf.py``
     - Import paths, autodoc/viewcode extensions, theme settings, and custom CSS.
   * - ``docs/index.rst``
     - Landing page and navigation tree.
   * - ``docs/usage.rst`` and ``docs/architecture.rst``
     - Operating instructions and design/lifecycle explanations.
   * - ``docs/testing.rst``, ``docs/scripts.rst``, and ``docs/project.rst``
     - Tests, executable tools, and this file inventory.
   * - ``docs/api.rst`` and ``docs/api/*.rst``
     - API navigation and generated package references.
   * - ``docs/_static/custom.css``
     - Layout, colors, cards, and responsive styling.
   * - ``docs/_static/decoder-flow.svg``
     - Offline decoder flow illustration.

Adding or changing code
-----------------------

Use reStructuredText docstrings with ``:param name:``, ``:returns:``, and
``:raises Exception:`` fields where relevant. Add new module pages to the API
toctree and update design guides when behavior changes. Do not autodoc-import
scripts that start reactors or network services at import time; use
``literalinclude`` instead. The documentation build imports runtime APIs, so
install both runtime and documentation dependencies in ``.venv37``.

Rebuild with the warning-as-error command in :doc:`usage` and rerun unit tests
after editing docstrings. Generated ``docs/_build/`` files are not source files
and should not be committed.
