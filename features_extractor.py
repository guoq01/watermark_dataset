import pandas as pd
import numpy as np
from scipy.stats import entropy
from collections import Counter

class FeatureExtractor:
    def __init__(self, processed_csv_dir, output_dir="features"):
        self.processed_csv_dir = processed_csv_dir
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def _extract_temporal_features(self, df):
        """提取时序类特征（针对包时间/序列水印）"""
        if len(df) < 2:
            return pd.Series(dtype="float64")
        # 包间隔时间（IAT）统计
        iat = df["timestamp"].diff().dropna().values
        temporal_feats = {
            "iat_mean": np.mean(iat),
            "iat_std": np.std(iat),
            "iat_max": np.max(iat),
            "iat_min": np.min(iat),
            "iat_median": np.median(iat),
            # 流持续时间
            "flow_duration": df["timestamp"].iloc[-1] - df["timestamp"].iloc[0],
            # 包数量
            "pkt_count": len(df)
        }
        return pd.Series(temporal_feats)

    def _extract_content_features(self, df):
        """提取内容类特征（针对包内容水印）"""
        if df.empty:
            return pd.Series(dtype="float64")
        # 包长统计
        pkt_lens = df["pkt_len"].values
        content_feats = {
            "pkt_len_mean": np.mean(pkt_lens),
            "pkt_len_std": np.std(pkt_lens),
            "pkt_len_max": np.max(pkt_lens),
            "pkt_len_min": np.min(pkt_lens),
            # 协议分布（TCP/UDP/ICMP占比）
            "tcp_ratio": len(df[df["protocol"] == 6]) / len(df),
            "udp_ratio": len(df[df["protocol"] == 17]) / len(df),
            "icmp_ratio": len(df[df["protocol"] == 1]) / len(df),
            # 载荷长度熵（反映内容随机性）
            "payload_entropy": entropy(df["payload_len"].value_counts(normalize=True)) if "payload_len" in df else 0
        }
        return pd.Series(content_feats)

    def _extract_sequence_features(self, df):
        """提取序列类特征（针对包序列模式水印）"""
        if len(df) < 3:
            return pd.Series(dtype="float64")
        # 包长序列自相关（滞后1阶）
        pkt_lens = df["pkt_len"].values
        seq_feats = {
            "seq_autocorr_lag1": np.corrcoef(pkt_lens[:-1], pkt_lens[1:])[0, 1] if len(pkt_lens) > 1 else 0,
            # 包长变化趋势（上升/下降次数占比）
            "len_increase_ratio": np.sum(np.diff(pkt_lens) > 0) / (len(pkt_lens) - 1),
            "len_decrease_ratio": np.sum(np.diff(pkt_lens) < 0) / (len(pkt_lens) - 1),
            # 高频包长占比（Top 3包长的总占比）
            "top3_len_ratio": sum([v for k, v in Counter(pkt_lens).most_common(3)]) / len(pkt_lens)
        }
        return pd.Series(seq_feats)

    def extract_all_features(self):
        """批量提取所有CSV的特征并合并"""
        csv_files = [f for f in os.listdir(self.processed_csv_dir) if f.endswith(".csv")]
        all_features = []
        for csv_file in tqdm(csv_files, desc="Extracting features"):
            csv_path = os.path.join(self.processed_csv_dir, csv_file)
            df = pd.read_csv(csv_path)
            # 提取三类特征
            temporal = self._extract_temporal_features(df)
            content = self._extract_content_features(df)
            sequence = self._extract_sequence_features(df)
            # 合并特征，保留文件名（用于后续打标签）
            feats = pd.concat([temporal, content, sequence])
            feats["file_name"] = csv_file
            all_features.append(feats)
        # 保存特征矩阵
        feature_df = pd.DataFrame(all_features).reset_index(drop=True)
        output_path = os.path.join(self.output_dir, "watermarking_features.csv")
        feature_df.to_csv(output_path, index=False)
        return feature_df

# ------------------- 示例用法 -------------------
if __name__ == "__main__":
    extractor = FeatureExtractor(processed_csv_dir="./processed_pcap", output_dir="./features")
    feature_df = extractor.extract_all_features()