import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import os

class DatasetSplitter:
    def __init__(self, labeled_csv_path, output_dir="datasets", test_size=0.3, random_state=42):
        self.labeled_df = pd.read_csv(labeled_csv_path)
        self.output_dir = output_dir
        self.test_size = test_size
        self.random_state = random_state
        os.makedirs(output_dir, exist_ok=True)

    def split_and_save(self):
        """分层划分数据集并保存"""
        # 分离特征（X）和标签（y），排除非特征列
        non_feature_cols = ["file_name", "label"] + [col for col in self.labeled_df.columns if "watermark_type_" in col]
        X = self.labeled_df.drop(columns=non_feature_cols)
        y = self.labeled_df["label"]  # 整数标签
        y_one_hot = self.labeled_df[[col for col in self.labeled_df.columns if "watermark_type_" in col]]  # One-Hot标签

        # 分层划分（保证各类别比例一致）
        X_train, X_test, y_train, y_test, y_train_one_hot, y_test_one_hot = train_test_split(
            X, y, y_one_hot, test_size=self.test_size, random_state=self.random_state, stratify=y
        )

        # 保存为CSV
        datasets = {
            "X_train.csv": X_train,
            "X_test.csv": X_test,
            "y_train.csv": y_train,
            "y_test.csv": y_test,
            "y_train_one_hot.csv": y_train_one_hot,
            "y_test_one_hot.csv": y_test_one_hot
        }
        for file_name, df in datasets.items():
            df.to_csv(os.path.join(self.output_dir, file_name), index=False)
        
        # 打印划分统计
        print(f"Dataset split complete!")
        print(f"Train set size: {len(X_train)}, Test set size: {len(X_test)}")
        print(f"Label distribution in train set:\n{y_train.value_counts().sort_index()}")

# ------------------- 示例用法 -------------------
if __name__ == "__main__":
    splitter = DatasetSplitter(
        labeled_csv_path="./features/watermarking_features_with_labels.csv",
        output_dir="./datasets",
        test_size=0.3
    )
    splitter.split_and_save()