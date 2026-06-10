"""
MEDHA Backend — Main Application Entry Point
Wires everything together: routers, middleware, database init.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from config import settings
import schemas

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("medha")

# Initialize DB tables
init_db()

# Create FastAPI app
app = FastAPI(
    title="MEDHA API",
    description="Behavioral exam analytics platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
from routers import students, questions, sessions, notes, profile, attempts
app.include_router(students.router, prefix="/api")
app.include_router(questions.router, prefix="/api")
app.include_router(sessions.router, prefix="/api")
app.include_router(notes.router, prefix="/api")
app.include_router(profile.router, prefix="/api")
app.include_router(attempts.router, prefix="/api")

# Serve static textbook PDFs with aggressive Cache-Control headers
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

class CachedStaticFiles(StaticFiles):
    def file_response(self, *args, **kwargs):
        response = super().file_response(*args, **kwargs)
        # Aggressive cache headers for textbook PDFs and assets
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        return response

static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", CachedStaticFiles(directory=str(static_dir)), name="static")


@app.get("/", tags=["health"])
async def root():
    return {"message": "MEDHA API is running"}

@app.get("/health", response_model=schemas.HealthResponse, tags=["health"])
async def health_check():
    """Detailed health check including classifier status."""
    from services.classifier_service import check_classifier_available
    from database import SessionLocal
    from models import Question, Student
    
    db = SessionLocal()
    try:
        q_count = db.query(Question).count()
        s_count = db.query(Student).count()
    finally:
        db.close()
        
    return {
        "status": "ok",
        "classifier_available": check_classifier_available(),
        "question_count": q_count,
        "student_count": s_count
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
