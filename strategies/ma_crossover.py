"""
Bước 3: Chiến lược MA Crossover đơn giản
- MA_fast (20 ngày) cắt lên MA_slow (50 ngày) = tín hiệu MUA
- MA_fast cắt xuống MA_slow = tín hiệu BÁN
"""

import pandas as pd

def ma_crossover_signals(
    csv_path: str,
    fast_window: int = 20,
    slow_window: int = 50
) -> pd.DataFrame:
    # Đọc CSV với multi-level header từ yfinance mới
    df = pd.read_csv(csv_path, header=[0, 1], index_col=0)
    
    # Flatten columns và lấy level đầu tiên
    df.columns = [col[0] for col in df.columns]
    
    # Reset index để Date thành cột
    df = df.reset_index()
    df.columns.values[0] = "Date"
    
    # Bỏ dòng có Date không hợp lệ (dòng Ticker)
    df = df[df["Date"].str.match(r"^\d{4}-\d{2}-\d{2}", na=False)].copy()
    
    # Convert types
    df["Date"] = pd.to_datetime(df["Date"])
    df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
    
    df = df.sort_values("Date").reset_index(drop=True)

    df["MA_fast"] = df["Close"].rolling(window=fast_window).mean()
    df["MA_slow"] = df["Close"].rolling(window=slow_window).mean()

    df["signal_raw"] = 0
    df.loc[df["MA_fast"] > df["MA_slow"], "signal_raw"] = 1   # vùng mua
    df.loc[df["MA_fast"] < df["MA_slow"], "signal_raw"] = -1  # vùng bán

    df["signal"] = df["signal_raw"].diff().fillna(0)
    # 2 = tín hiệu MUA mới, -2 = tín hiệu BÁN mới, 0 = giữ nguyên

    return df
