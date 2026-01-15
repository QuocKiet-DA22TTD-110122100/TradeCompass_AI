"""
Phân tích nâng cao với nhiều chỉ báo kỹ thuật và dự đoán xác suất
Sử dụng: python advanced_analysis.py
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import warnings
import os

warnings.filterwarnings('ignore')

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

def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Thêm nhiều chỉ báo kỹ thuật"""
    df = df.copy()
    
    # === MOVING AVERAGES ===
    df["SMA_5"] = df["Close"].rolling(5).mean()
    df["SMA_10"] = df["Close"].rolling(10).mean()
    df["SMA_20"] = df["Close"].rolling(20).mean()
    df["SMA_50"] = df["Close"].rolling(50).mean()
    df["SMA_200"] = df["Close"].rolling(200).mean()
    
    # EMA
    df["EMA_12"] = df["Close"].ewm(span=12).mean()
    df["EMA_26"] = df["Close"].ewm(span=26).mean()
    
    # === MACD ===
    df["MACD"] = df["EMA_12"] - df["EMA_26"]
    df["MACD_Signal"] = df["MACD"].ewm(span=9).mean()
    df["MACD_Hist"] = df["MACD"] - df["MACD_Signal"]
    
    # === RSI ===
    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))
    
    # === Stochastic Oscillator ===
    low_14 = df["Low"].rolling(14).min()
    high_14 = df["High"].rolling(14).max()
    df["Stoch_K"] = 100 * (df["Close"] - low_14) / (high_14 - low_14)
    df["Stoch_D"] = df["Stoch_K"].rolling(3).mean()
    
    # === Bollinger Bands ===
    df["BB_Middle"] = df["Close"].rolling(20).mean()
    bb_std = df["Close"].rolling(20).std()
    df["BB_Upper"] = df["BB_Middle"] + 2 * bb_std
    df["BB_Lower"] = df["BB_Middle"] - 2 * bb_std
    df["BB_Width"] = (df["BB_Upper"] - df["BB_Lower"]) / df["BB_Middle"]
    df["BB_Position"] = (df["Close"] - df["BB_Lower"]) / (df["BB_Upper"] - df["BB_Lower"])
    
    # === ATR (Average True Range) ===
    high_low = df["High"] - df["Low"]
    high_close = abs(df["High"] - df["Close"].shift())
    low_close = abs(df["Low"] - df["Close"].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df["ATR"] = tr.rolling(14).mean()
    
    # === ADX (Average Directional Index) ===
    plus_dm = df["High"].diff()
    minus_dm = -df["Low"].diff()
    plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0)
    minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0)
    
    atr_14 = tr.rolling(14).mean()
    plus_di = 100 * (plus_dm.rolling(14).mean() / atr_14)
    minus_di = 100 * (minus_dm.rolling(14).mean() / atr_14)
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
    df["ADX"] = dx.rolling(14).mean()
    df["Plus_DI"] = plus_di
    df["Minus_DI"] = minus_di
    
    # === OBV (On Balance Volume) ===
    obv = [0]
    for i in range(1, len(df)):
        if df["Close"].iloc[i] > df["Close"].iloc[i-1]:
            obv.append(obv[-1] + df["Volume"].iloc[i])
        elif df["Close"].iloc[i] < df["Close"].iloc[i-1]:
            obv.append(obv[-1] - df["Volume"].iloc[i])
        else:
            obv.append(obv[-1])
    df["OBV"] = obv
    df["OBV_SMA"] = df["OBV"].rolling(20).mean()
    
    # === Volume indicators ===
    df["Volume_SMA"] = df["Volume"].rolling(20).mean()
    df["Volume_Ratio"] = df["Volume"] / df["Volume_SMA"]
    
    # === Price features ===
    df["Returns"] = df["Close"].pct_change()
    df["Returns_5d"] = df["Close"].pct_change(5)
    df["Returns_10d"] = df["Close"].pct_change(10)
    df["Volatility"] = df["Returns"].rolling(20).std()
    
    # === Trend features ===
    df["Price_vs_SMA20"] = (df["Close"] - df["SMA_20"]) / df["SMA_20"]
    df["Price_vs_SMA50"] = (df["Close"] - df["SMA_50"]) / df["SMA_50"]
    df["SMA20_vs_SMA50"] = (df["SMA_20"] - df["SMA_50"]) / df["SMA_50"]
    
    return df

def create_labels(df: pd.DataFrame, forward_days: int = 5, threshold: float = 0.02) -> pd.DataFrame:
    """Tạo nhãn dự đoán: 1 = tăng > threshold, 0 = giảm/đi ngang"""
    df = df.copy()
    
    # Tính % thay đổi trong forward_days ngày tới
    df["Future_Return"] = df["Close"].shift(-forward_days) / df["Close"] - 1
    
    # Nhãn: 1 nếu tăng > threshold, 0 nếu không
    df["Target"] = (df["Future_Return"] > threshold).astype(int)
    
    return df

def prepare_features(df: pd.DataFrame) -> tuple:
    """Chuẩn bị features cho model"""
    feature_cols = [
        "RSI", "MACD", "MACD_Hist", "Stoch_K", "Stoch_D",
        "BB_Position", "BB_Width", "ATR", "ADX", "Plus_DI", "Minus_DI",
        "Volume_Ratio", "Returns", "Returns_5d", "Volatility",
        "Price_vs_SMA20", "Price_vs_SMA50", "SMA20_vs_SMA50"
    ]
    
    # Lọc các cột có sẵn
    available_cols = [c for c in feature_cols if c in df.columns]
    
    # Bỏ các dòng có NaN
    df_clean = df.dropna(subset=available_cols + ["Target"])
    
    X = df_clean[available_cols]
    y = df_clean["Target"]
    
    return X, y, available_cols

def train_model(X: pd.DataFrame, y: pd.Series) -> tuple:
    """Train Random Forest model"""
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False  # Không shuffle để giữ thứ tự thời gian
    )
    
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=10,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Đánh giá
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    return model, accuracy, X_test, y_test, y_pred

def predict_probability(model, df: pd.DataFrame, feature_cols: list) -> dict:
    """Dự đoán xác suất cho ngày gần nhất"""
    # Lấy dòng cuối cùng có đủ features
    df_recent = df.dropna(subset=feature_cols).tail(1)
    
    if len(df_recent) == 0:
        return None
    
    X_latest = df_recent[feature_cols]
    
    # Dự đoán xác suất
    prob = model.predict_proba(X_latest)[0]
    prediction = model.predict(X_latest)[0]
    
    return {
        "date": df_recent.index[0].strftime("%Y-%m-%d"),
        "prediction": "TANG" if prediction == 1 else "GIAM/DI NGANG",
        "prob_up": prob[1] * 100,
        "prob_down": prob[0] * 100
    }

def get_feature_importance(model, feature_cols: list) -> pd.DataFrame:
    """Lấy độ quan trọng của các features"""
    importance = pd.DataFrame({
        "Feature": feature_cols,
        "Importance": model.feature_importances_
    }).sort_values("Importance", ascending=False)
    
    return importance

def analyze_stock_advanced(symbol: str, forward_days: int = 5, threshold: float = 0.02):
    """Phân tích nâng cao cho 1 mã cổ phiếu"""
    csv_path = f"data/{symbol}.csv"
    
    if not os.path.exists(csv_path):
        print(f"Khong tim thay file {csv_path}")
        return
    
    print(f"\n{'='*60}")
    print(f"   PHAN TICH NANG CAO: {symbol}")
    print(f"   Du doan: Tang > {threshold*100:.0f}% trong {forward_days} ngay toi")
    print(f"{'='*60}")
    
    # Load và xử lý dữ liệu
    df = load_data(csv_path)
    df = add_technical_indicators(df)
    df = create_labels(df, forward_days, threshold)
    
    # Chuẩn bị features
    X, y, feature_cols = prepare_features(df)
    
    if len(X) < 100:
        print("Khong du du lieu de train model (can it nhat 100 dong)")
        return
    
    # Train model
    print("\nDang train model...")
    model, accuracy, X_test, y_test, y_pred = train_model(X, y)
    
    print(f"\n--- KET QUA MODEL ---")
    print(f"Do chinh xac (Accuracy): {accuracy*100:.1f}%")
    print(f"So mau train: {len(X) - len(X_test)}")
    print(f"So mau test: {len(X_test)}")
    
    # Thống kê chi tiết
    print(f"\nChi tiet:")
    print(f"  - Ty le du doan TANG dung: {(y_pred[y_test==1]==1).sum()}/{(y_test==1).sum()} = {(y_pred[y_test==1]==1).mean()*100:.1f}%")
    print(f"  - Ty le du doan GIAM dung: {(y_pred[y_test==0]==0).sum()}/{(y_test==0).sum()} = {(y_pred[y_test==0]==0).mean()*100:.1f}%")
    
    # Feature importance
    importance = get_feature_importance(model, feature_cols)
    print(f"\n--- CHI BAO QUAN TRONG NHAT ---")
    for _, row in importance.head(10).iterrows():
        print(f"  {row['Feature']}: {row['Importance']*100:.1f}%")
    
    # Dự đoán cho ngày hiện tại
    prediction = predict_probability(model, df, feature_cols)
    
    if prediction:
        print(f"\n--- DU DOAN CHO NGAY {prediction['date']} ---")
        print(f"  Ket qua: {prediction['prediction']}")
        print(f"  Xac suat TANG > {threshold*100:.0f}%: {prediction['prob_up']:.1f}%")
        print(f"  Xac suat GIAM/DI NGANG: {prediction['prob_down']:.1f}%")
        
        # Khuyến nghị
        if prediction['prob_up'] >= 70:
            print(f"\n  >>> KHUYEN NGHI: CO THE MUA (xac suat cao) <<<")
        elif prediction['prob_up'] >= 55:
            print(f"\n  >>> KHUYEN NGHI: THEO DOI (xac suat trung binh) <<<")
        else:
            print(f"\n  >>> KHUYEN NGHI: CHO DOI (xac suat thap) <<<")
    
    # Hiển thị các chỉ báo hiện tại
    latest = df.dropna().iloc[-1]
    print(f"\n--- CHI BAO HIEN TAI ---")
    print(f"  Gia: {latest['Close']:,.0f}")
    print(f"  RSI(14): {latest['RSI']:.1f}")
    print(f"  MACD: {latest['MACD']:.2f} | Signal: {latest['MACD_Signal']:.2f}")
    print(f"  Stochastic: K={latest['Stoch_K']:.1f}, D={latest['Stoch_D']:.1f}")
    print(f"  ADX: {latest['ADX']:.1f} (xu huong {'manh' if latest['ADX'] > 25 else 'yeu'})")
    print(f"  BB Position: {latest['BB_Position']*100:.0f}% (0=duoi, 100=tren)")
    print(f"  Volume Ratio: {latest['Volume_Ratio']:.2f}x")
    
    return model, df

if __name__ == "__main__":
    data_dir = "data"
    csv_files = [f.replace(".csv", "") for f in os.listdir(data_dir) if f.endswith(".csv")]
    
    print("Cac ma co phieu da tai:")
    print(", ".join(csv_files))
    
    symbol = input("\nNhap ma muon phan tich (VD: FPT): ").strip().upper()
    
    print("\nCau hinh du doan:")
    days = input("So ngay du doan (mac dinh 5): ").strip()
    days = int(days) if days.isdigit() else 5
    
    thresh = input("Nguong tang % (mac dinh 2): ").strip()
    thresh = float(thresh)/100 if thresh else 0.02
    
    analyze_stock_advanced(symbol, forward_days=days, threshold=thresh)
