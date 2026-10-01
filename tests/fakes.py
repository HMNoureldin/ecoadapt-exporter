from typing import Dict, List, Callable, Optional
from ecoadapt_exporter.models import Measurement
from ecoadapt_exporter.transport import Transport



class FakeTransport(Transport):
    """
    In-memory implementation of the Modbus transport.

    register_map maps a Modbus register address to the
    registers that should be returned from that address.
    """

    def __init__(self, register_map: Dict[int, List[int]]):
        self.register_map = register_map
        self.connect_called = False
        self.close_called = False

    def connect(self) -> None:
        self.connect_called = True

    def close(self) -> None:
        self.close_called = True

    def read_input_registers(
        self,
        address: int,
        count: int,
    ) -> List[int]:
        registers = self.register_map.get(address)

        if registers is None:
            raise ValueError(
                "No fake registers configured for address {}".format(
                    address
                )
            )

        return registers[:count]


class FakeDevice:
    def __init__(self, measurements):
        self.measurements = measurements
        self.connect_called = False
        self.close_called = False
        self.reads = []

    def connect(self) -> None:
        self.connect_called = True

    def close(self) -> None:
        self.close_called = True

    def read_measurement(
        self,
        definition,
        connector,
        channel,
    ) -> Measurement:
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
    """
    In-memory implementation of the Sender interface.

    Stores sent measurements so tests can inspect them.
    """

    def __init__(self):
        self.connect_called = False
        self.close_called = False
        self.sent = []

    def connect(self, on_connected: Callable[[], None]) -> None:
        self.connect_called = True
        on_connected()

    def close(self) -> None:
        self.close_called = True

    def send(self, measurement: Measurement) -> None:
        self.sent.append(measurement)