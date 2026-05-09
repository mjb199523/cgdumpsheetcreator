"""
Assessment Content Operations Platform — FastAPI Application Entry Point.
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import CORS_ORIGINS, OUTPUT_DIR, MEDIA_DIR
from app.api.routes import auth, upload, parse, validate, export, media, dashboard

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

app = FastAPI(
    title="Assessment Content Operations Platform",
    description="Automates creation, validation, and management of assessment dump sheets for SBA, PAT, and NIPUN workflows.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file serving for media
app.mount("/static/media", StaticFiles(directory=str(MEDIA_DIR)), name="media")
app.mount("/static/output", StaticFiles(directory=str(OUTPUT_DIR)), name="output")

# Register routers
app.include_router(auth.router, prefix="/api")
app.include_router(upload.router, prefix="/api")
app.include_router(parse.router, prefix="/api")
app.include_router(validate.router, prefix="/api")
app.include_router(export.router, prefix="/api")
app.include_router(media.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")


@app.get("/")
async def root():
    return {
        "name": "Assessment Content Operations Platform",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}
