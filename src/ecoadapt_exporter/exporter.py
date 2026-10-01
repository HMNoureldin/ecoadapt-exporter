from dataclasses import dataclass
from typing import List, Optional

from twisted.internet.task import LoopingCall

from .ecoadapt import EcoAdapt
from .models import Measurement
from .registers import CircuitRegisterDefinition
from .sender import Sender


@dataclass(frozen=True)
class MeasurementRequest:
    definition: CircuitRegisterDefinition
    connector: int
    channel: int


class Exporter:
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
        for request in self.measurements:
            measurement = self.device.read_measurement(
                definition=request.definition,
                connector=request.connector,
                channel=request.channel,
            )

            self.sender.send(measurement)

    def start(self) -> None:
        self.device.connect()
        self.sender.connect(
            on_connected=self._start_loop,
        )
    
    def _start_loop(self) -> None:
        self.loop = LoopingCall(self.run_once)

        self.loop.start(
            self.interval,
            now=True,
        )

    def stop(self) -> None:
        if self.loop is not None and self.loop.running:
            self.loop.stop()

        self.sender.close()
        self.device.close()