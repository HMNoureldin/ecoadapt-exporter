"""Coordinate device reads and measurement delivery on a Twisted timer."""

from dataclasses import dataclass
from typing import List, Optional

from twisted.internet.task import LoopingCall

from .ecoadapt import EcoAdapt
from .models import Measurement
from .registers import CircuitRegisterDefinition
from .sender import Sender


@dataclass(frozen=True)
class MeasurementRequest:
    """Configuration for one reading in each export cycle.

    :param definition: Circuit register definition to read.
    :param connector: One-based connector, validated by the device reader.
    :param channel: One-based channel, validated by the device reader.
    """
    definition: CircuitRegisterDefinition
    connector: int
    channel: int


class Exporter:
    """Poll requested measurements after the sender becomes ready.

    :param device: Device reader implementing connection and measurement methods.
    :param sender: Sender implementing connection, delivery, and cleanup methods.
    :param measurements: Requests processed in list order during every cycle.
    :param interval: Seconds between scheduled cycles; defaults to 10.

    The caller owns and runs the Twisted reactor. Reads are synchronous and
    can block its event loop. No retry or reconnection policy is implemented.
    """
    def __init__(
        self,
        device: EcoAdapt,
        sender: Sender,
        measurements: List[MeasurementRequest],
        interval: float = 10.0,
    ):
        self.device = device
        self.sender = sender
        self.measurements = measurements
        self.interval = interval
        self.loop: Optional[LoopingCall] = None

    def run_once(self) -> None:
        """Read and send each request in order.

        Read or send errors propagate and stop the current cycle. Earlier
        measurements may already have been sent.
        """
        for request in self.measurements:
            measurement = self.device.read_measurement(
                definition=request.definition,
                connector=request.connector,
                channel=request.channel,
            )

            self.sender.send(measurement)

    def start(self) -> None:
        """Connect the device, then request the sender connection.

        Periodic reads begin in the sender's readiness callback, not immediately
        on returning from this method. Connection errors are not recovered here.
        """
        self.device.connect()
        self.sender.connect(
            on_connected=self._start_loop,
        )
    
    def _start_loop(self) -> None:
        """Start the periodic loop and perform its first read immediately.
        """
        self.loop = LoopingCall(self.run_once)

        self.loop.start(
            self.interval,
            now=True,
        )

    def stop(self) -> None:
        """Stop an active loop, close the sender, then close the device.

        This does not stop the reactor. Cleanup exceptions are not suppressed.
        """
        if self.loop is not None and self.loop.running:
            self.loop.stop()

        self.sender.close()
        self.device.close()