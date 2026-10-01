# EcoAdapt Exporter

A proof-of-concept exporter for reading measurements from an Eco-Adapt
sensor over Modbus TCP and forwarding them to a server over WebSocket.

The current implementation reads:

-   RMS voltage
-   Frequency

It also supports selected general device information:

-   Software version
-   Modbus table version
-   MAC address

The project is intentionally scoped as a proof of concept for the
assignment. It focuses on demonstrating the communication flow,
testability without a physical sensor, and a structure that can be
extended into a production solution.

## Architecture

``` text
                   exporter-ecoadapt.py
                           |
                           v
                +----------------------+
                |       Exporter       |
                +----------+-----------+
                           |
              +------------+------------+
              |                         |
              v                         v
        +-----------+             +-------------+
        | EcoAdapt  |             | WebSocket   |
        |           |             | Sender      |
        +-----+-----+             +-------------+
              |
              v
     +-------------------+
     | Modbus Transport  |
     +---------+---------+
               |
               v
        Eco-Adapt sensor
```

### Transport

`ModbusTcpTransport` is responsible for communication with the sensor
using Modbus TCP.

It provides a small transport interface used by `EcoAdapt`, keeping
device-specific register decoding separate from the communication
mechanism.

The transport can be replaced by `FakeTransport` in tests, so the
application can be tested without a physical Modbus device.

### EcoAdapt

`EcoAdapt` contains the device-specific logic:

-   Modbus register definitions
-   measurement definitions
-   register decoding
-   connector and channel handling
-   general device information decoding

The device returns typed `Measurement` objects for measurements. General
device information is represented separately because it is not a
measurement.

### Exporter

`Exporter` orchestrates the measurement flow.

A `MeasurementRequest` contains:

-   measurement definition
-   connector
-   channel

Connector and channel are therefore configured per measurement rather
than globally.

For example:

``` python
MeasurementRequest(
    definition=RMS_VOLTAGE,
    connector=1,
    channel=1,
)

MeasurementRequest(
    definition=FREQUENCY,
    connector=2,
    channel=3,
)
```

The current application configuration uses connector 1 and channel 1 for
both voltage and frequency.

### WebSocket sender

`WebSocketSender` sends measurements to the configured WebSocket server.

The WebSocket connection is asynchronous. The sender uses a connection
callback:

``` text
connect()
    |
    v
WebSocket handshake
    |
    v
onOpen()
    |
    v
on_connected()
    |
    v
Exporter starts periodic measurements
```

This avoids relying on an arbitrary sleep or delay to determine whether
the connection is ready.

The development server is provided in `dev/server.py`.

## Project structure

```text
ecoadapt-exporter/
├── app/
│   └── exporter-ecoadapt.py       # Command-line entry point
├── src/
│   └── ecoadapt_exporter/
│       ├── __init__.py
│       ├── decoder.py
│       ├── ecoadapt.py
│       ├── exporter.py
│       ├── models.py
│       ├── registers.py
│       ├── sender.py
│       └── transport.py
├── tests/
│   ├── __init__.py
│   ├── fakes.py
│   ├── test_decoder.py
│   ├── test_ecoadapt.py
│   ├── test_exporter.py
│   ├── test_integration.py
│   ├── test_models.py
│   ├── test_registers.py
│   └── test_sender.py
├── dev/
│   ├── server.py                  # Local WebSocket server
│   └── test_sender.py             # Manual sender smoke test
├── docs/
│   ├── _static/                   # Custom CSS and architecture diagram
│   ├── api/                       # Individual API reference pages
│   ├── api.rst
│   ├── architecture.rst
│   ├── conf.py
│   ├── index.rst
│   └── usage.rst
├── .gitignore
├── pytest.ini
├── requirements.txt              # Runtime dependencies
├── requirements-dev.txt          # Runtime and test dependencies
├── requirements-docs.txt         # Documentation dependencies
└── README.md
```

The application entry point is under `app/`, and the reusable package is
under `src/ecoadapt_exporter/`. Tests and test doubles are under `tests/`,
while manual development tools are under `dev/`.

The local `.venv37/` environment and generated `docs/_build/` directory
are excluded from Git and omitted from the tree above.

## Installation and Python compatibility

The assignment requires compatibility with Python 3.7.3. Development and
testing are therefore performed in a Python 3.7 environment.

Use one virtual environment, `.venv37`, for the application, tests, and
documentation.

From the project root:

``` bash
python3.7 -m venv .venv37
source .venv37/bin/activate
python -m pip install -r requirements-dev.txt -r requirements-docs.txt
python -m pip check
```

If Python was installed with pyenv and `python3.7` is not on your PATH,
use:

``` bash
~/.pyenv/versions/3.7.17/bin/python
```

when creating the environment.

For subsequent sessions, activate `.venv37` before running commands. In
an IDE, select `.venv37/bin/python` as the project interpreter.

Runtime dependencies are declared in `requirements.txt`.

PyModbus is pinned to 2.5.3 because the transport uses its `client.sync`
import and `unit` argument. Upgrading to PyModbus 3.x requires updating
the transport adapter.

Autobahn, Twisted, and the development dependencies are pinned to
versions compatible with Python 3.7. Install dependencies using the
target interpreter so pip selects compatible transitive dependencies.

## Running the tests

Run the complete test suite:

``` bash
.venv37/bin/python -m pytest -v
```

The tests cover the main layers independently:

``` text
test_ecoadapt.py
    FakeTransport
        |
        v
    EcoAdapt

test_exporter.py
    FakeDevice
        |
        v
    Exporter
        |
        v
    FakeSender

test_sender.py
    WebSocketSender
        |
        v
    WebSocket server

test_integration.py
    FakeTransport
        |
        v
    EcoAdapt
        |
        v
    Exporter
        |
        v
    WebSocketSender
        |
        v
    dev/server.py
```

### Test doubles

Reusable test doubles are located in `tests/fakes.py`:

-   `FakeTransport` provides predefined Modbus register responses.
-   `FakeDevice` provides predefined `Measurement` responses.
-   `FakeSender` records measurements that would have been sent.

This allows core application logic to be tested without a physical
Eco-Adapt sensor.

### Device tests only

``` bash
.venv37/bin/python -m pytest tests/test_ecoadapt.py -v
```

### Integration smoke test

The integration test requires the local WebSocket server.

Start the server in another terminal:

``` bash
.venv37/bin/python dev/server.py
```

Then run:

``` bash
.venv37/bin/python -m pytest tests/test_integration.py -v
```

The integration test verifies the application flow from the fake Modbus
transport through `EcoAdapt`, `Exporter`, and the real
`WebSocketSender`.

The development server currently prints received messages rather than
exposing them as test assertions, so its output can also be inspected to
confirm receipt.

## Running the development WebSocket server

``` bash
.venv37/bin/python dev/server.py
```

By default it listens on:

``` text
ws://127.0.0.1:9000
```

The server is intended for local development and debugging only.

## Running the exporter

The application entry point is:

``` text
app/exporter-ecoadapt.py
```

Run it with:

``` bash
PYTHONPATH=src .venv37/bin/python app/exporter-ecoadapt.py
```

Default configuration:

``` text
Eco-Adapt host:       169.254.20.1
Modbus port:          502
Modbus unit ID:       1
WebSocket server:     ws://127.0.0.1:9000
Measurement interval: 10 seconds
```

These values can be changed using command-line arguments:

``` bash
PYTHONPATH=src .venv37/bin/python \
    app/exporter-ecoadapt.py \
    --device-host 169.254.20.1 \
    --device-port 502 \
    --unit-id 1 \
    --server-url ws://127.0.0.1:9000 \
    --interval 10
```

The current measurement configuration is defined in the application
entry point. It reads RMS voltage and frequency, with connector and
channel configured per measurement request.

## Configuration decisions

For this proof of concept, the device and server connections are
configurable through command-line arguments.

The measurement list is intentionally kept in the application wiring
rather than introducing a larger configuration system. This keeps the
PoC small while still allowing each measurement to have its own
connector and channel.

For a production implementation, customer-specific measurement
configuration would likely be supplied externally so that mappings could
change without modifying the application code.

## Error handling and connection lifecycle

The application separates Modbus and WebSocket communication from
measurement orchestration.

The transport raises an error when a Modbus connection cannot be
established or a register read fails.

The WebSocket sender raises an error if an attempt is made to send while
the WebSocket is not connected.

The WebSocket connection lifecycle is asynchronous. The exporter starts
periodic measurements only after the sender reports that the WebSocket
connection has been established.

Shutdown is handled by the application entry point. The exporter stops
its periodic loop and closes the sender and device connections.

The PoC does not implement a complete reconnect and retry strategy.

## Production considerations

This implementation is intentionally a proof of concept and is not
production-ready. If the solution were deployed to hundreds of bridges,
I would consider the following areas.

### Connectivity and retries

A production implementation should handle temporary Modbus and WebSocket
failures, including reconnecting after dropped connections, retrying
appropriate reads, exponential backoff, and distinguishing temporary
communication failures from invalid device responses.

### Configuration management

The current measurement configuration is defined in the application
entry point. Production configuration could be supplied externally so
customer-specific connector/channel mappings and enabled measurements do
not require a code change.

### Logging and monitoring

The PoC mainly relies on exceptions and development-server output. A
production implementation should provide structured logging and useful
health/error information such as connection state, failed reads,
WebSocket failures, and reconnect attempts.

### Security

The development setup uses a local, unencrypted WebSocket connection. A
production deployment would need an appropriate authenticated and
encrypted communication mechanism, with suitable credential and
certificate management.

### Deployment

The exporter would need to run as a managed service on the Sensorfact
bridge, with automatic startup, restart handling, configuration
management, log collection, software updates, and compatibility with the
bridge runtime.

### Scaling to many customers

Individual bridge failures should not affect other devices. The exporter
should be independently configurable and restartable, with enough
monitoring to identify devices that are offline or repeatedly failing.

### Testing

The current tests cover register decoding, device behavior, exporter
behavior, sender behavior, and an end-to-end path using a fake Modbus
transport.

A production implementation would benefit from additional tests for
Modbus failures, invalid register data, WebSocket disconnects, reconnect
behavior, malformed configuration, and long-running behavior.

## Limitations of the proof of concept

The following are intentionally outside the current scope:

-   persistent storage
-   cloud-side storage or analysis
-   production authentication
-   production TLS configuration
-   automatic reconnect/backoff
-   production monitoring
-   customer-specific external configuration
-   a production service manager
-   physical-device hardware testing

The goal is to demonstrate the core communication path and provide a
basis for estimating the work required for a production implementation.

## Documentation

Build the documentation in the same Python 3.7 environment used for the
application and tests.

Install the documentation dependencies:

``` bash
.venv37/bin/python -m pip install -r requirements-docs.txt
```

Build the documentation:

``` bash
.venv37/bin/python -m sphinx \
    -E -a -W --keep-going \
    -b html \
    docs \
    docs/_build/html
```

Open:

``` text
docs/_build/html/index.html
```

or serve it locally:

``` bash
.venv37/bin/python -m http.server \
    8000 \
    --bind 127.0.0.1 \
    --directory docs/_build/html
```

Then visit `http://localhost:8000`.

Stop the server with `Ctrl+C`.

The site uses the Read the Docs theme with expandable sidebar
navigation, separate function and enum pages, search, source links,
usage examples, and an architecture page with an offline SVG flow
diagram.

Rebuild the documentation after editing docstrings or documentation. Add
new modules to `docs/api.rst` using `automodule` directives as the
package grows.

## Development notes

`pytest.ini` adds `src/` to the test import path.

For commands executed directly from the project root, `PYTHONPATH=src`
can also be used explicitly when needed:

``` bash
PYTHONPATH=src .venv37/bin/python ...
```
