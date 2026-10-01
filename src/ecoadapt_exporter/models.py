from dataclasses import dataclass
from typing import Optional

from .registers import MeasurementType, Unit


@dataclass(frozen=True)
class Measurement:
    measurement_type: MeasurementType
    value: float
    unit: Unit


@dataclass(frozen=True)
class DeviceInfo:
    software_version: Optional[str] = None
    modbus_table_version: Optional[int] = None
    mac_address: Optional[str] = None