"""
TradeCompass AI - Main Backend Application
A comprehensive trading AI platform for everyone
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from core.config import (
    API_HOST, API_PORT, API_TITLE, API_VERSION, 
    API_DESCRIPTION, CORS_ORIGINS
)

# Initialize FastAPI app
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
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
        "name": API_TITLE,
        "version": API_VERSION,
        "description": API_DESCRIPTION,
        "endpoints": {
            "health": "/health",
            "market": "/api/market",
            "predictions": "/api/predictions",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host=API_HOST, port=API_PORT, reload=True)
