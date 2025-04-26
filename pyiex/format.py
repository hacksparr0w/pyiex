from typing import Literal


__all__ = (
    "ByteOrder",
    "FormatError"
)


type ByteOrder = Literal["little", "big"]


class FormatError(Exception):
    pass
