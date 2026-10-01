# EcoAdapt Exporter

Python utilities for decoding 16-bit register values.

## Tests

From the project root, create and activate a development environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pytest -v
```

For subsequent sessions, activate `.venv` before running tests. To run only
the device tests without activating the environment:

```bash
.venv/bin/python -m pytest tests/test_ecoadapt.py -v
```

Runtime dependencies are declared in `requirements.txt`. PyModbus is pinned
to 2.5.3 because the transport uses its `client.sync` import and `unit` argument;
upgrading to 3.x requires updating that adapter.

`pytest.ini` adds `src/` to the test import path.

## Documentation

The documentation tooling requires Python 3.11 or newer. From the project root:

```bash
python3 -m venv .venv-docs
.venv-docs/bin/python -m pip install -r requirements-docs.txt
.venv-docs/bin/python -m sphinx -W --keep-going -b html docs docs/_build/html
```

Open `docs/_build/html/index.html` in your browser, or serve the site locally:

```bash
.venv-docs/bin/python -m http.server 8000 --bind 127.0.0.1 --directory docs/_build/html
```

Visit <http://localhost:8000>. Stop the server with Ctrl+C.

The site uses the Read the Docs theme with expandable sidebar navigation,
separate function and enum pages, search, source links, and usage examples,
and an architecture page with an offline SVG flow diagram. Rebuild after
editing docstrings or documentation. Add new modules to `docs/api.rst`
using `automodule` directives as the package grows.
