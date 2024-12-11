from typing import Dict
import logging
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram

from core.config import settings
from core.logging import setup_logging
from api.v1.api import api_router
from db.session import engine
from db.base import Base

# Setup logging
logger = setup_logging()

# Initialize metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"]
)

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="Supply Chain Management API",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.middleware("http")
    async def metrics_middleware(request: Request, call_next):
        """Middleware to collect metrics for each request."""
        start_time = datetime.utcnow()
        
        response = await call_next(request)
        
        # Record metrics
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe((datetime.utcnow() - start_time).total_seconds())
        
        return response
    
    @app.middleware("http")
    async def logging_middleware(request: Request, call_next):
        """Middleware for request logging."""
        start_time = datetime.utcnow()
        
        try:
            response = await call_next(request)
            
            logger.info(
                "Request processed",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration": (datetime.utcnow() - start_time).total_seconds()
                }
            )
            
            return response
            
        except Exception as e:
            logger.error(
                "Request failed",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(e)
                }
            )
            
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"}
            )
    
    # Include API router
    app.include_router(
        api_router,
        prefix="/api/v1"
    )
    
    @app.get("/health")
    async def health_check() -> Dict[str, str]:
        """Health check endpoint."""
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    return app

app = create_app() 