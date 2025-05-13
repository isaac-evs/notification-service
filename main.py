# main.py for Notification Service with CloudWatch metrics middleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.database import engine
from app.models.notification import Notification
from app.views import notification as notification_views
from app.middleware.metrics import CloudWatchMetricsMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("notification_service")

# Create database tables
Notification.__table__.create(bind=engine, checkfirst=True)

app = FastAPI(title="Notification Service")

# Add CloudWatch metrics middleware
app.add_middleware(CloudWatchMetricsMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(notification_views.router, prefix="/api/notifications", tags=["notifications"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Notification Service API"}

@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers and monitoring"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)
