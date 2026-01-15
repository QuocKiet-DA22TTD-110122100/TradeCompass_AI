"""
TradeCompass AI - Main Backend Application
A comprehensive trading AI platform for everyone
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

# Initialize FastAPI app
app = FastAPI(
    title="TradeCompass AI",
    description="AI-powered trading insights and recommendations for everyone",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers
from api.routes import market, predictions, health

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(market.router, prefix="/api/market", tags=["market"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["predictions"])

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "TradeCompass AI",
        "version": "1.0.0",
        "description": "AI-powered trading ecosystem accessible to everyone",
        "endpoints": {
            "health": "/health",
            "market": "/api/market",
            "predictions": "/api/predictions",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
