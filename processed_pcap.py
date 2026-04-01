import os
import pandas as pd
from scapy.all import rdpcap, IP, TCP, UDP, ICMP
from tqdm import tqdm

class PCAPProcessor:
    def __init__(self, pcap_dir, output_dir="processed_pcap"):
        self.pcap_dir = pcap_dir
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def _parse_single_pcap(self, pcap_path):
        """解析单个PCAP文件，提取核心包信息"""
        packets = rdpcap(pcap_path)
        data = []
        for pkt in packets:
            if IP in pkt:  # 仅保留含IP层的包
                pkt_info = {
                    "timestamp": pkt.time,
                    "src_ip": pkt[IP].src,
                    "dst_ip": pkt[IP].dst,
                    "protocol": pkt[IP].proto,  # 6=TCP, 17=UDP, 1=ICMP
                    "pkt_len": len(pkt),
                    "payload_len": len(pkt[IP].payload) if IP in pkt else 0
                }
                # 补充TCP/UDP/ICMP层信息
                if TCP in pkt:
                    pkt_info.update({"src_port": pkt[TCP].sport, "dst_port": pkt[TCP].dport})
                elif UDP in pkt:
                    pkt_info.update({"src_port": pkt[UDP].sport, "dst_port": pkt[UDP].dport})
                elif ICMP in pkt:
                    pkt_info.update({"type": pkt[ICMP].type, "code": pkt[ICMP].code})
                data.append(pkt_info)
        return pd.DataFrame(data)

    def _clean_traffic(self, df):
        """流量清洗：去重、过滤异常包"""
        if df.empty:
            return df
        # 去重（完全相同的时间戳+五元组）
        df = df.drop_duplicates(subset=["timestamp", "src_ip", "dst_ip", "protocol", "src_port", "dst_port"], keep="first")
        # 过滤长度异常的包（小于20字节或大于MTU）
        df = df[(df["pkt_len"] >= 20) & (df["pkt_len"] <= 1500)]
        # 按时间戳排序
        df = df.sort_values("timestamp").reset_index(drop=True)
        return df

    def process_all(self):
        """批量处理所有PCAP文件"""
        pcap_files = [f for f in os.listdir(self.pcap_dir) if f.endswith(".pcap")]
        for pcap_file in tqdm(pcap_files, desc="Processing PCAP files"):
            pcap_path = os.path.join(self.pcap_dir, pcap_file)
            try:
                df = self._parse_single_pcap(pcap_path)
                df_clean = self._clean_traffic(df)
                # 保存为CSV，文件名与PCAP一致
                output_path = os.path.join(self.output_dir, f"{os.path.splitext(pcap_file)[0]}.csv")
                df_clean.to_csv(output_path, index=False)
            except Exception as e:
                print(f"Error processing {pcap_file}: {str(e)}")

# ------------------- 示例用法 -------------------
if __name__ == "__main__":
    processor = PCAPProcessor(pcap_dir="./raw_pcap", output_dir="./processed_pcap")
    processor.process_all()