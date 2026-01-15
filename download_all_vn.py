"""
Tải dữ liệu nhiều cổ phiếu Việt Nam
Sử dụng: python download_all_vn.py
"""

import yfinance as yf
from datetime import datetime
import os
import time

# DANH SÁCH 50+ CỔ PHIẾU VIỆT NAM PHỔ BIẾN
VN_STOCKS = {
    # Ngân hàng
    "VCB": "Vietcombank",
    "TCB": "Techcombank", 
    "MBB": "MB Bank",
    "VPB": "VPBank",
    "ACB": "ACB",
    "BID": "BIDV",
    "CTG": "Vietinbank",
    "STB": "Sacombank",
    "HDB": "HDBank",
    "TPB": "TPBank",
    "LPB": "LienVietPostBank",
    "EIB": "Eximbank",
    "SHB": "SHB",
    "SSB": "SeABank",
    "MSB": "MSB",
    
    # Bất động sản
    "VIC": "Vingroup",
    "VHM": "Vinhomes",
    "VRE": "Vincom Retail",
    "NVL": "Novaland",
    "KDH": "Khang Dien",
    "DXG": "Dat Xanh",
    "PDR": "Phat Dat",
    "NLG": "Nam Long",
    "DIG": "DIC Corp",
    "KBC": "Kinh Bac",
    "IJC": "Idico",
    
    # Công nghệ
    "FPT": "FPT",
    "CMG": "CMC",
    
    # Thực phẩm & Đồ uống
    "VNM": "Vinamilk",
    "MSN": "Masan",
    "SAB": "Sabeco",
    "QNS": "Duong Quang Ngai",
    "MCH": "Masan Consumer",
    
    # Bán lẻ
    "MWG": "The Gioi Di Dong",
    "PNJ": "PNJ",
    "FRT": "FPT Retail",
    "DGW": "Dien May Xanh",
    
    # Thép & Vật liệu
    "HPG": "Hoa Phat",
    "HSG": "Hoa Sen",
    "NKG": "Nam Kim",
    
    # Chứng khoán
    "SSI": "SSI",
    "VND": "VNDirect",
    "HCM": "HCMC Securities",
    "VCI": "Vietcap",
    "SHS": "SHS",
    
    # Dầu khí
    "GAS": "PV Gas",
    "PLX": "Petrolimex",
    "PVD": "PV Drilling",
    "PVS": "PV Technical",
    "BSR": "Binh Son Refining",
    
    # Điện
    "POW": "PV Power",
    "GEG": "Gia Lai Electricity",
    "PC1": "Power Construction 1",
    "REE": "REE",
    "NT2": "Nhon Trach 2",
    
    # Hàng không & Logistics
    "HVN": "Vietnam Airlines",
    "VJC": "Vietjet",
    "ACV": "Airports Corporation",
    "GMD": "Gemadept",
    
    # Khác
    "VGC": "Viglacera",
    "GVR": "Vietnam Rubber",
    "DCM": "Dam Ca Mau",
    "DPM": "Dam Phu My",
    "PHR": "Phuoc Hoa Rubber",
    "HAG": "Hoang Anh Gia Lai",
    "DBC": "Dabaco",
    "ANV": "Nam Viet",
    "VHC": "Vinh Hoan",
}

def download_stock(symbol: str, name: str, start: str = "2020-01-01"):
    """Tải dữ liệu 1 mã"""
    yf_symbol = symbol + ".VN"
    end = datetime.today().strftime("%Y-%m-%d")
    
    try:
        data = yf.download(yf_symbol, start=start, end=end, progress=False)
        
        if data.empty:
            return False, 0
        
        os.makedirs("data", exist_ok=True)
        output_path = f"data/{symbol}.csv"
        data.to_csv(output_path)
        
        return True, len(data)
    except Exception as e:
        return False, 0

def download_all():
    """Tải tất cả cổ phiếu"""
    print(f"\n{'='*60}")
    print(f"   TAI DU LIEU {len(VN_STOCKS)} CO PHIEU VIET NAM")
    print(f"{'='*60}\n")
    
    success = 0
    failed = 0
    failed_list = []
    
    for i, (symbol, name) in enumerate(VN_STOCKS.items(), 1):
        print(f"[{i}/{len(VN_STOCKS)}] {symbol} ({name})...", end=" ")
        
        ok, rows = download_stock(symbol, name)
        
        if ok:
            print(f"OK ({rows} ngay)")
            success += 1
        else:
            print("THAT BAI")
            failed += 1
            failed_list.append(symbol)
        
        # Delay để tránh bị block
        time.sleep(0.5)
    
    print(f"\n{'='*60}")
    print(f"   HOAN THANH: {success} thanh cong, {failed} that bai")
    print(f"{'='*60}")
    
    if failed_list:
        print(f"\nCac ma that bai: {', '.join(failed_list)}")

if __name__ == "__main__":
    print("Chon che do:")
    print("1. Tai tat ca 70+ ma co phieu VN")
    print("2. Tai theo nganh")
    print("3. Nhap danh sach tu chon")
    
    choice = input("\nLua chon (1/2/3): ").strip()
    
    if choice == "1":
        download_all()
    
    elif choice == "2":
        print("\nChon nganh:")
        print("1. Ngan hang (15 ma)")
        print("2. Bat dong san (11 ma)")
        print("3. Chung khoan (5 ma)")
        print("4. Dau khi (5 ma)")
        print("5. Thuc pham (5 ma)")
        
        sector = input("Chon nganh (1-5): ").strip()
        
        sectors = {
            "1": ["VCB", "TCB", "MBB", "VPB", "ACB", "BID", "CTG", "STB", "HDB", "TPB", "LPB", "EIB", "SHB", "SSB", "MSB"],
            "2": ["VIC", "VHM", "VRE", "NVL", "KDH", "DXG", "PDR", "NLG", "DIG", "KBC", "IJC"],
            "3": ["SSI", "VND", "HCM", "VCI", "SHS"],
            "4": ["GAS", "PLX", "PVD", "PVS", "BSR"],
            "5": ["VNM", "MSN", "SAB", "QNS", "MCH"],
        }
        
        if sector in sectors:
            for symbol in sectors[sector]:
                name = VN_STOCKS.get(symbol, symbol)
                print(f"Dang tai {symbol}...", end=" ")
                ok, rows = download_stock(symbol, name)
                print(f"OK ({rows} ngay)" if ok else "THAT BAI")
                time.sleep(0.5)
    
    elif choice == "3":
        symbols_input = input("Nhap cac ma (cach nhau boi dau phay): ").strip().upper()
        symbols = [s.strip() for s in symbols_input.split(",") if s.strip()]
        
        for symbol in symbols:
            name = VN_STOCKS.get(symbol, symbol)
            print(f"Dang tai {symbol}...", end=" ")
            ok, rows = download_stock(symbol, name)
            print(f"OK ({rows} ngay)" if ok else "THAT BAI")
            time.sleep(0.5)
