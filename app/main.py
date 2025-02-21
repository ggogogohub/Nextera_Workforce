from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.routes import auth

app = FastAPI(title="NextEra Workforce API", version="1.0.0")

# Registering routes
app.include_router(auth.router, prefix="/auth", tags=["auth"])

@app.on_event("startup")
async def startup_db_client():
    """
    Establish a connection to MongoDB on application startup.
    """
    app.mongodb_client = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db = app.mongodb_client["nextgen"]

@app.on_event("shutdown")
async def shutdown_db_client():
    """
    Close the MongoDB connection on application shutdown.
    """
    app.mongodb_client.close()

@app.get("/")
async def root():
    """
    Root endpoint to verify that the API is running.
    """
    return {"message": "Welcome to NextEra Workforce API"}
