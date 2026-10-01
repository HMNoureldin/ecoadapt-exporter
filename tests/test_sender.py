import pytest

from ecoadapt_exporter.models import Measurement
from ecoadapt_exporter.registers import MeasurementType, Unit
from ecoadapt_exporter.sender import Sender, WebSocketSender


def test_sender_is_abstract():
    with pytest.raises(TypeError):
        Sender()


def test_websocket_sender_starts_disconnected():
    sender = WebSocketSender("ws://127.0.0.1:9000")

    assert sender.protocol is None


def test_send_requires_connection():
    sender = WebSocketSender("ws://127.0.0.1:9000")

    measurement = Measurement(
        measurement_type=MeasurementType.FREQUENCY,
        value=51.45,
        unit=Unit.HERTZ,
    )

    with pytest.raises(RuntimeError):
        sender.send(measurement)