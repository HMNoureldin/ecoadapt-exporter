import json
from abc import ABC, abstractmethod
from typing import Callable, Optional

from autobahn.twisted.websocket import (
    WebSocketClientFactory,
    WebSocketClientProtocol,
)
from twisted.internet import reactor

from .models import Measurement


WEBSOCKET_SUBPROTOCOL = "ecoadapt-v1"


class Sender(ABC):

    @abstractmethod
    def connect(self, on_connected: Callable[[], None]) -> None:
        pass

    @abstractmethod
    def send(self, measurement: Measurement) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass


class ClientProtocol(WebSocketClientProtocol):

    def onOpen(self):
        self.factory.sender.protocol = self

        if self.factory.sender.on_connected is not None:
            self.factory.sender.on_connected()

    def onClose(self, wasClean, code, reason):
        if self.factory.sender.protocol is self:
            self.factory.sender.protocol = None


class WebSocketSender(Sender):

    def __init__(self, url: str):
        self.url = url
        self.protocol: Optional[ClientProtocol] = None
        self.on_connected: Optional[Callable[[], None]] = None

    def connect(self, on_connected: Callable[[], None]) -> None:
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
        if self.protocol is None:
            raise RuntimeError(
                "WebSocket is not connected"
            )

        payload = {
            "measurement": measurement.measurement_type.value,
            "value": measurement.value,
            "unit": measurement.unit.value,
        }

        message = json.dumps(payload)

        self.protocol.sendMessage(
            message.encode("utf-8"),
            isBinary=False,
        )

    def close(self) -> None:
        if self.protocol is not None:
            self.protocol.sendClose()
            self.protocol = None