import pyiex.pcap_tops
import pyiex.tops


def avg(x):
    return round(sum(x) / len(x))


def main():
    print("timestamp;symbol;bid_price;ask_price")

    aggregation_unit = 1e12
    is_regular_market_hours = False

    current_timestamp = None
    current_bid_prices = []
    current_ask_prices = []

    with open("./test.pcap", "rb") as stream:
        for message in pyiex.pcap_tops.read(stream):
            if message.__class__.__name__ == \
                pyiex.tops.SystemEventMessage.__name__:

                if message.event == \
                    pyiex.tops.SystemEvent.REGULAR_MARKET_HOURS_START:

                    is_regular_market_hours = True
                elif message.event == \
                    pyiex.tops.SystemEvent.REGULAR_MARKET_HOURS_END:

                    is_regular_market_hours = False

                continue

            if not is_regular_market_hours:
                continue

            if message.__class__.__name__ != \
                pyiex.tops.QuoteUpdateMessage.__name__:
                continue

            if message.symbol != "AAPL":
                continue

            if current_timestamp is None:
                current_timestamp = message.timestamp
            elif (current_timestamp + aggregation_unit) > message.timestamp:
                row = ";".join((
                    str(current_timestamp),
                    message.symbol,
                    str(avg(current_bid_prices)),
                    str(avg(current_ask_prices))
                ))

                print(row)

                current_timestamp = message.timestamp
                current_ask_prices.clear()
                current_bid_prices.clear()

            current_ask_prices.append(message.ask_price)
            current_bid_prices.append(message.bid_price)

    if current_ask_prices:
        row = ";".join((
            current_timestamp,
            message.symbol,
            avg(current_bid_prices),
            avg(current_ask_prices)
        ))

        print(row)


if __name__ == "__main__":
    main()
