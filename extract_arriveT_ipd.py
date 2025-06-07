from scapy.all import rdpcap
from scapy.layers.inet import IP
import time
import csv
import os

# Get pcap file directory
pcap_dir = './pcap' # Change it to your own address
pcap_files = [f for f in os.listdir(pcap_dir) if f.endswith('.pcap')]

for pcap_file in pcap_files:
    # Read pcap file
    pcap_path = os.path.join(pcap_dir, pcap_file)
    packets = rdpcap(pcap_path)
    
    # Generate corresponding csv file names
    filename = os.path.splitext(pcap_file)[0]
    arrive_time_csv = f'./watermark_pcap/list_csv/arrive_time_{filename}.csv'
    print(arrive_time_csv)
    ipd_csv = f'./watermark_pcap/list_csv/ipd_{filename}.csv'
    # Extract timestamps
    timestamps = [pkt.time for pkt in packets if IP in pkt]
    timestamps_arrive = timestamps[:100]

    timestamps = [pkt.time for pkt in packets if IP in pkt and pkt[IP].src == "192.168.5.11"]
    # Calculate IPD (Inter-Packet Delay)
    ipd_list = [t2 - t1 for t1, t2 in zip(timestamps[:-1], timestamps[1:])]
    ipd_list = ipd_list[:100]

    # Save arrival time to csv
    with open(arrive_time_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        for timestamp in timestamps_arrive:
            writer.writerow([timestamp])

    # Save IPD to csv
    with open(ipd_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        for ipd in ipd_list:
            writer.writerow([ipd])

    print(f'Processed file: {pcap_file}')