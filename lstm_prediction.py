"""
Phần 2: Dự đoán giá bằng Machine Learning
Sử dụng: python lstm_prediction.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
import os

warnings.filterwarnings('ignore')

# Kiểm tra thư viện ML
try:
    from sklearn.preprocessing import MinMaxScaler
    from sklearn.metrics import mean_squared_error, mean_absolute_error
    from sklearn.linear_model import LinearRegression
    from sklearn.ensemble import RandomForestRegressor
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    print("Chua cai scikit-learn. Chay: pip install scikit-learn")

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

def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Thêm các features cho model"""
    df = df.copy()
    
    # MA
    df["MA_5"] = df["Close"].rolling(5).mean()
    df["MA_10"] = df["Close"].rolling(10).mean()
    df["MA_20"] = df["Close"].rolling(20).mean()
    
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
    
    # Volatility
    df["Volatility"] = df["Close"].rolling(20).std()
    
    # Returns
    df["Returns"] = df["Close"].pct_change()
    df["Returns_5"] = df["Close"].pct_change(5)
    
    # Price position
    df["Price_vs_MA20"] = (df["Close"] - df["MA_20"]) / df["MA_20"]
    
    return df.dropna()

def prepare_data(df: pd.DataFrame, look_back: int = 20):
    """Chuẩn bị dữ liệu cho model"""
    feature_cols = ["MA_5", "MA_10", "MA_20", "RSI", "MACD", "Volatility", "Returns", "Returns_5", "Price_vs_MA20"]
    
    # Lọc các cột có sẵn
    available_cols = [c for c in feature_cols if c in df.columns]
    
    X = df[available_cols].values
    y = df["Close"].values
    
    # Chuẩn hóa
    scaler_X = MinMaxScaler()
    scaler_y = MinMaxScaler()
    
    X_scaled = scaler_X.fit_transform(X)
    y_scaled = scaler_y.fit_transform(y.reshape(-1, 1)).flatten()
    
    # Chia train/test
    train_size = int(len(X) * 0.8)
    X_train, X_test = X_scaled[:train_size], X_scaled[train_size:]
    y_train, y_test = y_scaled[:train_size], y_scaled[train_size:]
    
    return X_train, X_test, y_train, y_test, scaler_y, available_cols

def train_and_predict(X_train, X_test, y_train, y_test, scaler_y, model_type="rf"):
    """Train model và dự đoán"""
    
    if model_type == "rf":
        print("Su dung Random Forest Regressor...")
        model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    else:
        print("Su dung Linear Regression...")
        model = LinearRegression()
    
    # Train
    model.fit(X_train, y_train)
    
    # Predict
    y_pred_scaled = model.predict(X_test)
    
    # Inverse transform
    y_test_inv = scaler_y.inverse_transform(y_test.reshape(-1, 1)).flatten()
    y_pred_inv = scaler_y.inverse_transform(y_pred_scaled.reshape(-1, 1)).flatten()
    
    return model, y_test_inv, y_pred_inv

def run_prediction(symbol: str):
    """Chạy dự đoán"""
    csv_path = f"data/{symbol}.csv"
    
    if not os.path.exists(csv_path):
        print(f"Khong tim thay file {csv_path}")
        return
    
    print(f"\n{'='*60}")
    print(f"   DU DOAN GIA: {symbol}")
    print(f"{'='*60}")
    
    # Load và xử lý dữ liệu
    df = load_data(csv_path)
    print(f"So ngay du lieu: {len(df)}")
    
    if len(df) < 100:
        print("Khong du du lieu (can it nhat 100 ngay)")
        return
    
    # Thêm features
    df = add_features(df)
    print(f"So ngay sau xu ly: {len(df)}")
    
    # Chuẩn bị dữ liệu
    X_train, X_test, y_train, y_test, scaler_y, feature_cols = prepare_data(df)
    
    print(f"Train samples: {len(X_train)}")
    print(f"Test samples: {len(X_test)}")
    print(f"Features: {', '.join(feature_cols)}")
    
    # Train và dự đoán
    print(f"\nDang train model...")
    model, y_test_inv, y_pred_inv = train_and_predict(X_train, X_test, y_train, y_test, scaler_y, "rf")
    
    # Đánh giá
    rmse = np.sqrt(mean_squared_error(y_test_inv, y_pred_inv))
    mae = mean_absolute_error(y_test_inv, y_pred_inv)
    mape = np.mean(np.abs((y_test_inv - y_pred_inv) / y_test_inv)) * 100
    
    print(f"\n--- KET QUA ---")
    print(f"RMSE: {rmse:,.0f}")
    print(f"MAE: {mae:,.0f}")
    print(f"MAPE: {mape:.2f}%")
    print(f"Do chinh xac: {100 - mape:.1f}%")
    
    # Dự đoán xu hướng
    current_price = df["Close"].iloc[-1]
    predicted_price = y_pred_inv[-1]
    change_pct = (predicted_price - y_test_inv[-2]) / y_test_inv[-2] * 100 if len(y_test_inv) > 1 else 0
    
    print(f"\n--- DU DOAN ---")
    print(f"Gia hien tai: {current_price:,.0f}")
    print(f"Gia du doan gan nhat: {predicted_price:,.0f}")
    print(f"Xu huong: {change_pct:+.2f}%")
    
    # Dự đoán ngày tiếp theo
    last_features = df[feature_cols].iloc[-1:].values
    scaler_X = MinMaxScaler()
    scaler_X.fit(df[feature_cols].values)
    last_scaled = scaler_X.transform(last_features)
    next_pred_scaled = model.predict(last_scaled)
    next_price = scaler_y.inverse_transform(next_pred_scaled.reshape(-1, 1))[0, 0]
    
    next_change = (next_price - current_price) / current_price * 100
    
    print(f"\nDu doan ngay tiep theo: {next_price:,.0f} ({next_change:+.2f}%)")
    
    if next_change > 1:
        print(f"\n>>> KHUYEN NGHI: XEM XET MUA <<<")
    elif next_change < -1:
        print(f"\n>>> KHUYEN NGHI: CAN THAN <<<")
    else:
        print(f"\n>>> KHUYEN NGHI: GIU/THEO DOI <<<")
    
    # Vẽ biểu đồ
    plt.figure(figsize=(14, 6))
    plt.plot(y_test_inv, label='Gia thuc', color='blue')
    plt.plot(y_pred_inv, label='Du doan', color='red', alpha=0.7)
    plt.title(f'{symbol} - Gia thuc vs Du doan (Random Forest)')
    plt.xlabel('Ngay')
    plt.ylabel('Gia')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    if not HAS_SKLEARN:
        print("\n!!! Can cai scikit-learn !!!")
        print("Chay: pip install scikit-learn")
        exit()
    
    data_dir = "data"
    csv_files = [f.replace(".csv", "") for f in os.listdir(data_dir) if f.endswith(".csv")]
    
    print("Cac ma co phieu da tai:")
    print(", ".join(csv_files))
    
    symbol = input("\nNhap ma muon du doan (VD: FPT): ").strip().upper()
    
    run_prediction(symbol)
