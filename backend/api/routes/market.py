"""
Market Data Endpoints
Provides real-time and historical market data
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from core.config import SAMPLE_INDICES, SAMPLE_BASE_PRICE, SAMPLE_PRICE_VOLATILITY

router = APIRouter()

class MarketData(BaseModel):
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    timestamp: str

class MarketOverview(BaseModel):
    market: str
    status: str
    indices: List[dict]
    top_gainers: List[MarketData]
    top_losers: List[MarketData]

@router.get("/overview")
async def get_market_overview():
    """Get overall market overview"""
    # Sample data - in production, fetch from real market data API
    return {
        "market": "Global Markets",
        "status": "open",
        "timestamp": datetime.now().isoformat(),
        "indices": SAMPLE_INDICES,
        "top_gainers": [
            {
                "symbol": "AAPL",
                "price": 195.71,
                "change": 4.32,
                "change_percent": 2.26,
                "volume": 58432100,
                "timestamp": datetime.now().isoformat()
            },
            {
                "symbol": "MSFT",
                "price": 378.91,
                "change": 6.15,
                "change_percent": 1.65,
                "volume": 24531200,
                "timestamp": datetime.now().isoformat()
            }
        ],
        "top_losers": [
            {
                "symbol": "TSLA",
                "price": 238.45,
                "change": -5.23,
                "change_percent": -2.15,
                "volume": 78234500,
                "timestamp": datetime.now().isoformat()
            }
        ]
    }

@router.get("/quote/{symbol}")
async def get_quote(symbol: str):
    """Get real-time quote for a symbol"""
    # Sample data - in production, fetch from real market data API
    return {
        "symbol": symbol.upper(),
        "price": 195.71,
        "open": 193.50,
        "high": 196.45,
        "low": 192.80,
        "volume": 58432100,
        "change": 4.32,
        "change_percent": 2.26,
        "timestamp": datetime.now().isoformat(),
        "market_cap": "3.04T",
        "pe_ratio": 31.45
    }

@router.get("/history/{symbol}")
async def get_history(
    symbol: str,
    period: str = Query("1mo", description="Time period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 5y"),
    interval: str = Query("1d", description="Data interval: 1m, 5m, 15m, 1h, 1d, 1wk, 1mo")
):
    """Get historical data for a symbol"""
    # Sample data - in production, fetch from real market data API
    data_points = []
    days = 30
    base_price = SAMPLE_BASE_PRICE
    
    for i in range(days):
        date = datetime.now() - timedelta(days=days-i)
        price = base_price + (i - days/2) * SAMPLE_PRICE_VOLATILITY
        data_points.append({
            "date": date.isoformat(),
            "open": price - 1.5,
            "high": price + 2.0,
            "low": price - 2.5,
            "close": price,
            "volume": 50000000 + i * 1000000
        })
    
    return {
        "symbol": symbol.upper(),
        "period": period,
        "interval": interval,
        "data": data_points
    }

@router.get("/search")
async def search_symbols(q: str = Query(..., description="Search query")):
    """Search for stock symbols"""
    # Sample data - in production, integrate with real search API
    symbols = [
        {"symbol": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ"},
        {"symbol": "MSFT", "name": "Microsoft Corporation", "exchange": "NASDAQ"},
        {"symbol": "GOOGL", "name": "Alphabet Inc.", "exchange": "NASDAQ"},
        {"symbol": "AMZN", "name": "Amazon.com Inc.", "exchange": "NASDAQ"},
        {"symbol": "TSLA", "name": "Tesla Inc.", "exchange": "NASDAQ"},
    ]
    
    # Filter based on query
    query_lower = q.lower()
    results = [
        s for s in symbols 
        if query_lower in s["symbol"].lower() or query_lower in s["name"].lower()
    ]
    
    return {"query": q, "results": results}
