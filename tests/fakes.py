"""In-memory collaborators used to test the device and exporter without hardware."""

from typing import Dict, List, Callable, Optional
from ecoadapt_exporter.models import Measurement
from ecoadapt_exporter.transport import Transport



class FakeTransport(Transport):
    """Map starting addresses to deterministic raw-register responses.

    :param register_map: Mapping of starting addresses to register lists.

    Connection calls set flags; no sockets are opened.
    """

    def __init__(self, register_map: Dict[int, List[int]]):
        self.register_map = register_map
        self.connect_called = False
        self.close_called = False

    def connect(self) -> None:
        """Record that connection establishment was requested.
        """
        self.connect_called = True

    def close(self) -> None:
        """Record that connection cleanup was requested.
        """
        self.close_called = True

    def read_input_registers(
        self,
        address: int,
        count: int,
    ) -> List[int]:
        """Return a slice of the configured response.

        :param address: Exact mapping key to look up.
        :param count: Maximum number of registers to return.
        :returns: Up to ``count`` registers; short responses are not rejected here.
        :raises ValueError: If the starting address has no configured response.
        """
        registers = self.register_map.get(address)

        if registers is None:
            raise ValueError(
                "No fake registers configured for address {}".format(
                    address
                )
            )

        return registers[:count]


class FakeDevice:
    """Record measurement requests and return preconfigured values.

    :param measurements: Mapping from register definitions to measurements.
    """
    def __init__(self, measurements):
        self.measurements = measurements
        self.connect_called = False
        self.close_called = False
        self.reads = []

    def connect(self) -> None:
        """Record that device connection was requested.
        """
        self.connect_called = True

    def close(self) -> None:
        """Record that device cleanup was requested.
        """
        self.close_called = True

    def read_measurement(
        self,
        definition,
        connector,
        channel,
    ) -> Measurement:
        """Record a request and return the mapped measurement.

        :param definition: Register definition used as a mapping key.
        :param connector: Connector to record.
        :param channel: Channel to record.
        :returns: The preconfigured measurement.
        :raises ValueError: If no measurement is configured for the definition.
        """
        self.reads.append(
            {
                "definition": definition,
                "connector": connector,
                "channel": channel,
            }
        )

        measurement = self.measurements.get(definition)

        if measurement is None:
            raise ValueError(
                "No fake measurement configured for definition"
            )

        return measurement


class FakeSender:
    """Record sent measurements and invoke readiness callbacks synchronously.
    """

    def __init__(self):
        self.connect_called = False
        self.close_called = False
        self.sent = []

    def connect(self, on_connected: Callable[[], None]) -> None:
        """Record connection and immediately report readiness.

        :param on_connected: Zero-argument callback to invoke synchronously.
        """
        self.connect_called = True
        on_connected()

    def close(self) -> None:
        """Record that sender cleanup was requested.
        """
        self.close_called = True

    def send(self, measurement: Measurement) -> None:
        """Append a measurement to the recorded messages.

        :param measurement: Measurement object to retain in ``sent``.
        """
        self.sent.append(measurement)