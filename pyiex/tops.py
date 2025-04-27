from io import BufferedIOBase
from enum import StrEnum, auto
from dataclasses import dataclass

from pydantic import BaseModel

from .format import ByteOrder


__all__ = (
    "Message",
    "SystemEventMessage",

    "read_message"
)


class _MessageType:
    SYSTEM_EVENT = b"\x53"
    SECURITY_DIRECTORY = b"\x44"
    SECURITY_TRADING_STATUS = b"\x48"
    RETAIL_LIQUIDITY_INDICATOR = b"\x49"
    OPERATIONAL_HALT_STATUS = b"\x4f"
    SHORT_SALE_PRICE_TEST_STATUS = b"\x50"
    QUOTE_UPDATE = b"\x51"
    TRADE_REPORT = b"\x54"
    OFFICIAL_PRICE = b"\x58"
    TRADE_BREAK = b"\x42"
    AUCTION_INFORMATION = b"\x41"


class SystemEvent(StrEnum):
    MESSAGES_END = auto()
    MESSAGES_START = auto()
    REGULAR_MARKET_HOURS_END = auto()
    REGULAR_MARKET_HOURS_START = auto()
    SYSTEM_HOURS_END = auto()
    SYSTEM_HOURS_START = auto()


_SystemEventType = {
    b"\x4f": SystemEvent.MESSAGES_START,
    b"\x53": SystemEvent.SYSTEM_HOURS_START,
    b"\x52": SystemEvent.REGULAR_MARKET_HOURS_START,
    b"\x4d": SystemEvent.REGULAR_MARKET_HOURS_END,
    b"\x45": SystemEvent.SYSTEM_HOURS_END,
    b"\x43": SystemEvent.MESSAGES_END
}


@dataclass
class SystemEventMessage:
    event: bytes
    timestamp: int


@dataclass
class SecurityDirectoryMessage:
    flags: bytes
    timestamp: int
    symbol: str
    round_lot_size: int
    adjusted_poc_price: int
    luld_tier: bytes


@dataclass
class SecurityTradingStatusMessage:
    status: bytes
    timestamp: int
    symbol: str
    reason: str


@dataclass
class RetailLiquidityIndicatorMessage:
    indicator: bytes
    timestamp: int
    symbol: str


@dataclass
class OperationalHaltStatusMessage:
    status: bytes
    timestamp: int
    symbol: str


@dataclass
class ShortSalePriceTestStatusMessage:
    status: bytes
    timestamp: int
    symbol: str
    detail: bytes


@dataclass
class QuoteUpdateMessage:
    flags: bytes
    timestamp: int
    symbol: str
    bid_size: int
    bid_price: int
    ask_price: int
    ask_size: int


@dataclass
class TradeReportMessage:
    flags: bytes
    timestamp: int
    symbol: str
    size: int
    price: int
    trade_id: int


@dataclass
class OfficialPriceMessage:
    price_type: bytes
    timestamp: int
    symbol: str
    price: int


@dataclass
class TradeBreakMessage:
    flags: bytes
    timestamp: int
    symbol: int
    size: int
    price: int
    trade_id: int


@dataclass
class AuctionInformationMessage:
    auction_type: bytes
    timestamp: int
    symbol: str
    paired_shares: int
    reference_price: int
    indicative_clearing_price: int
    imbalance_shares: int
    imbalance_side: int
    extension_number: int
    scheduled_auction_time: int
    auction_book_clearing_price: int
    collar_reference_price: int
    lower_auction_collar: int
    upper_auction_collar: int


type Message = [
    SystemEventMessage,
]


def _read_price(stream: BufferedIOBase, byte_order: ByteOrder) -> int:
    return int.from_bytes(stream.read(8), byte_order)


def _read_timestamp(stream: BufferedIOBase, byte_order: ByteOrder) -> int:
    return int.from_bytes(stream.read(8), byte_order)


def _read_string(stream: BufferedIOBase, length: int) -> str:
    return stream.read(length).decode("utf-8").rstrip()


def _read_system_event_message(
    stream: BufferedIOBase,
    byte_order: ByteOrder
) -> SystemEventMessage:
    event = _SystemEventType[stream.read(1)]
    timestamp = _read_timestamp(stream, byte_order)

    return SystemEventMessage(event, timestamp)


def _read_security_directory_message(
    stream: BufferedIOBase,
    byte_order: ByteOrder
 ) -> SecurityDirectoryMessage:
    flags = stream.read(1)
    timestamp = _read_timestamp(stream, byte_order)
    symbol = _read_string(stream, 8)
    round_lot_size = int.from_bytes(stream.read(4), byte_order)
    adjusted_poc_price = _read_price(stream, byte_order)
    luld_tier = stream.read(1)

    return SecurityDirectoryMessage(
        flags,
        timestamp,
        symbol,
        round_lot_size,
        adjusted_poc_price,
        luld_tier
    )


def _read_security_trading_status_message(
    stream: BufferedIOBase,
    byte_order: ByteOrder
) -> SecurityTradingStatusMessage:
    status = stream.read(1)
    timestamp = _read_timestamp(stream, byte_order)
    symbol = _read_string(stream, 8)
    reason = _read_string(stream, 4)

    return SecurityTradingStatusMessage(
        status,
        timestamp,
        symbol,
        reason
    )


def _read_retail_liquidity_indicator_message(
    stream: BufferedIOBase,
    byte_order: ByteOrder
) -> RetailLiquidityIndicatorMessage:
    indicator = stream.read(1)
    timestamp = _read_timestamp(stream, byte_order)
    symbol = _read_string(stream, 8)

    return RetailLiquidityIndicatorMessage(
        indicator,
        timestamp,
        symbol
    )


def _read_operational_halt_status_message(
    stream: BufferedIOBase,
    byte_order: ByteOrder
) -> OperationalHaltStatusMessage:
    status = stream.read(1)
    timestamp = _read_timestamp(stream, byte_order)
    symbol = _read_string(stream, 8)

    return OperationalHaltStatusMessage(
        status,
        timestamp,
        symbol
    )


def _read_short_sale_price_test_message(
    stream: BufferedIOBase,
    byte_order: ByteOrder  
) -> ShortSalePriceTestStatusMessage:
    status = stream.read(1)
    timestamp = _read_timestamp(stream, byte_order)
    symbol = _read_string(stream, 8)
    detail = stream.read(1)

    return ShortSalePriceTestStatusMessage(
        status,
        timestamp,
        symbol,
        detail
    )


def _read_quote_update_message(
    stream: BufferedIOBase,
    byte_order: ByteOrder 
) -> QuoteUpdateMessage:
    flags = stream.read(1)
    timestamp = _read_timestamp(stream, byte_order)
    symbol = _read_string(stream, 8)
    bid_size = int.from_bytes(stream.read(4), byte_order)
    bid_price = _read_price(stream, byte_order)
    ask_price = _read_price(stream, byte_order)
    ask_size = int.from_bytes(stream.read(4), byte_order)

    return QuoteUpdateMessage(
        flags,
        timestamp,
        symbol,
        bid_size,
        bid_price,
        ask_price,
        ask_size
    )


def _read_trade_report_message(
    stream: BufferedIOBase,
    byte_order: ByteOrder
) -> TradeReportMessage:
    flags = stream.read(1)
    timestamp = _read_timestamp(stream, byte_order)
    symbol = _read_string(stream, 8)
    size = int.from_bytes(stream.read(4), byte_order)
    price = _read_price(stream, byte_order)
    trade_id = int.from_bytes(stream.read(8), byte_order)

    return TradeReportMessage(
        flags,
        timestamp,
        symbol,
        size,
        price,
        trade_id
    )


def _read_official_price_message(
    stream: BufferedIOBase,
    byte_order: ByteOrder
) -> OfficialPriceMessage:
    price_type = stream.read(1)
    timestamp = _read_timestamp(stream, byte_order)
    symbol = _read_string(stream, 8)
    price = _read_price(stream, byte_order)

    return OfficialPriceMessage(
        price_type,
        timestamp,
        symbol,
        price
    )


def _read_trade_break_message(
    stream: BufferedIOBase,
    byte_order: ByteOrder
) -> TradeBreakMessage:
    flags = stream.read(1)
    timestamp = _read_timestamp(stream, byte_order)
    symbol = _read_string(stream, 8)
    size = int.from_bytes(stream.read(4), byte_order)
    price = _read_price(stream, byte_order)
    trade_id = int.from_bytes(stream.read(8), byte_order)

    return TradeBreakMessage(
        flags,
        timestamp,
        symbol,
        size,
        price,
        trade_id
    )


def _read_auction_information_message(
    stream: BufferedIOBase,
    byte_order: ByteOrder
) -> AuctionInformationMessage:
    auction_type = stream.read(1)
    timestamp = _read_timestamp(stream, byte_order)
    symbol = _read_string(stream, 8)
    paired_shares = int.from_bytes(stream.read(4), byte_order)
    reference_price = _read_price(stream, byte_order)
    indicative_clearing_price = _read_price(stream, byte_order)
    imbalance_shares = int.from_bytes(stream.read(4), byte_order)
    imbalance_side = int.from_bytes(stream.read(1), byte_order)
    extension_number = int.from_bytes(stream.read(1), byte_order)
    scheduled_auction_time = int.from_bytes(stream.read(4), byte_order)
    auction_book_clearing_price = _read_price(stream, byte_order)
    collar_reference_price = _read_price(stream, byte_order)
    lower_auction_collar = _read_price(stream, byte_order)
    upper_auction_collar = _read_price(stream, byte_order)


    return AuctionInformationMessage(
        auction_type,
        timestamp,
        symbol,
        paired_shares,
        reference_price,
        indicative_clearing_price,
        imbalance_shares,
        imbalance_side,
        extension_number,
        scheduled_auction_time,
        auction_book_clearing_price,
        collar_reference_price,
        lower_auction_collar,
        upper_auction_collar
    )


def read_message(
    stream: BufferedIOBase,
    byte_order: ByteOrder = "little"
) -> Message:
    message_type = stream.read(1)

    if message_type == _MessageType.SYSTEM_EVENT:
        return _read_system_event_message(stream, byte_order)
    elif message_type == _MessageType.SECURITY_DIRECTORY:
        return _read_security_directory_message(stream, byte_order)
    elif message_type == _MessageType.SECURITY_TRADING_STATUS:
        return _read_security_trading_status_message(stream, byte_order)
    elif message_type == _MessageType.RETAIL_LIQUIDITY_INDICATOR:
        return _read_retail_liquidity_indicator_message(stream, byte_order)
    elif message_type == _MessageType.OPERATIONAL_HALT_STATUS:
        return _read_operational_halt_status_message(stream, byte_order)
    elif message_type == _MessageType.SHORT_SALE_PRICE_TEST_STATUS:
        return _read_short_sale_price_test_message(stream, byte_order)
    elif message_type == _MessageType.QUOTE_UPDATE:
        return _read_quote_update_message(stream, byte_order)
    elif message_type == _MessageType.TRADE_REPORT:
        return _read_trade_report_message(stream, byte_order)
    elif message_type == _MessageType.OFFICIAL_PRICE:
        return _read_official_price_message(stream, byte_order)
    elif message_type == _MessageType.TRADE_BREAK:
        return _read_trade_break_message(stream, byte_order)
    elif message_type == _MessageType.AUCTION_INFORMATION:
        return _read_auction_information_message(stream, byte_order)
    else:
        raise NotImplementedError(f"Unknown message type: '{message_type}'")
