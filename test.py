import cProfile

import pyiex.pcap_tops
import pyiex.tops


def main():
    with open("./test.pcap", "rb") as stream:
        for i, message in enumerate(pyiex.pcap_tops.read(stream)):
            if i == 1_000_000:
                return

            if not isinstance(message, pyiex.tops.QuoteUpdateMessage):
                continue

            if message.symbol != "AAPL":
                continue
            
            row = ",".join((
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
