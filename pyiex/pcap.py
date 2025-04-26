import os

from io import BufferedIOBase
from typing import Iterator, Optional, Union

from pydantic import BaseModel

from .format import ByteOrder, FormatError


__all__ = (
    "Stream",
    "StreamState"
)


class BlockType:
    HEADER = b"\x0a\x0d\x0d\x0a"
    INTERFACE_DESCRIPTION = b"\x01\x00\x00\x00"
    ENHANCED_PACKET = b"\x06\x00\x00\x00"


class HeaderBlock(BaseModel):
    byte_order: ByteOrder


class InterfaceDescriptionBlock(BaseModel):
    pass


class EnhancedPacketBlock(BaseModel):
    pass


type Block = Union[
    HeaderBlock,
    InterfaceDescriptionBlock,
    EnhancedPacketBlock
]


def _decode_header_block(data: bytes, byte_order: ByteOrder) -> HeaderBlock:
    return HeaderBlock(byte_order=byte_order)


def _decode_interface_description_block(
    data: bytes,
    byte_order: ByteOrder
) -> InterfaceDescriptionBlock:
    return None


def _decode_enhanced_packet_block(
    data: bytes,
    byte_order: ByteOrder
) -> EnhancedPacketBlock:
    return None


def _read_block(
    source: BufferedIOBase,
    byte_order: Optional[ByteOrder]
) -> Optional[Block]:
    buffer = source.read(8)

    if not buffer:
        return None

    block_type, block_length = buffer[0:4], buffer[4:8]

    if block_type == BlockType.HEADER:
        magic_bytes = source.read(4)
        byte_order: ByteOrder

        if magic_bytes == b"\x1a\x2b\x3c\x4d":
            byte_order = "big"
        elif magic_bytes == b"\x4d\x3c\x2b\x1a":
            byte_order = "little"
        else:
            raise FormatError

        data = source.read(int.from_bytes(block_length, byte_order) - 12)

        return _decode_header_block(data, byte_order)
    elif block_type == BlockType.INTERFACE_DESCRIPTION:
        data = source.read(int.from_bytes(block_length, byte_order) - 8)

        return _decode_interface_description_block(data, byte_order)
    elif block_type == BlockType.ENHANCED_PACKET:
        data = source.read(int.from_bytes(block_length, byte_order) - 8)

        return _decode_enhanced_packet_block(data, byte_order)
    else:
        raise NotImplementedError


class Stream:
    _source: BufferedIOBase
    _last_header_block: Optional[HeaderBlock]

    def __init__(self, source: BufferedIOBase) -> None:
        self._source = source
        self._last_header_block = None

    def __iter__(self) -> Iterator[Block]:
        return self

    def __next__(self) -> Block:
        byte_order = self._last_header_block.byte_order \
            if self._last_header_block else None

        block = _read_block(self._source, byte_order)

        if block is None:
            if not self._last_header_block:
                raise EOFError

            raise StopIteration
        elif isinstance(block, HeaderBlock):
            self._last_header_block = block
        elif not self._last_header_block:
            raise FormatError

        return block
