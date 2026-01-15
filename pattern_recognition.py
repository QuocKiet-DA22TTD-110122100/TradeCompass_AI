"""
AI Pattern Recognition - Nhận diện mẫu hình biểu đồ
Bao gồm: Mẫu nến, Mẫu hình giá, Hỗ trợ/Kháng cự
"""

import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
import os

class PatternRecognition:
    """Lớp nhận diện các mẫu hình kỹ thuật"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.patterns_found = []
        
    # ============ MẪU NẾN (CANDLESTICK PATTERNS) ============
    
    def detect_candle_patterns(self) -> list:
        """Nhận diện tất cả mẫu nến"""
        patterns = []
        df = self.df
        
        # Tính các thông số nến
        df["body"] = df["Close"] - df["Open"]
        df["body_abs"] = abs(df["body"])
        df["upper_shadow"] = df["High"] - df[["Open", "Close"]].max(axis=1)
        df["lower_shadow"] = df[["Open", "Close"]].min(axis=1) - df["Low"]
        df["range"] = df["High"] - df["Low"]
        avg_body = df["body_abs"].rolling(20).mean()
        
        for i in range(2, len(df)):
            date = df.index[i].strftime("%Y-%m-%d")
            curr = df.iloc[i]
            prev = df.iloc[i-1]
            prev2 = df.iloc[i-2]
            avg = avg_body.iloc[i] if not pd.isna(avg_body.iloc[i]) else curr["body_abs"]

            # 1. DOJI - Thân nến rất nhỏ
            if curr["body_abs"] < curr["range"] * 0.1 and curr["range"] > 0:
                patterns.append({
                    "date": date, "pattern": "Doji", "type": "candle",
                    "signal": "neutral", "strength": 1,
                    "description": "Doji - Thị trường do dự, có thể đảo chiều"
                })
            
            # 2. HAMMER - Búa (tín hiệu đáy)
            if (curr["lower_shadow"] > curr["body_abs"] * 2 and 
                curr["upper_shadow"] < curr["body_abs"] * 0.5 and
                curr["body_abs"] > 0):
                patterns.append({
                    "date": date, "pattern": "Hammer", "type": "candle",
                    "signal": "bullish", "strength": 2,
                    "description": "Hammer - Tín hiệu đảo chiều tăng ở đáy"
                })
            
            # 3. INVERTED HAMMER - Búa ngược
            if (curr["upper_shadow"] > curr["body_abs"] * 2 and
                curr["lower_shadow"] < curr["body_abs"] * 0.5 and
                curr["body_abs"] > 0):
                patterns.append({
                    "date": date, "pattern": "Inverted Hammer", "type": "candle",
                    "signal": "bullish", "strength": 2,
                    "description": "Inverted Hammer - Có thể đảo chiều tăng"
                })
            
            # 4. SHOOTING STAR - Sao băng (tín hiệu đỉnh)
            if (curr["upper_shadow"] > curr["body_abs"] * 2 and
                curr["lower_shadow"] < curr["body_abs"] * 0.3 and
                curr["body"] < 0):
                patterns.append({
                    "date": date, "pattern": "Shooting Star", "type": "candle",
                    "signal": "bearish", "strength": 2,
                    "description": "Shooting Star - Tín hiệu đảo chiều giảm ở đỉnh"
                })
            
            # 5. BULLISH ENGULFING - Nến tăng nuốt
            if (curr["body"] > 0 and prev["body"] < 0 and
                curr["Open"] < prev["Close"] and curr["Close"] > prev["Open"]):
                patterns.append({
                    "date": date, "pattern": "Bullish Engulfing", "type": "candle",
                    "signal": "bullish", "strength": 3,
                    "description": "Bullish Engulfing - Tín hiệu đảo chiều tăng mạnh"
                })

            # 6. BEARISH ENGULFING - Nến giảm nuốt
            if (curr["body"] < 0 and prev["body"] > 0 and
                curr["Open"] > prev["Close"] and curr["Close"] < prev["Open"]):
                patterns.append({
                    "date": date, "pattern": "Bearish Engulfing", "type": "candle",
                    "signal": "bearish", "strength": 3,
                    "description": "Bearish Engulfing - Tín hiệu đảo chiều giảm mạnh"
                })
            
            # 7. MORNING STAR - Sao mai (3 nến)
            if (prev2["body"] < 0 and abs(prev2["body"]) > avg and
                prev["body_abs"] < avg * 0.5 and
                curr["body"] > 0 and
                curr["Close"] > (prev2["Open"] + prev2["Close"]) / 2):
                patterns.append({
                    "date": date, "pattern": "Morning Star", "type": "candle",
                    "signal": "bullish", "strength": 4,
                    "description": "Morning Star - Tín hiệu đảo chiều tăng rất mạnh"
                })
            
            # 8. EVENING STAR - Sao hôm (3 nến)
            if (prev2["body"] > 0 and prev2["body"] > avg and
                prev["body_abs"] < avg * 0.5 and
                curr["body"] < 0 and
                curr["Close"] < (prev2["Open"] + prev2["Close"]) / 2):
                patterns.append({
                    "date": date, "pattern": "Evening Star", "type": "candle",
                    "signal": "bearish", "strength": 4,
                    "description": "Evening Star - Tín hiệu đảo chiều giảm rất mạnh"
                })
            
            # 9. THREE WHITE SOLDIERS - 3 lính trắng
            if (i >= 3 and
                df.iloc[i-2]["body"] > 0 and df.iloc[i-1]["body"] > 0 and curr["body"] > 0 and
                df.iloc[i-1]["Close"] > df.iloc[i-2]["Close"] and
                curr["Close"] > df.iloc[i-1]["Close"]):
                patterns.append({
                    "date": date, "pattern": "Three White Soldiers", "type": "candle",
                    "signal": "bullish", "strength": 4,
                    "description": "Three White Soldiers - Xu hướng tăng mạnh"
                })
            
            # 10. THREE BLACK CROWS - 3 con quạ đen
            if (i >= 3 and
                df.iloc[i-2]["body"] < 0 and df.iloc[i-1]["body"] < 0 and curr["body"] < 0 and
                df.iloc[i-1]["Close"] < df.iloc[i-2]["Close"] and
                curr["Close"] < df.iloc[i-1]["Close"]):
                patterns.append({
                    "date": date, "pattern": "Three Black Crows", "type": "candle",
                    "signal": "bearish", "strength": 4,
                    "description": "Three Black Crows - Xu hướng giảm mạnh"
                })
        
        return patterns

    # ============ MẪU HÌNH GIÁ (CHART PATTERNS) ============
    
    def find_peaks_troughs(self, order=5):
        """Tìm đỉnh và đáy"""
        close = self.df["Close"].values
        
        # Tìm đỉnh (local maxima)
        peaks_idx = argrelextrema(close, np.greater, order=order)[0]
        
        # Tìm đáy (local minima)
        troughs_idx = argrelextrema(close, np.less, order=order)[0]
        
        return peaks_idx, troughs_idx
    
    def detect_double_top(self, tolerance=0.03) -> list:
        """Nhận diện Double Top - Hai đỉnh"""
        patterns = []
        peaks_idx, _ = self.find_peaks_troughs()
        close = self.df["Close"].values
        
        for i in range(len(peaks_idx) - 1):
            idx1, idx2 = peaks_idx[i], peaks_idx[i+1]
            
            # Khoảng cách giữa 2 đỉnh: 10-50 nến
            if not (10 <= idx2 - idx1 <= 50):
                continue
            
            peak1, peak2 = close[idx1], close[idx2]
            
            # 2 đỉnh gần bằng nhau (trong tolerance)
            if abs(peak1 - peak2) / peak1 <= tolerance:
                # Tìm đáy giữa 2 đỉnh
                valley = close[idx1:idx2].min()
                
                # Đáy phải thấp hơn đỉnh ít nhất 3%
                if (peak1 - valley) / peak1 >= 0.03:
                    date = self.df.index[idx2].strftime("%Y-%m-%d")
                    patterns.append({
                        "date": date, "pattern": "Double Top", "type": "chart",
                        "signal": "bearish", "strength": 4,
                        "description": f"Double Top - Hai đỉnh tại {peak1:.0f} và {peak2:.0f}, tín hiệu đảo chiều giảm",
                        "price_levels": {"peak1": peak1, "peak2": peak2, "neckline": valley}
                    })
        
        return patterns
    
    def detect_double_bottom(self, tolerance=0.03) -> list:
        """Nhận diện Double Bottom - Hai đáy"""
        patterns = []
        _, troughs_idx = self.find_peaks_troughs()
        close = self.df["Close"].values
        
        for i in range(len(troughs_idx) - 1):
            idx1, idx2 = troughs_idx[i], troughs_idx[i+1]
            
            if not (10 <= idx2 - idx1 <= 50):
                continue
            
            trough1, trough2 = close[idx1], close[idx2]
            
            if abs(trough1 - trough2) / trough1 <= tolerance:
                peak = close[idx1:idx2].max()
                
                if (peak - trough1) / trough1 >= 0.03:
                    date = self.df.index[idx2].strftime("%Y-%m-%d")
                    patterns.append({
                        "date": date, "pattern": "Double Bottom", "type": "chart",
                        "signal": "bullish", "strength": 4,
                        "description": f"Double Bottom - Hai đáy tại {trough1:.0f} và {trough2:.0f}, tín hiệu đảo chiều tăng",
                        "price_levels": {"trough1": trough1, "trough2": trough2, "neckline": peak}
                    })
        
        return patterns

    def detect_head_shoulders(self, tolerance=0.03) -> list:
        """Nhận diện Head and Shoulders - Đầu và vai"""
        patterns = []
        peaks_idx, troughs_idx = self.find_peaks_troughs()
        close = self.df["Close"].values
        
        # Cần ít nhất 3 đỉnh
        if len(peaks_idx) < 3:
            return patterns
        
        for i in range(len(peaks_idx) - 2):
            left_shoulder_idx = peaks_idx[i]
            head_idx = peaks_idx[i+1]
            right_shoulder_idx = peaks_idx[i+2]
            
            left_shoulder = close[left_shoulder_idx]
            head = close[head_idx]
            right_shoulder = close[right_shoulder_idx]
            
            # Head phải cao hơn cả 2 vai
            if head <= left_shoulder or head <= right_shoulder:
                continue
            
            # 2 vai gần bằng nhau
            if abs(left_shoulder - right_shoulder) / left_shoulder > tolerance:
                continue
            
            # Head cao hơn vai ít nhất 3%
            if (head - left_shoulder) / left_shoulder < 0.03:
                continue
            
            date = self.df.index[right_shoulder_idx].strftime("%Y-%m-%d")
            neckline = min(close[left_shoulder_idx:right_shoulder_idx])
            
            patterns.append({
                "date": date, "pattern": "Head and Shoulders", "type": "chart",
                "signal": "bearish", "strength": 5,
                "description": f"Head & Shoulders - Đầu tại {head:.0f}, vai tại {left_shoulder:.0f}/{right_shoulder:.0f}",
                "price_levels": {"head": head, "left_shoulder": left_shoulder, 
                                "right_shoulder": right_shoulder, "neckline": neckline}
            })
        
        return patterns
    
    def detect_inverse_head_shoulders(self, tolerance=0.03) -> list:
        """Nhận diện Inverse Head and Shoulders"""
        patterns = []
        _, troughs_idx = self.find_peaks_troughs()
        close = self.df["Close"].values
        
        if len(troughs_idx) < 3:
            return patterns
        
        for i in range(len(troughs_idx) - 2):
            left_idx = troughs_idx[i]
            head_idx = troughs_idx[i+1]
            right_idx = troughs_idx[i+2]
            
            left = close[left_idx]
            head = close[head_idx]
            right = close[right_idx]
            
            # Head phải thấp hơn cả 2 vai
            if head >= left or head >= right:
                continue
            
            if abs(left - right) / left > tolerance:
                continue
            
            if (left - head) / head < 0.03:
                continue
            
            date = self.df.index[right_idx].strftime("%Y-%m-%d")
            neckline = max(close[left_idx:right_idx])
            
            patterns.append({
                "date": date, "pattern": "Inverse Head and Shoulders", "type": "chart",
                "signal": "bullish", "strength": 5,
                "description": f"Inverse H&S - Tín hiệu đảo chiều tăng mạnh",
                "price_levels": {"head": head, "left_shoulder": left, 
                                "right_shoulder": right, "neckline": neckline}
            })
        
        return patterns

    def detect_triangle(self, window=30) -> list:
        """Nhận diện các mẫu tam giác"""
        patterns = []
        df = self.df.tail(window)
        
        if len(df) < window:
            return patterns
        
        highs = df["High"].values
        lows = df["Low"].values
        
        # Tính xu hướng của đỉnh và đáy
        x = np.arange(len(highs))
        
        # Linear regression cho highs
        high_slope = np.polyfit(x, highs, 1)[0]
        
        # Linear regression cho lows
        low_slope = np.polyfit(x, lows, 1)[0]
        
        date = df.index[-1].strftime("%Y-%m-%d")
        
        # Ascending Triangle - Đỉnh ngang, đáy tăng
        if abs(high_slope) < 0.1 and low_slope > 0.1:
            patterns.append({
                "date": date, "pattern": "Ascending Triangle", "type": "chart",
                "signal": "bullish", "strength": 3,
                "description": "Ascending Triangle - Tam giác tăng, thường breakout lên"
            })
        
        # Descending Triangle - Đỉnh giảm, đáy ngang
        elif high_slope < -0.1 and abs(low_slope) < 0.1:
            patterns.append({
                "date": date, "pattern": "Descending Triangle", "type": "chart",
                "signal": "bearish", "strength": 3,
                "description": "Descending Triangle - Tam giác giảm, thường breakout xuống"
            })
        
        # Symmetrical Triangle - Đỉnh giảm, đáy tăng
        elif high_slope < -0.05 and low_slope > 0.05:
            patterns.append({
                "date": date, "pattern": "Symmetrical Triangle", "type": "chart",
                "signal": "neutral", "strength": 2,
                "description": "Symmetrical Triangle - Tam giác cân, chờ breakout"
            })
        
        return patterns
    
    def detect_support_resistance(self, window=60, num_levels=3) -> dict:
        """Tìm các mức hỗ trợ và kháng cự"""
        df = self.df.tail(window)
        
        peaks_idx, troughs_idx = self.find_peaks_troughs(order=3)
        close = df["Close"].values
        
        # Lấy giá tại các đỉnh và đáy
        peak_prices = close[peaks_idx] if len(peaks_idx) > 0 else []
        trough_prices = close[troughs_idx] if len(troughs_idx) > 0 else []
        
        # Cluster các mức giá gần nhau
        def cluster_levels(prices, tolerance=0.02):
            if len(prices) == 0:
                return []
            
            prices = sorted(prices)
            clusters = [[prices[0]]]
            
            for price in prices[1:]:
                if abs(price - clusters[-1][-1]) / clusters[-1][-1] <= tolerance:
                    clusters[-1].append(price)
                else:
                    clusters.append([price])
            
            # Trả về trung bình của mỗi cluster
            return [np.mean(c) for c in clusters]
        
        resistance_levels = cluster_levels(list(peak_prices))[-num_levels:]
        support_levels = cluster_levels(list(trough_prices))[:num_levels]
        
        current_price = df["Close"].iloc[-1]
        
        return {
            "current_price": current_price,
            "resistance": sorted(resistance_levels, reverse=True),
            "support": sorted(support_levels, reverse=True),
            "nearest_resistance": min([r for r in resistance_levels if r > current_price], default=None),
            "nearest_support": max([s for s in support_levels if s < current_price], default=None)
        }

    def detect_trend_channel(self, window=30) -> dict:
        """Nhận diện kênh xu hướng"""
        df = self.df.tail(window)
        
        highs = df["High"].values
        lows = df["Low"].values
        x = np.arange(len(highs))
        
        # Linear regression
        high_coef = np.polyfit(x, highs, 1)
        low_coef = np.polyfit(x, lows, 1)
        
        high_slope = high_coef[0]
        low_slope = low_coef[0]
        
        # Xác định loại kênh
        avg_slope = (high_slope + low_slope) / 2
        
        if avg_slope > 0.5:
            channel_type = "Uptrend Channel"
            signal = "bullish"
        elif avg_slope < -0.5:
            channel_type = "Downtrend Channel"
            signal = "bearish"
        else:
            channel_type = "Sideways Channel"
            signal = "neutral"
        
        # Tính đường kênh
        upper_line = high_coef[0] * x + high_coef[1]
        lower_line = low_coef[0] * x + low_coef[1]
        
        current_price = df["Close"].iloc[-1]
        channel_width = (upper_line[-1] - lower_line[-1]) / lower_line[-1] * 100
        
        # Vị trí trong kênh
        position = (current_price - lower_line[-1]) / (upper_line[-1] - lower_line[-1])
        
        return {
            "type": channel_type,
            "signal": signal,
            "upper_bound": upper_line[-1],
            "lower_bound": lower_line[-1],
            "channel_width_pct": channel_width,
            "position_in_channel": position,  # 0 = đáy kênh, 1 = đỉnh kênh
            "slope": avg_slope
        }
    
    def analyze_all(self) -> dict:
        """Phân tích tất cả mẫu hình"""
        results = {
            "candle_patterns": [],
            "chart_patterns": [],
            "support_resistance": {},
            "trend_channel": {},
            "summary": {}
        }
        
        # Mẫu nến (chỉ lấy 10 ngày gần nhất)
        candle_patterns = self.detect_candle_patterns()
        results["candle_patterns"] = candle_patterns[-10:] if candle_patterns else []
        
        # Mẫu hình giá
        chart_patterns = []
        chart_patterns.extend(self.detect_double_top())
        chart_patterns.extend(self.detect_double_bottom())
        chart_patterns.extend(self.detect_head_shoulders())
        chart_patterns.extend(self.detect_inverse_head_shoulders())
        chart_patterns.extend(self.detect_triangle())
        results["chart_patterns"] = chart_patterns
        
        # Hỗ trợ/Kháng cự
        results["support_resistance"] = self.detect_support_resistance()
        
        # Kênh xu hướng
        results["trend_channel"] = self.detect_trend_channel()
        
        # Tổng hợp
        bullish_signals = sum(1 for p in candle_patterns[-5:] if p["signal"] == "bullish")
        bearish_signals = sum(1 for p in candle_patterns[-5:] if p["signal"] == "bearish")
        
        for p in chart_patterns:
            if p["signal"] == "bullish":
                bullish_signals += p["strength"]
            elif p["signal"] == "bearish":
                bearish_signals += p["strength"]
        
        if bullish_signals > bearish_signals + 2:
            overall = "BULLISH"
        elif bearish_signals > bullish_signals + 2:
            overall = "BEARISH"
        else:
            overall = "NEUTRAL"
        
        results["summary"] = {
            "overall_signal": overall,
            "bullish_score": bullish_signals,
            "bearish_score": bearish_signals,
            "total_patterns": len(candle_patterns[-10:]) + len(chart_patterns)
        }
        
        return results


# ============ HELPER FUNCTIONS ============

def load_data(csv_path: str) -> pd.DataFrame:
    """Đọc CSV"""
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

def analyze_patterns(symbol: str) -> dict:
    """Phân tích mẫu hình cho 1 mã"""
    csv_path = f"data/{symbol}.csv"
    
    if not os.path.exists(csv_path):
        return {"error": f"Không tìm thấy {symbol}"}
    
    df = load_data(csv_path)
    
    if len(df) < 50:
        return {"error": "Không đủ dữ liệu"}
    
    pr = PatternRecognition(df)
    results = pr.analyze_all()
    results["symbol"] = symbol
    
    return results

def print_analysis(results: dict):
    """In kết quả phân tích"""
    if "error" in results:
        print(f"Lỗi: {results['error']}")
        return
    
    print(f"\n{'='*60}")
    print(f"   PHÂN TÍCH MẪU HÌNH: {results['symbol']}")
    print(f"{'='*60}")
    
    # Mẫu nến
    print(f"\n--- MẪU NẾN (10 ngày gần nhất) ---")
    if results["candle_patterns"]:
        for p in results["candle_patterns"]:
            emoji = "🟢" if p["signal"] == "bullish" else ("🔴" if p["signal"] == "bearish" else "⚪")
            print(f"  {emoji} {p['date']}: {p['pattern']}")
            print(f"     {p['description']}")
    else:
        print("  Không phát hiện mẫu nến đặc biệt")
    
    # Mẫu hình giá
    print(f"\n--- MẪU HÌNH GIÁ ---")
    if results["chart_patterns"]:
        for p in results["chart_patterns"]:
            emoji = "🟢" if p["signal"] == "bullish" else ("🔴" if p["signal"] == "bearish" else "⚪")
            print(f"  {emoji} {p['pattern']} ({p['date']})")
            print(f"     {p['description']}")
    else:
        print("  Không phát hiện mẫu hình đặc biệt")
    
    # Hỗ trợ/Kháng cự
    sr = results["support_resistance"]
    print(f"\n--- HỖ TRỢ / KHÁNG CỰ ---")
    print(f"  Giá hiện tại: {sr['current_price']:,.0f}")
    print(f"  Kháng cự gần nhất: {sr['nearest_resistance']:,.0f}" if sr['nearest_resistance'] else "  Kháng cự: N/A")
    print(f"  Hỗ trợ gần nhất: {sr['nearest_support']:,.0f}" if sr['nearest_support'] else "  Hỗ trợ: N/A")
    
    # Kênh xu hướng
    tc = results["trend_channel"]
    print(f"\n--- KÊNH XU HƯỚNG ---")
    print(f"  Loại: {tc['type']}")
    print(f"  Biên trên: {tc['upper_bound']:,.0f}")
    print(f"  Biên dưới: {tc['lower_bound']:,.0f}")
    print(f"  Vị trí trong kênh: {tc['position_in_channel']*100:.0f}%")
    
    # Tổng kết
    summary = results["summary"]
    print(f"\n--- TỔNG KẾT ---")
    print(f"  Tín hiệu tổng hợp: {summary['overall_signal']}")
    print(f"  Điểm Bullish: {summary['bullish_score']}")
    print(f"  Điểm Bearish: {summary['bearish_score']}")

if __name__ == "__main__":
    data_dir = "data"
    csv_files = [f.replace(".csv", "") for f in os.listdir(data_dir) if f.endswith(".csv")]
    
    print("Các mã cổ phiếu đã tải:")
    print(", ".join(csv_files))
    
    symbol = input("\nNhập mã muốn phân tích (VD: FPT): ").strip().upper()
    
    results = analyze_patterns(symbol)
    print_analysis(results)
