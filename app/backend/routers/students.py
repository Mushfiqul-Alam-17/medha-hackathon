"""
MEDHA — Students Router
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas

router = APIRouter(prefix="/students", tags=["students"])


@router.post("/register", response_model=schemas.StudentResponse)
def register_student(req: schemas.StudentRegister, db: Session = Depends(get_db)):
    """Register a new student."""
    # Check if username exists
    existing = db.query(models.Student).filter(models.Student.username == req.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")

    student = models.Student(username=req.username)
    db.add(student)
    db.commit()
    db.refresh(student)

    return schemas.StudentResponse.model_validate(student)


@router.post("/login", response_model=schemas.StudentLoginResponse)
def login_student(req: schemas.StudentLogin, db: Session = Depends(get_db)):
    """Simple login (no password)."""
    student = db.query(models.Student).filter(models.Student.username == req.username).first()
    
    if student:
        return {
            "student_id": student.id,
            "username": student.username,
            "exists": True,
            "total_sessions": student.total_sessions
        }
    else:
        # Auto-register pattern (low friction)
        new_student = models.Student(username=req.username)
        db.add(new_student)
        db.commit()
        db.refresh(new_student)
        return {
            "student_id": new_student.id,
            "username": new_student.username,
            "exists": False,
            "total_sessions": 0
        }
