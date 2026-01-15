"""
AI Predictions Endpoints
Provides AI-powered trading predictions and recommendations
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from core.config import (
    SAMPLE_BASE_PRICE, PREDICTION_POSITIVE_CHANGE, 
    PREDICTION_NEGATIVE_CHANGE, DEFAULT_CONFIDENCE
)

router = APIRouter()

class PredictionRequest(BaseModel):
    symbol: str
    horizon: str = "1d"  # 1d, 1w, 1m

class Prediction(BaseModel):
    symbol: str
    current_price: float
    predicted_price: float
    confidence: float
    direction: str  # "up", "down", "neutral"
    recommendation: str  # "buy", "sell", "hold"
    timestamp: str

class Signal(BaseModel):
    symbol: str
    signal_type: str  # "buy", "sell"
    strength: float  # 0-100
    price: float
    reasoning: str
    timestamp: str

@router.post("/predict")
async def predict_price(request: PredictionRequest):
    """Get AI price prediction for a symbol"""
    # Sample AI prediction - in production, use real ML model
    current_price = SAMPLE_BASE_PRICE
    predicted_change = PREDICTION_POSITIVE_CHANGE if hash(request.symbol) % 2 == 0 else PREDICTION_NEGATIVE_CHANGE
    predicted_price = current_price + predicted_change
    confidence = DEFAULT_CONFIDENCE
    
    direction = "up" if predicted_change > 0 else "down" if predicted_change < 0 else "neutral"
    recommendation = "buy" if direction == "up" and confidence > 0.7 else \
                    "sell" if direction == "down" and confidence > 0.7 else "hold"
    
    return {
        "symbol": request.symbol.upper(),
        "horizon": request.horizon,
        "current_price": current_price,
        "predicted_price": round(predicted_price, 2),
        "predicted_change": round(predicted_change, 2),
        "predicted_change_percent": round((predicted_change / current_price) * 100, 2),
        "confidence": confidence,
        "direction": direction,
        "recommendation": recommendation,
        "timestamp": datetime.now().isoformat(),
        "factors": [
            {"name": "Technical Analysis", "score": 0.72, "impact": "positive"},
            {"name": "Market Sentiment", "score": 0.68, "impact": "positive"},
            {"name": "Volume Trend", "score": 0.81, "impact": "positive"}
        ]
    }

@router.get("/signals")
async def get_trading_signals(
    limit: int = Query(10, description="Number of signals to return")
):
    """Get current trading signals"""
    # Sample signals - in production, generate from real AI model
    symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "NFLX"]
    signals = []
    
    for i, symbol in enumerate(symbols[:limit]):
        signal_type = "buy" if i % 2 == 0 else "sell"
        strength = 65 + (i * 5) % 30
        
        signals.append({
            "symbol": symbol,
            "signal_type": signal_type,
            "strength": strength,
            "price": 195.71 + i * 10,
            "reasoning": f"AI detected strong {signal_type} signal based on technical indicators and market sentiment",
            "timestamp": datetime.now().isoformat()
        })
    
    return {"signals": signals, "count": len(signals)}

@router.get("/recommendations")
async def get_recommendations(
    risk_level: str = Query("medium", description="Risk level: low, medium, high")
):
    """Get personalized trading recommendations"""
    # Sample recommendations - in production, use user profile and AI model
    recommendations = [
        {
            "symbol": "AAPL",
            "action": "buy",
            "confidence": 0.82,
            "target_price": 210.00,
            "stop_loss": 185.00,
            "reasoning": "Strong fundamentals, positive technical indicators, and growing market share in AI space",
            "risk_level": "low",
            "time_horizon": "medium-term"
        },
        {
            "symbol": "MSFT",
            "action": "hold",
            "confidence": 0.75,
            "target_price": 395.00,
            "stop_loss": 360.00,
            "reasoning": "Solid position, but waiting for better entry point",
            "risk_level": "low",
            "time_horizon": "long-term"
        },
        {
            "symbol": "NVDA",
            "action": "buy",
            "confidence": 0.88,
            "target_price": 550.00,
            "stop_loss": 450.00,
            "reasoning": "AI boom continues, strong demand for GPUs, expanding data center business",
            "risk_level": "medium",
            "time_horizon": "long-term"
        }
    ]
    
    # Filter by risk level
    filtered = [r for r in recommendations if r["risk_level"] == risk_level or risk_level == "all"]
    
    return {
        "risk_level": risk_level,
        "recommendations": filtered,
        "count": len(filtered),
        "timestamp": datetime.now().isoformat()
    }

@router.get("/sentiment/{symbol}")
async def get_sentiment(symbol: str):
    """Get AI sentiment analysis for a symbol"""
    # Sample sentiment - in production, analyze news, social media, etc.
    return {
        "symbol": symbol.upper(),
        "overall_sentiment": "positive",
        "sentiment_score": 0.72,  # -1 to 1
        "news_sentiment": 0.68,
        "social_sentiment": 0.75,
        "analyst_sentiment": 0.73,
        "sources_analyzed": 247,
        "timestamp": datetime.now().isoformat(),
        "key_topics": [
            {"topic": "AI Innovation", "sentiment": "positive", "mentions": 45},
            {"topic": "Revenue Growth", "sentiment": "positive", "mentions": 38},
            {"topic": "Market Competition", "sentiment": "neutral", "mentions": 22}
        ]
    }
