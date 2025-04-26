from pydantic import BaseModel

from .format import ByteOrder


__all__ = (
    "Packet",

    "decode"
)


class Packet(BaseModel):
    version: int
    protocol_id: int
    channel_id: int
    session_id: int
    payload_length: int
    message_count: int
    stream_offset: int
    sequence_number: int
    sent_at: int

    messages: list[bytes]


def decode(data: bytes, byte_order: ByteOrder = "little") -> Packet:
    version = int.from_bytes(data[0:1], byte_order)
    protocol_id = int.from_bytes(data[2:4], byte_order)
    channel_id = int.from_bytes(data[4:8], byte_order)
    session_id = int.from_bytes(data[8:12], byte_order)
    payload_length = int.from_bytes(data[12:14], byte_order)
    message_count = int.from_bytes(data[14:16], byte_order)
    stream_offset = int.from_bytes(data[16:24], byte_order)
    sequence_number = int.from_bytes(data[24:32], byte_order)
    sent_at = int.from_bytes(data[32:40], byte_order)

    messages = []
    offset = 40

    for _ in range(message_count):
        message_length = int.from_bytes(data[offset:offset + 2], byte_order)
        offset += 2

        message = data[offset:offset + message_length]
        offset += message_length

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
