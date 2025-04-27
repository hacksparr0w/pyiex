import pandas as pd
import pyiex.pcap_tops
import pyiex.tops


def main():
    rows = []

    with open("./test.pcap", "rb") as stream:
        for message in pyiex.pcap_tops.read(stream):
            if not isinstance(message, pyiex.tops.QuoteUpdateMessage):
                continue

            if message.symbol != "AAPL":
                continue

            row = (
                message.timestamp,
                message.symbol,
                message.bid_price,
                message.bid_size,
                message.ask_price,
                message.ask_size
            )

            rows.append(row)

    df = pd.DataFrame(
        rows,
        columns=[
            "timestamp",
            "symbol",
            "bid_price",
            "bid_size",
            "ask_price",
            "ask_size"
        ]
    )

    df.to_csv("test.csv", index=False)


if __name__ == "__main__":
    main()
