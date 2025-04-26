import pyiex.pcap


def main():
    source = open("./test.pcap", "rb")

    for i, x in enumerate(pyiex.pcap.Stream(source)):
        pass


if __name__ == "__main__":
    main()
