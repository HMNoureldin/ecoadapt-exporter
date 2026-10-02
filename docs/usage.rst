Setup and usage
===============

Makefile shortcuts
------------------

Run ``make help`` from the project root to list available commands. Targets use
``.venv37/bin/python`` directly; activation is optional.

.. code-block:: bash

   make install       # Create the environment if missing; install all dependencies
   make check         # Python version and dependency consistency
   make test          # Unit tests without network services
   make server        # Development receiver; leave running in another terminal
   make test-integration  # Smoke test against the receiver on port 9000
   make sender        # Manual sample sender to port 9000
   make run           # Exporter; requires a reachable Modbus device
   make docs          # Fresh HTML build, failing on warnings
   make show-docs     # Build and serve at http://localhost:8000
   make clean         # Delete generated docs and project caches, retaining the environment

These commands are alternatives, not a script to run sequentially: server and
application targets stay running until Ctrl+C. The integration smoke test still
requires manual inspection of receiver output to confirm delivery.

Override ``PYTHON`` when creating an environment, for example
``make install PYTHON="$HOME/.pyenv/versions/3.7.17/bin/python"``.
Use ``make run ARGS="--help"`` for application options or
``make test TEST_ARGS="-k frequency"`` to filter tests. ``VENV`` changes the
environment path. ``DOCS_PORT`` changes the documentation server port;
``SERVER_PORT`` changes the development receiver port. The manual sender and
integration test always use port 9000; for the exporter, match a changed
receiver port by setting ``server_url`` in the JSON file.

``make clean`` does not delete the environment or stop running servers.
Use ``make clean-venv`` to delete the environment and its installed packages
(default ``.venv37``, or the ``VENV`` override). Stop processes using it and
run ``deactivate`` if active first. Recreate it with ``make install``, using
the ``PYTHON`` override above if needed. Source files and built docs are retained.
The target refuses symlinks and directories without ``pyvenv.cfg``.

One Python environment
----------------------

Run commands from the project root. The assignment targets Python 3.7.3;
the local environment has been validated with Python 3.7.17. Exact 3.7.3 runtime
execution has not been verified.

.. code-block:: bash

   python3.7 -m venv .venv37
   source .venv37/bin/activate
   python -m pip install -r requirements-dev.txt -r requirements-docs.txt
   python -m pip check

If using pyenv without its shims, replace ``python3.7`` in the first command
with ``~/.pyenv/versions/3.7.17/bin/python``. Select ``.venv37/bin/python`` in
your IDE. PyModbus 2.5.3 supplies the ``client.sync``/``unit`` APIs used by the
transport; the other pinned tools also support this Python environment.

Start the receiver and exporter
-------------------------------

Start the development receiver in one terminal:

.. code-block:: bash

   .venv37/bin/python dev/server.py

It defaults to port 9000, binds ``0.0.0.0`` (all interfaces), and prints incoming
messages. ``--port`` changes its port. It is a debugging tool without storage.

With a reachable physical Modbus device, run the exporter in another terminal:

.. code-block:: bash

   make run

This automatically reads ``config.json``. Use ``make run CONFIG=other.json``
to choose a different file. ``--help`` prints options without connecting.
Use a plain ``ws://`` endpoint; this sender does not configure TLS.
The receiver must accept the ``ecoadapt-v1`` WebSocket subprotocol. Ctrl+C
initiates reactor shutdown and exporter cleanup. See :doc:`testing` to exercise
the project without hardware.

Logging
-------

The application configures a shared standard-library logger and injects it into
``Exporter``, ``EcoAdapt``, ``ModbusTcpTransport``, and ``WebSocketSender`` via
the optional ``logger=`` constructor argument. Without injection, these classes
use their module logger; they do not configure handlers. Immutable data models
and decoder functions do not require logger instances. Autobahn creates protocol
instances itself; callbacks use the sender's injected logger.

.. code-block:: bash

   make run

Set ``"log_level": "DEBUG"`` in your JSON file for debugging.
The default threshold is INFO. Supported levels are DEBUG, INFO, WARNING,
ERROR, and CRITICAL, in increasing severity; the selected level and higher
severities are emitted. Values are case insensitive. Logs go to stderr with a
local timestamp (including milliseconds), severity, logger name, source filename,
and source line number, for example::

   2026-10-01 14:30:00,123 INFO ecoadapt_exporter exporter.py:90 Starting exporter (interval=10.0 seconds)

DEBUG includes register reads, decoded values, export cycles, and queued JSON;
INFO covers lifecycle events; WARNING reports connection retries and unclean
WebSocket closure; ERROR
reports transport and disconnected-send failures. Export-cycle errors propagate
without a custom failure handler. Modbus connection setup retries up to three
attempts, with five seconds between failures; export cycles are not retried. Log
configuration affects this application's logger hierarchy, not all third-party
libraries or Python warnings. Repeated configuration avoids duplicate handlers.

JSON configuration
------------------

.. code-block:: bash

   make run

Edit ``config.json`` to set the six connection, polling, and logging settings.
The file is included in the project and is not ignored by Git. Files are loaded only with ``--config``;
relative paths use the current working directory. File values replace defaults;
missing settings retain their defaults. When running the Python application directly without ``--config``, all defaults
apply. ``make run`` supplies ``--config config.json`` automatically.
Unreadable files, malformed JSON, and unknown keys produce a CLI error.
Use JSON numbers for numeric settings and a plain ``ws://`` receiver URL.
Measurement selection remains in the application request list.

.. literalinclude:: ../config.json
   :language: json

Select measurements
-------------------

Edit the request list in ``app/exporter-ecoadapt.py`` to change selection:

.. code-block:: python

   from ecoadapt_exporter.exporter import MeasurementRequest
   from ecoadapt_exporter.registers import RMS_VOLTAGE, FREQUENCY

   measurements = [
       MeasurementRequest(RMS_VOLTAGE, connector=1, channel=1),
       MeasurementRequest(FREQUENCY, connector=2, channel=3),
   ]

The application currently uses connector 1/channel 1 for both. The address
map contains additional measurement definitions; the default CLI does not
select all of them. See :doc:`architecture` for payload identity limitations.

Read device metadata
--------------------

Start an interactive interpreter with ``PYTHONPATH=src .venv37/bin/python``:

.. code-block:: python

   from ecoadapt_exporter.ecoadapt import EcoAdapt
   from ecoadapt_exporter.transport import ModbusTcpTransport
   from ecoadapt_exporter.registers import SOFTWARE_VERSION, MODBUS_TABLE_VERSION, MAC_ADDRESS

   device = EcoAdapt(ModbusTcpTransport("169.254.20.1"))
   device.connect()
   try:
       info = device.read_device_info([SOFTWARE_VERSION, MODBUS_TABLE_VERSION, MAC_ADDRESS])
       print(info)
   finally:
       device.close()

Decode values without a connection
----------------------------------

The package uses a ``src`` layout: running Python in the root alone does not
make it importable. Set ``PYTHONPATH=src`` as above (pytest configures this itself).

.. code-block:: python

   from ecoadapt_exporter.decoder import DataType, WordOrder, decode_registers

   assert decode_registers([0x0001, 0x0002], DataType.UINT32) == 65538
   assert decode_registers([0x3F80, 0x0000], DataType.FLOAT32) == 1.0
   assert decode_registers(
       [0x0000, 0x3F80], DataType.FLOAT32, word_order=WordOrder.LSW_FIRST
   ) == 1.0

.. list-table:: Supported numeric formats
   :header-rows: 1

   * - Type
     - Registers
     - Python result
   * - UINT16 / INT16
     - 1
     - int
   * - UINT32 / INT32
     - 2
     - int
   * - FLOAT32
     - 2
     - float
   * - FLOAT64
     - 4
     - float

The defaults are MSB-first bytes and MSW-first words. LSW-first reverses the
word sequence; LSB-first swaps bytes inside each word. The final unpack always
uses big-endian after normalization. Use enum members for ordering arguments.
Bad register count, non-integer words, and values outside 0 through 65535 raise
``ValueError``.

Build and view documentation
----------------------------

.. code-block:: bash

   .venv37/bin/python -m sphinx -E -a -W --keep-going -b html docs docs/_build/html
   .venv37/bin/python -m http.server 8000 --bind 127.0.0.1 --directory docs/_build/html

Visit http://localhost:8000 and use Ctrl+C to stop the server. Rebuild after
editing source docstrings or RST pages. ``-E -a`` forces a fresh build and ``-W``
fails on warnings. Generated HTML and the virtual environment are ignored by Git.
