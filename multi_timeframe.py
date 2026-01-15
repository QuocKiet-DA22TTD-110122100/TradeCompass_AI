"""
Phần 3: Phân tích đa khung thời gian (Multi-Timeframe Analysis)
Kết hợp tín hiệu từ Ngày, Tuần, Tháng để tăng độ chính xác
Sử dụng: python multi_timeframe.py
"""

import pandas as pd
import numpy as np
import os

def load_data(csv_path: str) -> pd.DataFrame:
    """Đọc CSV từ yfinance"""
    try:
        df = pd.read_csv(csv_path, header=[0, 1], index_col=0)
        df.columns = [col[0] for col in df.columns]
    except:
        df = pd.read_csv(csv_path, index_col=0)
    
    df = df.reset_index()
    df.columns.values[0] = "Date"
    
    if df["Date"].dtype == object:
        df = df[df["Date"].str.match(r"^\d{4}-\d{2}-\d{2}", na=False)].copy()
    
    df["Date"] = pd.to_datetime(df["Date"])
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    
    df = df.set_index("Date").dropna()
    return df

def resample_ohlc(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    """Chuyển đổi dữ liệu theo khung thời gian"""
    if timeframe == "D":
        return df
    
    df_resampled = df.resample(timeframe).agg({
        "Open": "first",
        "High": "max",
        "Low": "min",
        "Close": "last",
        "Volume": "sum"
    }).dropna()
    
    return df_resampled

def add_indicators(df: pd.DataFrame, prefix: str = "") -> pd.DataFrame:
    """Thêm các chỉ báo kỹ thuật"""
    df = df.copy()
    p = prefix + "_" if prefix else ""
    
    # MA
    df[f"{p}MA_fast"] = df["Close"].rolling(20 if not prefix else 4).mean()
    df[f"{p}MA_slow"] = df["Close"].rolling(50 if not prefix else 10).mean()
    
    # RSI
    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df[f"{p}RSI"] = 100 - (100 / (1 + rs))
    
    # MACD
    ema12 = df["Close"].ewm(span=12).mean()
    ema26 = df["Close"].ewm(span=26).mean()
    df[f"{p}MACD"] = ema12 - ema26
    df[f"{p}MACD_Signal"] = df[f"{p}MACD"].ewm(span=9).mean()
    
    # Stochastic
    low_14 = df["Low"].rolling(14).min()
    high_14 = df["High"].rolling(14).max()
    df[f"{p}Stoch_K"] = 100 * (df["Close"] - low_14) / (high_14 - low_14)
    
    # Trend
    df[f"{p}Trend"] = np.where(df[f"{p}MA_fast"] > df[f"{p}MA_slow"], 1, -1)
    
    return df

def analyze_timeframe(df: pd.DataFrame, tf_name: str) -> dict:
    """Phân tích 1 khung thời gian"""
    if len(df) < 50:
        return None
    
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    # Xu hướng MA
    ma_trend = "TANG" if latest["MA_fast"] > latest["MA_slow"] else "GIAM"
    ma_cross = ""
    if prev["MA_fast"] <= prev["MA_slow"] and latest["MA_fast"] > latest["MA_slow"]:
        ma_cross = "GOLDEN CROSS"
    elif prev["MA_fast"] >= prev["MA_slow"] and latest["MA_fast"] < latest["MA_slow"]:
        ma_cross = "DEATH CROSS"
    
    # RSI
    rsi = latest["RSI"]
    rsi_signal = "QUA BAN" if rsi < 30 else ("QUA MUA" if rsi > 70 else "TRUNG TINH")
    
    # MACD
    macd_trend = "TANG" if latest["MACD"] > latest["MACD_Signal"] else "GIAM"
    
    # Stochastic
    stoch = latest["Stoch_K"]
    stoch_signal = "QUA BAN" if stoch < 20 else ("QUA MUA" if stoch > 80 else "TRUNG TINH")
    
    # Điểm số (1 = bullish, -1 = bearish, 0 = neutral)
    score = 0
    if ma_trend == "TANG":
        score += 1
    else:
        score -= 1
    
    if ma_cross == "GOLDEN CROSS":
        score += 2
    elif ma_cross == "DEATH CROSS":
        score -= 2
    
    if rsi_signal == "QUA BAN":
        score += 1
    elif rsi_signal == "QUA MUA":
        score -= 1
    
    if macd_trend == "TANG":
        score += 1
    else:
        score -= 1
    
    if stoch_signal == "QUA BAN":
        score += 1
    elif stoch_signal == "QUA MUA":
        score -= 1
    
    return {
        "timeframe": tf_name,
        "ma_trend": ma_trend,
        "ma_cross": ma_cross,
        "rsi": rsi,
        "rsi_signal": rsi_signal,
        "macd_trend": macd_trend,
        "stoch": stoch,
        "stoch_signal": stoch_signal,
        "score": score,
        "max_score": 6  # Điểm tối đa có thể
    }

def multi_timeframe_analysis(symbol: str):
    """Phân tích đa khung thời gian"""
    csv_path = f"data/{symbol}.csv"
    
    if not os.path.exists(csv_path):
        print(f"Khong tim thay file {csv_path}")
        return
    
    print(f"\n{'='*70}")
    print(f"   PHAN TICH DA KHUNG THOI GIAN: {symbol}")
    print(f"{'='*70}")
    
    # Load dữ liệu
    df_daily = load_data(csv_path)
    
    # Tạo các khung thời gian
    timeframes = {
        "NGAY": resample_ohlc(df_daily, "D"),
        "TUAN": resample_ohlc(df_daily, "W"),
        "THANG": resample_ohlc(df_daily, "M")
    }
    
    # Thêm indicators và phân tích
    results = {}
    for tf_name, df in timeframes.items():
        df = add_indicators(df)
        result = analyze_timeframe(df, tf_name)
        if result:
            results[tf_name] = result
    
    # Hiển thị kết quả từng khung
    for tf_name, result in results.items():
        print(f"\n--- {tf_name} ---")
        print(f"  MA Trend: {result['ma_trend']} {result['ma_cross']}")
        print(f"  RSI: {result['rsi']:.1f} ({result['rsi_signal']})")
        print(f"  MACD: {result['macd_trend']}")
        print(f"  Stochastic: {result['stoch']:.1f} ({result['stoch_signal']})")
        print(f"  Diem: {result['score']}/{result['max_score']}")
    
    # Tổng hợp
    total_score = sum(r["score"] for r in results.values())
    max_total = sum(r["max_score"] for r in results.values())
    
    # Trọng số: Tháng > Tuần > Ngày
    weighted_score = (
        results.get("THANG", {}).get("score", 0) * 3 +
        results.get("TUAN", {}).get("score", 0) * 2 +
        results.get("NGAY", {}).get("score", 0) * 1
    )
    max_weighted = 6 * 3 + 6 * 2 + 6 * 1  # 36
    
    print(f"\n{'='*70}")
    print(f"   TONG HOP")
    print(f"{'='*70}")
    print(f"  Tong diem: {total_score}/{max_total}")
    print(f"  Diem co trong so: {weighted_score}/{max_weighted}")
    
    # Kiểm tra sự đồng thuận
    trends = [r["ma_trend"] for r in results.values()]
    all_bullish = all(t == "TANG" for t in trends)
    all_bearish = all(t == "GIAM" for t in trends)
    
    print(f"\n  Dong thuan xu huong: ", end="")
    if all_bullish:
        print("TAT CA TANG (Manh)")
    elif all_bearish:
        print("TAT CA GIAM (Yeu)")
    else:
        print("KHONG DONG NHAT (Can than)")
    
    # Khuyến nghị
    print(f"\n--- KHUYEN NGHI ---")
    
    if weighted_score >= 20 and all_bullish:
        print("  >>> MUA MANH: Tat ca khung thoi gian dong thuan TANG <<<")
        confidence = "CAO"
    elif weighted_score >= 12:
        print("  >>> XEM XET MUA: Xu huong tich cuc <<<")
        confidence = "TRUNG BINH"
    elif weighted_score <= -20 and all_bearish:
        print("  >>> BAN/TRANH: Tat ca khung thoi gian dong thuan GIAM <<<")
        confidence = "CAO"
    elif weighted_score <= -12:
        print("  >>> CAN THAN: Xu huong tieu cuc <<<")
        confidence = "TRUNG BINH"
    else:
        print("  >>> THEO DOI: Chua ro xu huong <<<")
        confidence = "THAP"
    
    print(f"  Do tin cay: {confidence}")
    
    # Chi tiết tín hiệu
    print(f"\n--- TIN HIEU CHI TIET ---")
    
    signals = []
    for tf_name, result in results.items():
        if result["ma_cross"]:
            signals.append(f"  - {tf_name}: {result['ma_cross']}")
        if result["rsi_signal"] != "TRUNG TINH":
            signals.append(f"  - {tf_name}: RSI {result['rsi_signal']}")
        if result["stoch_signal"] != "TRUNG TINH":
            signals.append(f"  - {tf_name}: Stoch {result['stoch_signal']}")
    
    if signals:
        for s in signals:
            print(s)
    else:
        print("  Khong co tin hieu dac biet")
    
    return results

if __name__ == "__main__":
    data_dir = "data"
    csv_files = [f.replace(".csv", "") for f in os.listdir(data_dir) if f.endswith(".csv")]
    
    print("Cac ma co phieu da tai:")
    print(", ".join(csv_files))
    
    symbol = input("\nNhap ma muon phan tich (VD: FPT): ").strip().upper()
    
    multi_timeframe_analysis(symbol)
