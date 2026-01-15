"""
Quét và lọc cổ phiếu theo tín hiệu kỹ thuật
Sử dụng: python scan_stocks.py
"""

import pandas as pd
import os
import yfinance as yf
from datetime import datetime

# Danh sách mã cần quét
SCAN_SYMBOLS = ["FPT", "VHM", "ANV", "VCB", "SCB", "VNM"]

def download_if_needed(symbol: str):
    """Tải dữ liệu nếu chưa có"""
    csv_path = f"data/{symbol}.csv"
    if not os.path.exists(csv_path):
        print(f"Dang tai du lieu {symbol}...")
        yf_symbol = symbol + ".VN"
        data = yf.download(yf_symbol, start="2019-01-01", progress=False)
        if not data.empty:
            os.makedirs("data", exist_ok=True)
            data.to_csv(csv_path)
            print(f"  Da luu {symbol}.csv")
            return True
        else:
            print(f"  Khong tim thay du lieu cho {symbol}")
            return False
    return True

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
    
    df = df.set_index("Date")
    return df

def analyze_stock(df: pd.DataFrame, symbol: str) -> dict:
    """Phân tích kỹ thuật cho 1 mã"""
    if len(df) < 50:
        return None
    
    df = df.copy()
    
    # Giá hiện tại
    current_price = df["Close"].iloc[-1]
    prev_price = df["Close"].iloc[-2]
    change_pct = (current_price - prev_price) / prev_price * 100
    
    # MA
    df["MA20"] = df["Close"].rolling(20).mean()
    df["MA50"] = df["Close"].rolling(50).mean()
    
    ma20 = df["MA20"].iloc[-1]
    ma50 = df["MA50"].iloc[-1]
    
    # Tín hiệu MA crossover
    ma_signal = "NEUTRAL"
    if df["MA20"].iloc[-1] > df["MA50"].iloc[-1] and df["MA20"].iloc[-2] <= df["MA50"].iloc[-2]:
        ma_signal = "BUY (Golden Cross)"
    elif df["MA20"].iloc[-1] < df["MA50"].iloc[-1] and df["MA20"].iloc[-2] >= df["MA50"].iloc[-2]:
        ma_signal = "SELL (Death Cross)"
    elif df["MA20"].iloc[-1] > df["MA50"].iloc[-1]:
        ma_signal = "BULLISH"
    elif df["MA20"].iloc[-1] < df["MA50"].iloc[-1]:
        ma_signal = "BEARISH"
    
    # RSI
    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))
    rsi = df["RSI"].iloc[-1]
    
    rsi_signal = "NEUTRAL"
    if rsi < 30:
        rsi_signal = "OVERSOLD (Qua ban)"
    elif rsi > 70:
        rsi_signal = "OVERBOUGHT (Qua mua)"
    
    # Mẫu nến
    df["body"] = df["Close"] - df["Open"]
    df["body_abs"] = abs(df["body"])
    df["upper_shadow"] = df["High"] - df[["Open", "Close"]].max(axis=1)
    df["lower_shadow"] = df[["Open", "Close"]].min(axis=1) - df["Low"]
    df["range"] = df["High"] - df["Low"]
    
    candle_patterns = []
    last = df.iloc[-1]
    prev = df.iloc[-2]
    
    # Doji
    if last["body_abs"] < last["range"] * 0.1:
        candle_patterns.append("Doji")
    
    # Hammer
    if last["lower_shadow"] > last["body_abs"] * 2 and last["upper_shadow"] < last["body_abs"] * 0.5:
        candle_patterns.append("Hammer")
    
    # Bullish Engulfing
    if last["body"] > 0 and prev["body"] < 0:
        if last["Open"] < prev["Close"] and last["Close"] > prev["Open"]:
            candle_patterns.append("Bullish Engulfing")
    
    # Bearish Engulfing
    if last["body"] < 0 and prev["body"] > 0:
        if last["Open"] > prev["Close"] and last["Close"] < prev["Open"]:
            candle_patterns.append("Bearish Engulfing")
    
    # Volume
    avg_vol = df["Volume"].rolling(20).mean().iloc[-1]
    current_vol = df["Volume"].iloc[-1]
    vol_ratio = current_vol / avg_vol if avg_vol > 0 else 0
    
    vol_signal = "NORMAL"
    if vol_ratio > 2:
        vol_signal = "VERY HIGH"
    elif vol_ratio > 1.5:
        vol_signal = "HIGH"
    elif vol_ratio < 0.5:
        vol_signal = "LOW"
    
    # Xu hướng 5 ngày
    trend_5d = (df["Close"].iloc[-1] - df["Close"].iloc[-5]) / df["Close"].iloc[-5] * 100
    
    return {
        "symbol": symbol,
        "price": current_price,
        "change_pct": change_pct,
        "ma20": ma20,
        "ma50": ma50,
        "ma_signal": ma_signal,
        "rsi": rsi,
        "rsi_signal": rsi_signal,
        "candle_patterns": candle_patterns,
        "vol_ratio": vol_ratio,
        "vol_signal": vol_signal,
        "trend_5d": trend_5d,
        "last_date": df.index[-1].strftime("%Y-%m-%d")
    }

def print_analysis(result: dict):
    """In kết quả phân tích"""
    print(f"\n{'='*50}")
    print(f"  {result['symbol']} - Gia: {result['price']:,.0f} ({result['change_pct']:+.2f}%)")
    print(f"{'='*50}")
    print(f"  Ngay cap nhat: {result['last_date']}")
    print(f"  Xu huong 5 ngay: {result['trend_5d']:+.2f}%")
    print(f"  MA20: {result['ma20']:,.0f} | MA50: {result['ma50']:,.0f}")
    print(f"  MA Signal: {result['ma_signal']}")
    print(f"  RSI(14): {result['rsi']:.1f} - {result['rsi_signal']}")
    print(f"  Volume: {result['vol_ratio']:.2f}x TB20 - {result['vol_signal']}")
    
    if result['candle_patterns']:
        print(f"  Mau nen: {', '.join(result['candle_patterns'])}")
    
    # Đánh giá tổng hợp
    score = 0
    if "BUY" in result['ma_signal'] or result['ma_signal'] == "BULLISH":
        score += 1
    if result['rsi_signal'] == "OVERSOLD (Qua ban)":
        score += 1
    if "Bullish" in str(result['candle_patterns']) or "Hammer" in str(result['candle_patterns']):
        score += 1
    if result['trend_5d'] > 0:
        score += 1
    
    if score >= 3:
        print(f"  >>> DANH GIA: CO THE MUA <<<")
    elif score <= 1 and (result['rsi_signal'] == "OVERBOUGHT (Qua mua)" or "SELL" in result['ma_signal']):
        print(f"  >>> DANH GIA: CAN THAN <<<")

def scan_all():
    """Quét tất cả các mã"""
    print("\n" + "="*60)
    print("   QUET CO PHIEU - " + datetime.now().strftime("%Y-%m-%d %H:%M"))
    print("="*60)
    
    results = []
    
    for symbol in SCAN_SYMBOLS:
        if download_if_needed(symbol):
            csv_path = f"data/{symbol}.csv"
            try:
                df = load_data(csv_path)
                result = analyze_stock(df, symbol)
                if result:
                    results.append(result)
                    print_analysis(result)
            except Exception as e:
                print(f"\nLoi khi phan tich {symbol}: {e}")
    
    # Tổng kết
    print("\n" + "="*60)
    print("   TONG KET")
    print("="*60)
    
    # Sắp xếp theo xu hướng 5 ngày
    results_sorted = sorted(results, key=lambda x: x['trend_5d'], reverse=True)
    
    print("\nXep hang theo xu huong 5 ngay:")
    for i, r in enumerate(results_sorted, 1):
        signal = ""
        if "BUY" in r['ma_signal']:
            signal = "[MUA]"
        elif "SELL" in r['ma_signal']:
            signal = "[BAN]"
        print(f"  {i}. {r['symbol']}: {r['trend_5d']:+.2f}% | RSI: {r['rsi']:.0f} | {r['ma_signal']} {signal}")
    
    # Cổ phiếu đáng chú ý
    print("\nCo phieu dang chu y:")
    for r in results:
        notes = []
        if "BUY" in r['ma_signal']:
            notes.append("Golden Cross")
        if r['rsi'] < 30:
            notes.append("RSI qua ban")
        if r['vol_ratio'] > 1.5:
            notes.append("Volume cao")
        if "Bullish Engulfing" in r['candle_patterns']:
            notes.append("Nen tang nuot")
        if "Hammer" in r['candle_patterns']:
            notes.append("Nen bua")
        
        if notes:
            print(f"  - {r['symbol']}: {', '.join(notes)}")

if __name__ == "__main__":
    scan_all()
