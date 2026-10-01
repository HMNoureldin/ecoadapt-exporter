from abc import ABC, abstractmethod
from typing import List

from pymodbus.client.sync import ModbusTcpClient


class Transport(ABC):
    """
    Base interface for communication with the Eco-Adapt device.
    """

    @abstractmethod
    def connect(self) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass

    @abstractmethod
    def read_input_registers(
        self,
        address: int,
        count: int,
    ) -> List[int]:
        pass


class ModbusTcpTransport(Transport):
    """
    Modbus TCP implementation of the Transport interface.
    """

    DEFAULT_PORT = 502
    DEFAULT_UNIT_ID = 1

    def __init__(
        self,
        host: str,
        port: int = DEFAULT_PORT,
        unit_id: int = DEFAULT_UNIT_ID,
    ):
        self.host = host
        self.port = port
        self.unit_id = unit_id

        self._client = ModbusTcpClient(
            host=self.host,
            port=self.port,
        )

    def connect(self) -> None:
        connected = self._client.connect()

        if not connected:
            raise ConnectionError(
                "Could not connect to Eco-Adapt device at {}:{}".format(
                    self.host,
                    self.port,
                )
            )

    def close(self) -> None:
        self._client.close()

    def read_input_registers(
        self,
        address: int,
        count: int,
    ) -> List[int]:
        response = self._client.read_input_registers(
            address,
            count,
            unit=self.unit_id,
        )

        if response.isError():
            raise IOError(
                "Failed to read {} input register(s) "
                "starting at address {}".format(
                    count,
                    address,
                )
            )

        return response.registers