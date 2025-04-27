from enum import StrEnum, auto

from pydantic import BaseModel

from .format import ByteOrder


__all__ = (
    "Message",
    "SystemEventMessage",

    "decode"
)


class _MessageType:
    SYSTEM_EVENT = b"\0x53"


class SystemEvent(StrEnum):
    MESSAGES_END = auto()
    MESSAGES_START = auto()
    REGULAR_MARKET_HOURS_END = auto()
    REGULAR_MARKET_HOURS_START = auto()
    SYSTEM_HOURS_END = auto()
    SYSTEM_HOURS_START = auto()


_SystemEventCodes = {
    b"\x4f": SystemEvent.MESSAGES_START,
    b"\x53": SystemEvent.SYSTEM_HOURS_START,
    b"\x52": SystemEvent.REGULAR_MARKET_HOURS_START,
    b"\x4d": SystemEvent.REGULAR_MARKET_HOURS_END,
    b"\x45": SystemEvent.SYSTEM_HOURS_END,
    b"\x43": SystemEvent.MESSAGES_END
}


class SystemEventMessage(BaseModel):
    event: bytes
    timestamp: int


type Message = [
    SystemEventMessage,
]


def _decode_system_event_message(
    data: bytes,
    offset: int,
    byte_order: ByteOrder
) -> tuple[SystemEventMessage, int]:
    event = _SystemEventCodes[data[offset]]
    offset += 1

    timestamp = int.from_bytes(event[offset:offset + 8])
    offset += 8

    return SystemEventMessage(event=event, timestamp=timestamp), offset


def read_message(: bytes, offset: int, byte_order: ByteOrder = "little") -> Message:
    pass
