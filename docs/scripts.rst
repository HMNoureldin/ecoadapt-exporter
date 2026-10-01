Application and development scripts
===================================

Application entry point
-----------------------

``app/exporter-ecoadapt.py`` constructs ``ModbusTcpTransport``, ``EcoAdapt``,
``WebSocketSender``, and ``Exporter``. ``create_exporter()`` accepts device host,
port, unit ID, receiver URL, and interval, and returns an unconnected exporter.
``main()`` parses CLI settings, registers cleanup, starts connection setup, and
runs the reactor. See :doc:`usage` for commands and :doc:`architecture` for lifecycle.

The source is included rather than imported under its hyphenated filename:

.. literalinclude:: ../app/exporter-ecoadapt.py
   :language: python
   :linenos:

Development receiver
--------------------

``dev/server.py`` is an asyncio WebSocket receiver. Its ``MyServerProtocol``
logs connection events and incoming text/binary frames. ``--port`` defaults to
9000; the listener binds all interfaces. It prints messages but does not assert,
store, or acknowledge their contents at application level.

.. literalinclude:: ../dev/server.py
   :language: python
   :pyobject: MyServerProtocol

Manual sender check
-------------------

``dev/test_sender.py`` sends a sample frequency measurement (50.92 Hz) after
handshake, then schedules connection close and reactor stop. Run it with a
receiver already listening:

.. code-block:: bash

   PYTHONPATH=src .venv37/bin/python dev/test_sender.py

This is a manual script, not a pytest test. It starts networking when executed
or imported, so documentation includes its source without importing it.

.. literalinclude:: ../dev/test_sender.py
   :language: python
   :linenos:
