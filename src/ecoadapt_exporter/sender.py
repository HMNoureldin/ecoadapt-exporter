"""Serialize measurements as JSON over an asynchronous Twisted WebSocket."""

import logging
import json
from abc import ABC, abstractmethod
from typing import Callable, Optional

from autobahn.twisted.websocket import (
    WebSocketClientFactory,
    WebSocketClientProtocol,
)
from twisted.internet import reactor

from .models import Measurement


#: WebSocket subprotocol shared by sender and development receiver.
WEBSOCKET_SUBPROTOCOL = "ecoadapt-v1"


class Sender(ABC):

    """Interface for asynchronous readiness, measurement delivery, and cleanup.
    """
    @abstractmethod
    def connect(self, on_connected: Callable[[], None]) -> None:
        """Begin connecting and notify the caller when ready.

        :param on_connected: Zero-argument callback invoked after connection readiness.
        """
        pass

    @abstractmethod
    def send(self, measurement: Measurement) -> None:
        """Deliver one measurement.

        :param measurement: Typed measurement to send.
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the sender connection.
        """
        pass


class ClientProtocol(WebSocketClientProtocol):

    """Bridge Autobahn connection events to the owning sender.
    """
    def onOpen(self):
        """Store the open protocol and invoke the sender readiness callback.
        """
        self.factory.sender.logger.info("WebSocket connection open")
        self.factory.sender.protocol = self

        if self.factory.sender.on_connected is not None:
            self.factory.sender.on_connected()

    def onClose(self, wasClean, code, reason):
        """Clear this protocol if it is still the sender's active connection.

        :param wasClean: Whether the WebSocket closed cleanly.
        :param code: WebSocket close status supplied by Autobahn.
        :param reason: Close description supplied by Autobahn.
        """
        log = self.factory.sender.logger.info if wasClean else self.factory.sender.logger.warning
        log("WebSocket closed: clean=%s code=%s reason=%s", wasClean, code, reason)
        if self.factory.sender.protocol is self:
            self.factory.sender.protocol = None


class WebSocketSender(Sender):

    """Send measurement JSON using the ``ecoadapt-v1`` subprotocol.

    :param url: Plain WebSocket URL, for example ``ws://127.0.0.1:9000``.
    :param logger: Optional shared logger; defaults to this module's logger.

    The implementation uses ``reactor.connectTCP``; it does not configure TLS,
    reconnections, acknowledgements, or message persistence.
    """
    def __init__(self, url: str, logger: Optional[logging.Logger] = None):
        self.logger = logger if logger is not None else logging.getLogger(__name__)
        self.url = url
        self.protocol: Optional[ClientProtocol] = None
        self.on_connected: Optional[Callable[[], None]] = None

    def connect(self, on_connected: Callable[[], None]) -> None:
        """Begin a TCP/WebSocket connection using the shared reactor.

        :param on_connected: Zero-argument callback invoked after the handshake.

        The caller must run the reactor for connection events to be processed.
        """
        self.logger.info("Connecting WebSocket sender")
        self.on_connected = on_connected
        factory = WebSocketClientFactory(
            self.url,
            protocols=[WEBSOCKET_SUBPROTOCOL],
        )

        factory.protocol = ClientProtocol
        factory.sender = self

        reactor.connectTCP(
            factory.host,
            factory.port,
            factory,
        )

    def send(self, measurement: Measurement) -> None:
        """Queue one UTF-8 JSON text message on the open protocol.

        :param measurement: Value, measurement identity, and engineering unit.
        :raises RuntimeError: If no open protocol is available.

        Payload keys are ``measurement``, ``value``, and ``unit``. Queueing does
        not acknowledge receipt by the remote server.
        """
        if self.protocol is None:
            self.logger.error("Cannot send measurement: WebSocket is not connected")
            raise RuntimeError(
                "WebSocket is not connected"
            )

        payload = {
            "measurement": measurement.measurement_type.value,
            "value": measurement.value,
            "unit": measurement.unit.value,
        }

        message = json.dumps(payload)

        self.logger.debug("Queueing WebSocket measurement: %s", message)
        self.protocol.sendMessage(
            message.encode("utf-8"),
            isBinary=False,
        )

    def close(self) -> None:
        """Request a WebSocket close handshake and clear the active protocol.
        """
        self.logger.info("Closing WebSocket sender")
        if self.protocol is not None:
            self.protocol.sendClose()
            self.protocol = None