import pyiex.pcap_tops
import pyiex.tops


def main():
    print("timestamp;symbol;bid_price;bid_size;ask_price;ask_size")

    with open("./test.pcap", "rb") as stream:
        for message in pyiex.pcap_tops.read(stream):

            if message.__class__.__name__ != \
                pyiex.tops.QuoteUpdateMessage.__name__:
                continue

            if message.symbol != "AAPL":
                continue

            if message.bid_price == 0 or message.ask_price == 0:
                continue

            row = ";".join((
                str(message.timestamp),
                message.symbol,
                str(message.bid_price),
                str(message.bid_size),
                str(message.ask_price),
                str(message.ask_size)
            ))

            print(row)


if __name__ == "__main__":
    main()
