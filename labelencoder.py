import pandas as pd
import os

class LabelEncoder:
    def __init__(self, feature_csv_path, output_dir="features"):
        self.feature_df = pd.read_csv(feature_csv_path)
        self.output_dir = output_dir
        # 定义水印类型映射（根据实际文件名调整）
        self.watermark_mapping = {
            "normal": 0,
            "Quaternary": 1,
            "Hexadecimal": 2,
            "SIBW": 3,
            "FRW-TRACE": 4,
            "IP-Based": 5,
            "TCP-Based": 6,
            "HTTP-Based": 7,
            "DNS-Based": 8
        }

    def _map_label_from_filename(self, file_name):
        """从文件名中提取水印类型并映射为整数标签"""
        for watermark_type, label in self.watermark_mapping.items():
            if watermark_type in file_name:
                return label
        return -1  # 未识别类型

    def encode_labels(self):
        """完成标签编码并保存"""
        # 映射整数标签
        self.feature_df["label"] = self.feature_df["file_name"].apply(self._map_label_from_filename)
        # 过滤未识别标签的样本
        self.feature_df = self.feature_df[self.feature_df["label"] != -1].reset_index(drop=True)
        # 生成One-Hot编码（可选）
        one_hot = pd.get_dummies(self.feature_df["label"], prefix="watermark_type")
        self.feature_df = pd.concat([self.feature_df, one_hot], axis=1)
        # 保存带标签的特征矩阵
        output_path = os.path.join(self.output_dir, "watermarking_features_with_labels.csv")
        self.feature_df.to_csv(output_path, index=False)
        return self.feature_df

# ------------------- 示例用法 -------------------
if __name__ == "__main__":
    encoder = LabelEncoder(feature_csv_path="./features/watermarking_features.csv")
    labeled_df = encoder.encode_labels()