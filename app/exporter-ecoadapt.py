#!/usr/bin/env python3

import argparse

from twisted.internet import reactor

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
from ecoadapt_exporter.transport import ModbusTcpTransport


DEFAULT_DEVICE_HOST = "169.254.20.1"
DEFAULT_DEVICE_PORT = 502
DEFAULT_UNIT_ID = 1
DEFAULT_SERVER_URL = "ws://127.0.0.1:9000"
DEFAULT_INTERVAL = 10.0


def create_exporter(
    device_host: str,
    device_port: int,
    unit_id: int,
    server_url: str,
    interval: float,
) -> Exporter:
    transport = ModbusTcpTransport(
        host=device_host,
        port=device_port,
        unit_id=unit_id,
    )

    device = EcoAdapt(transport)

    sender = WebSocketSender(server_url)

    measurements = [
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
    ]

    return Exporter(
        device=device,
        sender=sender,
        measurements=measurements,
        interval=interval,
    )


def main():
    parser = argparse.ArgumentParser(
        description="Eco-Adapt Modbus exporter"
    )

    parser.add_argument(
        "--device-host",
        default=DEFAULT_DEVICE_HOST,
    )

    parser.add_argument(
        "--device-port",
        type=int,
        default=DEFAULT_DEVICE_PORT,
    )

    parser.add_argument(
        "--unit-id",
        type=int,
        default=DEFAULT_UNIT_ID,
    )

    parser.add_argument(
        "--server-url",
        default=DEFAULT_SERVER_URL,
    )

    parser.add_argument(
        "--interval",
        type=float,
        default=DEFAULT_INTERVAL,
    )

    args = parser.parse_args()

    exporter = create_exporter(
        device_host=args.device_host,
        device_port=args.device_port,
        unit_id=args.unit_id,
        server_url=args.server_url,
        interval=args.interval,
    )

    def shutdown():
        exporter.stop()

    reactor.addSystemEventTrigger(
        "before",
        "shutdown",
        shutdown,
    )

    exporter.start()

    reactor.run()


if __name__ == "__main__":
    main()