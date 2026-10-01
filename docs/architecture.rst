Architecture
============

Responsibilities and dependency direction
-----------------------------------------

The application constructs collaborators explicitly. Device access does not
know about WebSockets, and numeric decoding does not know about networking.

.. code-block:: text

   app/exporter-ecoadapt.py  (composition and reactor ownership)
       |
       +--> Exporter --MeasurementRequest--> EcoAdapt
       |       |                              |
       |       |                              +--> Transport --> Modbus TCP sensor
       |       |                              +--> registers + decoder
       |       |                              +--> Measurement / DeviceInfo
       |       |
       |       +--> Sender --> WebSocketSender --> WebSocket receiver
       |
       +--> Twisted reactor (callbacks, timer, shutdown trigger)

.. list-table:: Layer responsibilities
   :header-rows: 1
   :widths: 25 75

   * - Component
     - Responsibility
   * - :doc:`Transport <api/transport>`
     - Connect, close, and read raw input registers; no measurement interpretation.
   * - :doc:`Registers <api/registers>`
     - Describe address ranges, data formats, units, and channel stride.
   * - :doc:`Decoder <api/decoder>`
     - Normalize word/byte significance and turn register values into numbers.
   * - :doc:`EcoAdapt <api/ecoadapt>`
     - Calculate addresses, acquire registers, and construct typed results.
   * - :doc:`Models <api/models>`
     - Immutable measurement and metadata values shared across layers.
   * - :doc:`Exporter <api/exporter>`
     - Process selected requests in order and schedule periodic cycles.
   * - :doc:`Sender <api/sender>`
     - Report connection readiness and serialize measurements as JSON.
   * - :doc:`Application <scripts>`
     - Choose concrete adapters and requests; own CLI options and the reactor.

Startup and shutdown
--------------------

.. code-block:: text

   main()
     -> create_exporter()                 construct objects; no connection yet
     -> register before-shutdown hook
     -> Exporter.start()
          -> EcoAdapt.connect()          synchronous Modbus connection
          -> WebSocketSender.connect()   begin asynchronous WebSocket connection
     -> reactor.run()
          -> ClientProtocol.onOpen()     handshake complete
          -> on_connected()
          -> Exporter._start_loop()
          -> LoopingCall(run_once), now=True

   reactor shutdown
     -> Exporter.stop()
          -> stop active timer
          -> sender.close()
          -> device.close()

The readiness callback avoids guessing when a handshake is complete. The
first export runs immediately after readiness; later cycles use the configured
interval. The exporter itself does not run or stop the reactor.

One measurement cycle
---------------------

For each ``MeasurementRequest``, the exporter asks ``EcoAdapt`` to read its
register definition for that request's connector and channel. Addressing is::

   channel_index = (connector - 1) * 3 + (channel - 1)
   address = definition.start_address + channel_index * definition.words_per_channel

Connectors are numbered 1 through 6 and channels 1 through 3. Address-range
validation ensures the requested words fit within the definition. The transport
reads the raw words, and the decoder applies the definition's format and ordering.
``EcoAdapt`` returns a ``Measurement`` containing identity, value, and unit.
The exporter sends it before moving on to the next request.

For RMS voltage at connector 1/channel 1, the address is 352 and the read
contains two words. Frequency at the same location starts at 424. These
measurements use FLOAT32, MSB-first bytes, and LSW-first words.

The sender emits one JSON text frame per measurement, for example:

.. code-block:: json

   {"measurement": "frequency", "value": 50.92, "unit": "Hz"}

The payload currently has no connector, channel, device identifier, or timestamp.
Selecting multiple channels is possible, but their identity is not preserved in
the outgoing payload. A production protocol would need to address this.

Configuration and device metadata
---------------------------------

Connection settings are CLI options. Measurement selection is a list in
``create_exporter()`` rather than an external configuration file. Each request
owns its connector/channel pair, allowing different locations in one cycle.

``DeviceInfo`` is separate from ``Measurement`` because software version,
Modbus table version, and MAC address are device metadata. They can be queried
with ``read_device_info()`` but are not periodically exported by the application.
Special version/MAC decoding uses the identity of the register constants;
``GeneralRegisterDefinition.encoding`` is descriptive metadata, not a generic
dispatch mechanism in the current reader. Circuit configuration has a decoder
helper but no dedicated high-level reader; it is not a measurement.

Decoder flow
------------

.. image:: _static/decoder-flow.svg
   :alt: Copy and validate registers, normalize word and byte order, then unpack a number.
   :width: 640px

``decode_registers`` copies the iterable, validates count and unsigned register
values, optionally reverses words, optionally swaps bytes within each word,
and always unpacks the normalized bytes as big-endian. This preserves the
caller's register list. Format and size tables are independent of device access.

Failure behavior and proof-of-concept boundaries
------------------------------------------------

A failed connection raises ``ConnectionError``; an error Modbus response raises
``IOError``. Invalid register values or addressing raise ``ValueError``. Sending
without an open WebSocket raises ``RuntimeError``. These exceptions are not
converted into retries. A failed read/send interrupts that cycle; previous
messages may already have been sent. A failing ``LoopingCall`` stops; the
exporter does not attach recovery logic to its failure result.

The Modbus client is synchronous and can block the Twisted event loop. A sender
close clears its protocol, but does not automatically stop polling or reconnect.
Shutdown requests a WebSocket close; it does not wait for delivery acknowledgements,
and cleanup exceptions are not isolated from later cleanup steps.

The implementation does not provide TLS setup (it uses ``connectTCP``),
authentication, buffering, persistence, reconnect/backoff, structured monitoring,
or a deployment service. Future work includes nonblocking device reads, explicit
failure policies, external customer mappings, payload source identity, and hardware
validation. The existing separation allows alternate transports and senders to be
introduced without embedding those concerns in register decoding.
