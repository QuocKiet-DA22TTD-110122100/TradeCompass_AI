"""
Test nhanh chiến lược MA Crossover
Sử dụng: python backtest_ma.py
"""

from strategies.ma_crossover import ma_crossover_signals
import os

# Liệt kê các file CSV có sẵn
data_dir = "data"
csv_files = [f.replace(".csv", "") for f in os.listdir(data_dir) if f.endswith(".csv")]

print("Cac ma co phieu da tai:")
print(", ".join(csv_files))

symbol = input("\nNhap ma muon backtest (VD: FPT): ").strip().upper()
csv_path = f"data/{symbol}.csv"

if not os.path.exists(csv_path):
    print(f"Khong tim thay file {csv_path}")
else:
    df = ma_crossover_signals(csv_path)
    
    print(f"\n=== Ket qua MA Crossover cho {symbol} ===")
    print(df[["Date", "Close", "MA_fast", "MA_slow", "signal"]].tail(20))
    
    # Thống kê tín hiệu
    buy_signals = (df["signal"] == 2).sum()
    sell_signals = (df["signal"] == -2).sum()
    print(f"\nTong tin hieu MUA: {buy_signals}")
    print(f"Tong tin hieu BAN: {sell_signals}")
