"""Check channel addressing and device-specific version and MAC decoding."""

from ecoadapt_exporter.registers import (
    RMS_VOLTAGE,
    decode_mac_address,
    decode_software_version,
    get_channel_address,
)


def test_get_channel_address():
    address = get_channel_address(
        definition=RMS_VOLTAGE,
        connector=1,
        channel=2,
    )

    assert address == 354


def test_decode_software_version():
    result = decode_software_version(514)

    assert result == "2.2"


def test_decode_mac_address():
    registers = [30, 44285, 17639]

    result = decode_mac_address(registers)

    assert result == "00:1E:AC:FD:44:E7"