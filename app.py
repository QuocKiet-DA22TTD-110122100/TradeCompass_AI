"""
Stock AI Web Application - Với cập nhật giá realtime
Chạy: python app.py
Truy cập: http://localhost:5000
"""

from flask import Flask, render_template, jsonify, request
import pandas as pd
import numpy as np
import yfinance as yf
import os
import json
from datetime import datetime, timedelta
import threading
import time
import schedule
from pattern_recognition import PatternRecognition, load_data as load_pattern_data

app = Flask(__name__)

# ============ AUTO UPDATE CONFIG ============
AUTO_UPDATE_ENABLED = True
UPDATE_INTERVAL_MINUTES = 15  # Cập nhật mỗi 15 phút trong giờ giao dịch
last_auto_update = None

# Cache để lưu dữ liệu
data_cache = {}
last_update = {}

# ============ DATA FUNCTIONS ============

def get_realtime_price(symbol: str) -> dict:
    """Lấy giá realtime từ Yahoo Finance"""
    try:
        yf_symbol = symbol + ".VN"
        ticker = yf.Ticker(yf_symbol)
        
        # Lấy thông tin realtime
        info = ticker.info
        
        # Lấy giá từ history nếu info không có
        hist = ticker.history(period="5d")
        
        if hist.empty:
            return None
        
        latest = hist.iloc[-1]
        prev = hist.iloc[-2] if len(hist) > 1 else hist.iloc[-1]
        
        current_price = float(latest["Close"])
        prev_close = float(prev["Close"])
        change = current_price - prev_close
        change_pct = (change / prev_close) * 100
        
        return {
            "symbol": symbol,
            "price": current_price,
            "change": change,
            "change_pct": change_pct,
            "open": float(latest["Open"]),
            "high": float(latest["High"]),
            "low": float(latest["Low"]),
            "volume": int(latest["Volume"]),
            "prev_close": prev_close,
            "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        print(f"Lỗi lấy giá {symbol}: {e}")
        return None

def update_stock_data(symbol: str) -> bool:
    """Cập nhật dữ liệu cổ phiếu mới nhất"""
    try:
        yf_symbol = symbol + ".VN"
        
        # Lấy dữ liệu từ 2020 đến nay
        data = yf.download(yf_symbol, start="2020-01-01", progress=False)
        
        if data.empty:
            # Thử không có .VN (cho mã US)
            data = yf.download(symbol, start="2020-01-01", progress=False)
        
        if data.empty:
            return False
        
        # Lưu file
        os.makedirs("data", exist_ok=True)
        data.to_csv(f"data/{symbol}.csv")
        
        # Cập nhật cache
        last_update[symbol] = datetime.now()
        
        return True
    except Exception as e:
        print(f"Lỗi cập nhật {symbol}: {e}")
        return False

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

def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Tính các chỉ báo kỹ thuật"""
    df = df.copy()
    
    # MA
    df["MA20"] = df["Close"].rolling(20).mean()
    df["MA50"] = df["Close"].rolling(50).mean()
    
    # RSI
    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))
    
    # MACD
    ema12 = df["Close"].ewm(span=12).mean()
    ema26 = df["Close"].ewm(span=26).mean()
    df["MACD"] = ema12 - ema26
    df["MACD_Signal"] = df["MACD"].ewm(span=9).mean()
    
    # Bollinger Bands
    df["BB_Mid"] = df["Close"].rolling(20).mean()
    bb_std = df["Close"].rolling(20).std()
    df["BB_Upper"] = df["BB_Mid"] + 2 * bb_std
    df["BB_Lower"] = df["BB_Mid"] - 2 * bb_std
    
    # Volume MA
    df["Vol_MA20"] = df["Volume"].rolling(20).mean()
    
    return df

def ai_analyze(df: pd.DataFrame, symbol: str, realtime_price: dict = None) -> dict:
    """AI phân tích và đánh giá cổ phiếu"""
    if len(df) < 50:
        return {"error": "Không đủ dữ liệu"}
    
    df = calculate_indicators(df)
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    # Sử dụng giá realtime nếu có
    if realtime_price:
        current_price = realtime_price["price"]
        price_change = realtime_price["change_pct"]
        updated_time = realtime_price["updated"]
    else:
        current_price = float(latest["Close"])
        price_change = float((latest["Close"] - prev["Close"]) / prev["Close"] * 100)
        updated_time = df.index[-1].strftime("%Y-%m-%d")
    
    score = 0
    max_score = 100
    signals = []
    
    # 1. Xu hướng MA (25 điểm)
    ma20 = float(latest["MA20"])
    ma50 = float(latest["MA50"])
    
    if current_price > ma20 > ma50:
        score += 25
        signals.append({"type": "bullish", "text": "Giá trên MA20 và MA50 - Xu hướng tăng mạnh"})
    elif current_price > ma20:
        score += 15
        signals.append({"type": "bullish", "text": "Giá trên MA20 - Xu hướng tăng"})
    elif current_price < ma20 < ma50:
        score += 0
        signals.append({"type": "bearish", "text": "Giá dưới MA20 và MA50 - Xu hướng giảm"})
    else:
        score += 10
        signals.append({"type": "neutral", "text": "Xu hướng chưa rõ ràng"})
    
    # Golden/Death Cross
    prev_ma20 = float(prev["MA20"])
    prev_ma50 = float(prev["MA50"])
    
    if prev_ma20 <= prev_ma50 and ma20 > ma50:
        score += 10
        signals.append({"type": "bullish", "text": "🔥 GOLDEN CROSS - Tín hiệu mua mạnh!"})
    elif prev_ma20 >= prev_ma50 and ma20 < ma50:
        score -= 10
        signals.append({"type": "bearish", "text": "⚠️ DEATH CROSS - Tín hiệu bán!"})
    
    # 2. RSI (20 điểm)
    rsi = float(latest["RSI"])
    if 30 <= rsi <= 40:
        score += 20
        signals.append({"type": "bullish", "text": f"RSI {rsi:.0f} - Gần vùng quá bán, cơ hội mua"})
    elif rsi < 30:
        score += 15
        signals.append({"type": "bullish", "text": f"RSI {rsi:.0f} - Quá bán, có thể hồi phục"})
    elif 40 <= rsi <= 60:
        score += 15
        signals.append({"type": "neutral", "text": f"RSI {rsi:.0f} - Vùng trung tính"})
    elif 60 < rsi <= 70:
        score += 10
        signals.append({"type": "neutral", "text": f"RSI {rsi:.0f} - Đang mạnh"})
    else:
        score += 5
        signals.append({"type": "bearish", "text": f"RSI {rsi:.0f} - Quá mua, cẩn thận"})
    
    # 3. MACD (20 điểm)
    macd = float(latest["MACD"])
    macd_signal = float(latest["MACD_Signal"])
    prev_macd = float(prev["MACD"])
    prev_signal = float(prev["MACD_Signal"])
    
    if macd > macd_signal:
        score += 15
        signals.append({"type": "bullish", "text": "MACD trên Signal - Động lượng tăng"})
    else:
        score += 5
        signals.append({"type": "bearish", "text": "MACD dưới Signal - Động lượng giảm"})
    
    if prev_macd <= prev_signal and macd > macd_signal:
        score += 5
        signals.append({"type": "bullish", "text": "MACD vừa cắt lên Signal!"})
    
    # 4. Volume (15 điểm)
    vol_ma20 = float(latest["Vol_MA20"])
    vol_ratio = float(latest["Volume"]) / vol_ma20 if vol_ma20 > 0 else 1
    
    if vol_ratio > 1.5:
        score += 15
        signals.append({"type": "bullish", "text": f"Volume cao gấp {vol_ratio:.1f}x - Có sự quan tâm"})
    elif vol_ratio > 1:
        score += 10
        signals.append({"type": "neutral", "text": f"Volume bình thường ({vol_ratio:.1f}x)"})
    else:
        score += 5
        signals.append({"type": "bearish", "text": f"Volume thấp ({vol_ratio:.1f}x)"})
    
    # 5. Bollinger Bands (10 điểm)
    bb_upper = float(latest["BB_Upper"])
    bb_lower = float(latest["BB_Lower"])
    bb_pos = (current_price - bb_lower) / (bb_upper - bb_lower) if bb_upper != bb_lower else 0.5
    
    if bb_pos < 0.2:
        score += 10
        signals.append({"type": "bullish", "text": "Giá gần đáy Bollinger - Cơ hội mua"})
    elif bb_pos > 0.8:
        score += 3
        signals.append({"type": "bearish", "text": "Giá gần đỉnh Bollinger - Cẩn thận"})
    else:
        score += 7
        signals.append({"type": "neutral", "text": "Giá trong vùng Bollinger an toàn"})
    
    # 6. Xu hướng ngắn hạn (10 điểm)
    price_5d_ago = float(df["Close"].iloc[-5])
    ret_5d = (current_price - price_5d_ago) / price_5d_ago * 100
    
    if ret_5d > 3:
        score += 10
        signals.append({"type": "bullish", "text": f"Tăng {ret_5d:.1f}% trong 5 ngày"})
    elif ret_5d > 0:
        score += 7
        signals.append({"type": "neutral", "text": f"Tăng nhẹ {ret_5d:.1f}% trong 5 ngày"})
    else:
        score += 3
        signals.append({"type": "bearish", "text": f"Giảm {abs(ret_5d):.1f}% trong 5 ngày"})
    
    # Xếp hạng
    if score >= 80:
        rating = "A+"
        recommendation = "MUA MẠNH"
        rec_class = "buy-strong"
    elif score >= 70:
        rating = "A"
        recommendation = "NÊN MUA"
        rec_class = "buy"
    elif score >= 60:
        rating = "B+"
        recommendation = "THEO DÕI ĐỂ MUA"
        rec_class = "watch"
    elif score >= 50:
        rating = "B"
        recommendation = "TRUNG LẬP"
        rec_class = "neutral"
    elif score >= 40:
        rating = "C"
        recommendation = "CẨN THẬN"
        rec_class = "caution"
    else:
        rating = "D"
        recommendation = "TRÁNH"
        rec_class = "avoid"
    
    return {
        "symbol": symbol,
        "price": current_price,
        "change": price_change,
        "score": score,
        "max_score": max_score,
        "rating": rating,
        "recommendation": recommendation,
        "rec_class": rec_class,
        "signals": signals,
        "indicators": {
            "rsi": rsi,
            "macd": macd,
            "macd_signal": macd_signal,
            "ma20": ma20,
            "ma50": ma50,
            "vol_ratio": vol_ratio
        },
        "updated": updated_time
    }

# ============ ROUTES ============

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/stocks")
def get_stocks():
    """Lấy danh sách cổ phiếu"""
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    stocks = [f.replace(".csv", "") for f in os.listdir(data_dir) if f.endswith(".csv")]
    return jsonify(sorted(stocks))

@app.route("/api/stock/<symbol>")
def get_stock_data(symbol):
    """Lấy dữ liệu 1 cổ phiếu"""
    csv_path = f"data/{symbol}.csv"
    
    if not os.path.exists(csv_path):
        return jsonify({"error": "Không tìm thấy dữ liệu"}), 404
    
    df = load_data(csv_path)
    df = calculate_indicators(df)
    
    # Lấy 200 ngày gần nhất
    df = df.tail(200)
    
    data = {
        "dates": df.index.strftime("%Y-%m-%d").tolist(),
        "open": df["Open"].tolist(),
        "high": df["High"].tolist(),
        "low": df["Low"].tolist(),
        "close": df["Close"].tolist(),
        "volume": df["Volume"].tolist(),
        "ma20": df["MA20"].tolist(),
        "ma50": df["MA50"].tolist(),
        "rsi": df["RSI"].tolist(),
        "macd": df["MACD"].tolist(),
        "macd_signal": df["MACD_Signal"].tolist(),
        "bb_upper": df["BB_Upper"].tolist(),
        "bb_lower": df["BB_Lower"].tolist(),
        "last_date": df.index[-1].strftime("%Y-%m-%d")
    }
    
    return jsonify(data)

@app.route("/api/realtime/<symbol>")
def get_realtime(symbol):
    """Lấy giá realtime"""
    price = get_realtime_price(symbol)
    if price:
        return jsonify(price)
    return jsonify({"error": "Không lấy được giá"}), 404

@app.route("/api/update/<symbol>")
def update_stock(symbol):
    """Cập nhật dữ liệu cổ phiếu"""
    success = update_stock_data(symbol)
    if success:
        return jsonify({"success": True, "message": f"Đã cập nhật {symbol}"})
    return jsonify({"success": False, "message": "Cập nhật thất bại"}), 500

@app.route("/api/update-all")
def update_all_stocks():
    """Cập nhật tất cả cổ phiếu"""
    data_dir = "data"
    stocks = [f.replace(".csv", "") for f in os.listdir(data_dir) if f.endswith(".csv")]
    
    updated = 0
    failed = 0
    
    for symbol in stocks:
        if update_stock_data(symbol):
            updated += 1
        else:
            failed += 1
        time.sleep(0.5)  # Delay để tránh bị block
    
    return jsonify({
        "success": True,
        "updated": updated,
        "failed": failed,
        "total": len(stocks)
    })

@app.route("/api/analyze/<symbol>")
def analyze_stock(symbol):
    """AI phân tích cổ phiếu"""
    csv_path = f"data/{symbol}.csv"
    
    if not os.path.exists(csv_path):
        return jsonify({"error": "Không tìm thấy dữ liệu"}), 404
    
    df = load_data(csv_path)
    
    # Lấy giá realtime
    realtime = get_realtime_price(symbol)
    
    result = ai_analyze(df, symbol, realtime)
    
    return jsonify(result)

@app.route("/api/screener")
def stock_screener():
    """Sàng lọc tất cả cổ phiếu"""
    data_dir = "data"
    stocks = [f.replace(".csv", "") for f in os.listdir(data_dir) if f.endswith(".csv")]
    
    results = []
    for symbol in stocks:
        try:
            df = load_data(f"data/{symbol}.csv")
            realtime = get_realtime_price(symbol)
            result = ai_analyze(df, symbol, realtime)
            if "error" not in result:
                results.append(result)
        except Exception as e:
            pass
    
    results.sort(key=lambda x: x["score"], reverse=True)
    
    return jsonify(results)

@app.route("/api/download/<symbol>")
def download_new_stock(symbol):
    """Tải dữ liệu cổ phiếu mới"""
    symbol = symbol.upper()
    success = update_stock_data(symbol)
    
    if success:
        return jsonify({"success": True, "message": f"Đã tải {symbol}"})
    return jsonify({"success": False, "message": "Không tìm thấy mã này"}), 404

@app.route("/api/auto-update/status")
def auto_update_status():
    """Trạng thái auto update"""
    return jsonify({
        "enabled": AUTO_UPDATE_ENABLED,
        "interval_minutes": UPDATE_INTERVAL_MINUTES,
        "last_update": last_auto_update.strftime("%Y-%m-%d %H:%M:%S") if last_auto_update else None
    })

@app.route("/api/auto-update/toggle")
def toggle_auto_update():
    """Bật/tắt auto update"""
    global AUTO_UPDATE_ENABLED
    AUTO_UPDATE_ENABLED = not AUTO_UPDATE_ENABLED
    return jsonify({"enabled": AUTO_UPDATE_ENABLED})

@app.route("/api/patterns/<symbol>")
def get_patterns(symbol):
    """Lấy mẫu hình kỹ thuật"""
    csv_path = f"data/{symbol}.csv"
    
    if not os.path.exists(csv_path):
        return jsonify({"error": "Không tìm thấy dữ liệu"}), 404
    
    try:
        df = load_pattern_data(csv_path)
        pr = PatternRecognition(df)
        results = pr.analyze_all()
        results["symbol"] = symbol
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    os.makedirs("templates", exist_ok=True)
    os.makedirs("static", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    
    # ============ AUTO UPDATE FUNCTIONS ============
    def is_trading_hours():
        """Kiểm tra có trong giờ giao dịch không"""
        now = datetime.now()
        if now.weekday() >= 5:  # T7, CN
            return False
        hour = now.hour
        minute = now.minute
        current_time = hour * 60 + minute
        
        # 9:00-11:30 và 13:00-15:00
        return (9*60 <= current_time <= 11*60+30) or (13*60 <= current_time <= 15*60)
    
    def auto_update_job():
        """Job tự động cập nhật"""
        global last_auto_update
        
        if not AUTO_UPDATE_ENABLED:
            return
        
        if is_trading_hours() or datetime.now().hour == 15:  # Trong giờ GD hoặc 15h
            print(f"\n[AUTO] {datetime.now().strftime('%H:%M:%S')} - Đang cập nhật...")
            
            stocks = [f.replace(".csv", "") for f in os.listdir("data") if f.endswith(".csv")]
            updated = 0
            
            for symbol in stocks[:20]:  # Giới hạn 20 mã mỗi lần
                if update_stock_data(symbol):
                    updated += 1
                time.sleep(0.3)
            
            last_auto_update = datetime.now()
            print(f"[AUTO] Đã cập nhật {updated} mã")
    
    def run_scheduler():
        """Chạy scheduler trong thread riêng"""
        schedule.every(UPDATE_INTERVAL_MINUTES).minutes.do(auto_update_job)
        schedule.every().day.at("15:30").do(auto_update_job)  # Cuối ngày
        
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    # Khởi động auto updater trong thread riêng
    if AUTO_UPDATE_ENABLED:
        updater_thread = threading.Thread(target=run_scheduler, daemon=True)
        updater_thread.start()
        print("✓ Auto Updater đã khởi động")
    
    print("\n" + "="*50)
    print("   STOCK AI WEB APPLICATION")
    print("   Truy cap: http://localhost:5000")
    print("   Auto Update: " + ("BẬT" if AUTO_UPDATE_ENABLED else "TẮT"))
    print("="*50 + "\n")
    
    app.run(debug=False, port=5000, threaded=True)
