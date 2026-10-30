# -*- coding: utf-8 -*-
import os
import pandas as pd
from config import PRICE_FILE

class PaymentModel:
    @staticmethod
    def get_price_table():
        """Đọc bảng đơn giá từ file data/don_gia.xlsx"""
        if os.path.exists(PRICE_FILE):
            try:
                df_p = pd.read_excel(PRICE_FILE)
                df_p.columns = [str(c).strip() for c in df_p.columns]
                return df_p
            except Exception:
                pass
        return None

    @staticmethod
    def classify_role_group(role_str):
        """Phân loại nhóm vai trò: CBCT hay BTC"""
        if not role_str or pd.isna(role_str):
            return "CBCT"
        
        r_upper = str(role_str).upper().strip()
        # Các vai trò thuộc CBCT trực tiếp
        if "CBCT" in r_upper or "COI THI" in r_upper:
            return "CBCT"
        # Các vai trò thuộc Ban tổ chức / Ban coi thi
        return "BTC"

    @staticmethod
    def process(df_summary, df_price=None):
        if df_summary is None or df_summary.empty:
            return pd.DataFrame()

        df_pay = df_summary.copy()

        if df_price is None:
            df_price = PaymentModel.get_price_table()

        dg_60_list, dg_75_list, dg_120_list = [], [], []

        for _, row in df_pay.iterrows():
            role = str(row.get("Vai trò", "")).strip()
            ht = str(row.get("Hình thức", "")).strip()
            tg = str(row.get("Thời gian", "")).strip()

            role_group = PaymentModel.classify_role_group(role)

            p60, p75, p120 = None, None, None

            # Tra cứu trong file don_gia.xlsx theo Nhóm vai trò + Hình thức + Thời gian
            if df_price is not None and not df_price.empty:
                match = df_price[
                    (df_price["Nhóm vai trò"].astype(str).str.strip().str.upper() == role_group) &
                    (df_price["Hình thức"].astype(str).str.strip().str.lower() == ht.lower()) &
                    (df_price["Thời gian"].astype(str).str.strip().str.lower() == tg.lower())
                ]
                if not match.empty:
                    r_match = match.iloc[0]
                    p60 = r_match.get("Thi 60", None)
                    p75 = r_match.get("Thi 75-90", None)
                    p120 = r_match.get("Thi 120", None)

            # Đơn giá dự phòng (Fallback) nếu không khớp dòng
            if p60 is None or pd.isna(p60):
                if role_group == "BTC":
                    if ht == "Trực tuyến" and tg == "Trong giờ": p60, p75, p120 = 52500, 78750, 105000
                    elif ht == "Trực tuyến" and tg == "Ngoài giờ": p60, p75, p120 = 78750, 105000, 131250
                    elif ht == "Trực tiếp" and tg == "Trong giờ": p60, p75, p120 = 70000, 105000, 140000
                    else: p60, p75, p120 = 105000, 140000, 175000
                else:
                    if ht == "Trực tuyến" and tg == "Trong giờ": p60, p75, p120 = 105000, 157500, 210000
                    elif ht == "Trực tuyến" and tg == "Ngoài giờ": p60, p75, p120 = 157500, 210000, 262500
                    elif ht == "Trực tiếp" and tg == "Trong giờ": p60, p75, p120 = 70000, 105000, 140000
                    else: p60, p75, p120 = 105000, 140000, 175000

            dg_60_list.append(p60)
            dg_75_list.append(p75)
            dg_120_list.append(p120)

        df_pay["Đơn giá 60"] = dg_60_list
        df_pay["Đơn giá 75-90"] = dg_75_list
        df_pay["Đơn giá 120"] = dg_120_list

        # Tính thành tiền
        df_pay["Tiền Thi 60"] = df_pay["Thi 60"] * df_pay["Đơn giá 60"]
        df_pay["Tiền Thi 75-90"] = df_pay["Thi 75-90"] * df_pay["Đơn giá 75-90"]
        df_pay["Tiền Thi 120"] = df_pay["Thi 120"] * df_pay["Đơn giá 120"]

        df_pay["Tổng tiền"] = df_pay["Tiền Thi 60"] + df_pay["Tiền Thi 75-90"] + df_pay["Tiền Thi 120"]

        return df_pay

    @staticmethod
    def calculate(df, df_price=None):
        from models.summary_model import SummaryModel
        df_summary = SummaryModel.process(df)
        return PaymentModel.process(df_summary, df_price)
