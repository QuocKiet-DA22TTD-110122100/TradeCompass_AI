"""
Configuration constants for the TradeCompass AI backend
"""

# Sample Data Configuration
# These values are used for demonstration purposes
# In production, replace with real market data API calls

# Market Data Sample Values
SAMPLE_INDICES = [
    {"name": "S&P 500", "value": 4783.45, "change": 0.65},
    {"name": "NASDAQ", "value": 15043.23, "change": 1.23},
    {"name": "DOW", "value": 37440.34, "change": 0.43}
]

SAMPLE_BASE_PRICE = 195.71
SAMPLE_PRICE_VOLATILITY = 2.5

# AI Prediction Sample Values
PREDICTION_POSITIVE_CHANGE = 2.5
PREDICTION_NEGATIVE_CHANGE = -1.8
DEFAULT_CONFIDENCE = 0.75

# API Configuration
API_HOST = "0.0.0.0"
API_PORT = 8000
API_TITLE = "TradeCompass AI"
API_VERSION = "1.0.0"
API_DESCRIPTION = "AI-powered trading insights and recommendations for everyone"

# CORS Configuration
CORS_ORIGINS = ["*"]  # In production, specify exact origins
