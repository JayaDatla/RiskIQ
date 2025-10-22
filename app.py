#!/usr/bin/env python3
"""
Hugging Face Spaces entry point for RiskIQ Web Application
This file serves both the API and the frontend for HF Spaces deployment.
"""

import os
import sys
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Add the backend directory to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Import the API routes
from backend.api.app import app as api_app

# Create the main FastAPI app
app = FastAPI(
    title="RiskIQ - Advanced Risk Analysis Platform",
    description="A comprehensive risk analysis platform with AI-powered volatility forecasting",
    version="1.0.0",
)

# Add CORS middleware for HF Spaces
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for HF Spaces
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the API routes
app.mount("/api", api_app)

# Mount static files (frontend)
frontend_path = Path(__file__).parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")


# Root endpoint - serve the frontend
@app.get("/")
async def read_root():
    """Serve the main frontend page"""
    frontend_file = frontend_path / "index.html"
    if frontend_file.exists():
        return FileResponse(str(frontend_file))
    else:
        return {"message": "RiskIQ API is running! Frontend not found."}


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for HF Spaces"""
    return {"status": "healthy", "message": "RiskIQ is running!"}


# API documentation redirect
@app.get("/docs")
async def api_docs():
    """Redirect to API documentation"""
    from fastapi.responses import RedirectResponse

    return RedirectResponse(url="/api/docs")


if __name__ == "__main__":
    # Get port from environment variable (HF Spaces sets this)
    port = int(os.environ.get("PORT", 7860))

    # Run the server
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload in production
    )
