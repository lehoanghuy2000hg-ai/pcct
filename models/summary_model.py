# -*- coding: utf-8 -*-
import pandas as pd
import re

class SummaryModel:
    @staticmethod
    def get_time_category(tg_val):
        """Phân loại chính xác mốc thời gian thi: 60 phút, 75-90 phút, 120 phút"""
        if pd.isna(tg_val) or str(tg_val).strip() == "":
            return "75-90"
            
        tg_str = str(tg_val).lower().strip()
        
        # Trích xuất tất cả các số có trong chuỗi thời gian
        nums = re.findall(r'\d+', tg_str)
        if not nums:
            return "75-90"
            
        minutes = int(nums[0])
        
        # Kiểm tra ngưỡng điều kiện chuẩn
        if minutes <= 60:
            return "60"
        elif minutes <= 90:
            return "75-90"
        else:
            return "120"

    @staticmethod
    def process(df):
        if df is None or df.empty:
            return pd.DataFrame()

        df = df.copy()

        # Xác định cột thời gian làm bài
        dur_col = next((c for c in df.columns if "tg" in c.lower() or "thời gian" in c.lower()), "TG (đề)")
        if dur_col in df.columns:
            df["Time_Cat"] = df[dur_col].apply(SummaryModel.get_time_category)
        else:
            df["Time_Cat"] = "75-90"

        # Định danh nhóm giảng viên & vai trò, hình thức, thời gian (trong/ngoài giờ)
        group_cols = [c for c in ["Họ tên", "Vai trò", "Hình thức", "Thời gian"] if c in df.columns]

        if not group_cols:
            return pd.DataFrame()

        records = []
        grouped = df.groupby(group_cols, sort=False)

        for name, group in grouped:
            row_dict = {}
            if isinstance(name, tuple):
                for idx, col_name in enumerate(group_cols):
                    row_dict[col_name] = name[idx]
            else:
                row_dict[group_cols[0]] = name

            counts = group["Time_Cat"].value_counts()
            row_dict["Thi 60"] = int(counts.get("60", 0))
            row_dict["Thi 75-90"] = int(counts.get("75-90", 0))
            row_dict["Thi 120"] = int(counts.get("120", 0))
            row_dict["Tổng số ca"] = len(group)

            records.append(row_dict)

        return pd.DataFrame(records)
