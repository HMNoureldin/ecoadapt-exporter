"""Immutable values exchanged between device access and export layers."""

from dataclasses import dataclass
from typing import Optional

from .registers import MeasurementType, Unit


@dataclass(frozen=True)
class Measurement:
    """A decoded value and its semantic identity.

    :param measurement_type: Kind of measurement, used in the JSON payload.
    :param value: Decoded numeric value.
    :param unit: Engineering unit associated with the register definition.

    Connector and channel belong to the request, not this result.
    """
    measurement_type: MeasurementType
    value: float
    unit: Unit


@dataclass(frozen=True)
class DeviceInfo:
    """Selected device metadata; unread fields remain ``None``.

    :param software_version: Major/minor version string.
    :param modbus_table_version: Numeric register-table version.
    :param mac_address: Colon-separated hexadecimal MAC address.
    """
    software_version: Optional[str] = None
    modbus_table_version: Optional[int] = None
    mac_address: Optional[str] = None