"""Check measurement and device-information field values."""

from ecoadapt_exporter.models import DeviceInfo, Measurement
from ecoadapt_exporter.registers import MeasurementType, Unit


def test_voltage_measurement():
    measurement = Measurement(
        measurement_type=MeasurementType.RMS_VOLTAGE,
        value=238.75,
        unit=Unit.VOLT,
    )

    assert measurement.measurement_type == MeasurementType.RMS_VOLTAGE
    assert measurement.value == 238.75
    assert measurement.unit == Unit.VOLT


def test_frequency_measurement():
    measurement = Measurement(
        measurement_type=MeasurementType.FREQUENCY,
        value=51.4573,
        unit=Unit.HERTZ,
    )

    assert measurement.measurement_type == MeasurementType.FREQUENCY
    assert measurement.value == 51.4573
    assert measurement.unit == Unit.HERTZ


def test_device_info():
    device_info = DeviceInfo(
        software_version="2.2",
        modbus_table_version=2,
        mac_address="00:1E:AC:FD:44:E7",
    )

    assert device_info.software_version == "2.2"
    assert device_info.modbus_table_version == 2
    assert device_info.mac_address == "00:1E:AC:FD:44:E7"