"""
PHAN TICH TONG HOP - Ket hop tat ca cac phuong phap
Su dung: python full_analysis.py
"""

import os
from datetime import datetime

def run_full_analysis(symbol: str):
    """Chạy phân tích tổng hợp cho 1 mã"""
    
    print(f"\n{'#'*70}")
    print(f"#   PHAN TICH TONG HOP: {symbol}")
    print(f"#   Ngay: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'#'*70}")
    
    results = {}
    
    # 1. Phân tích kỹ thuật nâng cao
    print(f"\n[1/4] PHAN TICH KY THUAT NANG CAO...")
    try:
        from advanced_analysis import load_data, add_technical_indicators, create_labels, prepare_features, train_model, predict_probability
        
        csv_path = f"data/{symbol}.csv"
        if os.path.exists(csv_path):
            df = load_data(csv_path)
            df = add_technical_indicators(df)
            df = create_labels(df, forward_days=5, threshold=0.02)
            X, y, feature_cols = prepare_features(df)
            
            if len(X) >= 100:
                model, accuracy, _, _, _ = train_model(X, y)
                prediction = predict_probability(model, df, feature_cols)
                
                results["technical"] = {
                    "accuracy": accuracy,
                    "prediction": prediction
                }
                print(f"   Do chinh xac model: {accuracy*100:.1f}%")
                print(f"   Du doan: {prediction['prediction']} (xac suat tang: {prediction['prob_up']:.1f}%)")
    except Exception as e:
        print(f"   Loi: {e}")
    
    # 2. Phân tích đa khung thời gian
    print(f"\n[2/4] PHAN TICH DA KHUNG THOI GIAN...")
    try:
        from multi_timeframe import multi_timeframe_analysis
        mtf_results = multi_timeframe_analysis(symbol)
        if mtf_results:
            results["multi_timeframe"] = mtf_results
    except Exception as e:
        print(f"   Loi: {e}")
    
    # 3. Phân tích sentiment
    print(f"\n[3/4] PHAN TICH SENTIMENT...")
    try:
        from sentiment_analysis import analyze_stock_sentiment, print_summary
        sentiment = analyze_stock_sentiment(symbol, use_sample=True)
        if "error" not in sentiment:
            results["sentiment"] = sentiment
            print(f"   Sentiment: {sentiment['overall_label']} (diem: {sentiment['avg_score']:.2f})")
    except Exception as e:
        print(f"   Loi: {e}")
    
    # 4. Phân tích vĩ mô
    print(f"\n[4/4] PHAN TICH VI MO...")
    try:
        from macro_analysis import macro_analysis
        macro_results, impacts = macro_analysis()
        if macro_results:
            positive = sum(1 for i in impacts.values() if i["impact"] == "TICH CUC")
            negative = sum(1 for i in impacts.values() if i["impact"] == "TIEU CUC")
            results["macro"] = {
                "positive": positive,
                "negative": negative,
                "impacts": impacts
            }
    except Exception as e:
        print(f"   Loi: {e}")
    
    # TỔNG KẾT
    print(f"\n{'#'*70}")
    print(f"#   TONG KET PHAN TICH: {symbol}")
    print(f"{'#'*70}")
    
    total_score = 0
    max_score = 0
    
    # Điểm từ technical
    if "technical" in results:
        tech = results["technical"]
        if tech["prediction"]["prob_up"] >= 60:
            total_score += 2
        elif tech["prediction"]["prob_up"] >= 50:
            total_score += 1
        elif tech["prediction"]["prob_up"] < 40:
            total_score -= 1
        max_score += 2
        print(f"\n  [KY THUAT] Xac suat tang: {tech['prediction']['prob_up']:.1f}%")
    
    # Điểm từ multi-timeframe
    if "multi_timeframe" in results:
        mtf = results["multi_timeframe"]
        mtf_score = sum(r.get("score", 0) for r in mtf.values())
        if mtf_score > 6:
            total_score += 2
        elif mtf_score > 0:
            total_score += 1
        elif mtf_score < -6:
            total_score -= 2
        elif mtf_score < 0:
            total_score -= 1
        max_score += 2
        print(f"  [DA KHUNG] Diem: {mtf_score}")
    
    # Điểm từ sentiment
    if "sentiment" in results:
        sent = results["sentiment"]
        if sent["overall_label"] == "TICH CUC":
            total_score += 1
        elif sent["overall_label"] == "TIEU CUC":
            total_score -= 1
        max_score += 1
        print(f"  [SENTIMENT] {sent['overall_label']}")
    
    # Điểm từ macro
    if "macro" in results:
        macro = results["macro"]
        if macro["positive"] > macro["negative"]:
            total_score += 1
        elif macro["negative"] > macro["positive"]:
            total_score -= 1
        max_score += 1
        print(f"  [VI MO] Tich cuc: {macro['positive']}, Tieu cuc: {macro['negative']}")
    
    # Khuyến nghị cuối cùng
    print(f"\n  TONG DIEM: {total_score}/{max_score}")
    
    print(f"\n  {'='*50}")
    if total_score >= 4:
        print(f"  >>> KHUYEN NGHI: MUA MANH <<<")
        print(f"  Do tin cay: CAO")
    elif total_score >= 2:
        print(f"  >>> KHUYEN NGHI: XEM XET MUA <<<")
        print(f"  Do tin cay: TRUNG BINH")
    elif total_score <= -4:
        print(f"  >>> KHUYEN NGHI: BAN/TRANH <<<")
        print(f"  Do tin cay: CAO")
    elif total_score <= -2:
        print(f"  >>> KHUYEN NGHI: CAN THAN <<<")
        print(f"  Do tin cay: TRUNG BINH")
    else:
        print(f"  >>> KHUYEN NGHI: THEO DOI <<<")
        print(f"  Do tin cay: THAP")
    print(f"  {'='*50}")
    
    return results

if __name__ == "__main__":
    data_dir = "data"
    csv_files = [f.replace(".csv", "") for f in os.listdir(data_dir) if f.endswith(".csv")]
    
    print("Cac ma co phieu da tai:")
    print(", ".join(csv_files))
    
    symbol = input("\nNhap ma muon phan tich tong hop (VD: FPT): ").strip().upper()
    
    run_full_analysis(symbol)
