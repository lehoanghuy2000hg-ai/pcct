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
    def process(df_summary, df_price=None):
        if df_summary is None or df_summary.empty:
            return pd.DataFrame()

        df_pay = df_summary.copy()

        if df_price is None:
            df_price = PaymentModel.get_price_table()

        # Bảng đơn giá mặc định fallback nếu không đọc được file
        fallback_prices = {
            ("Trực tuyến", "Trong giờ"): (105000, 157500, 210000),
            ("Trực tuyến", "Ngoài giờ"): (157500, 210000, 262500),
            ("Trực tiếp", "Trong giờ"): (70000, 105000, 140000),
            ("Trực tiếp", "Ngoài giờ"): (105000, 140000, 175000)
        }

        dg_60_list, dg_75_list, dg_120_list = [], [], []

        for _, row in df_pay.iterrows():
            ht = str(row.get("Hình thức", "")).strip()
            tg = str(row.get("Thời gian", "")).strip()

            p60, p75, p120 = None, None, None

            # Tìm trong file don_gia.xlsx
            if df_price is not None and not df_price.empty:
                match = df_price[
                    (df_price["Hình thức"].astype(str).str.strip().str.lower() == ht.lower()) &
                    (df_price["Thời gian"].astype(str).str.strip().str.lower() == tg.lower())
                ]
                if not match.empty:
                    r_match = match.iloc[0]
                    p60 = r_match.get("Thi 60", None)
                    p75 = r_match.get("Thi 75-90", None)
                    p120 = r_match.get("Thi 120", None)

            # Nếu không tìm thấy, lấy từ fallback_prices
            if p60 is None or pd.isna(p60):
                key = (ht, tg)
                p60, p75, p120 = fallback_prices.get(key, (157500, 210000, 262500))

            dg_60_list.append(p60)
            dg_75_list.append(p75)
            dg_120_list.append(p120)

        df_pay["Đơn giá 60"] = dg_60_list
        df_pay["Đơn giá 75-90"] = dg_75_list
        df_pay["Đơn giá 120"] = dg_120_list

        # Tính tiền
        df_pay["Tiền Thi 60"] = df_pay["Thi 60"] * df_pay["Đơn giá 60"]
        df_pay["Tiền Thi 75-90"] = df_pay["Thi 75-90"] * df_pay["Đơn giá 75-90"]
        df_pay["Tiền Thi 120"] = df_pay["Thi 120"] * df_pay["Đơn giá 120"]

        # Tổng tiền
        df_pay["Tổng tiền"] = df_pay["Tiền Thi 60"] + df_pay["Tiền Thi 75-90"] + df_pay["Tiền Thi 120"]

        return df_pay

    @staticmethod
    def calculate(df, df_price=None):
        from models.summary_model import SummaryModel
        df_summary = SummaryModel.process(df)
        return PaymentModel.process(df_summary, df_price)
