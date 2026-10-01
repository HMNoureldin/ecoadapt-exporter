from typing import Iterable

from .decoder import decode_registers
from .models import DeviceInfo, Measurement
from .registers import (
    MAC_ADDRESS,
    MODBUS_TABLE_VERSION,
    SOFTWARE_VERSION,
    CircuitRegisterDefinition,
    GeneralRegisterDefinition,
    decode_mac_address,
    decode_software_version,
    get_channel_address,
)
from .transport import Transport

class EcoAdapt:
    """
    Represents an Eco-Adapt Power-Elec device.
    """

    def __init__(self, transport: Transport):
        self.transport = transport
    
    def connect(self) -> None:
        self.transport.connect()
    
    def close(self) -> None:
        self.transport.close()
    
    def read_measurement(
        self,
        definition: CircuitRegisterDefinition,
        connector: int,
        channel: int,
    ) -> Measurement:
        address = get_channel_address(
            definition,
            connector,
            channel,
        )

        registers = self.transport.read_input_registers(
            address=address,
            count=definition.words_per_channel,
        )

        value = decode_registers(
            registers=registers,
            data_type=definition.data_type,
            byte_order=definition.byte_order,
            word_order=definition.word_order,
        )

        if definition.measurement_type is None:
            raise ValueError(
                "Register definition does not represent a measurement"
            )

        return Measurement(
            measurement_type=definition.measurement_type,
            value=value,
            unit=definition.unit,
        )

    def read_general_information(
        self,
        definition: GeneralRegisterDefinition,
    ):
        count = (
            definition.end_address
            - definition.start_address
            + 1
        )

        registers = self.transport.read_input_registers(
            address=definition.start_address,
            count=count,
        )

        if definition is SOFTWARE_VERSION:
            if len(registers) != 1:
                raise ValueError(
                    "Software version requires exactly one register"
                )

            return decode_software_version(registers[0])

        if definition is MAC_ADDRESS:
            return decode_mac_address(registers)

        return decode_registers(
            registers=registers,
            data_type=definition.data_type,
            byte_order=definition.byte_order,
            word_order=definition.word_order,
        )

    def read_device_info(
        self,
        definitions: Iterable[GeneralRegisterDefinition],
    ) -> DeviceInfo:
        software_version = None
        modbus_table_version = None
        mac_address = None

        for definition in definitions:
            value = self.read_general_information(definition)

            if definition is SOFTWARE_VERSION:
                software_version = value

            elif definition is MODBUS_TABLE_VERSION:
                modbus_table_version = value

            elif definition is MAC_ADDRESS:
                mac_address = value

            else:
                raise ValueError(
                    "Unsupported general register definition"
                )

        return DeviceInfo(
            software_version=software_version,
            modbus_table_version=modbus_table_version,
            mac_address=mac_address,
        )