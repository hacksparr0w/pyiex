import os

from io import BufferedIOBase
from typing import Any, Iterator

from . import iextp
from . import pcap
from . import tops


__all__ = (
    "read",
)


def read(stream: BufferedIOBase) -> Iterator[Any]:
    for block in pcap.read(stream):
        if block.__class__.__name__ != pcap.EnhancedPacketBlock.__name__:
            continue

        block.payload.seek(42, os.SEEK_CUR)
        packet = iextp.read_packet(block.payload)

        if packet.protocol_id != 0x8003 or packet.channel_id != 1:
            continue

        for message in packet.messages:
            yield tops.read_message(message)
