"""
Phân tích khối lượng giao dịch (Volume Analysis)
Sử dụng: python volume_analysis.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
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

def analyze_volume(df: pd.DataFrame, symbol: str):
    """Phân tích khối lượng giao dịch"""
    df = df.copy()
    
    # Tính các chỉ số volume
    df["Vol_MA5"] = df["Volume"].rolling(5).mean()
    df["Vol_MA20"] = df["Volume"].rolling(20).mean()
    df["Vol_MA50"] = df["Volume"].rolling(50).mean()
    df["Vol_Ratio"] = df["Volume"] / df["Vol_MA20"]
    
    # Giá trị giao dịch (ước tính)
    df["Value"] = df["Close"] * df["Volume"]
    df["Value_MA20"] = df["Value"].rolling(20).mean()
    
    # OBV (On Balance Volume)
    df["OBV"] = 0
    for i in range(1, len(df)):
        if df["Close"].iloc[i] > df["Close"].iloc[i-1]:
            df.iloc[i, df.columns.get_loc("OBV")] = df["OBV"].iloc[i-1] + df["Volume"].iloc[i]
        elif df["Close"].iloc[i] < df["Close"].iloc[i-1]:
            df.iloc[i, df.columns.get_loc("OBV")] = df["OBV"].iloc[i-1] - df["Volume"].iloc[i]
        else:
            df.iloc[i, df.columns.get_loc("OBV")] = df["OBV"].iloc[i-1]
    
    # Volume Price Trend
    df["VPT"] = (df["Close"].pct_change() * df["Volume"]).cumsum()
    
    # Accumulation/Distribution
    df["AD"] = ((df["Close"] - df["Low"]) - (df["High"] - df["Close"])) / (df["High"] - df["Low"]) * df["Volume"]
    df["AD"] = df["AD"].cumsum()
    
    return df

def print_volume_stats(df: pd.DataFrame, symbol: str):
    """In thống kê khối lượng"""
    latest = df.iloc[-1]
    
    print(f"\n{'='*60}")
    print(f"   PHAN TICH KHOI LUONG: {symbol}")
    print(f"   Ngay: {df.index[-1].strftime('%Y-%m-%d')}")
    print(f"{'='*60}")
    
    # Thống kê cơ bản
    print(f"\n--- THONG KE CO BAN ---")
    print(f"  Khoi luong hom nay: {latest['Volume']:,.0f}")
    print(f"  TB 5 ngay: {latest['Vol_MA5']:,.0f}")
    print(f"  TB 20 ngay: {latest['Vol_MA20']:,.0f}")
    print(f"  TB 50 ngay: {latest['Vol_MA50']:,.0f}")
    print(f"  Ty le so voi TB20: {latest['Vol_Ratio']:.2f}x")
    
    # Giá trị giao dịch
    print(f"\n--- GIA TRI GIAO DICH ---")
    print(f"  Gia tri hom nay: {latest['Value']:,.0f}")
    print(f"  TB 20 ngay: {latest['Value_MA20']:,.0f}")
    
    # Đánh giá volume
    print(f"\n--- DANH GIA ---")
    
    vol_ratio = latest['Vol_Ratio']
    if vol_ratio > 2:
        print(f"  Volume: RAT CAO (gap {vol_ratio:.1f}x TB)")
        vol_signal = "MANH"
    elif vol_ratio > 1.5:
        print(f"  Volume: CAO (gap {vol_ratio:.1f}x TB)")
        vol_signal = "TANG"
    elif vol_ratio < 0.5:
        print(f"  Volume: RAT THAP (chi {vol_ratio:.1f}x TB)")
        vol_signal = "YEU"
    elif vol_ratio < 0.7:
        print(f"  Volume: THAP (chi {vol_ratio:.1f}x TB)")
        vol_signal = "GIAM"
    else:
        print(f"  Volume: BINH THUONG ({vol_ratio:.1f}x TB)")
        vol_signal = "TRUNG TINH"
    
    # Xu hướng giá + volume
    price_change = (latest['Close'] - df['Close'].iloc[-2]) / df['Close'].iloc[-2] * 100
    
    print(f"\n--- TIN HIEU GIA + VOLUME ---")
    print(f"  Gia thay doi: {price_change:+.2f}%")
    
    if price_change > 0 and vol_ratio > 1.2:
        print(f"  >>> TANG GIA + VOLUME CAO = XU HUONG TANG MANH <<<")
    elif price_change > 0 and vol_ratio < 0.8:
        print(f"  >>> TANG GIA + VOLUME THAP = TANG YEU, CAN THAN <<<")
    elif price_change < 0 and vol_ratio > 1.2:
        print(f"  >>> GIAM GIA + VOLUME CAO = AP LUC BAN MANH <<<")
    elif price_change < 0 and vol_ratio < 0.8:
        print(f"  >>> GIAM GIA + VOLUME THAP = GIAM NHE, CO THE HOI PHUC <<<")
    else:
        print(f"  >>> CHUA RO XU HUONG <<<")
    
    # Thống kê 30 ngày
    df_30d = df.tail(30)
    
    print(f"\n--- THONG KE 30 NGAY ---")
    print(f"  Volume cao nhat: {df_30d['Volume'].max():,.0f}")
    print(f"  Volume thap nhat: {df_30d['Volume'].min():,.0f}")
    print(f"  Volume trung binh: {df_30d['Volume'].mean():,.0f}")
    
    # Số ngày volume cao/thấp
    high_vol_days = (df_30d['Vol_Ratio'] > 1.5).sum()
    low_vol_days = (df_30d['Vol_Ratio'] < 0.7).sum()
    
    print(f"  So ngay volume cao (>1.5x): {high_vol_days}")
    print(f"  So ngay volume thap (<0.7x): {low_vol_days}")
    
    # Top 5 ngày volume cao nhất
    print(f"\n--- TOP 5 NGAY VOLUME CAO NHAT (30 ngay) ---")
    top_vol = df_30d.nlargest(5, 'Volume')[['Close', 'Volume', 'Vol_Ratio']]
    for date, row in top_vol.iterrows():
        print(f"  {date.strftime('%Y-%m-%d')}: {row['Volume']:>12,.0f} ({row['Vol_Ratio']:.1f}x) - Gia: {row['Close']:,.0f}")
    
    return df

def plot_volume(df: pd.DataFrame, symbol: str, days: int = 60):
    """Vẽ biểu đồ volume"""
    df_plot = df.tail(days)
    
    fig, axes = plt.subplots(3, 1, figsize=(14, 12))
    
    # Chart 1: Giá và Volume
    ax1 = axes[0]
    ax1.plot(df_plot.index, df_plot['Close'], color='blue', label='Gia')
    ax1.set_ylabel('Gia', color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    ax1_vol = ax1.twinx()
    colors = ['green' if df_plot['Close'].iloc[i] >= df_plot['Open'].iloc[i] else 'red' 
              for i in range(len(df_plot))]
    ax1_vol.bar(df_plot.index, df_plot['Volume'], color=colors, alpha=0.5, label='Volume')
    ax1_vol.plot(df_plot.index, df_plot['Vol_MA20'], color='orange', linestyle='--', label='Vol MA20')
    ax1_vol.set_ylabel('Volume', color='gray')
    ax1_vol.legend(loc='upper right')
    ax1.set_title(f'{symbol} - Gia va Khoi luong ({days} ngay)')
    
    # Chart 2: Volume Ratio
    ax2 = axes[1]
    colors2 = ['green' if r > 1 else 'red' for r in df_plot['Vol_Ratio']]
    ax2.bar(df_plot.index, df_plot['Vol_Ratio'], color=colors2, alpha=0.7)
    ax2.axhline(y=1, color='black', linestyle='-', linewidth=1)
    ax2.axhline(y=1.5, color='orange', linestyle='--', linewidth=1, label='1.5x')
    ax2.axhline(y=2, color='red', linestyle='--', linewidth=1, label='2x')
    ax2.set_ylabel('Volume Ratio')
    ax2.set_title('Ty le Volume so voi TB20')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Chart 3: OBV
    ax3 = axes[2]
    ax3.plot(df_plot.index, df_plot['OBV'], color='purple', label='OBV')
    ax3.set_ylabel('OBV')
    ax3.set_title('On Balance Volume (OBV)')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

def scan_volume_all(symbols: list = None):
    """Quét volume tất cả các mã"""
    data_dir = "data"
    
    if symbols is None:
        csv_files = [f.replace(".csv", "") for f in os.listdir(data_dir) if f.endswith(".csv")]
    else:
        csv_files = symbols
    
    print(f"\n{'='*70}")
    print(f"   QUET KHOI LUONG TAT CA CO PHIEU")
    print(f"{'='*70}")
    
    results = []
    
    for symbol in csv_files:
        csv_path = f"data/{symbol}.csv"
        if os.path.exists(csv_path):
            try:
                df = load_data(csv_path)
                df = analyze_volume(df, symbol)
                
                latest = df.iloc[-1]
                price_change = (latest['Close'] - df['Close'].iloc[-2]) / df['Close'].iloc[-2] * 100
                
                results.append({
                    "symbol": symbol,
                    "price": latest['Close'],
                    "change": price_change,
                    "volume": latest['Volume'],
                    "vol_ma20": latest['Vol_MA20'],
                    "vol_ratio": latest['Vol_Ratio']
                })
            except Exception as e:
                print(f"Loi {symbol}: {e}")
    
    # Sắp xếp theo volume ratio
    results_sorted = sorted(results, key=lambda x: x['vol_ratio'], reverse=True)
    
    print(f"\n{'Ma':<8} {'Gia':>12} {'%':>8} {'Volume':>15} {'TB20':>15} {'Ratio':>8}")
    print("-" * 70)
    
    for r in results_sorted:
        emoji = "🔥" if r['vol_ratio'] > 2 else ("📈" if r['vol_ratio'] > 1.5 else "")
        print(f"{r['symbol']:<8} {r['price']:>12,.0f} {r['change']:>+7.2f}% {r['volume']:>15,.0f} {r['vol_ma20']:>15,.0f} {r['vol_ratio']:>7.2f}x {emoji}")
    
    # Highlight
    print(f"\n--- CO PHIEU VOLUME DOT BIEN ---")
    high_vol = [r for r in results if r['vol_ratio'] > 1.5]
    if high_vol:
        for r in high_vol:
            signal = "TANG" if r['change'] > 0 else "GIAM"
            print(f"  {r['symbol']}: Volume gap {r['vol_ratio']:.1f}x, Gia {signal} {abs(r['change']):.2f}%")
    else:
        print("  Khong co co phieu nao co volume dot bien")

if __name__ == "__main__":
    data_dir = "data"
    csv_files = [f.replace(".csv", "") for f in os.listdir(data_dir) if f.endswith(".csv")]
    
    print("Cac ma co phieu da tai:")
    print(", ".join(csv_files))
    
    print("\nChon che do:")
    print("1. Phan tich 1 ma co phieu")
    print("2. Quet volume tat ca")
    
    choice = input("\nLua chon (1/2): ").strip()
    
    if choice == "1":
        symbol = input("Nhap ma co phieu (VD: FPT): ").strip().upper()
        csv_path = f"data/{symbol}.csv"
        
        if os.path.exists(csv_path):
            df = load_data(csv_path)
            df = analyze_volume(df, symbol)
            print_volume_stats(df, symbol)
            
            show_chart = input("\nHien thi bieu do? (y/n): ").strip().lower()
            if show_chart == 'y':
                days = input("So ngay (mac dinh 60): ").strip()
                days = int(days) if days.isdigit() else 60
                plot_volume(df, symbol, days)
        else:
            print(f"Khong tim thay file {csv_path}")
    
    elif choice == "2":
        scan_volume_all()
