"""Synchronous register acquisition through a replaceable transport interface."""

import logging
from abc import ABC, abstractmethod
from typing import List, Optional

from pymodbus.client.sync import ModbusTcpClient


class Transport(ABC):
    """Interface for connection lifecycle and raw input-register reads.
    """

    @abstractmethod
    def connect(self) -> None:
        """Establish the device connection or raise an implementation-specific error.
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """Release the device connection.
        """
        pass

    @abstractmethod
    def read_input_registers(
        self,
        address: int,
        count: int,
    ) -> List[int]:
        """Read consecutive input registers.

        :param address: First register address.
        :param count: Number of 16-bit registers requested.
        :returns: A list of raw register integers.
        """
        pass


class ModbusTcpTransport(Transport):
    """PyModbus 2.x adapter for synchronous Modbus TCP reads.

    :param host: Device hostname or IP address.
    :param port: TCP port; defaults to 502.
    :param unit_id: Modbus unit identifier; defaults to 1.
    :param logger: Optional shared logger; defaults to this module's logger.
    """

    DEFAULT_PORT = 502
    DEFAULT_UNIT_ID = 1

    def __init__(
        self,
        host: str,
        port: int = DEFAULT_PORT,
        unit_id: int = DEFAULT_UNIT_ID,
        logger: Optional[logging.Logger] = None,
    ):
        self.logger = logger if logger is not None else logging.getLogger(__name__)
        self.host = host
        self.port = port
        self.unit_id = unit_id

        self._client = ModbusTcpClient(
            host=self.host,
            port=self.port,
        )

    def connect(self) -> None:
        """Open the underlying TCP connection.

        :raises ConnectionError: If the PyModbus client cannot connect.
        """
        self.logger.info("Connecting to Modbus device %s:%s (unit %s)", self.host, self.port, self.unit_id)
        connected = self._client.connect()

        if not connected:
            self.logger.error("Modbus connection failed: %s:%s", self.host, self.port)
            raise ConnectionError(
                "Could not connect to Eco-Adapt device at {}:{}".format(
                    self.host,
                    self.port,
                )
            )

    def close(self) -> None:
        """Close the underlying PyModbus client.
        """
        self.logger.info("Closing Modbus connection")
        self._client.close()

    def read_input_registers(
        self,
        address: int,
        count: int,
    ) -> List[int]:
        """Read raw values using the configured Modbus unit identifier.

        :param address: First input-register address.
        :param count: Number of registers requested.
        :returns: The register list supplied by PyModbus.
        :raises IOError: If the device response reports a Modbus error.

        This adapter does not validate returned register count or implement retries.
        """
        self.logger.debug("Reading input registers address=%s count=%s unit=%s", address, count, self.unit_id)
        response = self._client.read_input_registers(
            address,
            count,
            unit=self.unit_id,
        )

        if response.isError():
            self.logger.error("Modbus read failed: address=%s count=%s response=%s", address, count, response)
            raise IOError(
                "Failed to read {} input register(s) "
                "starting at address {}".format(
                    count,
                    address,
                )
            )

        self.logger.debug("Received registers: %s", response.registers)
        return response.registers