"""
Phần 1: Phân tích Sentiment từ tin tức
Sử dụng: python sentiment_analysis.py
"""

import requests
from datetime import datetime, timedelta
import re
import os

# Từ điển sentiment tiếng Việt cho chứng khoán
POSITIVE_WORDS = [
    "tăng", "tăng trưởng", "lợi nhuận", "kỷ lục", "đột phá", "bứt phá",
    "khởi sắc", "tích cực", "lạc quan", "hồi phục", "vượt", "cao nhất",
    "thắng", "thành công", "hiệu quả", "mạnh", "vững", "ổn định",
    "cơ hội", "tiềm năng", "triển vọng", "khuyến nghị mua", "outperform",
    "nâng mục tiêu", "doanh thu tăng", "cổ tức", "chia thưởng",
    "hợp đồng lớn", "mở rộng", "đầu tư", "phát triển", "tốt"
]

NEGATIVE_WORDS = [
    "giảm", "sụt", "lỗ", "thua", "thấp nhất", "đáy", "suy giảm",
    "tiêu cực", "bi quan", "rủi ro", "cảnh báo", "lo ngại", "khó khăn",
    "yếu", "bán tháo", "thoái vốn", "nợ", "phá sản", "điều tra",
    "vi phạm", "xử phạt", "đình chỉ", "hủy niêm yết", "khuyến nghị bán",
    "underperform", "hạ mục tiêu", "doanh thu giảm", "cắt giảm",
    "sa thải", "đóng cửa", "thua lỗ", "xấu"
]

def analyze_text_sentiment(text: str) -> dict:
    """Phân tích sentiment của một đoạn text"""
    text_lower = text.lower()
    
    positive_count = sum(1 for word in POSITIVE_WORDS if word in text_lower)
    negative_count = sum(1 for word in NEGATIVE_WORDS if word in text_lower)
    
    total = positive_count + negative_count
    if total == 0:
        score = 0
        label = "TRUNG TINH"
    else:
        score = (positive_count - negative_count) / total
        if score > 0.2:
            label = "TICH CUC"
        elif score < -0.2:
            label = "TIEU CUC"
        else:
            label = "TRUNG TINH"
    
    return {
        "score": score,
        "label": label,
        "positive_count": positive_count,
        "negative_count": negative_count
    }

def search_news_google(symbol: str, company_name: str = "") -> list:
    """Tìm tin tức từ Google News RSS (không cần API key)"""
    search_query = f"{symbol} cổ phiếu {company_name}".strip()
    search_query = search_query.replace(" ", "+")
    
    url = f"https://news.google.com/rss/search?q={search_query}&hl=vi&gl=VN&ceid=VN:vi"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            # Parse RSS đơn giản
            content = response.text
            
            # Tìm các item trong RSS
            items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)
            
            news_list = []
            for item in items[:10]:  # Lấy 10 tin mới nhất
                title_match = re.search(r'<title>(.*?)</title>', item)
                link_match = re.search(r'<link>(.*?)</link>', item)
                date_match = re.search(r'<pubDate>(.*?)</pubDate>', item)
                
                if title_match:
                    title = title_match.group(1)
                    # Loại bỏ CDATA
                    title = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', title)
                    
                    news_list.append({
                        "title": title,
                        "link": link_match.group(1) if link_match else "",
                        "date": date_match.group(1) if date_match else ""
                    })
            
            return news_list
    except Exception as e:
        print(f"Loi khi lay tin tuc: {e}")
    
    return []

def get_sample_news(symbol: str) -> list:
    """Tin tức mẫu để test khi không có internet"""
    sample_news = {
        "FPT": [
            {"title": "FPT đạt doanh thu kỷ lục, lợi nhuận tăng 20%", "date": "2024-01-10"},
            {"title": "FPT ký hợp đồng lớn với đối tác Nhật Bản", "date": "2024-01-09"},
            {"title": "Cổ phiếu FPT được khuyến nghị mua với tiềm năng tăng trưởng", "date": "2024-01-08"},
        ],
        "VNM": [
            {"title": "Vinamilk công bố chia cổ tức tiền mặt", "date": "2024-01-10"},
            {"title": "VNM mở rộng thị trường xuất khẩu", "date": "2024-01-09"},
        ],
        "VCB": [
            {"title": "Vietcombank báo lãi kỷ lục năm 2023", "date": "2024-01-10"},
            {"title": "VCB được nâng hạng tín nhiệm", "date": "2024-01-09"},
        ],
        "DEFAULT": [
            {"title": "Thị trường chứng khoán Việt Nam khởi sắc", "date": "2024-01-10"},
            {"title": "VN-Index hồi phục mạnh trong phiên giao dịch", "date": "2024-01-09"},
        ]
    }
    
    return sample_news.get(symbol, sample_news["DEFAULT"])

def analyze_stock_sentiment(symbol: str, use_sample: bool = False) -> dict:
    """Phân tích sentiment tổng hợp cho 1 mã cổ phiếu"""
    
    print(f"\nDang tim tin tuc cho {symbol}...")
    
    if use_sample:
        news_list = get_sample_news(symbol)
    else:
        news_list = search_news_google(symbol)
        if not news_list:
            print("Khong tim thay tin tuc online, su dung tin mau...")
            news_list = get_sample_news(symbol)
    
    if not news_list:
        return {"error": "Khong tim thay tin tuc"}
    
    # Phân tích từng tin
    results = []
    total_score = 0
    
    print(f"\n--- TIN TUC VA SENTIMENT ({symbol}) ---\n")
    
    for i, news in enumerate(news_list, 1):
        sentiment = analyze_text_sentiment(news["title"])
        results.append({
            "title": news["title"],
            "date": news.get("date", ""),
            "sentiment": sentiment
        })
        total_score += sentiment["score"]
        
        # Hiển thị
        emoji = "🟢" if sentiment["label"] == "TICH CUC" else ("🔴" if sentiment["label"] == "TIEU CUC" else "⚪")
        print(f"{i}. {emoji} [{sentiment['label']}]")
        print(f"   {news['title'][:80]}...")
        print()
    
    # Tính sentiment trung bình
    avg_score = total_score / len(results) if results else 0
    
    if avg_score > 0.15:
        overall_label = "TICH CUC"
        recommendation = "Tin tuc ho tro - Co the xem xet MUA"
    elif avg_score < -0.15:
        overall_label = "TIEU CUC"
        recommendation = "Tin tuc tieu cuc - CAN THAN"
    else:
        overall_label = "TRUNG TINH"
        recommendation = "Tin tuc trung tinh - THEO DOI"
    
    summary = {
        "symbol": symbol,
        "news_count": len(results),
        "avg_score": avg_score,
        "overall_label": overall_label,
        "recommendation": recommendation,
        "positive_news": sum(1 for r in results if r["sentiment"]["label"] == "TICH CUC"),
        "negative_news": sum(1 for r in results if r["sentiment"]["label"] == "TIEU CUC"),
        "neutral_news": sum(1 for r in results if r["sentiment"]["label"] == "TRUNG TINH"),
    }
    
    return summary

def print_summary(summary: dict):
    """In tổng kết sentiment"""
    print(f"\n{'='*50}")
    print(f"   TONG KET SENTIMENT: {summary['symbol']}")
    print(f"{'='*50}")
    print(f"  So tin phan tich: {summary['news_count']}")
    print(f"  Tin tich cuc: {summary['positive_news']}")
    print(f"  Tin tieu cuc: {summary['negative_news']}")
    print(f"  Tin trung tinh: {summary['neutral_news']}")
    print(f"  Diem sentiment: {summary['avg_score']:.2f} (-1 den +1)")
    print(f"  Danh gia: {summary['overall_label']}")
    print(f"\n  >>> {summary['recommendation']} <<<")

if __name__ == "__main__":
    data_dir = "data"
    if os.path.exists(data_dir):
        csv_files = [f.replace(".csv", "") for f in os.listdir(data_dir) if f.endswith(".csv")]
        print("Cac ma co phieu da tai:")
        print(", ".join(csv_files))
    
    symbol = input("\nNhap ma co phieu (VD: FPT): ").strip().upper()
    
    print("\nChon nguon tin:")
    print("1. Tim tin tuc online (Google News)")
    print("2. Su dung tin mau (de test)")
    
    choice = input("Lua chon (1/2): ").strip()
    use_sample = choice == "2"
    
    summary = analyze_stock_sentiment(symbol, use_sample)
    
    if "error" not in summary:
        print_summary(summary)
