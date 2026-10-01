"""Eco-Adapt register metadata, channel addressing, and device-specific codecs."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .decoder import (
    ByteOrder,
    DataType,
    WordOrder,
    decode_uint8_pair,
)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class Unit(Enum):
    """Engineering-unit strings used in measurements and JSON payloads.
    """
    KWH = "kWh"
    KVARH = "kVArh"
    WATT = "W"
    VAR = "Var"
    AMPERE = "A"
    VOLT = "V"
    HERTZ = "Hz"
    DIMENSIONLESS = "-"
    NONE = ""


class MeasurementType(Enum):
    """Stable measurement identifiers sent to the WebSocket receiver.
    """
    ACTIVE_ENERGY_IMPORT = "active_energy_import"
    REACTIVE_ENERGY_IMPORT = "reactive_energy_import"
    ACTIVE_ENERGY_EXPORT = "active_energy_export"
    REACTIVE_ENERGY_EXPORT = "reactive_energy_export"
    ACTIVE_POWER = "active_power"
    REACTIVE_POWER = "reactive_power"
    POWER_FACTOR = "power_factor"
    RMS_CURRENT = "rms_current"
    RMS_CURRENT_ONE_MIN_AVERAGE = "rms_current_one_min_average"
    RMS_VOLTAGE = "rms_voltage"
    RMS_VOLTAGE_ONE_MIN_AVERAGE = "rms_voltage_one_min_average"
    FREQUENCY = "frequency"


class CircuitConfiguration(Enum):
    """Device configuration codes for disabled and supported circuit arrangements.
    """
    DISABLED = 0x0000
    SINGLE_PHASE = 0x0001
    THREE_PHASE_WITH_NEUTRAL = 0x0002
    BALANCED_THREE_PHASE_WITH_NEUTRAL = 0x0003
    THREE_PHASE_WITHOUT_NEUTRAL = 0x0004
    BALANCED_THREE_PHASE_WITHOUT_NEUTRAL = 0x0005
    THREE_PHASE_WITH_VOLTAGE_TRANSFORMER = 0x0006


class RegisterEncoding(Enum):
    """Metadata identifying special general-information encodings.
    """
    SOFTWARE_VERSION = "software_version"
    MAC_ADDRESS = "mac_address"


# ---------------------------------------------------------------------------
# Register definition types
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RegisterDefinition:
    """An inclusive register range and its numeric decoding settings.

    :param start_address: First Modbus address in the range.
    :param end_address: Last Modbus address in the range, inclusive.
    :param data_type: Numeric representation.
    :param byte_order: Byte order within each register.
    :param word_order: Word order across a value.
    """
    start_address: int
    end_address: int
    data_type: DataType
    byte_order: ByteOrder
    word_order: WordOrder


@dataclass(frozen=True)
class GeneralRegisterDefinition(RegisterDefinition):
    """Device-wide register metadata.

    :param encoding: Optional special encoding label. The current device reader
        dispatches special decoding by constant identity, not by this field.

    Inherits the range and decoding fields of :class:`RegisterDefinition`.
    """
    encoding: Optional[RegisterEncoding] = None


@dataclass(frozen=True)
class CircuitRegisterDefinition(RegisterDefinition):
    """Register metadata shared by the device's 18 channel positions.

    :param unit: Engineering unit of decoded values.
    :param words_per_channel: Number of consecutive registers per channel.
    :param measurement_type: Measurement identity, or ``None`` for configuration.

    Inherits the range and decoding fields of :class:`RegisterDefinition`.
    """
    unit: Unit
    words_per_channel: int
    measurement_type: Optional[MeasurementType]


# ---------------------------------------------------------------------------
# General information
# ---------------------------------------------------------------------------

#: Register definition for software version.
SOFTWARE_VERSION = GeneralRegisterDefinition(
    start_address=0,
    end_address=0,
    data_type=DataType.UINT16,
    byte_order=ByteOrder.MSB_FIRST,
    word_order=WordOrder.MSW_FIRST,
    encoding=RegisterEncoding.SOFTWARE_VERSION,
)


#: Register definition for modbus table version.
MODBUS_TABLE_VERSION = GeneralRegisterDefinition(
    start_address=1,
    end_address=1,
    data_type=DataType.UINT16,
    byte_order=ByteOrder.MSB_FIRST,
    word_order=WordOrder.MSW_FIRST,
)


#: Register definition for mac address.
MAC_ADDRESS = GeneralRegisterDefinition(
    start_address=2,
    end_address=4,
    data_type=DataType.UINT16,
    byte_order=ByteOrder.MSB_FIRST,
    word_order=WordOrder.MSW_FIRST,
    encoding=RegisterEncoding.MAC_ADDRESS,
)


# ---------------------------------------------------------------------------
# Circuit information
# ---------------------------------------------------------------------------

#: Register definition for circuit configuration.
CIRCUIT_CONFIGURATION = CircuitRegisterDefinition(
    start_address=8,
    end_address=25,
    data_type=DataType.UINT16,
    byte_order=ByteOrder.MSB_FIRST,
    word_order=WordOrder.MSW_FIRST,
    unit=Unit.NONE,
    words_per_channel=1,
    measurement_type=None
)


#: Register definition for active energy import index.
ACTIVE_ENERGY_IMPORT_INDEX = CircuitRegisterDefinition(
    start_address=28,
    end_address=63,
    data_type=DataType.FLOAT32,
    byte_order=ByteOrder.MSB_FIRST,
    word_order=WordOrder.LSW_FIRST,
    unit=Unit.KWH,
    words_per_channel=2,
    measurement_type=MeasurementType.ACTIVE_ENERGY_IMPORT
)


#: Register definition for reactive energy import index.
REACTIVE_ENERGY_IMPORT_INDEX = CircuitRegisterDefinition(
    start_address=64,
    end_address=99,
    data_type=DataType.FLOAT32,
    byte_order=ByteOrder.MSB_FIRST,
    word_order=WordOrder.LSW_FIRST,
    unit=Unit.KVARH,
    words_per_channel=2,
    measurement_type=MeasurementType.REACTIVE_ENERGY_IMPORT
)


#: Register definition for active energy export index.
ACTIVE_ENERGY_EXPORT_INDEX = CircuitRegisterDefinition(
    start_address=100,
    end_address=135,
    data_type=DataType.FLOAT32,
    byte_order=ByteOrder.MSB_FIRST,
    word_order=WordOrder.LSW_FIRST,
    unit=Unit.KWH,
    words_per_channel=2,
    measurement_type=MeasurementType.ACTIVE_ENERGY_EXPORT
)


#: Register definition for reactive energy export index.
REACTIVE_ENERGY_EXPORT_INDEX = CircuitRegisterDefinition(
    start_address=136,
    end_address=171,
    data_type=DataType.FLOAT32,
    byte_order=ByteOrder.MSB_FIRST,
    word_order=WordOrder.LSW_FIRST,
    unit=Unit.KVARH,
    words_per_channel=2,
    measurement_type=MeasurementType.REACTIVE_ENERGY_EXPORT
)


#: Register definition for active power.
ACTIVE_POWER = CircuitRegisterDefinition(
    start_address=172,
    end_address=207,
    data_type=DataType.FLOAT32,
    byte_order=ByteOrder.MSB_FIRST,
    word_order=WordOrder.LSW_FIRST,
    unit=Unit.WATT,
    words_per_channel=2,
    measurement_type=MeasurementType.ACTIVE_POWER
)


#: Register definition for reactive power.
REACTIVE_POWER = CircuitRegisterDefinition(
    start_address=208,
    end_address=243,
    data_type=DataType.FLOAT32,
    byte_order=ByteOrder.MSB_FIRST,
    word_order=WordOrder.LSW_FIRST,
    unit=Unit.VAR,
    words_per_channel=2,
    measurement_type=MeasurementType.REACTIVE_POWER
)


#: Register definition for power factor.
POWER_FACTOR = CircuitRegisterDefinition(
    start_address=244,
    end_address=279,
    data_type=DataType.FLOAT32,
    byte_order=ByteOrder.MSB_FIRST,
    word_order=WordOrder.LSW_FIRST,
    unit=Unit.DIMENSIONLESS,
    words_per_channel=2,
    measurement_type=MeasurementType.POWER_FACTOR
)


#: Register definition for rms current.
RMS_CURRENT = CircuitRegisterDefinition(
    start_address=280,
    end_address=315,
    data_type=DataType.FLOAT32,
    byte_order=ByteOrder.MSB_FIRST,
    word_order=WordOrder.LSW_FIRST,
    unit=Unit.AMPERE,
    words_per_channel=2,
    measurement_type=MeasurementType.RMS_CURRENT
)


#: Register definition for rms current one min average.
RMS_CURRENT_ONE_MIN_AVERAGE = CircuitRegisterDefinition(
    start_address=316,
    end_address=351,
    data_type=DataType.FLOAT32,
    byte_order=ByteOrder.MSB_FIRST,
    word_order=WordOrder.LSW_FIRST,
    unit=Unit.AMPERE,
    words_per_channel=2,
    measurement_type=MeasurementType.RMS_CURRENT_ONE_MIN_AVERAGE
)


#: Register definition for rms voltage.
RMS_VOLTAGE = CircuitRegisterDefinition(
    start_address=352,
    end_address=387,
    data_type=DataType.FLOAT32,
    byte_order=ByteOrder.MSB_FIRST,
    word_order=WordOrder.LSW_FIRST,
    unit=Unit.VOLT,
    words_per_channel=2,
    measurement_type=MeasurementType.RMS_VOLTAGE
)


#: Register definition for rms voltage one min average.
RMS_VOLTAGE_ONE_MIN_AVERAGE = CircuitRegisterDefinition(
    start_address=388,
    end_address=423,
    data_type=DataType.FLOAT32,
    byte_order=ByteOrder.MSB_FIRST,
    word_order=WordOrder.LSW_FIRST,
    unit=Unit.VOLT,
    words_per_channel=2,
    measurement_type=MeasurementType.RMS_VOLTAGE_ONE_MIN_AVERAGE
)


#: Register definition for frequency.
FREQUENCY = CircuitRegisterDefinition(
    start_address=424,
    end_address=459,
    data_type=DataType.FLOAT32,
    byte_order=ByteOrder.MSB_FIRST,
    word_order=WordOrder.LSW_FIRST,
    unit=Unit.HERTZ,
    words_per_channel=2,
    measurement_type=MeasurementType.FREQUENCY
)


# ---------------------------------------------------------------------------
# Device-specific decoding
# ---------------------------------------------------------------------------

def decode_software_version(register: int) -> str:
    """Decode a major/minor software version.

    :param register: Unsigned register with major in the high byte.
    :returns: A string such as ``"1.6"``.
    :raises ValueError: If the register value is invalid.
    """
    major, minor = decode_uint8_pair(
        register,
        byte_order=ByteOrder.MSB_FIRST,
    )
    return "{}.{}".format(major, minor)


def decode_mac_address(registers) -> str:
    """Decode three registers into a six-byte MAC address.

    :param registers: Iterable of exactly three unsigned 16-bit integers.
    :returns: Uppercase hexadecimal bytes separated by colons.
    :raises ValueError: If the count or any register value is invalid.
    """
    registers = list(registers)

    if len(registers) != 3:
        raise ValueError("MAC address requires exactly 3 registers")

    mac_bytes = []

    for register in registers:
        first_byte, second_byte = decode_uint8_pair(
            register,
            byte_order=ByteOrder.MSB_FIRST,
        )
        mac_bytes.extend([first_byte, second_byte])

    return ":".join(
        "{:02X}".format(byte)
        for byte in mac_bytes
    )


def decode_circuit_configuration(
    register: int,
) -> CircuitConfiguration:
    """Interpret a circuit configuration code.

    :param register: Numeric configuration code.
    :returns: The corresponding :class:`CircuitConfiguration` member.
    :raises ValueError: If the code is unknown.
    """
    try:
        return CircuitConfiguration(register)
    except ValueError:
        raise ValueError(
            "Unknown circuit configuration value: {}".format(register)
        )


# ---------------------------------------------------------------------------
# Circuit address calculation
# ---------------------------------------------------------------------------

def get_channel_address(
    definition: CircuitRegisterDefinition,
    connector: int,
    channel: int,
) -> int:
    """Calculate the first register address for a connector/channel pair.

    :param definition: Circuit register range and stride.
    :param connector: One-based connector number, from 1 through 6.
    :param channel: One-based channel number, from 1 through 3.
    :returns: ``start_address + ((connector - 1) * 3 + channel - 1) * stride``.
    :raises ValueError: If either index or the resulting range is invalid.
    """
    if not 1 <= connector <= 6:
        raise ValueError("Connector must be between 1 and 6")

    if not 1 <= channel <= 3:
        raise ValueError("Channel must be between 1 and 3")

    channel_index = (
        (connector - 1) * 3
        + (channel - 1)
    )

    address = (
        definition.start_address
        + channel_index * definition.words_per_channel
    )

    if (
        address
        + definition.words_per_channel
        - 1
        > definition.end_address
    ):
        raise ValueError(
            "Calculated register address is outside the register range"
        )

    return address