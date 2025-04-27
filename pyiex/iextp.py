import os

from io import BufferedIOBase, BytesIO

from pydantic import BaseModel, ConfigDict as ModelConfig

from .format import ByteOrder


__all__ = (
    "Packet",

    "read_packet"
)


class Packet(BaseModel):
    model_config = ModelConfig(arbitrary_types_allowed=True)

    version: int
    protocol_id: int
    channel_id: int
    session_id: int
    payload_length: int
    message_count: int
    stream_offset: int
    sequence_number: int
    sent_at: int

    messages: list[BytesIO]


def read_packet(
    stream: BufferedIOBase,
    byte_order: ByteOrder = "little"
) -> Packet:
    version = int.from_bytes(stream.read(1), byte_order)
    stream.seek(1, os.SEEK_CUR)
    protocol_id = int.from_bytes(stream.read(2), byte_order)
    channel_id = int.from_bytes(stream.read(4), byte_order)
    session_id = int.from_bytes(stream.read(4), byte_order)
    payload_length = int.from_bytes(stream.read(2), byte_order)
    message_count = int.from_bytes(stream.read(2), byte_order)
    stream_offset = int.from_bytes(stream.read(8), byte_order)
    sequence_number = int.from_bytes(stream.read(8), byte_order)
    sent_at = int.from_bytes(stream.read(8), byte_order)

    messages = []

    for _ in range(message_count):
        message_length = int.from_bytes(stream.read(2), byte_order)
        message = BytesIO(stream.read(message_length))

        messages.append(message)

    return Packet(
        version=version,
        protocol_id=protocol_id,
        channel_id=channel_id,
        session_id=session_id,
        payload_length=payload_length,
        message_count=message_count,
        stream_offset=stream_offset,
        sequence_number=sequence_number,
        sent_at=sent_at,
        messages=messages
    )
