import pytest

from ecoadapt_exporter.ecoadapt import EcoAdapt
from ecoadapt_exporter.registers import (
    FREQUENCY,
    MAC_ADDRESS,
    MeasurementType,
    MODBUS_TABLE_VERSION,
    RMS_VOLTAGE,
    SOFTWARE_VERSION,
    Unit,
)

from tests.fakes import FakeTransport


def test_read_rms_voltage():
    transport = FakeTransport(
        {
            352: [49709, 17262],
        }
    )
    device = EcoAdapt(transport)

    result = device.read_measurement(
        definition=RMS_VOLTAGE,
        connector=1,
        channel=1,
    )

    assert result.measurement_type == MeasurementType.RMS_VOLTAGE
    assert result.value == pytest.approx(238.7585, abs=0.001)
    assert result.unit == Unit.VOLT


def test_read_frequency():
    transport = FakeTransport(
        {
            424: [54339, 16973],
        }
    )
    device = EcoAdapt(transport)

    result = device.read_measurement(
        definition=FREQUENCY,
        connector=1,
        channel=1,
    )

    assert result.measurement_type == MeasurementType.FREQUENCY
    assert result.value == pytest.approx(51.4573, abs=0.001)
    assert result.unit == Unit.HERTZ


def test_read_software_version():
    transport = FakeTransport(
        {
            0: [514],
        }
    )
    device = EcoAdapt(transport)

    result = device.read_general_information(
        definition=SOFTWARE_VERSION,
    )

    assert result == "2.2"


def test_read_modbus_table_version():
    transport = FakeTransport(
        {
            1: [2],
        }
    )
    device = EcoAdapt(transport)

    result = device.read_general_information(
        definition=MODBUS_TABLE_VERSION,
    )

    assert result == 2


def test_read_mac_address():
    transport = FakeTransport(
        {
            2: [30, 44285, 17639],
        }
    )
    device = EcoAdapt(transport)

    result = device.read_general_information(
        definition=MAC_ADDRESS,
    )

    assert result == "00:1E:AC:FD:44:E7"


def test_read_device_info():
    transport = FakeTransport(
        {
            0: [514],
            1: [2],
            2: [30, 44285, 17639],
        }
    )
    device = EcoAdapt(transport)

    result = device.read_device_info(
        [
            SOFTWARE_VERSION,
            MODBUS_TABLE_VERSION,
            MAC_ADDRESS,
        ]
    )

    assert result.software_version == "2.2"
    assert result.modbus_table_version == 2
    assert result.mac_address == "00:1E:AC:FD:44:E7"


def test_read_device_info_with_mac_address_only():
    transport = FakeTransport(
        {
            2: [30, 44285, 17639],
        }
    )
    device = EcoAdapt(transport)

    result = device.read_device_info(
        [
            MAC_ADDRESS,
        ]
    )

    assert result.software_version is None
    assert result.modbus_table_version is None
    assert result.mac_address == "00:1E:AC:FD:44:E7"