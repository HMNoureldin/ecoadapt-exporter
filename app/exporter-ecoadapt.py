#!/usr/bin/env python3

"""Wire the device, sender, and exporter into the command-line application."""

import argparse
import logging
from typing import Optional

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
    logger: Optional[logging.Logger] = None,
) -> Exporter:
    """Build an exporter without opening network connections.

    :param device_host: Modbus device hostname or IP address.
    :param device_port: Modbus TCP port.
    :param unit_id: Modbus unit identifier.
    :param server_url: Plain WebSocket receiver URL.
    :param interval: Polling interval in seconds.
    :param logger: Shared logger passed to all runtime collaborators.
    :returns: An exporter configured for RMS voltage and frequency on
        connector 1, channel 1. Edit the request list to change these selections.
    """
    transport = ModbusTcpTransport(
        host=device_host,
        port=device_port,
        unit_id=unit_id,
        logger=logger,
    )

    device = EcoAdapt(transport, logger=logger)

    sender = WebSocketSender(server_url, logger=logger)

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
        logger=logger,
    )


def configure_logging(level: str = "INFO") -> logging.Logger:
    """Configure application console logging and return its shared logger.

    :param level: DEBUG, INFO, WARNING, ERROR, or CRITICAL (case insensitive).
    :returns: The application logger, writing formatted records to stderr.
    :raises ValueError: If the level is unsupported.

    Repeated configuration replaces only this application's handlers.
    Library constructors never configure handlers or the root logger.
    """
    level = level.upper()
    if level not in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
        raise ValueError("Unsupported log level: {}".format(level))
    logger = logging.getLogger("ecoadapt_exporter")
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s %(filename)s:%(lineno)d %(message)s"
    ))
    logger.addHandler(handler)
    logger.setLevel(getattr(logging, level))
    logger.propagate = False
    return logger


def main():
    """Parse CLI options, register shutdown cleanup, start the exporter and reactor.
    """
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

    parser.add_argument(
        "--log-level",
        type=str.upper,
        choices=("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"),
        default="INFO",
        help="Application logging threshold (default: INFO)",
    )

    args = parser.parse_args()
    logger = configure_logging(args.log_level)

    exporter = create_exporter(
        device_host=args.device_host,
        device_port=args.device_port,
        unit_id=args.unit_id,
        server_url=args.server_url,
        interval=args.interval,
        logger=logger,
    )

    def shutdown():
        """Close exporter resources before reactor shutdown.
        """
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