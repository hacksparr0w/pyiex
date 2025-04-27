import subprocess
import gzip

import pyiex.pcap_tops
import pyiex.tops


def avg(x):
    return round(sum(x) / len(x))


def process_file(input_path, output_path, aggregation_unit=1e9):

    with gzip.open(input_path, "rb") as input_stream, \
        open(output_path, "w", encoding="utf-8") as output_stream:

        print("timestamp;symbol;bid_price;ask_price", file=output_stream)

        is_regular_market_hours = False

        current_timestamp = None
        current_bid_prices = []
        current_ask_prices = []
        for message in pyiex.pcap_tops.read(input_stream):
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
            elif (current_timestamp + aggregation_unit) < message.timestamp:
                row = ";".join((
                    str(current_timestamp),
                    message.symbol,
                    str(avg(current_bid_prices)),
                    str(avg(current_ask_prices))
                ))

                print(row, file=output_stream)

                current_timestamp = message.timestamp
                current_ask_prices.clear()
                current_bid_prices.clear()

            current_ask_prices.append(message.ask_price)
            current_bid_prices.append(message.bid_price)


def main():
    links = {
        "2025-04-25": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250425%2F20250425_IEXTP1_TOPS1.6.pcap.gz?generation=1745626974023747&alt=media",
        "2025-04-24": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250424%2F20250424_IEXTP1_TOPS1.6.pcap.gz?generation=1745545069801576&alt=media",
        "2025-04-23": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250423%2F20250423_IEXTP1_TOPS1.6.pcap.gz?generation=1745459879028669&alt=media",
        "2025-04-22": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250422%2F20250422_IEXTP1_TOPS1.6.pcap.gz?generation=1745369952143289&alt=media",
        "2025-04-21": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250421%2F20250421_IEXTP1_TOPS1.6.pcap.gz?generation=1745283721222606&alt=media",
        "2025-04-17": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250417%2F20250417_IEXTP1_TOPS1.6.pcap.gz?generation=1744942534048351&alt=media",
        "2025-04-16": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250416%2F20250416_IEXTP1_TOPS1.6.pcap.gz?generation=1744853556336085&alt=media",
        "2025-04-15": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250415%2F20250415_IEXTP1_TOPS1.6.pcap.gz?generation=1744764186822710&alt=media",
        "2025-04-14": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250414%2F20250414_IEXTP1_TOPS1.6.pcap.gz?generation=1744681153883400&alt=media",
        "2025-04-11": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250411%2F20250411_IEXTP1_TOPS1.6.pcap.gz?generation=1744431185489107&alt=media",
        "2025-04-10": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250410%2F20250410_IEXTP1_TOPS1.6.pcap.gz?generation=1744354138437081&alt=media",
        "2025-04-09": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250409%2F20250409_IEXTP1_TOPS1.6.pcap.gz?generation=1744277763134834&alt=media",
        "2025-04-08": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250408%2F20250408_IEXTP1_TOPS1.6.pcap.gz?generation=1744194017871262&alt=media",
        "2025-04-07": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250407%2F20250407_IEXTP1_TOPS1.6.pcap.gz?generation=1744115490610187&alt=media",
        "2025-04-04": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250404%2F20250404_IEXTP1_TOPS1.6.pcap.gz?generation=1743842813662616&alt=media",
        "2025-04-03": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250403%2F20250403_IEXTP1_TOPS1.6.pcap.gz?generation=1743735209413997&alt=media",
        "2025-04-02": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250402%2F20250402_IEXTP1_TOPS1.6.pcap.gz?generation=1743643308760910&alt=media",
        "2025-04-01": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250401%2F20250401_IEXTP1_TOPS1.6.pcap.gz?generation=1743560236323284&alt=media",
        "2025-03-31": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250331%2F20250331_IEXTP1_TOPS1.6.pcap.gz?generation=1743473680847250&alt=media",
        "2025-03-28": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250328%2F20250328_IEXTP1_TOPS1.6.pcap.gz?generation=1743211583122927&alt=media",
        "2025-03-27": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250327%2F20250327_IEXTP1_TOPS1.6.pcap.gz?generation=1743131733645884&alt=media",
        "2025-03-26": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250326%2F20250326_IEXTP1_TOPS1.6.pcap.gz?generation=1743042825877458&alt=media",
        "2025-03-25": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250325%2F20250325_IEXTP1_TOPS1.6.pcap.gz?generation=1742946995506801&alt=media",
        "2025-03-24": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250324%2F20250324_IEXTP1_TOPS1.6.pcap.gz?generation=1742867244811298&alt=media",
        "2025-03-21": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250321%2F20250321_IEXTP1_TOPS1.6.pcap.gz?generation=1742608870460449&alt=media",
        "2025-03-20": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250320%2F20250320_IEXTP1_TOPS1.6.pcap.gz?generation=1742523901262889&alt=media",
        "2025-03-19": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250319%2F20250319_IEXTP1_TOPS1.6.pcap.gz?generation=1742434060446634&alt=media",
        "2025-03-18": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250318%2F20250318_IEXTP1_TOPS1.6.pcap.gz?generation=1742345543230290&alt=media",
        "2025-03-17": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250317%2F20250317_IEXTP1_TOPS1.6.pcap.gz?generation=1742259135221766&alt=media",
        "2025-03-14": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250314%2F20250314_IEXTP1_TOPS1.6.pcap.gz?generation=1742003525373136&alt=media",
        "2025-03-13": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250313%2F20250313_IEXTP1_TOPS1.6.pcap.gz?generation=1741930090972703&alt=media",
        "2025-03-12": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250312%2F20250312_IEXTP1_TOPS1.6.pcap.gz?generation=1741836300748624&alt=media",
        "2025-03-11": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250311%2F20250311_IEXTP1_TOPS1.6.pcap.gz?generation=1741748364330444&alt=media",
        "2025-03-10": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250310%2F20250310_IEXTP1_TOPS1.6.pcap.gz?generation=1741659600016093&alt=media",
        "2025-03-07": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250307%2F20250307_IEXTP1_TOPS1.6.pcap.gz?generation=1741404233268614&alt=media",
        "2025-03-06": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250306%2F20250306_IEXTP1_TOPS1.6.pcap.gz?generation=1741339823007285&alt=media",
        "2025-03-05": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250305%2F20250305_IEXTP1_TOPS1.6.pcap.gz?generation=1741237305792573&alt=media",
        "2025-03-04": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250304%2F20250304_IEXTP1_TOPS1.6.pcap.gz?generation=1741149009323669&alt=media",
        "2025-03-03": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250303%2F20250303_IEXTP1_TOPS1.6.pcap.gz?generation=1741058226560004&alt=media",
        "2025-02-28": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250228%2F20250228_IEXTP1_TOPS1.6.pcap.gz?generation=1740802381327139&alt=media",
        "2025-02-27": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250227%2F20250227_IEXTP1_TOPS1.6.pcap.gz?generation=1740723952786520&alt=media",
        "2025-02-26": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250226%2F20250226_IEXTP1_TOPS1.6.pcap.gz?generation=1740625634125909&alt=media",
        "2025-02-25": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250225%2F20250225_IEXTP1_TOPS1.6.pcap.gz?generation=1740538318892793&alt=media",
        "2025-02-24": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250224%2F20250224_IEXTP1_TOPS1.6.pcap.gz?generation=1740448206690539&alt=media",
        "2025-02-21": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250221%2F20250221_IEXTP1_TOPS1.6.pcap.gz?generation=1740201545261211&alt=media",
        "2025-02-20": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250220%2F20250220_IEXTP1_TOPS1.6.pcap.gz?generation=1740105616822995&alt=media",
        "2025-02-19": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250219%2F20250219_IEXTP1_TOPS1.6.pcap.gz?generation=1740013297627357&alt=media",
        "2025-02-18": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250218%2F20250218_IEXTP1_TOPS1.6.pcap.gz?generation=1739926682613249&alt=media",
        "2025-02-14": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250214%2F20250214_IEXTP1_TOPS1.6.pcap.gz?generation=1739586157511015&alt=media",
        "2025-02-13": "https://www.googleapis.com/download/storage/v1/b/iex/o/data%2Ffeeds%2F20250213%2F20250213_IEXTP1_TOPS1.6.pcap.gz?generation=1739495726621072&alt=media"
    }

    for i, (name, link) in enumerate(links.items()):
        print(f"Job {i}")

        subprocess.run(
            f"curl -s --output ./data/{name}.pcap.gzip \"{link}\"",
            shell=True,
            check=True
        )

        process_file(f"./data/{name}.pcap.gzip", f"./data/{name}-AAPL-1s.csv", aggregation_unit=1e9)
        process_file(f"./data/{name}.pcap.gzip", f"./data/{name}-AAPL-1m.csv", aggregation_unit=60 * 1e9)

        subprocess.run(f"rm -f ./data/{name}.pcap.gzip", shell=True, check=True)
        print(f"Finished job {i}")


if __name__ == "__main__":
    main()
