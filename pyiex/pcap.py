from io import BufferedIOBase, BytesIO
from typing import Iterator, NamedTuple, Optional, Union

from .format import ByteOrder, FormatError


__all__ = (
    "Block",
    "EnhancedPacketBlock",
    "HeaderBlock",
    "InterfaceDescriptionBlock",

    "read",
    "read_block"
)


class HeaderBlock(NamedTuple):
    byte_order: ByteOrder


class InterfaceDescriptionBlock(NamedTuple):
    pass


class EnhancedPacketBlock(NamedTuple):
    payload: BytesIO


type Block = Union[
    HeaderBlock,
    InterfaceDescriptionBlock,
    EnhancedPacketBlock
]


class _BlockType:
    HEADER = b"\x0a\x0d\x0d\x0a"
    INTERFACE_DESCRIPTION = b"\x01\x00\x00\x00"
    ENHANCED_PACKET = b"\x06\x00\x00\x00"


def _read_header_block(
    stream: BufferedIOBase,
    byte_order: ByteOrder
) -> HeaderBlock:
    return HeaderBlock(byte_order=byte_order)


def _read_interface_description_block(
    stream: BufferedIOBase,
    byte_order: ByteOrder
) -> InterfaceDescriptionBlock:
    return InterfaceDescriptionBlock()


def _read_enhanced_packet_block(
    stream: BufferedIOBase,
    byte_order: ByteOrder
) -> EnhancedPacketBlock:
    stream.seek(16)

    original_length = int.from_bytes(stream.read(4), byte_order)
    payload = BytesIO(stream.read(original_length))

    return EnhancedPacketBlock(payload)


def read_block(
    stream: BufferedIOBase,
    byte_order: Optional[ByteOrder]
) -> Optional[Block]:
    buffer = stream.read(8)

    if not buffer:
        return None

    block_type, block_length = buffer[0:4], buffer[4:8]

    if block_type == _BlockType.HEADER:
        magic_bytes = stream.read(4)
        byte_order: ByteOrder

        if magic_bytes == b"\x1a\x2b\x3c\x4d":
            byte_order = "big"
        elif magic_bytes == b"\x4d\x3c\x2b\x1a":
            byte_order = "little"
        else:
            raise FormatError

        data = stream.read(int.from_bytes(block_length, byte_order) - 12)

        return _read_header_block(BytesIO(data), byte_order)
    elif block_type == _BlockType.INTERFACE_DESCRIPTION:
        data = stream.read(int.from_bytes(block_length, byte_order) - 8)

        return _read_interface_description_block(BytesIO(data), byte_order)
    elif block_type == _BlockType.ENHANCED_PACKET:
        data = stream.read(int.from_bytes(block_length, byte_order) - 8)

        return _read_enhanced_packet_block(BytesIO(data), byte_order)
    else:
        raise NotImplementedError


def read(stream: BufferedIOBase) -> Iterator[Block]:
    last_header_block = None

    while True:
        byte_order = last_header_block.byte_order \
            if last_header_block else None

        block = read_block(stream, byte_order)

        if block is None:
            if last_header_block is None:
                raise EOFError

            return
        elif block.__class__.__name__ == HeaderBlock.__name__:
            last_header_block = block
        elif not last_header_block:
            raise FormatError

        yield block
