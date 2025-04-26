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
    InterfaceDescriptionBlock
]


def _read_header_block(source: BufferedIOBase) -> HeaderBlock:
    block_type = source.read(4)

    if block_type != BlockType.HEADER:
        raise FormatError

    block_length = source.read(4)
    magic_bytes = source.read(4)
    byte_order: ByteOrder

    if magic_bytes == b"\x1a\x2b\x3c\x4d":
        byte_order = "big"
    elif magic_bytes == b"\x4d\x3c\x2b\x1a":
        byte_order = "little"
    else:
        raise FormatError

    block_length = int.from_bytes(block_length, byte_order)

    source.seek(block_length - 12, os.SEEK_CUR)

    return HeaderBlock(byte_order=byte_order)


def _read_interface_description_block(
    source: BufferedIOBase,
    byte_order: ByteOrder
) -> InterfaceDescriptionBlock:
    block_type = source.read(4)

    if block_type != BlockType.INTERFACE_DESCRIPTION:
        raise FormatError

    block_length = int.from_bytes(source.read(4), byte_order)

    source.seek(block_length - 8, os.SEEK_CUR)

    return None


def _read_enhanced_packet_block(
    source: BufferedIOBase,
    byte_order: ByteOrder
) -> EnhancedPacketBlock:
    block_type = source.read(4)

    if block_type != BlockType.ENHANCED_PACKET:
        raise FormatError
    
    block_length = int.from_bytes(source.read(4), byte_order)

    source.seek(block_length - 8, os.SEEK_CUR)

    return None


def _read_block(source: BufferedIOBase, byte_order: Optional[ByteOrder]) -> Block:
    block_type = source.read(4)

    if not block_type:
        raise EOFError

    source.seek(-4, os.SEEK_CUR)

    match block_type:
        case BlockType.HEADER:
            return _read_header_block(source)
        case BlockType.INTERFACE_DESCRIPTION:
            return _read_interface_description_block(source, byte_order)
        case BlockType.ENHANCED_PACKET:
            return _read_enhanced_packet_block(source, byte_order)
        case _:
            raise FormatError


class Stream:
    _source: BufferedIOBase
    _last_header_block: Optional[HeaderBlock]

    def __init__(self, source: BufferedIOBase) -> None:
        self._source = source
        self._last_header_block = None

    def __iter__(self) -> Iterator[Block]:
        return self

    def __next__(self) -> Block:
        block: Block

        if self._last_header_block is None:
            block = _read_header_block(self._source)
        else:
            block = _read_block(
                self._source,
                self._last_header_block.byte_order
            )

        if isinstance(block, HeaderBlock):
            self._last_header_block = block

        return block
