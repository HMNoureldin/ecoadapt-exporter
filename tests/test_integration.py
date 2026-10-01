import pytest

from ecoadapt_exporter.ecoadapt import EcoAdapt
from ecoadapt_exporter.exporter import (
    Exporter,
    MeasurementRequest,
)
from ecoadapt_exporter.registers import (
    FREQUENCY,
    RMS_VOLTAGE,
)
from ecoadapt_exporter.sender import WebSocketSender
from tests.fakes import FakeTransport


def test_exporter_sends_measurements_to_websocket():
    transport = FakeTransport(
        {
            352: [49709, 17262],
            424: [54339, 16973],
        }
    )

    device = EcoAdapt(transport)

    sender = WebSocketSender(
        "ws://127.0.0.1:9000",
    )

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

    def run_export():
        exporter.run_once()
        exporter.stop()

    sender.connect(
        on_connected=run_export,
    )

    from twisted.internet import reactor

    reactor.callLater(2.0, reactor.stop)
    reactor.run()