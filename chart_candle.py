"""
Biểu đồ nến (Candlestick) với nhận diện mẫu nến phổ biến
Hỗ trợ hiển thị theo: Ngày, Tuần, Tháng
Sử dụng: python chart_candle.py
"""

import pandas as pd
import mplfinance as mpf
import os

def load_data(csv_path: str) -> pd.DataFrame:
    """Đọc CSV từ yfinance và chuẩn hóa format"""
    df = pd.read_csv(csv_path, header=[0, 1], index_col=0)
    df.columns = [col[0] for col in df.columns]
    df = df.reset_index()
    df.columns.values[0] = "Date"
    
    df = df[df["Date"].str.match(r"^\d{4}-\d{2}-\d{2}", na=False)].copy()
    
    df["Date"] = pd.to_datetime(df["Date"])
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    
    df = df.set_index("Date")
    return df

def resample_ohlc(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    """Chuyển đổi dữ liệu theo khung thời gian: D (ngày), W (tuần), M (tháng)"""
    if timeframe == "D":
        return df
    
    # Resample theo tuần hoặc tháng
    df_resampled = df.resample(timeframe).agg({
        "Open": "first",
        "High": "max",
        "Low": "min",
        "Close": "last",
        "Volume": "sum"
    }).dropna()
    
    return df_resampled

def detect_candle_patterns(df: pd.DataFrame) -> pd.DataFrame:
    """Nhận diện các mẫu nến phổ biến"""
    df = df.copy()
    
    df["body"] = df["Close"] - df["Open"]
    df["body_abs"] = abs(df["body"])
    df["upper_shadow"] = df["High"] - df[["Open", "Close"]].max(axis=1)
    df["lower_shadow"] = df[["Open", "Close"]].min(axis=1) - df["Low"]
    df["range"] = df["High"] - df["Low"]
    
    avg_body = df["body_abs"].rolling(20).mean()
    
    # 1. DOJI
    df["Doji"] = df["body_abs"] < (df["range"] * 0.1)
    
    # 2. HAMMER
    df["Hammer"] = (
        (df["lower_shadow"] > df["body_abs"] * 2) &
        (df["upper_shadow"] < df["body_abs"] * 0.5) &
        (df["body_abs"] > 0)
    )
    
    # 3. INVERTED HAMMER
    df["Inverted_Hammer"] = (
        (df["upper_shadow"] > df["body_abs"] * 2) &
        (df["lower_shadow"] < df["body_abs"] * 0.5) &
        (df["body_abs"] > 0)
    )
    
    # 4. BULLISH ENGULFING
    df["Bullish_Engulfing"] = (
        (df["body"] > 0) &
        (df["body"].shift(1) < 0) &
        (df["Open"] < df["Close"].shift(1)) &
        (df["Close"] > df["Open"].shift(1))
    )
    
    # 5. BEARISH ENGULFING
    df["Bearish_Engulfing"] = (
        (df["body"] < 0) &
        (df["body"].shift(1) > 0) &
        (df["Open"] > df["Close"].shift(1)) &
        (df["Close"] < df["Open"].shift(1))
    )
    
    # 6. MORNING STAR
    df["Morning_Star"] = (
        (df["body"].shift(2) < 0) &
        (df["body_abs"].shift(2) > avg_body.shift(2)) &
        (df["body_abs"].shift(1) < avg_body.shift(1) * 0.5) &
        (df["body"] > 0) &
        (df["Close"] > (df["Open"].shift(2) + df["Close"].shift(2)) / 2)
    )
    
    # 7. EVENING STAR
    df["Evening_Star"] = (
        (df["body"].shift(2) > 0) &
        (df["body_abs"].shift(2) > avg_body.shift(2)) &
        (df["body_abs"].shift(1) < avg_body.shift(1) * 0.5) &
        (df["body"] < 0) &
        (df["Close"] < (df["Open"].shift(2) + df["Close"].shift(2)) / 2)
    )
    
    # 8. SHOOTING STAR
    df["Shooting_Star"] = (
        (df["upper_shadow"] > df["body_abs"] * 2) &
        (df["lower_shadow"] < df["body_abs"] * 0.3) &
        (df["body"] < 0)
    )
    
    # 9. MARUBOZU
    df["Marubozu"] = (
        (df["upper_shadow"] < df["range"] * 0.05) &
        (df["lower_shadow"] < df["range"] * 0.05) &
        (df["body_abs"] > avg_body)
    )
    
    # 10. SPINNING TOP
    df["Spinning_Top"] = (
        (df["body_abs"] < df["range"] * 0.3) &
        (df["upper_shadow"] > df["body_abs"]) &
        (df["lower_shadow"] > df["body_abs"])
    )
    
    return df

def plot_candlestick(df: pd.DataFrame, symbol: str, timeframe: str, last_n: int = 60):
    """Vẽ biểu đồ nến với MA"""
    # Resample theo timeframe
    df_plot = resample_ohlc(df, timeframe).tail(last_n).copy()
    
    # Tên timeframe
    tf_names = {"D": "Ngay", "W": "Tuan", "M": "Thang"}
    tf_name = tf_names.get(timeframe, timeframe)
    
    # Thêm MA (điều chỉnh theo timeframe)
    ma_fast = 20 if timeframe == "D" else (4 if timeframe == "W" else 3)
    ma_slow = 50 if timeframe == "D" else (10 if timeframe == "W" else 6)
    
    df_plot["MA_fast"] = df_plot["Close"].rolling(ma_fast).mean()
    df_plot["MA_slow"] = df_plot["Close"].rolling(ma_slow).mean()
    
    # Tạo addplot cho MA
    ap = [
        mpf.make_addplot(df_plot["MA_fast"], color="blue", width=1, label=f"MA{ma_fast}"),
        mpf.make_addplot(df_plot["MA_slow"], color="orange", width=1, label=f"MA{ma_slow}"),
    ]
    
    # Vẽ biểu đồ
    mpf.plot(
        df_plot,
        type="candle",
        style="charles",
        title=f"\n{symbol} - Bieu do nen theo {tf_name} ({last_n} {tf_name.lower()} gan nhat)",
        ylabel="Gia",
        volume=True,
        addplot=ap,
        figsize=(14, 8),
        warn_too_much_data=1000
    )

def show_patterns(df: pd.DataFrame, symbol: str, timeframe: str, last_n: int = 30):
    """Hiển thị các mẫu nến được phát hiện"""
    df_resampled = resample_ohlc(df, timeframe)
    df_analyzed = detect_candle_patterns(df_resampled)
    df_recent = df_analyzed.tail(last_n)
    
    tf_names = {"D": "ngay", "W": "tuan", "M": "thang"}
    tf_name = tf_names.get(timeframe, timeframe)
    
    patterns = [
        "Doji", "Hammer", "Inverted_Hammer", 
        "Bullish_Engulfing", "Bearish_Engulfing",
        "Morning_Star", "Evening_Star", 
        "Shooting_Star", "Marubozu", "Spinning_Top"
    ]
    
    print(f"\n=== Mau nen phat hien trong {last_n} {tf_name} gan nhat ({symbol}) ===\n")
    
    found_any = False
    for pattern in patterns:
        if pattern in df_recent.columns:
            dates = df_recent[df_recent[pattern] == True].index.strftime("%Y-%m-%d").tolist()
            if dates:
                found_any = True
                print(f"{pattern}: {len(dates)} lan")
                print(f"   Ngay: {', '.join(dates[-5:])}")
                print()
    
    if not found_any:
        print("Khong phat hien mau nen dac biet nao.")

if __name__ == "__main__":
    data_dir = "data"
    csv_files = [f.replace(".csv", "") for f in os.listdir(data_dir) if f.endswith(".csv")]
    
    print("Cac ma co phieu da tai:")
    print(", ".join(csv_files))
    
    symbol = input("\nNhap ma muon xem bieu do (VD: FPT): ").strip().upper()
    csv_path = f"data/{symbol}.csv"
    
    if not os.path.exists(csv_path):
        print(f"Khong tim thay file {csv_path}")
    else:
        df = load_data(csv_path)
        
        print("\nChon khung thoi gian:")
        print("1. Ngay (D)")
        print("2. Tuan (W)")
        print("3. Thang (M)")
        
        tf_choice = input("Nhap lua chon (1/2/3): ").strip()
        timeframe_map = {"1": "D", "2": "W", "3": "M"}
        timeframe = timeframe_map.get(tf_choice, "D")
        
        tf_names = {"D": "ngay", "W": "tuan", "M": "thang"}
        tf_name = tf_names[timeframe]
        
        # Hiển thị mẫu nến
        show_patterns(df, symbol, timeframe, last_n=30)
        
        # Vẽ biểu đồ
        default_n = {"D": 60, "W": 52, "M": 24}
        n_input = input(f"So {tf_name} muon hien thi (mac dinh {default_n[timeframe]}): ").strip()
        n = int(n_input) if n_input.isdigit() else default_n[timeframe]
        
        plot_candlestick(df, symbol, timeframe, last_n=n)
