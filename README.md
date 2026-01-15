# 🤖 TradeCompass AI - Phân tích cổ phiếu thông minh

Ứng dụng AI hỗ trợ phân tích và dự đoán cổ phiếu Việt Nam với nhiều công cụ kỹ thuật.

## ✨ Tính năng

- 📊 **Biểu đồ nến** với MA, Bollinger Bands, RSI, MACD
- 🤖 **AI đánh giá** cổ phiếu với điểm số và khuyến nghị
- 🔍 **Sàng lọc** cổ phiếu tiềm năng tự động
- 📈 **Nhận diện mẫu hình** (Chart Patterns, Candlestick Patterns)
- 🔄 **Tự động cập nhật** dữ liệu giá
- 📱 **Giao diện web** thân thiện

## 🚀 Cài đặt

```bash
# Clone repo
git clone https://github.com/QuocKiet-DA22TTD-110122100/TradeCompass_AI.git
cd TradeCompass_AI

# Tạo môi trường ảo
python -m venv venv

# Kích hoạt venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Cài thư viện
pip install -r requirements.txt
```

## 📖 Sử dụng

### 1. Tải dữ liệu cổ phiếu
```bash
python download_all_vn.py
```

### 2. Chạy web app
```bash
python app.py
```
Truy cập: http://localhost:5000

### 3. Các công cụ khác
```bash
python stock_screener.py      # Sàng lọc cổ phiếu
python pattern_recognition.py # Nhận diện mẫu hình
python volume_analysis.py     # Phân tích khối lượng
python multi_timeframe.py     # Phân tích đa khung thời gian
python lstm_prediction.py     # Dự đoán ML
```

## 📁 Cấu trúc dự án

```
TradeCompass_AI/
├── app.py                  # Web application chính
├── templates/
│   └── index.html          # Giao diện web
├── data/                   # Dữ liệu CSV cổ phiếu
├── strategies/
│   └── ma_crossover.py     # Chiến lược MA
├── pattern_recognition.py  # Nhận diện mẫu hình
├── stock_screener.py       # Sàng lọc cổ phiếu
├── volume_analysis.py      # Phân tích volume
├── multi_timeframe.py      # Đa khung thời gian
├── lstm_prediction.py      # Dự đoán ML
├── auto_updater.py         # Tự động cập nhật
├── download_all_vn.py      # Tải dữ liệu VN
└── requirements.txt        # Thư viện cần thiết
```

## 🛠️ Công nghệ

- Python 3.10+
- Flask (Web framework)
- Pandas, NumPy (Xử lý dữ liệu)
- yfinance (Lấy dữ liệu)
- scikit-learn (Machine Learning)
- Chart.js (Biểu đồ)

## ⚠️ Lưu ý

- Dữ liệu từ Yahoo Finance có delay 15-20 phút
- Đây là công cụ hỗ trợ, không phải khuyến nghị đầu tư
- Luôn nghiên cứu kỹ trước khi đầu tư

## 📝 License

MIT License
