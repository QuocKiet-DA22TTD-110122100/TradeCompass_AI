# TradeCompass AI - API Reference

## Base URL

```
http://localhost:8000
```

For production, replace with your deployed API URL.

## API Overview

TradeCompass AI provides a RESTful API for accessing market data, AI predictions, and trading signals.

## Authentication

Currently, the API is open and doesn't require authentication. In production, implement proper authentication mechanisms.

## Endpoints

### Health & Status

#### GET /health

Check if the API is healthy and running.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-15T17:10:26.984684",
  "service": "TradeCompass AI"
}
```

#### GET /status

Get detailed status of all system components.

**Response:**
```json
{
  "status": "operational",
  "version": "1.0.0",
  "timestamp": "2026-01-15T17:10:26.984684",
  "components": {
    "api": "operational",
    "ai_engine": "operational",
    "market_data": "operational"
  }
}
```

### Market Data

#### GET /api/market/overview

Get overall market overview including indices and top movers.

**Response:**
```json
{
  "market": "Global Markets",
  "status": "open",
  "timestamp": "2026-01-15T17:10:34.261057",
  "indices": [
    {
      "name": "S&P 500",
      "value": 4783.45,
      "change": 0.65
    }
  ],
  "top_gainers": [
    {
      "symbol": "AAPL",
      "price": 195.71,
      "change": 4.32,
      "change_percent": 2.26,
      "volume": 58432100,
      "timestamp": "2026-01-15T17:10:34.261063"
    }
  ],
  "top_losers": [...]
}
```

#### GET /api/market/quote/{symbol}

Get real-time quote for a specific stock symbol.

**Parameters:**
- `symbol` (path): Stock symbol (e.g., AAPL, MSFT)

**Example:**
```bash
curl http://localhost:8000/api/market/quote/AAPL
```

**Response:**
```json
{
  "symbol": "AAPL",
  "price": 195.71,
  "open": 193.50,
  "high": 196.45,
  "low": 192.80,
  "volume": 58432100,
  "change": 4.32,
  "change_percent": 2.26,
  "timestamp": "2026-01-15T17:10:34.261063",
  "market_cap": "3.04T",
  "pe_ratio": 31.45
}
```

#### GET /api/market/history/{symbol}

Get historical data for a stock.

**Parameters:**
- `symbol` (path): Stock symbol
- `period` (query): Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 5y) - default: 1mo
- `interval` (query): Data interval (1m, 5m, 15m, 1h, 1d, 1wk, 1mo) - default: 1d

**Example:**
```bash
curl "http://localhost:8000/api/market/history/AAPL?period=1mo&interval=1d"
```

**Response:**
```json
{
  "symbol": "AAPL",
  "period": "1mo",
  "interval": "1d",
  "data": [
    {
      "date": "2026-01-15T00:00:00",
      "open": 193.50,
      "high": 196.45,
      "low": 192.80,
      "close": 195.71,
      "volume": 58432100
    }
  ]
}
```

#### GET /api/market/search

Search for stock symbols.

**Parameters:**
- `q` (query): Search query

**Example:**
```bash
curl "http://localhost:8000/api/market/search?q=apple"
```

**Response:**
```json
{
  "query": "apple",
  "results": [
    {
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "exchange": "NASDAQ"
    }
  ]
}
```

### AI Predictions

#### POST /api/predictions/predict

Get AI price prediction for a stock.

**Request Body:**
```json
{
  "symbol": "AAPL",
  "horizon": "1d"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/predictions/predict \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL","horizon":"1d"}'
```

**Response:**
```json
{
  "symbol": "AAPL",
  "horizon": "1d",
  "current_price": 195.71,
  "predicted_price": 198.21,
  "predicted_change": 2.5,
  "predicted_change_percent": 1.28,
  "confidence": 0.75,
  "direction": "up",
  "recommendation": "buy",
  "timestamp": "2026-01-15T17:10:42.798512",
  "factors": [
    {
      "name": "Technical Analysis",
      "score": 0.72,
      "impact": "positive"
    }
  ]
}
```

#### GET /api/predictions/signals

Get current trading signals.

**Parameters:**
- `limit` (query): Number of signals to return (default: 10)

**Example:**
```bash
curl "http://localhost:8000/api/predictions/signals?limit=5"
```

**Response:**
```json
{
  "signals": [
    {
      "symbol": "AAPL",
      "signal_type": "buy",
      "strength": 65,
      "price": 195.71,
      "reasoning": "AI detected strong buy signal...",
      "timestamp": "2026-01-15T17:10:34.259649"
    }
  ],
  "count": 5
}
```

#### GET /api/predictions/recommendations

Get personalized trading recommendations.

**Parameters:**
- `risk_level` (query): Risk level (low, medium, high) - default: medium

**Example:**
```bash
curl "http://localhost:8000/api/predictions/recommendations?risk_level=medium"
```

**Response:**
```json
{
  "risk_level": "medium",
  "recommendations": [
    {
      "symbol": "AAPL",
      "action": "buy",
      "confidence": 0.82,
      "target_price": 210.00,
      "stop_loss": 185.00,
      "reasoning": "Strong fundamentals...",
      "risk_level": "low",
      "time_horizon": "medium-term"
    }
  ],
  "count": 3,
  "timestamp": "2026-01-15T17:10:34.259649"
}
```

#### GET /api/predictions/sentiment/{symbol}

Get AI sentiment analysis for a stock.

**Parameters:**
- `symbol` (path): Stock symbol

**Example:**
```bash
curl http://localhost:8000/api/predictions/sentiment/AAPL
```

**Response:**
```json
{
  "symbol": "AAPL",
  "overall_sentiment": "positive",
  "sentiment_score": 0.72,
  "news_sentiment": 0.68,
  "social_sentiment": 0.75,
  "analyst_sentiment": 0.73,
  "sources_analyzed": 247,
  "timestamp": "2026-01-15T17:10:34.259649",
  "key_topics": [
    {
      "topic": "AI Innovation",
      "sentiment": "positive",
      "mentions": 45
    }
  ]
}
```

## Error Responses

All endpoints may return the following error responses:

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "symbol"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

Currently, there are no rate limits. In production, implement appropriate rate limiting.

## CORS

The API allows cross-origin requests from any origin. In production, configure specific allowed origins.

## Interactive Documentation

Visit http://localhost:8000/docs for interactive API documentation powered by Swagger UI.

## Code Examples

### Python

```python
import requests

# Get market overview
response = requests.get('http://localhost:8000/api/market/overview')
data = response.json()
print(data)

# Get AI prediction
response = requests.post(
    'http://localhost:8000/api/predictions/predict',
    json={'symbol': 'AAPL', 'horizon': '1d'}
)
prediction = response.json()
print(f"Predicted price: ${prediction['predicted_price']}")
```

### JavaScript

```javascript
// Get market overview
fetch('http://localhost:8000/api/market/overview')
  .then(response => response.json())
  .then(data => console.log(data));

// Get AI prediction
fetch('http://localhost:8000/api/predictions/predict', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    symbol: 'AAPL',
    horizon: '1d'
  })
})
  .then(response => response.json())
  .then(prediction => {
    console.log(`Predicted price: $${prediction.predicted_price}`);
  });
```

### cURL

```bash
# Get market overview
curl http://localhost:8000/api/market/overview

# Get stock quote
curl http://localhost:8000/api/market/quote/AAPL

# Get AI prediction
curl -X POST http://localhost:8000/api/predictions/predict \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL","horizon":"1d"}'

# Get trading signals
curl "http://localhost:8000/api/predictions/signals?limit=5"
```

## Support

For issues or questions about the API, please create an issue on GitHub or contact support@tradecompass-ai.com.
