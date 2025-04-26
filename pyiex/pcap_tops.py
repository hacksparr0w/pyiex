from io import BufferedIOBase
from typing import Any, Iterator

from . import iextp
from . import pcap


__all__ = (
    "stream",
)


def stream(source: BufferedIOBase) -> Iterator[Any]:
    wrapped = pcap.stream(source)

    while True:
        block = next(wrapped)

        if not isinstance(block, pcap.EnhancedPacketBlock):
            continue

        packet = iextp.decode(block.payload[42:])

        if packet.protocol_id != 0x8003 or packet.channel_id != 1:
            continue

        for message in packet.messages:
            yield message
