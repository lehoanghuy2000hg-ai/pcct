# -*- coding: utf-8 -*-
import pandas as pd

class PaymentModel:
    @staticmethod
    def process(df_summary, df_price=None):
        if df_summary is None or df_summary.empty:
            return pd.DataFrame()

        df_pay = df_summary.copy()

        # Đơn giá mặc định chuẩn theo mốc thời gian
        default_prices = {
            "Thi 60": 157500,
            "Thi 75-90": 210000,
            "Thi 120": 262500
        }

        # Áp đơn giá
        df_pay["Đơn giá 60"] = default_prices["Thi 60"]
        df_pay["Đơn giá 75-90"] = default_prices["Thi 75-90"]
        df_pay["Đơn giá 120"] = default_prices["Thi 120"]

        # Tính thành tiền theo từng mốc thi
        df_pay["Tiền Thi 60"] = df_pay["Thi 60"] * df_pay["Đơn giá 60"]
        df_pay["Tiền Thi 75-90"] = df_pay["Thi 75-90"] * df_pay["Đơn giá 75-90"]
        df_pay["Tiền Thi 120"] = df_pay["Thi 120"] * df_pay["Đơn giá 120"]

        # Tổng tiền thanh toán
        df_pay["Tổng tiền"] = df_pay["Tiền Thi 60"] + df_pay["Tiền Thi 75-90"] + df_pay["Tiền Thi 120"]

        return df_pay
