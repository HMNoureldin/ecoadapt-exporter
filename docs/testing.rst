Testing and test collaborators
==============================

Unit tests
----------

Run the tests that do not need hardware or a listening server:

.. code-block:: bash

   .venv37/bin/python -m pytest --ignore=tests/test_integration.py -v

``pytest.ini`` limits discovery to ``tests/`` and adds ``src/`` to the import
path, excluding the executable manual script in ``dev/``. ``tests/__init__.py``
makes shared helpers importable as ``tests.fakes``.

.. list-table:: Current test coverage
   :header-rows: 1
   :widths: 30 70

   * - File
     - Checks
   * - ``test_decoder.py``
     - One device FLOAT32 LSW-first example; not all formats/order combinations.
   * - ``test_registers.py``
     - A channel-address example, software version, and MAC decoding.
   * - ``test_models.py``
     - Measurement fields and selected device metadata fields.
   * - ``test_ecoadapt.py``
     - Voltage/frequency and metadata reads from ``FakeTransport``.
   * - ``test_exporter.py``
     - Request processing, different channel selections, lifecycle, and fake delivery.
   * - ``test_sender.py``
     - Abstract interface, initial disconnected state, and rejection before connect.
   * - ``test_integration.py``
     - Fake register reads connected to a real WebSocket sender; manual delivery check.

The unit sender tests do not connect to a WebSocket server. Test doubles isolate
orchestration from network I/O; a fake sender invokes readiness synchronously.
Physical hardware, transport failures, reconnection, and complete decoder edge
cases are not covered by this suite.

Integration smoke test
----------------------

Start ``.venv37/bin/python dev/server.py`` in another terminal, then run:

.. code-block:: bash

   .venv37/bin/python -m pytest tests/test_integration.py -v

The smoke test uses fake registers but the real device reader, exporter, sender,
and Twisted reactor. Its callback runs one cycle and closes resources; a timer
stops the reactor after two seconds. It does not call ``Exporter.start()`` and
does not test periodic scheduling or a physical Modbus connection.

There are no delivery assertions or explicit connection-failure assertions.
A passing test alone does not prove messages arrived. Inspect receiver output
for ``rms_voltage`` and ``frequency`` messages. Run this test in a fresh process
because the shared Twisted reactor is not restartable after stopping.

Test-double reference
---------------------

.. automodule:: tests.fakes
   :members:
   :show-inheritance:
