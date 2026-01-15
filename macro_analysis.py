"""
Phần 4: Phân tích dữ liệu vĩ mô (Macro Analysis)
Lãi suất, tỷ giá, chỉ số thị trường
Sử dụng: python macro_analysis.py
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import os

# Các mã để lấy dữ liệu vĩ mô từ Yahoo Finance
MACRO_SYMBOLS = {
    "VN_INDEX": "^VNINDEX",      # VN-Index (có thể không có)
    "USD_VND": "VND=X",          # Tỷ giá USD/VND
    "GOLD": "GC=F",              # Giá vàng
    "OIL": "CL=F",               # Giá dầu
    "SP500": "^GSPC",            # S&P 500
    "DXY": "DX-Y.NYB",           # Dollar Index
    "US_10Y": "^TNX",            # Lãi suất trái phiếu Mỹ 10 năm
}

def download_macro_data(days: int = 365) -> dict:
    """Tải dữ liệu vĩ mô"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    macro_data = {}
    
    print("Dang tai du lieu vi mo...")
    
    for name, symbol in MACRO_SYMBOLS.items():
        try:
            data = yf.download(symbol, start=start_date, end=end_date, progress=False)
            if not data.empty:
                macro_data[name] = data
                print(f"  {name}: OK ({len(data)} ngay)")
            else:
                print(f"  {name}: Khong co du lieu")
        except Exception as e:
            print(f"  {name}: Loi - {e}")
    
    return macro_data

def analyze_macro_trend(data: pd.DataFrame, name: str) -> dict:
    """Phân tích xu hướng của 1 chỉ số vĩ mô"""
    if data is None or len(data) < 20:
        return None
    
    # Lấy cột Close, xử lý multi-level columns
    if isinstance(data.columns, pd.MultiIndex):
        close = data[("Close", data.columns.get_level_values(1)[0])]
    else:
        close = data["Close"]
    
    close = pd.to_numeric(close, errors="coerce").dropna()
    
    if len(close) < 20:
        return None
    
    current = close.iloc[-1]
    prev_day = close.iloc[-2]
    prev_week = close.iloc[-5] if len(close) >= 5 else close.iloc[0]
    prev_month = close.iloc[-22] if len(close) >= 22 else close.iloc[0]
    
    # Tính % thay đổi
    change_1d = (current - prev_day) / prev_day * 100
    change_1w = (current - prev_week) / prev_week * 100
    change_1m = (current - prev_month) / prev_month * 100
    
    # MA
    ma20 = close.rolling(20).mean().iloc[-1]
    ma50 = close.rolling(50).mean().iloc[-1] if len(close) >= 50 else ma20
    
    trend = "TANG" if current > ma20 > ma50 else ("GIAM" if current < ma20 < ma50 else "DI NGANG")
    
    return {
        "name": name,
        "current": current,
        "change_1d": change_1d,
        "change_1w": change_1w,
        "change_1m": change_1m,
        "trend": trend
    }

def get_macro_impact(macro_results: dict) -> dict:
    """Đánh giá tác động của các yếu tố vĩ mô đến TTCK VN"""
    impacts = {}
    
    # USD/VND
    if "USD_VND" in macro_results:
        usd = macro_results["USD_VND"]
        if usd["change_1m"] > 2:
            impacts["USD_VND"] = {
                "impact": "TIEU CUC",
                "reason": "USD tang manh, ap luc ban rong khoi ngoai"
            }
        elif usd["change_1m"] < -2:
            impacts["USD_VND"] = {
                "impact": "TICH CUC",
                "reason": "USD giam, dong tien co the quay lai"
            }
        else:
            impacts["USD_VND"] = {
                "impact": "TRUNG TINH",
                "reason": "Ty gia on dinh"
            }
    
    # Lãi suất Mỹ
    if "US_10Y" in macro_results:
        rate = macro_results["US_10Y"]
        if rate["change_1m"] > 0.3:
            impacts["US_10Y"] = {
                "impact": "TIEU CUC",
                "reason": "Lai suat tang, dong tien rut khoi thi truong moi noi"
            }
        elif rate["change_1m"] < -0.3:
            impacts["US_10Y"] = {
                "impact": "TICH CUC",
                "reason": "Lai suat giam, dong tien tim kiem loi nhuan cao hon"
            }
        else:
            impacts["US_10Y"] = {
                "impact": "TRUNG TINH",
                "reason": "Lai suat on dinh"
            }
    
    # Giá dầu
    if "OIL" in macro_results:
        oil = macro_results["OIL"]
        if oil["change_1m"] > 10:
            impacts["OIL"] = {
                "impact": "TIEU CUC",
                "reason": "Gia dau tang manh, ap luc lam phat"
            }
        elif oil["change_1m"] < -10:
            impacts["OIL"] = {
                "impact": "TICH CUC",
                "reason": "Gia dau giam, giam ap luc chi phi"
            }
        else:
            impacts["OIL"] = {
                "impact": "TRUNG TINH",
                "reason": "Gia dau on dinh"
            }
    
    # S&P 500
    if "SP500" in macro_results:
        sp = macro_results["SP500"]
        if sp["trend"] == "TANG":
            impacts["SP500"] = {
                "impact": "TICH CUC",
                "reason": "Thi truong My tang, tam ly tich cuc lan toa"
            }
        elif sp["trend"] == "GIAM":
            impacts["SP500"] = {
                "impact": "TIEU CUC",
                "reason": "Thi truong My giam, tam ly e ngai"
            }
        else:
            impacts["SP500"] = {
                "impact": "TRUNG TINH",
                "reason": "Thi truong My di ngang"
            }
    
    # Dollar Index
    if "DXY" in macro_results:
        dxy = macro_results["DXY"]
        if dxy["change_1m"] > 2:
            impacts["DXY"] = {
                "impact": "TIEU CUC",
                "reason": "USD manh len, ap luc len thi truong moi noi"
            }
        elif dxy["change_1m"] < -2:
            impacts["DXY"] = {
                "impact": "TICH CUC",
                "reason": "USD yeu di, ho tro thi truong moi noi"
            }
        else:
            impacts["DXY"] = {
                "impact": "TRUNG TINH",
                "reason": "Dollar Index on dinh"
            }
    
    return impacts

def macro_analysis():
    """Phân tích tổng hợp dữ liệu vĩ mô"""
    print(f"\n{'='*70}")
    print(f"   PHAN TICH DU LIEU VI MO")
    print(f"   Ngay: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"{'='*70}")
    
    # Tải dữ liệu
    macro_data = download_macro_data(365)
    
    if not macro_data:
        print("Khong tai duoc du lieu vi mo")
        return
    
    # Phân tích từng chỉ số
    macro_results = {}
    
    print(f"\n--- CHI SO VI MO ---\n")
    print(f"{'Chi so':<12} {'Gia':<12} {'1D':<10} {'1W':<10} {'1M':<10} {'Xu huong':<10}")
    print("-" * 70)
    
    for name, data in macro_data.items():
        result = analyze_macro_trend(data, name)
        if result:
            macro_results[name] = result
            print(f"{name:<12} {result['current']:<12,.2f} {result['change_1d']:>+8.2f}% {result['change_1w']:>+8.2f}% {result['change_1m']:>+8.2f}% {result['trend']:<10}")
    
    # Đánh giá tác động
    impacts = get_macro_impact(macro_results)
    
    print(f"\n--- TAC DONG DEN TTCK VIET NAM ---\n")
    
    positive = 0
    negative = 0
    
    for name, impact in impacts.items():
        emoji = "🟢" if impact["impact"] == "TICH CUC" else ("🔴" if impact["impact"] == "TIEU CUC" else "⚪")
        print(f"{emoji} {name}: {impact['impact']}")
        print(f"   {impact['reason']}")
        print()
        
        if impact["impact"] == "TICH CUC":
            positive += 1
        elif impact["impact"] == "TIEU CUC":
            negative += 1
    
    # Tổng kết
    print(f"\n{'='*70}")
    print(f"   TONG KET")
    print(f"{'='*70}")
    print(f"  Yeu to tich cuc: {positive}")
    print(f"  Yeu to tieu cuc: {negative}")
    print(f"  Yeu to trung tinh: {len(impacts) - positive - negative}")
    
    if positive > negative + 1:
        print(f"\n  >>> MOI TRUONG VI MO: THUAN LOI cho TTCK VN <<<")
    elif negative > positive + 1:
        print(f"\n  >>> MOI TRUONG VI MO: BAT LOI cho TTCK VN <<<")
    else:
        print(f"\n  >>> MOI TRUONG VI MO: TRUNG TINH <<<")
    
    return macro_results, impacts

if __name__ == "__main__":
    macro_analysis()
