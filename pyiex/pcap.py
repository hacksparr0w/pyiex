from io import BufferedIOBase
from typing import Iterator, Optional, Union

from pydantic import BaseModel

from .format import ByteOrder, FormatError


__all__ = (
    "Block",
    "EnhancedPacketBlock",
    "HeaderBlock",
    "InterfaceDescriptionBlock",

    "stream"
)


class HeaderBlock(BaseModel):
    byte_order: ByteOrder


class InterfaceDescriptionBlock(BaseModel):
    pass


class EnhancedPacketBlock(BaseModel):
    payload: bytes


type Block = Union[
    HeaderBlock,
    InterfaceDescriptionBlock,
    EnhancedPacketBlock
]


class _BlockType:
    HEADER = b"\x0a\x0d\x0d\x0a"
    INTERFACE_DESCRIPTION = b"\x01\x00\x00\x00"
    ENHANCED_PACKET = b"\x06\x00\x00\x00"


def _decode_header_block(data: bytes, byte_order: ByteOrder) -> HeaderBlock:
    return HeaderBlock(byte_order=byte_order)


def _decode_interface_description_block(
    data: bytes,
    byte_order: ByteOrder
) -> InterfaceDescriptionBlock:
    return InterfaceDescriptionBlock()


def _decode_enhanced_packet_block(
    data: bytes,
    byte_order: ByteOrder
) -> EnhancedPacketBlock:
    original_length = int.from_bytes(data[16:20], byte_order)
    payload = data[20:20 + original_length]

    return EnhancedPacketBlock(payload=payload)


def _read_block(
    source: BufferedIOBase,
    byte_order: Optional[ByteOrder]
) -> Optional[Block]:
    buffer = source.read(8)

    if not buffer:
        return None

    block_type, block_length = buffer[0:4], buffer[4:8]

    if block_type == _BlockType.HEADER:
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
    elif block_type == _BlockType.INTERFACE_DESCRIPTION:
        data = source.read(int.from_bytes(block_length, byte_order) - 8)

        return _decode_interface_description_block(data, byte_order)
    elif block_type == _BlockType.ENHANCED_PACKET:
        data = source.read(int.from_bytes(block_length, byte_order) - 8)

        return _decode_enhanced_packet_block(data, byte_order)
    else:
        raise NotImplementedError


def stream(source: BufferedIOBase) -> Iterator[Block]:
    last_header_block = None

    while True:
        byte_order = last_header_block.byte_order \
            if last_header_block else None

        block = _read_block(source, byte_order)

        if block is None:
            if last_header_block is None:
                raise EOFError

            return
        elif isinstance(block, HeaderBlock):
            last_header_block = block
        elif not last_header_block:
            raise FormatError

        yield block
