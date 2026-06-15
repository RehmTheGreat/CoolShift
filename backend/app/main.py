"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.database import engine, Base
from app.routers import scenarios, data_import, optimization, results, export
from app.schemas import HealthResponse

# Create SQLite database directory if it does not exist
os.makedirs("./data", exist_ok=True)

# Initialize database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CoolShift API",
    description="Cooling energy optimization decision support engine",
    version="1.0.0",
)

# CORS configuration
# Allow local Next.js frontend calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API module routers
app.include_router(scenarios.router, prefix="/api")
app.include_router(data_import.router, prefix="/api")
app.include_router(optimization.router, prefix="/api")
app.include_router(results.router, prefix="/api")
app.include_router(export.router, prefix="/api")

@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    """Health status check endpoint."""
    return HealthResponse()
