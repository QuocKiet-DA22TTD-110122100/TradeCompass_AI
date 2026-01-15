"""
Auto Updater - Tự động cập nhật dữ liệu cổ phiếu
Chạy nền: python auto_updater.py
"""

import yfinance as yf
import os
import time
import schedule
from datetime import datetime, timedelta
import threading

# Cấu hình
UPDATE_INTERVAL_MINUTES = 15  # Cập nhật mỗi 15 phút trong giờ giao dịch
DATA_DIR = "data"

def get_all_symbols():
    """Lấy danh sách tất cả mã cổ phiếu"""
    if not os.path.exists(DATA_DIR):
        return []
    return [f.replace(".csv", "") for f in os.listdir(DATA_DIR) if f.endswith(".csv")]

def update_stock(symbol: str) -> bool:
    """Cập nhật 1 mã cổ phiếu"""
    try:
        # Thử với .VN trước (cổ phiếu VN)
        yf_symbol = symbol + ".VN"
        data = yf.download(yf_symbol, start="2020-01-01", progress=False)
        
        if data.empty:
            # Thử không có .VN (cổ phiếu US)
            data = yf.download(symbol, start="2020-01-01", progress=False)
        
        if data.empty:
            return False
        
        os.makedirs(DATA_DIR, exist_ok=True)
        data.to_csv(f"{DATA_DIR}/{symbol}.csv")
        return True
    except Exception as e:
        print(f"  Lỗi {symbol}: {e}")
        return False

def update_all_stocks():
    """Cập nhật tất cả cổ phiếu"""
    symbols = get_all_symbols()
    
    if not symbols:
        print("Không có cổ phiếu nào để cập nhật")
        return
    
    now = datetime.now()
    print(f"\n[{now.strftime('%Y-%m-%d %H:%M:%S')}] Bắt đầu cập nhật {len(symbols)} mã...")
    
    success = 0
    failed = 0
    
    for symbol in symbols:
        if update_stock(symbol):
            success += 1
            print(f"  ✓ {symbol}")
        else:
            failed += 1
            print(f"  ✗ {symbol}")
        time.sleep(0.5)  # Delay tránh bị block
    
    print(f"Hoàn thành: {success} thành công, {failed} thất bại")
    
    # Ghi log
    with open("update_log.txt", "a", encoding="utf-8") as f:
        f.write(f"{now.strftime('%Y-%m-%d %H:%M:%S')} - Updated {success}/{len(symbols)} stocks\n")

def is_trading_hours():
    """Kiểm tra có trong giờ giao dịch không (9:00 - 15:00, T2-T6)"""
    now = datetime.now()
    
    # Thứ 7, CN không giao dịch
    if now.weekday() >= 5:
        return False
    
    # Giờ giao dịch: 9:00 - 11:30 và 13:00 - 15:00
    hour = now.hour
    minute = now.minute
    current_time = hour * 60 + minute
    
    morning_start = 9 * 60  # 9:00
    morning_end = 11 * 60 + 30  # 11:30
    afternoon_start = 13 * 60  # 13:00
    afternoon_end = 15 * 60  # 15:00
    
    return (morning_start <= current_time <= morning_end) or \
           (afternoon_start <= current_time <= afternoon_end)

def scheduled_update():
    """Cập nhật theo lịch - chỉ trong giờ giao dịch"""
    if is_trading_hours():
        print("\n📊 Đang trong giờ giao dịch - Cập nhật dữ liệu...")
        update_all_stocks()
    else:
        print(f"\n⏸️ Ngoài giờ giao dịch - Bỏ qua cập nhật ({datetime.now().strftime('%H:%M')})")

def end_of_day_update():
    """Cập nhật cuối ngày (15:30)"""
    print("\n🌙 Cập nhật cuối ngày...")
    update_all_stocks()

def run_scheduler():
    """Chạy scheduler"""
    print("="*50)
    print("   AUTO UPDATER - Tự động cập nhật dữ liệu")
    print("="*50)
    print(f"\nCấu hình:")
    print(f"  - Cập nhật mỗi {UPDATE_INTERVAL_MINUTES} phút trong giờ giao dịch")
    print(f"  - Giờ giao dịch: 9:00-11:30, 13:00-15:00 (T2-T6)")
    print(f"  - Cập nhật cuối ngày: 15:30")
    print(f"\nĐang chạy... (Ctrl+C để dừng)\n")
    
    # Lịch cập nhật trong giờ giao dịch
    schedule.every(UPDATE_INTERVAL_MINUTES).minutes.do(scheduled_update)
    
    # Cập nhật cuối ngày
    schedule.every().day.at("15:30").do(end_of_day_update)
    
    # Cập nhật ngay khi khởi động
    update_all_stocks()
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        # Chạy 1 lần
        update_all_stocks()
    else:
        # Chạy liên tục
        run_scheduler()
