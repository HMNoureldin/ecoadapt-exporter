import pytest
from ecoadapt_exporter.exporter import (
    Exporter,
    MeasurementRequest,
)
from ecoadapt_exporter.models import Measurement
from ecoadapt_exporter.ecoadapt import EcoAdapt
from ecoadapt_exporter.registers import (
    FREQUENCY,
    RMS_VOLTAGE,
    MeasurementType,
    Unit,
)

from tests.fakes import FakeTransport ,FakeDevice, FakeSender


def test_run_once_reads_and_sends_measurements():
    device = FakeDevice(
        {
            RMS_VOLTAGE: Measurement(
                measurement_type=MeasurementType.RMS_VOLTAGE,
                value=230.0,
                unit=Unit.VOLT,
            ),
            FREQUENCY: Measurement(
                measurement_type=MeasurementType.FREQUENCY,
                value=50.0,
                unit=Unit.HERTZ,
            ),
        }
    )
    sender = FakeSender()

    exporter = Exporter(
        device=device,
        sender=sender,
        measurements=[
            MeasurementRequest(
                definition=RMS_VOLTAGE,
                connector=1,
                channel=1,
            ),
            MeasurementRequest(
                definition=FREQUENCY,
                connector=1,
                channel=1,
            ),
        ],
    )

    exporter.run_once()

    assert len(device.reads) == 2
    assert len(sender.sent) == 2

    assert device.reads[0] == {
        "definition": RMS_VOLTAGE,
        "connector": 1,
        "channel": 1,
    }

    assert device.reads[1] == {
        "definition": FREQUENCY,
        "connector": 1,
        "channel": 1,
    }

    assert sender.sent[0].measurement_type == (
        MeasurementType.RMS_VOLTAGE
    )
    assert sender.sent[0].value == 230.0
    assert sender.sent[0].unit == Unit.VOLT

    assert sender.sent[1].measurement_type == (
        MeasurementType.FREQUENCY
    )
    assert sender.sent[1].value == 50.0
    assert sender.sent[1].unit == Unit.HERTZ


def test_measurements_can_use_different_connectors_and_channels():
    device = FakeDevice(
        {
            RMS_VOLTAGE: Measurement(
                measurement_type=MeasurementType.RMS_VOLTAGE,
                value=230.0,
                unit=Unit.VOLT,
            ),
            FREQUENCY: Measurement(
                measurement_type=MeasurementType.FREQUENCY,
                value=50.0,
                unit=Unit.HERTZ,
            ),
        }
    )
    sender = FakeSender()

    exporter = Exporter(
        device=device,
        sender=sender,
        measurements=[
            MeasurementRequest(
                definition=RMS_VOLTAGE,
                connector=1,
                channel=1,
            ),
            MeasurementRequest(
                definition=FREQUENCY,
                connector=2,
                channel=3,
            ),
        ],
    )

    exporter.run_once()

    assert device.reads[0] == {
        "definition": RMS_VOLTAGE,
        "connector": 1,
        "channel": 1,
    }

    assert device.reads[1] == {
        "definition": FREQUENCY,
        "connector": 2,
        "channel": 3,
    }


def test_start_connects_device_and_sender():
    device = FakeDevice(
        {
            RMS_VOLTAGE: Measurement(
                measurement_type=MeasurementType.RMS_VOLTAGE,
                value=230.0,
                unit=Unit.VOLT,
            ),
            FREQUENCY: Measurement(
                measurement_type=MeasurementType.FREQUENCY,
                value=50.0,
                unit=Unit.HERTZ,
            ),
        }
    )
    sender = FakeSender()

    exporter = Exporter(
        device=device,
        sender=sender,
        measurements=[],
    )

    exporter.start()

    assert device.connect_called is True
    assert sender.connect_called is True

    exporter.stop()


def test_stop_closes_device_and_sender():
    device = FakeDevice(
        {
            RMS_VOLTAGE: Measurement(
                measurement_type=MeasurementType.RMS_VOLTAGE,
                value=230.0,
                unit=Unit.VOLT,
            ),
            FREQUENCY: Measurement(
                measurement_type=MeasurementType.FREQUENCY,
                value=50.0,
                unit=Unit.HERTZ,
            ),
        }
    )
    sender = FakeSender()

    exporter = Exporter(
        device=device,
        sender=sender,
        measurements=[],
    )

    exporter.start()
    exporter.stop()

    assert device.close_called is True
    assert sender.close_called is True


def test_exporter_reads_ecoadapt_and_sends_measurements():
    transport = FakeTransport(
        {
            352: [49709, 17262],
            424: [54339, 16973],
        }
    )

    device = EcoAdapt(transport)
    sender = FakeSender()

    exporter = Exporter(
        device=device,
        sender=sender,
        measurements=[
            MeasurementRequest(
                definition=RMS_VOLTAGE,
                connector=1,
                channel=1,
            ),
            MeasurementRequest(
                definition=FREQUENCY,
                connector=1,
                channel=1,
            ),
        ],
    )

    exporter.run_once()

    assert len(sender.sent) == 2

    assert sender.sent[0].measurement_type == (
        MeasurementType.RMS_VOLTAGE
    )
    assert sender.sent[0].value == pytest.approx(
        238.7585,
        abs=0.001,
    )
    assert sender.sent[0].unit == Unit.VOLT

    assert sender.sent[1].measurement_type == (
        MeasurementType.FREQUENCY
    )
    assert sender.sent[1].value == pytest.approx(
        51.4573,
        abs=0.001,
    )
    assert sender.sent[1].unit == Unit.HERTZ