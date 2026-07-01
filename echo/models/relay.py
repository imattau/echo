from dataclasses import dataclass
from enum import Enum, auto


class RelayStatus(Enum):
    DISCONNECTED = auto()
    CONNECTING = auto()
    CONNECTED = auto()
    SLOW = auto()
    ERROR = auto()


@dataclass
class Relay:
    url: str
    status: RelayStatus = RelayStatus.DISCONNECTED
    latency_ms: int = 0
    read: bool = True
    write: bool = True
