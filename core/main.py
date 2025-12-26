"""
FastAPI application with APScheduler for Reddit crawler.
"""
import os
import sys
from pathlib import Path

# Setup Django before importing anything else
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.scheduler.scheduler_service import SchedulerService
from src.api.fastapi_routes import router as posts_router
from src.api.auth_routes import router as auth_router
from src.utils.logging import get_logger

logger = get_logger(__name__)

# Global scheduler service
scheduler_service: SchedulerService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    global scheduler_service
    
    # Startup
    logger.info("Starting FastAPI application...")
    try:
        scheduler_service = SchedulerService()
        scheduler_service.start()
        logger.info("APScheduler started successfully")
    except Exception as e:
        logger.error(f"Failed to start scheduler: {str(e)}", exc_info=True)
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down FastAPI application...")
    if scheduler_service:
        try:
            scheduler_service.shutdown()
            logger.info("APScheduler shut down gracefully")
        except Exception as e:
            logger.error(f"Error during scheduler shutdown: {str(e)}", exc_info=True)


# Create FastAPI app
app = FastAPI(
    title="Reddit Crawler API",
    description="Reddit crawling system with scheduled background jobs and worker dashboard",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(auth_router)
app.include_router(posts_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Reddit Crawler API",
        "status": "running",
        "scheduler": "active" if scheduler_service and scheduler_service.is_running() else "inactive"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "scheduler": "active" if scheduler_service and scheduler_service.is_running() else "inactive"
    }


@app.post("/admin/run-crawler")
async def run_crawler_manual():
    """
    Manually trigger the crawler.
    This endpoint runs the crawler immediately, bypassing the schedule.
    """
    if not scheduler_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Scheduler service not available"
        )
    
    try:
        logger.info("Manual crawler trigger requested")
        result = await scheduler_service.run_crawler_job()
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "success",
                "message": "Crawler job completed",
                "result": result
            }
        )
    except Exception as e:
        logger.error(f"Manual crawler trigger failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run crawler: {str(e)}"
        )


@app.get("/admin/scheduler/status")
async def get_scheduler_status():
    """Get scheduler status and information"""
    if not scheduler_service:
        return {
            "status": "not_initialized",
            "running": False
        }
    
    return {
        "status": "running" if scheduler_service.is_running() else "stopped",
        "running": scheduler_service.is_running(),
        "job_running": scheduler_service.is_job_running(),
        "next_run": scheduler_service.get_next_run_time(),
        "interval_hours": scheduler_service.get_interval_hours()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )

