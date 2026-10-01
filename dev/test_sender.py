from ecoadapt_exporter.models import Measurement
from ecoadapt_exporter.registers import MeasurementType, Unit
from ecoadapt_exporter.sender import WebSocketSender
from twisted.internet import reactor


sender = WebSocketSender("ws://127.0.0.1:9000")


def close_sender():
    sender.close()
    reactor.callLater(0.5, reactor.stop)


def send_measurement():
    measurement = Measurement(
        measurement_type=MeasurementType.FREQUENCY,
        value=50.92,
        unit=Unit.HERTZ,
    )

    sender.send(measurement)

    # Give the WebSocket time to transmit the message.
    reactor.callLater(0.5, close_sender)


sender.connect(
    on_connected=send_measurement
)

reactor.run()