"""
Bước 2: Download dữ liệu cổ phiếu từ Yahoo Finance
Sử dụng: python download_data.py
"""

import yfinance as yf
from datetime import datetime
import os

# Danh sách các mã cổ phiếu phổ biến để học
DEFAULT_SYMBOLS = [
    "AAPL",   # Apple
    "MSFT",   # Microsoft
    "GOOGL",  # Google
    "AMZN",   # Amazon
    "TSLA",   # Tesla
    "META",   # Meta (Facebook)
    "NVDA",   # Nvidia
    "JPM",    # JPMorgan
    "V",      # Visa
    "JNJ",    # Johnson & Johnson
]

def download_data(symbol: str, start: str = "2019-01-01", end: str | None = None):
    if end is None:
        end = datetime.today().strftime("%Y-%m-%d")

    print(f"Tải dữ liệu {symbol} từ {start} đến {end}...")
    data = yf.download(symbol, start=start, end=end, progress=False)

    if data.empty:
        print(f"  ❌ Không có dữ liệu cho {symbol}")
        return False

    # Tạo thư mục data nếu chưa có
    os.makedirs("data", exist_ok=True)
    
    output_path = f"data/{symbol}.csv"
    data.to_csv(output_path)
    print(f"  ✅ Đã lưu {len(data)} dòng vào {output_path}")
    return True

def download_multiple(symbols: list[str]):
    """Tải nhiều mã cổ phiếu cùng lúc"""
    print(f"\n=== Bắt đầu tải {len(symbols)} mã cổ phiếu ===\n")
    
    success = 0
    failed = 0
    
    for symbol in symbols:
        if download_data(symbol):
            success += 1
        else:
            failed += 1
    
    print(f"\n=== Hoàn thành: {success} thành công, {failed} thất bại ===")

if __name__ == "__main__":
    print("Chọn chế độ:")
    print("1. Tải 1 mã cổ phiếu")
    print("2. Tải tất cả mã mặc định (10 mã US phổ biến)")
    print("3. Nhập danh sách mã (cách nhau bởi dấu phẩy)")
    
    choice = input("\nNhập lựa chọn (1/2/3): ").strip()
    
    if choice == "1":
        symbol = input("Nhập mã cổ phiếu (ví dụ AAPL): ").strip().upper()
        download_data(symbol)
    elif choice == "2":
        download_multiple(DEFAULT_SYMBOLS)
    elif choice == "3":
        symbols_input = input("Nhập các mã (VD: AAPL,MSFT,GOOGL): ").strip().upper()
        symbols = [s.strip() for s in symbols_input.split(",") if s.strip()]
        download_multiple(symbols)
    else:
        print("Lựa chọn không hợp lệ!")
