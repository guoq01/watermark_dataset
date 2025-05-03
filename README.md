# watermark_dataset
## Project Overview
This project aims to construct a network stream data set with watermarks created by different watermarking methods, so that researchers can understand the structure of the watermarked streams rather than just having an abstract understanding. The data set should contain network stream data with watermarks associated by different watermarking methods.
The network flow datasets constructed by various flow embedding methods.

## Feature Description
1. **Network Structure Description:** We have set up a one-way transmission local area network, which consists of four nodes and devices including sending, embedding, collecting and receiving. The IP address of the sending end is 192.168.5.11, and that of the receiving end is 192.168.8.12.
2. **traffic description:**ICMP, SSH, IP, TCp, HTTP, DNS

## Source Directory
### Files
- [LICENSE](./LICENSE): Specify the usage permissions of developers or organizations using the code.
- [README.md](./README.md):Contains a basic introduction to this project.
### Subfolders
[WateramrkDA](./):Contains the network stream data set. Each method involves ten pcap files (for continuous collection)

- [SIBW](./centroid/)

- [Quaternary](./interval_counting_2bit/)

- [Hexadecimal](./interval_counting_4bit/)

- [FRW-TRACE](./multi_beacon/)

- [IP-Based](./packet_content_based/ip_based/)

- [TCP-Based](./packet_content_based/tcp_based/)

- [HTTP-Based](./packet_content_based/http_based/)

- [DNS-Based](./packet_content_based/dns_based/)

## Method Description
- In IP-Based dataset, watermark is embedded in IP ID filed.
- In TCP-Based dataset, watermark is embedded in TCP Options filed.
- In HTTP-Based dataset, watermark is embedded in HTTP user-agent filed.
- In DNS-Based dataset, watermark is embedded in DNS Query question filed.

## Usage Instructions
You can use Wireshark/Python ... to view each pcap file.


The command for collecting network flow data：`tcpdump -i ens224 dst host 192.168.8.12 xxx.pcap`

## Result Dataset
The data structure should be like this:
```
/watermarkDA
    /FRW-TRACE
        /icmp
        /ssh
    /Hexadecimal
        /icmp
        /ssh
    /Packet_Content_Based
        /dns_based
            dns_1.pcap
            ...
    ...
```

## Version History
- initial version: May 3, 2025
## Contact Information
_If you have any questions or need further assistance, please contact us via Contact Information._