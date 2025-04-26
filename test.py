import pyiex.pcap


def main():
    source = open("./test.pcap", "rb")

    for x in pyiex.pcap.Stream(source):
        pass


if __name__ == "__main__":
    main()
