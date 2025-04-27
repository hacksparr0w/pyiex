import pyiex.pcap_tops


def main():
    source = open("./test.pcap", "rb")

    for x in pyiex.pcap_tops.read(source):
        pass


if __name__ == "__main__":
    main()
