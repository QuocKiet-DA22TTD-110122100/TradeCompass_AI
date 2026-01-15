"""
Sàng lọc cổ phiếu tiềm năng (Stock Screener)
Đánh giá và xếp hạng các cổ phiếu theo nhiều tiêu chí
Sử dụng: python stock_screener.py
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime

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

def calculate_score(df: pd.DataFrame) -> dict:
    """Tính điểm đánh giá cho 1 cổ phiếu"""
    if len(df) < 50:
        return None
    
    df = df.copy()
    latest = df.iloc[-1]
    
    score = 0
    max_score = 0
    details = {}
    
    # === 1. XU HƯỚNG GIÁ (max 20 điểm) ===
    max_score += 20
    
    # MA crossover
    df["MA20"] = df["Close"].rolling(20).mean()
    df["MA50"] = df["Close"].rolling(50).mean()
    df["MA200"] = df["Close"].rolling(200).mean()
    
    ma20 = df["MA20"].iloc[-1]
    ma50 = df["MA50"].iloc[-1]
    ma200 = df["MA200"].iloc[-1] if len(df) >= 200 else ma50
    price = latest["Close"]
    
    # Giá trên MA
    if price > ma20:
        score += 5
        details["price_vs_ma20"] = "Tren MA20"
    if price > ma50:
        score += 5
        details["price_vs_ma50"] = "Tren MA50"
    if price > ma200:
        score += 5
        details["price_vs_ma200"] = "Tren MA200"
    
    # Golden cross
    if ma20 > ma50:
        score += 5
        details["ma_cross"] = "MA20 > MA50 (Bullish)"
    
    # === 2. RSI (max 15 điểm) ===
    max_score += 15
    
    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))
    rsi = df["RSI"].iloc[-1]
    
    if 40 <= rsi <= 60:
        score += 10
        details["rsi"] = f"RSI {rsi:.0f} (Trung tinh)"
    elif 30 <= rsi < 40:
        score += 15  # Cơ hội mua
        details["rsi"] = f"RSI {rsi:.0f} (Gan qua ban - Co hoi)"
    elif rsi < 30:
        score += 12
        details["rsi"] = f"RSI {rsi:.0f} (Qua ban)"
    elif 60 < rsi <= 70:
        score += 8
        details["rsi"] = f"RSI {rsi:.0f} (Manh)"
    else:
        score += 3
        details["rsi"] = f"RSI {rsi:.0f} (Qua mua - Can than)"
    
    # === 3. MACD (max 15 điểm) ===
    max_score += 15
    
    ema12 = df["Close"].ewm(span=12).mean()
    ema26 = df["Close"].ewm(span=26).mean()
    df["MACD"] = ema12 - ema26
    df["MACD_Signal"] = df["MACD"].ewm(span=9).mean()
    
    macd = df["MACD"].iloc[-1]
    macd_signal = df["MACD_Signal"].iloc[-1]
    macd_prev = df["MACD"].iloc[-2]
    signal_prev = df["MACD_Signal"].iloc[-2]
    
    if macd > macd_signal:
        score += 10
        details["macd"] = "MACD > Signal (Bullish)"
    
    # MACD cross
    if macd_prev <= signal_prev and macd > macd_signal:
        score += 5
        details["macd_cross"] = "MACD vua cat len Signal"
    
    # === 4. VOLUME (max 15 điểm) ===
    max_score += 15
    
    df["Vol_MA20"] = df["Volume"].rolling(20).mean()
    vol_ratio = latest["Volume"] / df["Vol_MA20"].iloc[-1]
    
    if vol_ratio > 1.5:
        score += 15
        details["volume"] = f"Volume cao ({vol_ratio:.1f}x TB)"
    elif vol_ratio > 1:
        score += 10
        details["volume"] = f"Volume kha ({vol_ratio:.1f}x TB)"
    elif vol_ratio > 0.7:
        score += 5
        details["volume"] = f"Volume TB ({vol_ratio:.1f}x)"
    else:
        details["volume"] = f"Volume thap ({vol_ratio:.1f}x)"
    
    # === 5. XU HƯỚNG NGẮN HẠN (max 15 điểm) ===
    max_score += 15
    
    ret_5d = (price - df["Close"].iloc[-5]) / df["Close"].iloc[-5] * 100
    ret_20d = (price - df["Close"].iloc[-20]) / df["Close"].iloc[-20] * 100
    
    if ret_5d > 3:
        score += 8
        details["trend_5d"] = f"5 ngay: +{ret_5d:.1f}%"
    elif ret_5d > 0:
        score += 5
        details["trend_5d"] = f"5 ngay: +{ret_5d:.1f}%"
    else:
        details["trend_5d"] = f"5 ngay: {ret_5d:.1f}%"
    
    if ret_20d > 5:
        score += 7
        details["trend_20d"] = f"20 ngay: +{ret_20d:.1f}%"
    elif ret_20d > 0:
        score += 4
        details["trend_20d"] = f"20 ngay: +{ret_20d:.1f}%"
    else:
        details["trend_20d"] = f"20 ngay: {ret_20d:.1f}%"
    
    # === 6. BOLLINGER BANDS (max 10 điểm) ===
    max_score += 10
    
    df["BB_Mid"] = df["Close"].rolling(20).mean()
    bb_std = df["Close"].rolling(20).std()
    df["BB_Upper"] = df["BB_Mid"] + 2 * bb_std
    df["BB_Lower"] = df["BB_Mid"] - 2 * bb_std
    
    bb_pos = (price - df["BB_Lower"].iloc[-1]) / (df["BB_Upper"].iloc[-1] - df["BB_Lower"].iloc[-1])
    
    if 0.3 <= bb_pos <= 0.7:
        score += 10
        details["bb"] = f"BB: {bb_pos*100:.0f}% (Vung an toan)"
    elif bb_pos < 0.2:
        score += 8
        details["bb"] = f"BB: {bb_pos*100:.0f}% (Gan day - Co hoi)"
    elif bb_pos > 0.8:
        score += 3
        details["bb"] = f"BB: {bb_pos*100:.0f}% (Gan dinh - Can than)"
    else:
        score += 5
        details["bb"] = f"BB: {bb_pos*100:.0f}%"
    
    # === 7. STOCHASTIC (max 10 điểm) ===
    max_score += 10
    
    low_14 = df["Low"].rolling(14).min()
    high_14 = df["High"].rolling(14).max()
    df["Stoch_K"] = 100 * (df["Close"] - low_14) / (high_14 - low_14)
    stoch = df["Stoch_K"].iloc[-1]
    
    if 20 <= stoch <= 80:
        score += 10
        details["stoch"] = f"Stoch: {stoch:.0f} (Trung tinh)"
    elif stoch < 20:
        score += 8
        details["stoch"] = f"Stoch: {stoch:.0f} (Qua ban - Co hoi)"
    else:
        score += 3
        details["stoch"] = f"Stoch: {stoch:.0f} (Qua mua)"
    
    # Tính % điểm
    score_pct = score / max_score * 100
    
    # Xếp hạng
    if score_pct >= 80:
        rating = "A+ (Rat tiem nang)"
    elif score_pct >= 70:
        rating = "A (Tiem nang)"
    elif score_pct >= 60:
        rating = "B+ (Kha)"
    elif score_pct >= 50:
        rating = "B (Trung binh)"
    elif score_pct >= 40:
        rating = "C (Yeu)"
    else:
        rating = "D (Kem)"
    
    return {
        "price": price,
        "score": score,
        "max_score": max_score,
        "score_pct": score_pct,
        "rating": rating,
        "rsi": rsi,
        "vol_ratio": vol_ratio,
        "ret_5d": ret_5d,
        "ret_20d": ret_20d,
        "details": details
    }

def screen_all_stocks():
    """Sàng lọc tất cả cổ phiếu"""
    data_dir = "data"
    csv_files = [f.replace(".csv", "") for f in os.listdir(data_dir) if f.endswith(".csv")]
    
    print(f"\n{'='*70}")
    print(f"   SANG LOC CO PHIEU TIEM NANG")
    print(f"   Ngay: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"   So ma phan tich: {len(csv_files)}")
    print(f"{'='*70}")
    
    results = []
    
    for symbol in csv_files:
        csv_path = f"data/{symbol}.csv"
        try:
            df = load_data(csv_path)
            result = calculate_score(df)
            if result:
                result["symbol"] = symbol
                results.append(result)
        except Exception as e:
            pass
    
    # Sắp xếp theo điểm
    results_sorted = sorted(results, key=lambda x: x["score_pct"], reverse=True)
    
    # Hiển thị bảng xếp hạng
    print(f"\n{'='*90}")
    print(f"   BANG XEP HANG CO PHIEU")
    print(f"{'='*90}")
    print(f"{'STT':<4} {'Ma':<8} {'Gia':>12} {'Diem':>8} {'%':>6} {'Rating':<18} {'RSI':>6} {'Vol':>6} {'5D':>8} {'20D':>8}")
    print("-" * 90)
    
    for i, r in enumerate(results_sorted, 1):
        print(f"{i:<4} {r['symbol']:<8} {r['price']:>12,.0f} {r['score']:>5}/{r['max_score']:<2} {r['score_pct']:>5.0f}% {r['rating']:<18} {r['rsi']:>5.0f} {r['vol_ratio']:>5.1f}x {r['ret_5d']:>+7.1f}% {r['ret_20d']:>+7.1f}%")
    
    # Top cổ phiếu tiềm năng
    print(f"\n{'='*70}")
    print(f"   TOP CO PHIEU TIEM NANG (Rating A tro len)")
    print(f"{'='*70}")
    
    top_stocks = [r for r in results_sorted if r["score_pct"] >= 70]
    
    if top_stocks:
        for r in top_stocks:
            print(f"\n  {r['symbol']} - {r['rating']}")
            print(f"  Gia: {r['price']:,.0f} | Diem: {r['score']}/{r['max_score']} ({r['score_pct']:.0f}%)")
            print(f"  Chi tiet:")
            for key, value in r["details"].items():
                print(f"    - {value}")
    else:
        print("  Khong co co phieu nao dat rating A tro len")
    
    # Cổ phiếu có tín hiệu mua
    print(f"\n{'='*70}")
    print(f"   CO PHIEU CO TIN HIEU MUA")
    print(f"{'='*70}")
    
    buy_signals = []
    for r in results_sorted:
        signals = []
        if r["rsi"] < 35:
            signals.append("RSI qua ban")
        if r["vol_ratio"] > 1.5 and r["ret_5d"] > 0:
            signals.append("Volume dot bien + Tang gia")
        if "MACD vua cat len" in str(r["details"]):
            signals.append("MACD cross")
        if "Gan day" in str(r["details"].get("bb", "")):
            signals.append("Gan day Bollinger")
        
        if signals:
            buy_signals.append({"symbol": r["symbol"], "signals": signals, "score_pct": r["score_pct"]})
    
    if buy_signals:
        for b in buy_signals[:10]:
            print(f"  {b['symbol']} ({b['score_pct']:.0f}%): {', '.join(b['signals'])}")
    else:
        print("  Khong co tin hieu mua ro rang")
    
    # Cổ phiếu cần tránh
    print(f"\n{'='*70}")
    print(f"   CO PHIEU CAN TRANH (Rating C, D)")
    print(f"{'='*70}")
    
    avoid_stocks = [r for r in results_sorted if r["score_pct"] < 50]
    if avoid_stocks:
        for r in avoid_stocks[:5]:
            print(f"  {r['symbol']}: {r['rating']} - Diem {r['score_pct']:.0f}%")
    else:
        print("  Khong co")
    
    return results_sorted

def analyze_single(symbol: str):
    """Phân tích chi tiết 1 mã"""
    csv_path = f"data/{symbol}.csv"
    
    if not os.path.exists(csv_path):
        print(f"Khong tim thay file {csv_path}")
        return
    
    df = load_data(csv_path)
    result = calculate_score(df)
    
    if not result:
        print("Khong du du lieu de phan tich")
        return
    
    print(f"\n{'='*60}")
    print(f"   PHAN TICH CHI TIET: {symbol}")
    print(f"{'='*60}")
    
    print(f"\n  Gia hien tai: {result['price']:,.0f}")
    print(f"  Diem: {result['score']}/{result['max_score']} ({result['score_pct']:.0f}%)")
    print(f"  Rating: {result['rating']}")
    
    print(f"\n  --- CHI TIET DIEM ---")
    for key, value in result["details"].items():
        print(f"    {value}")
    
    # Khuyến nghị
    print(f"\n  --- KHUYEN NGHI ---")
    if result["score_pct"] >= 70:
        print(f"  >>> XEM XET MUA - Co phieu tiem nang <<<")
    elif result["score_pct"] >= 50:
        print(f"  >>> THEO DOI - Cho tin hieu ro hon <<<")
    else:
        print(f"  >>> CAN THAN - Chua phai thoi diem tot <<<")

if __name__ == "__main__":
    data_dir = "data"
    csv_files = [f.replace(".csv", "") for f in os.listdir(data_dir) if f.endswith(".csv")]
    
    print(f"Da co {len(csv_files)} ma co phieu trong thu muc data")
    
    print("\nChon che do:")
    print("1. Sang loc tat ca co phieu")
    print("2. Phan tich chi tiet 1 ma")
    
    choice = input("\nLua chon (1/2): ").strip()
    
    if choice == "1":
        screen_all_stocks()
    elif choice == "2":
        print(f"\nCac ma co san: {', '.join(csv_files)}")
        symbol = input("Nhap ma co phieu: ").strip().upper()
        analyze_single(symbol)
